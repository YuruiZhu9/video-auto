#!/usr/bin/env python3
"""
钉钉交互卡片处理器
支持：消息卡片 / ActionCard / FeedCard / 链接跳转 / 按钮交互

文档参考：https://open.dingtalk.com/document/org/card-messages
"""

import os
import time
import hmac
import hashlib
import base64
import json
import logging
import requests
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

# ── 钉钉卡片常量 ──────────────────────────────────────────────────────────────

DINGTALK_API = "https://oapi.dingtalk.com"
DEFAULT_TIMEOUT = 10


class CardType(Enum):
    """卡片类型"""
    TEXT = "text"                      # 纯文本（通过文本消息）
    MARKDOWN = "markdown"              # Markdown 卡片
    ACTION_CARD = "actionCard"         # ActionCard 互动卡片
    FEED_CARD = "feedCard"            # FeedCard 链接卡片


# ── 消息模板 ──────────────────────────────────────────────────────────────────

TASK_START_TEMPLATE = """\
# 🚀 任务已启动

**任务**：{task_name}
**执行器**：{agent}
**模板**：{template_id}

⏱ 开始时间：{timestamp}
"""

TASK_COMPLETE_TEMPLATE = """\
# ✅ 任务完成

**任务**：{task_name}
**状态**：{status}
⏱ 耗时：{duration}

---

{result_summary}

---
_由 OpenClaw 跨设备控制系统发送_ 🐾
"""

TASK_FAILED_TEMPLATE = """\
# ❌ 任务失败

**任务**：{task_name}
**错误**：{error}

⏱ 开始时间：{started_at}

---
_请检查任务配置或重试_ 🐾
"""

DAG_STATUS_TEMPLATE = """\
# 📊 DAG 执行状态

**DAG**：{dag_name}
**ID**：`{dag_id}`

---

**节点进度**：{completed}/{total}

{node_list}

---

⏱ 运行时长：{elapsed}
"""

STATUS_CARD_TEMPLATE = """\
# 🐾 OpenClaw 状态

**系统**：正常运行 ✅
**时间**：{timestamp}
**会话数**：{session_count}

---

**📡 Agent 运行状态**

{agent_status}

---

**📈 资源使用**

- 💾 内存：{mem_pct}%
- 💿 磁盘：{disk_pct}%

---
_小M · OpenClaw 跨设备控制_ 🤖
"""


# ── 钉钉 API 客户端 ───────────────────────────────────────────────────────────

