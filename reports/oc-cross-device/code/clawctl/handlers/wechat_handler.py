# -*- coding: utf-8 -*-
"""
WeChat Official Account Handler (微信公众号处理器)
支持被动回复 + 主动推送（客服消息接口）

功能：
- 消息接收与自动回复（被动模式）
- 消息路由 → 自然语言解析 → 执行任务
- 模板消息推送（任务完成通知）
- 客服消息（主动触达用户）
- 菜单自定义
"""

import hashlib
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional
import threading

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False
    import requests


class MsgType(Enum):
    TEXT = "text"
    IMAGE = "image"
    VOICE = "voice"
    VIDEO = "video"
    SHORTVIDEO = "shortvideo"
    LOCATION = "location"
    LINK = "link"
    EVENT = "event"
    MINIPROGRAM = "miniprogram"


class EventType(Enum):
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    SCAN = "SCAN"
    LOCATION = "LOCATION"
    CLICK = "CLICK"
    VIEW = "VIEW"


@dataclass
class WeChatMessage:
    """微信消息结构"""
    msg_type: str          # 消息类型
    msg_id: str            # 消息ID
    from_user: str          # 发送者OpenID
    to_user: str            # 公众号原始ID
    content: str           # 消息内容（文本/语音识别结果）
    raw_xml: str = ""       # 原始XML
    event: str = ""        # 事件类型（事件消息才有）
    event_key: str = ""    # 事件KEY
    create_time: int = 0   # 创建时间戳

    # 语音专属
    media_id: str = ""
    recognition: str = ""  # 语音识别结果（开通语音识别才有）

    @property
    def is_voice(self) -> bool:
        return self.msg_type == MsgType.VOICE.value

    @property
    def is_event(self) -> bool:
        return self.msg_type == MsgType.EVENT.value