class DingTalkClient:
    """
    钉钉消息/卡片发送客户端

    支持：
    - 群自定义机器人（Webhook）
    -企业内部应用（access_token）
    - 互动卡片（需要 card_id / template_id）
    """

    def __init__(
        self,
        token: str,
        secret: Optional[str] = None,
        access_token: Optional[str] = None,
        session: Optional[requests.Session] = None,
    ):
        self.token = token
        self.secret = secret
        self._access_token = access_token
        self._session = session or requests.Session()
        self._token_expires_at = 0.0

    # ── 认证 ─────────────────────────────────────────────────────────────────

    def _get_robot_sign(self) -> Dict[str, str]:
        """获取加签签名（群机器人安全模式）"""
        if not self.secret:
            return {}
        timestamp = str(round(time.time() * 1000))
        sign_str = f"{timestamp}\n{self.secret}"
        sign = base64.b64encode(
            hmac.new(sign_str.encode("utf-8"), digestmod=hashlib.sha256).digest()
        ).decode("utf-8")
        return {"timestamp": timestamp, "sign": sign}

    def _get_access_token(self) -> str:
        """获取 Access Token（企业内部应用）"""
        if self._access_token and time.time() < self._token_expires_at - 60:
            return self._access_token

        resp = self._session.get(
            f"{DINGTALK_API}/gettoken",
            params={
                "appkey": self.token,      # 实际使用时替换为 corpid/corpsecret
                "appsecret": self.secret or "",
            },
            timeout=DEFAULT_TIMEOUT,
        )
        data = resp.json()
        if data.get("errcode") == 0:
            self._access_token = data["access_token"]
            self._token_expires_at = time.time() + data.get("expires_in", 7200)
            return self._access_token
        raise RuntimeError(f"获取 AccessToken 失败: {data}")

    # ── 消息发送 ─────────────────────────────────────────────────────────────

    def _post_webhook(self, payload: dict) -> dict:
        """发送群机器人消息"""
        url = f"{DINGTALK_API}/robot/send"
        params = {"access_token": self.token}
        params.update(self._get_robot_sign())

        resp = self._session.post(
            url, json=payload, params=params, timeout=DEFAULT_TIMEOUT
        )
        result = resp.json()
        if result.get("errcode") != 0:
            logger.warning(f"钉钉消息发送失败: {result}")
        return result

    def send_text(self, content: str, at_mobiles: Optional[List[str]] = None) -> dict:
        """发送纯文本消息"""
        return self._post_webhook({
            "msgtype": "text",
            "text": {"content": content},
            "at": {"atMobiles": at_mobiles or []},
        })

    def send_markdown(
        self,
        title: str,
        text: str,
        at_mobiles: Optional[List[str]] = None,
    ) -> dict:
        """发送 Markdown 格式消息（仅支持部分 Markdown）"""
        return self._post_webhook({
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": text,
            },
            "at": {"atMobiles": at_mobiles or []},
        })

    def send_action_card(
        self,
        title: str,
        text: str,
        single_title: Optional[str] = None,
        single_url: Optional[str] = None,
        btn_orientation: str = "0",
        btns: Optional[List[Dict[str, str]]] = None,
    ) -> dict:
        """
        发送 ActionCard 互动卡片

        single_title / single_url: 整卡模式（单个按钮）
        btns: 独立按钮模式 [{"title": "...", "actionURL": "..."}]
        btn_orientation: "0"=竖直 "1"=横向
        """
        card = {
            "title": title,
            "text": text,
            "btn_orientation": btn_orientation,
        }
        if btns:
            card["btns"] = btns
        elif single_title and single_url:
            card["single_title"] = single_title
            card["single_url"] = single_url

        return self._post_webhook({
            "msgtype": "actionCard",
            "actionCard": card,
        })

    def send_feed_card(self, links: List[Dict[str, str]]) -> dict:
        """
        发送 FeedCard 多链接卡片

        links: [{"title": "...", "messageURL": "...", "picURL": "..."}]
        """
        return self._post_webhook({
            "msgtype": "feedCard",
            "feedCard": {"links": links},
        })

    def send_card_with_buttons(
        self,
        title: str,
        content: str,
        buttons: List[Dict[str, str]],
        header: Optional[Dict[str, str]] = None,
    ) -> dict:
        """
        使用独立按钮 ActionCard 发送多按钮卡片

        buttons: [{"title": "按钮名", "actionURL": "https://..."}]
        header: {"title": "标题", " bgcolor": "FFCC99"}  # 顶部颜色条
        """
        card_text = (f"**{title}**\n\n{content}" if header else
                     f"**{title}**\n\n{content}")
        return self.send_action_card(
            title=title,
            text=content,
            btns=buttons,
            btn_orientation="1",  # 横向排列
        )

    # ── 快捷发送 ─────────────────────────────────────────────────────────────

    def notify_task_start(
        self,
        task_name: str,
        agent: str,
        template_id: str = "",
        timestamp: Optional[str] = None,
    ) -> dict:
        ts = timestamp or time.strftime("%Y-%m-%d %H:%M:%S")
        return self.send_markdown(
            title=f"🚀 任务启动：{task_name}",
            text=TASK_START_TEMPLATE.format(
                task_name=task_name,
                agent=agent,
                template_id=template_id,
                timestamp=ts,
            ),
        )

    def notify_task_complete(
        self,
        task_name: str,
        status: str,
        duration: str,
        result_summary: str,
    ) -> dict:
        icon = "✅" if status == "success" else "❌"
        return self.send_markdown(
            title=f"{icon} 任务完成：{task_name}",
            text=TASK_COMPLETE_TEMPLATE.format(
                task_name=task_name,
                status=status,
                duration=duration,
                result_summary=result_summary,
            ),
        )

    def notify_task_failed(
        self,
        task_name: str,
        error: str,
        started_at: str,
    ) -> dict:
        return self.send_markdown(
            title=f"❌ 任务失败：{task_name}",
            text=TASK_FAILED_TEMPLATE.format(
                task_name=task_name,
                error=error,
                started_at=started_at,
            ),
        )

    def notify_dag_status(self, dag) -> dict:
        """发送 DAG 执行状态卡片"""
        total = len(dag.nodes)
        completed = sum(
            1 for n in dag.nodes.values()
            if n.status.value in ("success", "failed", "skipped")
        )
        node_list = "\n".join(
            f"- **{n.id}** ({n.name}): {n.status.value}"
            for n in dag.nodes.values()
        )
        elapsed = ""
        started = min(n.started_at or time.time() for n in dag.nodes.values())
        elapsed_s = int(time.time() - started)
        elapsed = f"{elapsed_s // 60}分{elapsed_s % 60}秒"

        return self.send_markdown(
            title=f"📊 DAG 状态：{dag.name}",
            text=DAG_STATUS_TEMPLATE.format(
                dag_name=dag.name,
                dag_id=dag.dag_id,
                completed=completed,
                total=total,
                node_list=node_list or "_暂无节点_",
                elapsed=elapsed,
            ),
        )

    def notify_system_status(
        self,
        timestamp: str,
        session_count: int,
        agent_status: str,
        mem_pct: float,
        disk_pct: float,
    ) -> dict:
        return self.send_markdown(
            title="🐾 OpenClaw 系统状态",
            text=STATUS_CARD_TEMPLATE.format(
                timestamp=timestamp,
                session_count=session_count,
                agent_status=agent_status,
                mem_pct=mem_pct,
                disk_pct=disk_pct,
            ),
        )

    def send_command_menu(self, commands: List[Dict[str, str]]) -> dict:
        """
        发送快捷命令菜单（按钮列表）
        commands: [{"title": "📊 状态", "actionURL": "..."}, ...]
        """
        if not commands:
            return {"errcode": 0}
        return self.send_card_with_buttons(
            title="🧭 OpenClaw 控制面板",
            content="请选择要执行的操作：",
            buttons=commands,
        )


# ── 钉钉 Webhook 回调解析 ─────────────────────────────────────────────────────

class DingTalkCallback:
    """
    解析钉钉回调请求（URL 解密 + 事件处理）

    用于接收钉钉群机器人的互动回调（按钮点击等）
    参考：https://open.dingtalk.com/document/org/customize-customer-robots
    """

    @staticmethod
    def verify(url: str, msg_signature: str, timestamp: str,
               token: str, encoding_aes_key: str) -> bool:
        """
        验证回调签名（企业内建应用使用）
        群机器人交互回调暂无加密，此方法预留
        """
        return True

    @staticmethod
    def parse_text_message(payload: dict) -> Optional[str]:
        """从回调 payload 中提取文本内容"""
        try:
            return payload.get("text", {}).get("content", "").strip()
        except Exception:
            return None

    @staticmethod
    def parse_button_action(payload: dict) -> Optional[dict]:
        """解析按钮点击回调"""
        try:
            action = payload.get("actionCard", {})
            return {
                "button_title": action.get("btnOrientation", ""),
                "clicked_text": action.get("content", ""),
                "space": payload.get("space", ""),
            }
        except Exception:
            return None


# ── 快捷命令处理器 ───────────────────────────────────────────────────────────

@dataclass
class CommandItem:
    """快捷命令定义"""
    keywords: List[str]          # 触发关键词（支持多关键词 or 关系）
    description: str             # 命令描述
    template_id: str             # 对应模板ID
    icon: str = "▶️"
    require_confirm: bool = False  # 是否需要二次确认


# 预定义快捷命令（适配用户三个 Agent）
BUILTIN_COMMANDS: List[CommandItem] = [
    CommandItem(
        keywords=["简报", "日报", "报告", "brief", "report"],
        description="生成今日 AI 资讯简报",
        template_id="quick-report",
        icon="📰",
    ),
    CommandItem(
        keywords=["技术", "tech", "论文", "arxiv"],
        description="技术前沿分析（推荐系统 + 大模型）",
        template_id="tech-analyst",
        icon="🔬",
    ),
    CommandItem(
        keywords=["商业", "市场", "商 机", "market", "insight"],
        description="AI 商业洞察与机会分析",
        template_id="market-insight",
        icon="💡",
    ),
    CommandItem(
        keywords=["全量", "全扫", "扫描", "full"],
        description="全量信息抓取（所有来源）",
        template_id="full-scan",
        icon="🌐",
    ),
    CommandItem(
        keywords=["深度", "deep"],
        description="深度研究（DAG 编排多步任务）",
        template_id="deep-research",
        icon="🧠",
    ),
    CommandItem(
        keywords=["状态", "status"],
        description="查看系统状态",
        template_id="__status__",
        icon="📊",
    ),
    CommandItem(
        keywords=["帮助", "help", "菜单"],
        description="显示所有可用命令",
        template_id="__help__",
        icon="❓",
    ),
]