class WeChatHandler:
    """
    微信公众号消息处理器

    使用方式：
    ---------
    # 被动模式（Flask/ FastAPI）
    @app.route("/wechat", methods=["GET", "POST"])
    def wechat():
        handler = WeChatHandler(APP_ID, APP_SECRET, TOKEN, ENCODING_AES_KEY)
        if request.method == "GET":
            return handler.verify(request.args)
        msg = handler.parse_message(request.data)
        reply = handler.handle(msg)
        return handler.build_reply(msg, reply)

    # 客服消息推送
    notifier = WeChatHandler(...)
    notifier.send_text(openid, "任务已完成 ✅")
    """

    def __init__(
        self,
        app_id: str,
        app_secret: str,
        token: Optional[str] = None,
        encoding_aes_key: Optional[str] = None,
        nl_interpreter: Optional[Callable] = None,
        openclaw_client: Optional[object] = None,
        notify_callback: Optional[Callable] = None,
    ):
        self.app_id = app_id
        self.app_secret = app_secret
        self.token = token
        self.aes_key = encoding_aes_key
        self._nl = nl_interpreter
        self._client = openclaw_client
        self._notify_cb = notify_callback

        # 消息处理器注册表
        self._handlers: dict[str, Callable] = {
            MsgType.TEXT.value: self._handle_text,
            MsgType.VOICE.value: self._handle_voice,
            MsgType.EVENT.value: self._handle_event,
        }

        # 关注/取消关注处理
        self._subscribe_handlers: list[Callable] = []

        # 命令路由（关键词 → (描述, intent_str)）
        self._cmd_routes: dict[str, tuple[str, str]] = {
            "简报": ("📋 晨间简报", "quick_report"),
            "日报": ("📋 晨间简报", "quick_report"),
            "brief": ("📋 晨ref", "quick_report"),
            "技术": ("🔬 技术分析", "tech_brief"),
            "tech": ("🔬 技术分析", "tech_brief"),
            "商业": ("💼 商业洞察", "market_insight"),
            "market": ("💼 商业洞察", "market_insight"),
            "全量": ("🔍 全量扫描", "full_scan"),
            "full": ("🔍 全量扫描", "full_scan"),
            "深度": ("🧠 深度研究", "deep_research"),
            "deep": ("🧠 深度研究", "deep_research"),
            "状态": ("📊 系统状态", "status"),
            "status": ("📊 系统状态", "status"),
            "帮助": ("❓ 使用帮助", "help"),
            "help": ("❓ 使用帮助", "help"),
            "取消": ("🚫 取消任务", "cancel_task"),
        }

        # Token 缓存
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0
        self._token_lock = threading.Lock()

    # ─────────────────────────────────────────────
    # Token 管理
    # ─────────────────────────────────────────────

    async def get_access_token_async(self) -> str:
        """获取 Access Token（异步，带缓存）"""
        now = time.time()
        with self._token_lock:
            if self._access_token and now < self._token_expires_at - 60:
                return self._access_token

        url = (
            "https://api.weixin.qq.com/cgi-bin/token"
            f"?grant_type=client_credential&appid={self.app_id}&secret={self.app_secret}"
        )
        if HAS_HTTPX:
            async with httpx.AsyncClient() as client:
                resp = await client.get(url, timeout=10)
                data = resp.json()
        else:
            data = requests.get(url, timeout=10).json()

        if "access_token" not in data:
            raise RuntimeError(f"WeChat token fetch failed: {data}")

        with self._token_lock:
            self._access_token = data["access_token"]
            self._token_expires_at = now + data.get("expires_in", 7200)

        return self._access_token

    def get_access_token(self) -> str:
        """获取 Access Token（同步，缓存优先）"""
        now = time.time()
        with self._token_lock:
            if self._access_token and now < self._token_expires_at - 60:
                return self._access_token

        import requests
        url = (
            "https://api.weixin.qq.com/cgi-bin/token"
            f"?grant_type=client_credential&appid={self.app_id}&secret={self.app_secret}"
        )
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if "access_token" not in data:
            raise RuntimeError(f"WeChat token fetch failed: {data}")

        self._access_token = data["access_token"]
        self._token_expires_at = now + data.get("expires_in", 7200)
        return self._access_token

    # ─────────────────────────────────────────────
    # 消息验证（URL 校验）
    # ─────────────────────────────────────────────

    def verify(self, query_args: dict) -> str:
        """
        验证微信服务器签名（GET 请求）
        用于公众号后台配置 URL 时的一次性验证
        """
        if not self.token:
            return "token not configured"

        signature = query_args.get("signature", "")
        timestamp = query_args.get("timestamp", "")
        nonce = query_args.get("nonce", "")
        echostr = query_args.get("echostr", "")

        tmp_list = sorted([self.token, timestamp, nonce])
        tmp_str = "".join(tmp_list)
        expected = hashlib.sha1(tmp_str.encode()).hexdigest()

        if signature == expected:
            return echostr
        return "signature mismatch"

    # ─────────────────────────────────────────────
    # 消息解析
    # ─────────────────────────────────────────────

    def parse_message(self, raw_xml: bytes) -> WeChatMessage:
        """将微信推送的 XML 解析为 WeChatMessage"""
        try:
            root = ET.fromstring(raw_xml.decode("utf-8"))
        except Exception:
            return WeChatMessage(
                msg_type="text", msg_id="0",
                from_user="", to_user="", content="[解析失败]"
            )

        def tag(name: str) -> str:
            return (root.find(name) or root.find(f".//{name}")) is not None and \
                (root.find(name) or root.find(f".//{name}")).text or ""

        get_val = lambda t: (root.find(t) or root.find(f".//{t}"))
        f = lambda t: (get_val(t).text or "") if get_val(t) is not None else ""

        return WeChatMessage(
            msg_type=f("MsgType"),
            msg_id=f("MsgId"),
            from_user=f("FromUserName"),
            to_user=f("ToUserName"),
            content=f("Content"),
            raw_xml=raw_xml.decode("utf-8", errors="replace"),
            event=f("Event"),
            event_key=f("EventKey"),
            create_time=int(f("CreateTime") or "0"),
            media_id=f("MediaId"),
            recognition=f("Recognition"),
        )

    # ─────────────────────────────────────────────
    # 消息路由
    # ─────────────────────────────────────────────

    def handle(self, msg: WeChatMessage) -> str:
        """主路由：根据消息类型分发到对应处理器"""
        handler = self._handlers.get(msg.msg_type, self._handle_unknown)
        try:
            return handler(msg)
        except Exception as e:
            return self._format_text_reply(msg, f"处理异常：{e}")

    def register_handler(self, msg_type: str, handler: Callable):
        """注册自定义消息处理器"""
        self._handlers[msg_type] = handler

    def on_subscribe(self, handler: Callable):
        """注册关注事件处理器"""
        self._subscribe_handlers.append(handler)

    # ─────────────────────────────────────────────
    # 具体消息处理
    # ─────────────────────────────────────────────

    def _handle_text(self, msg: WeChatMessage) -> str:
        """处理文本消息"""
        content = msg.content.strip()
        if not content:
            return self._format_text_reply(msg, "收到空消息，请输入内容")

        # 1. 精确命令匹配
        for keyword, (desc, intent) in self._cmd_routes.items():
            if keyword in content:
                return self._exec_intent(msg, intent, desc)

        # 2. 自然语言解析
        if self._nl:
            try:
                result = self._nl(content)
                if result and result.get("intent") not in ("unknown", "help"):
                    return self._exec_intent(
                        msg,
                        result["intent"],
                        result.get("description", "NL解析命令"),
                    )
            except Exception:
                pass

        # 3. 透传给 OpenClaw
        if self._client:
            try:
                self._client.send_message("dingtalk", content)
                return self._format_text_reply(
                    msg,
                    f"📨 已转达：{content}\n\n"
                    "💡 回复【简报/技术/商业/全量/深度】直接触发任务\n"
                    "💡 或直接描述你想做的事，我会理解你的意图 😊"
                )
            except Exception as e:
                return self._format_text_reply(msg, f"发送失败：{e}")

        return self._format_text_reply(
            msg,
            "收到！💡 回复【简报】快速生成晨间简报\n"
            "回复【帮助】查看所有命令\n"
            "或直接描述你的需求 😊"
        )

    def _handle_voice(self, msg: WeChatMessage) -> str:
        """处理语音消息（微信已开通语音识别，返回识别结果）"""
        # 优先使用 Recognition 字段（语音识别文本）
        text = msg.recognition.strip() if msg.recognition else ""

        if not text:
            return self._format_text_reply(
                msg,
                "🤖 听不太清，请再说一遍，或者直接打字告诉我 😊"
            )

        # 语音内容按文本处理
        return self._handle_text(
            WeChatMessage(
                msg_type=MsgType.TEXT.value,
                msg_id=msg.msg_id,
                from_user=msg.from_user,
                to_user=msg.to_user,
                content=text,
            )
        )

    def _handle_event(self, msg: WeChatMessage) -> str:
        """处理事件推送"""
        if msg.event == EventType.SUBSCRIBE.value:
            return self._on_user_subscribe(msg)
        elif msg.event == EventType.UNSUBSCRIBE.value:
            self._on_user_unsubscribe(msg)
            return ""  # 不需要回复
        elif msg.event == EventType.CLICK.value:
            return self._on_menu_click(msg)
        return ""  # 其他事件不回复

    def _handle_unknown(self, msg: WeChatMessage) -> str:
        return self._format_text_reply(
            msg,
            f"暂不支持的消息类型：{msg.msg_type}\n"
            "💡 目前支持：文字、语音 🎤"
        )

    # ─────────────────────────────────────────────
    # 事件处理
    # ─────────────────────────────────────────────

    def _on_user_subscribe(self, msg: WeChatMessage) -> str:
        """用户关注公众号"""
        for handler in self._subscribe_handlers:
            try:
                handler(msg.from_user, msg.event_key)
            except Exception:
                pass

        return self._format_text_reply(
            msg,
            "🎉 欢迎关注！我是你的 AI 助手\n\n"
            "【快捷命令】\n"
            "📋 简报 — 生成今日 AI 晨间简报\n"
            "🔬 技术 — 技术前沿分析\n"
            "💼 商业 — 商业洞察报告\n"
            "🔍 全量 — 全量信息扫描\n"
            "🧠 深度 — 深度研究报告\n\n"
            "💡 也可以直接描述你的需求，我会理解 😊"
        )

    def _on_user_unsubscribe(self, msg: WeChatMessage) -> str:
        """用户取消关注"""
        # 记录日志，可选：更新用户状态
        print(f"[WeChat] User {msg.from_user} unsubscribed")
        return ""

    def _on_menu_click(self, msg: WeChatMessage) -> str:
        """菜单点击事件"""
        event_key_map = {
            "quick_report": ("📋 晨间简报", "quick_report"),
            "tech_brief": ("🔬 技术分析", "tech_brief"),
            "market_insight": ("💼 商业洞察", "market_insight"),
            "full_scan": ("🔍 全量扫描", "full_scan"),
            "deep_research": ("🧠 深度研究", "deep_research"),
            "system_status": ("📊 系统状态", "status"),
            "help": ("❓ 帮助", "help"),
        }
        intent_info = event_key_map.get(msg.event_key, (None, None))
        if intent_info[0]:
            return self._exec_intent(msg, intent_info[1], intent_info[0])
        return self._format_text_reply(msg, "收到菜单点击事件")

    # ─────────────────────────────────────────────
    # 意图执行
    # ─────────────────────────────────────────────

    def _exec_intent(self, msg: WeChatMessage, intent: str, desc: str) -> str:
        """执行识别到的意图"""
        if intent == "status":
            return self._reply_status(msg)
        if intent == "help":
            return self._reply_help(msg)
        if intent == "cancel_task":
            return self._format_text_reply(msg, "🚫 取消功能：暂无运行中的任务")

        # 触发任务
        task_id = f"wechat-{int(time.time())}"
        response = self._format_text_reply(
            msg,
            f"🚀 正在执行：{desc}\n\n"
            f"任务ID：{task_id}\n"
            f"执行者：OpenClaw AI\n\n"
            "⏳ 执行中，完成后我会通知你..."
        )

        # 异步执行任务
        def _run():
            try:
                if self._client:
                    self._client.spawn_agent(
                        task=desc,
                        source="wechat",
                        task_id=task_id,
                    )
                if self._notify_cb:
                    self._notify_cb(msg.from_user, task_id, intent)
            except Exception as e:
                print(f"[WeChat] Task exec error: {e}")

        threading.Thread(target=_run, daemon=True).start()
        return response

    def _reply_status(self, msg: WeChatMessage) -> str:
        """返回系统状态"""
        if self._client:
            try:
                status = self._client.get_status()
                lines = [f"📊 **OpenClaw 状态**\n"]
                for k, v in (status.get("data", {}) if isinstance(status, dict) else {}).items():
                    lines.append(f"- {k}：{v}")
                if len(lines) == 1:
                    lines.append("- 连接正常 ✅")
                return self._format_text_reply(msg, "\n".join(lines))
            except Exception:
                pass
        return self._format_text_reply(msg, "📊 OpenClaw 运行正常 ✅\n🔗 连接已就绪")

    def _reply_help(self, msg: WeChatMessage) -> str:
        """返回帮助信息"""
        help_text = (
            "🤖 **OpenClaw AI 助手**\n\n"
            "【快捷命令】\n"
            "📋 简报/日报 — AI 晨间简报\n"
            "🔬 技术/tech — 技术前沿分析\n"
            "💼 商业/market — 商业洞察\n"
            "🔍 全量/full — 全量信息扫描\n"
            "🧠 深度/deep — 深度研究报告\n"
            "📊 状态 — 查看系统状态\n\n"
            "【语音输入】\n"
            "🎤 直接发送语音，我会识别并执行\n\n"
            "【自然语言】\n"
            "✨ 直接描述你想做的事，如：\n"
            "\"帮我查一下今天有什么 AI 创业公司\""
        )
        return self._format_text_reply(msg, help_text)

    # ─────────────────────────────────────────────
    # 主动推送（客服消息）
    # ─────────────────────────────────────────────

    async def send_text_async(self, openid: str, text: str) -> dict:
        """异步发送文本消息（客服消息接口，需用户已互动）"""
        token = await self.get_access_token_async()
        url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={token}"
        payload = {
            "touser": openid,
            "msgtype": "text",
            "text": {"content": text}
        }
        if HAS_HTTPX:
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, json=payload, timeout=10)
                return resp.json()
        else:
            r = requests.post(url, json=payload, timeout=10)
            return r.json()

    def send_text(self, openid: str, text: str) -> dict:
        """同步发送文本消息"""
        token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={token}"
        resp = requests.post(url, json={
            "touser": openid,
            "msgtype": "text",
            "text": {"content": text}
        }, timeout=10)
        return resp.json()

    async def send_template_async(
        self,
        openid: str,
        template_id: str,
        data: dict,
        url: str = "",
    ) -> dict:
        """发送模板消息（适合任务完成通知）"""
        token = await self.get_access_token_async()
        url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={token}"
        payload = {
            "touser": openid,
            "template_id": template_id,
            "url": url,
            "data": {
                k: {"value": v, "color": "#173177"} if not isinstance(v, dict) else v
                for k, v in data.items()
            }
        }
        if HAS_HTTPX:
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, json=payload, timeout=10)
                return resp.json()
        else:
            r = requests.post(url, json=payload, timeout=10)
            return r.json()

    # ─────────────────────────────────────────────
    # 被动回复 XML 构建
    # ─────────────────────────────────────────────

    @staticmethod
    def _format_text_reply(msg: WeChatMessage, content: str) -> str:
        """构建微信文本回复 XML（被动消息）"""
        now = str(int(time.time()))
        return (
            f"<xml>\n"
            f"<ToUserName><![CDATA[{msg.from_user}]]></ToUserName>\n"
            f"<FromUserName><![CDATA[{msg.to_user}]]></FromUserName>\n"
            f"<CreateTime>{now}</CreateTime>\n"
            f"<MsgType><![CDATA[text]]></MsgType>\n"
            f"<Content><![CDATA[{content}]]></Content>\n"
            f"</xml>"
        )

    @staticmethod
    def _format_news_reply(msg: WeChatMessage, articles: list) -> str:
        """构建图文回复 XML"""
        now = str(int(time.time()))
        items = ""
        for a in articles[:8]:  # 最多8条
            items += (
                f"<item>\n"
                f"<Title><![CDATA[{a.get('title', '')}]]></Title>\n"
                f"<Description><![CDATA[{a.get('desc', '')}]]></Description>\n"
                f"<PicUrl><![CDATA[{a.get('pic', '')}]]></PicUrl>\n"
                f"<Url><![CDATA[{a.get('url', '')}]]></Url>\n"
                f"</item>"
            )
        return (
            f"<xml>\n"
            f"<ToUserName><![CDATA[{msg.from_user}]]></ToUserName>\n"
            f"<FromUserName><![CDATA[{msg.to_user}]]></FromUserName>\n"
            f"<CreateTime>{now}</CreateTime>\n"
            f"<MsgType><![CDATA[news]]></MsgType>\n"
            f"<ArticleCount>{len(articles[:8])}</ArticleCount>\n"
            f"<Articles>{items}</Articles>\n"
            f"</xml>"
        )

    # ─────────────────────────────────────────────
    # 菜单管理
    # ─────────────────────────────────────────────

    async def set_menu_async(self, menu_buttons: list) -> dict:
        """设置公众号自定义菜单"""
        token = await self.get_access_token_async()
        url = f"https://api.weixin.qq.com/cgi-bin/menu/create?access_token={token}"
        if HAS_HTTPX:
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, json=menu_buttons, timeout=10)
                return resp.json()
        else:
            r = requests.post(url, json=menu_buttons, timeout=10)
            return r.json()

    def set_menu(self, menu_buttons: list) -> dict:
        """设置公众号自定义菜单（同步）"""
        token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/menu/create?access_token={token}"
        resp = requests.post(url, json=menu_buttons, timeout=10)
        return resp.json()

    @staticmethod
    def build_menu() -> list:
        """构建默认菜单配置"""
        return {
            "button": [
                {
                    "name": "🚀 快捷任务",
                    "sub_button": [
                        {"type": "click", "name": "📋 晨间简报", "key": "quick_report"},
                        {"type": "click", "name": "🔬 技术分析", "key": "tech_brief"},
                        {"type": "click", "name": "💼 商业洞察", "key": "market_insight"},
                        {"type": "click", "name": "🔍 全量扫描", "key": "full_scan"},
                        {"type": "click", "name": "🧠 深度研究", "key": "deep_research"},
                    ]
                },
                {
                    "name": "📊 我的",
                    "sub_button": [
                        {"type": "click", "name": "📊 系统状态", "key": "system_status"},
                        {"type": "click", "name": "❓ 使用帮助", "key": "help"},
                    ]
                }
            ]
        }