class CommandRouter:
    """
    命令路由器：将自然语言文本路由到对应任务模板

    工作流程：
    1. 精确匹配关键词
    2. 正则模糊匹配
    3. NL 解析器辅助（如果可用）
    """

    def __init__(self, commands: Optional[List[CommandItem]] = None):
        self.commands = commands or BUILTIN_COMMANDS

    def route(self, text: str) -> Optional[CommandItem]:
        """
        路由文本命令，返回匹配的 CommandItem 或 None
        """
        text_lower = text.lower().strip()
        for cmd in self.commands:
            for kw in cmd.keywords:
                if kw.lower() in text_lower:
                    return cmd
        return None

    def get_all_commands(self) -> List[dict]:
        """返回所有可用命令（用于生成帮助）"""
        return [
            {
                "keywords": cmd.keywords,
                "description": cmd.description,
                "icon": cmd.icon,
                "require_confirm": cmd.require_confirm,
            }
            for cmd in self.commands
        ]

    def build_help_text(self) -> str:
        """生成帮助文本"""
        lines = [
            "# 🧭 OpenClaw 快捷命令",
            "",
            "发送以下关键词即可触发对应任务：",
            "",
        ]
        for cmd in self.commands:
            icons_cmds = " / ".join(f"`{k}`" for k in cmd.keywords[:2])
            lines.append(f"{cmd.icon} **{cmd.description}**")
            lines.append(f"   → {icons_cmds}")
            lines.append("")
        lines.append("---")
        lines.append("_也可以发送任意自然语言，我会自动理解并执行_ 🤖")
        return "\n".join(lines)


# ── DingTalk Notifier（高级版）─────────────────────────────────────────────────

class DingTalkNotifier:
    """
    钉钉通知器（整合卡片 + 命令路由）
    用于接入 clawctl 通知体系
    """

    def __init__(
        self,
        token: str,
        secret: Optional[str] = None,
        router: Optional[CommandRouter] = None,
    ):
        self.client = DingTalkClient(token=token, secret=secret)
        self.router = router or CommandRouter()

    def send(self, message: str, msg_type: str = "markdown", **kwargs) -> dict:
        """统一发送接口"""
        if msg_type == "markdown":
            return self.client.send_markdown(
                title=kwargs.get("title", "OpenClaw"),
                text=message,
            )
        elif msg_type == "text":
            return self.client.send_text(message)
        elif msg_type == "action_card":
            return self.client.send_action_card(**kwargs)
        return self.client.send_text(message)

    def notify_task(self, task_name: str, event: str, **kwargs) -> dict:
        """任务事件通知"""
        if event == "start":
            return self.client.notify_task_start(task_name, **kwargs)
        elif event == "complete":
            return self.client.notify_task_complete(task_name, **kwargs)
        elif event == "failed":
            return self.client.notify_task_failed(task_name, **kwargs)
        return {}

    def handle_inbound(self, text: str) -> dict:
        """
        处理收到的钉钉消息，返回响应内容

        返回 dict：
          - matched: bool  是否匹配到命令
          - command: CommandItem 或 None
          - response: str  回复文本
          - action: str  动作类型（task / status / help / none）
        """
        # 路由到内置命令
        cmd = self.router.route(text)
        if cmd:
            if cmd.template_id == "__status__":
                return {
                    "matched": True,
                    "command": cmd,
                    "response": "📊 正在获取系统状态...",
                    "action": "status",
                }
            elif cmd.template_id == "__help__":
                return {
                    "matched": True,
                    "command": cmd,
                    "response": self.router.build_help_text(),
                    "action": "help",
                }
            else:
                return {
                    "matched": True,
                    "command": cmd,
                    "response": f"{cmd.icon} 已收到！正在执行：**{cmd.description}**",
                    "action": "task",
                }

        # 未匹配：透传给 NL 解析器或返回帮助
        return {
            "matched": False,
            "command": None,
            "response": (
                "🤔 没有理解这个命令。\n\n"
                + self.router.build_help_text()
            ),
            "action": "none",
        }
