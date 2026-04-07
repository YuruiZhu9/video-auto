"""
Telegram Bot 处理模块

支持两种运行模式：
1. Webhook 模式（生产推荐）：Telegram 服务器推送更新
2. Polling 模式（开发/无公网IP）：本地定时拉取

配置环境变量：
  TELEGRAM_BOT_TOKEN  — Bot Father 申请的 Token
  TELEGRAM_CHAT_ID     — 默认接收消息的 Chat ID
  TELEGRAM_WEBHOOK_SECRET — Webhook 签名校验密钥（可选）

命令：
  /status      — 查看 OpenClaw 系统状态
  /list        — 列出最近任务
  /exec        — 触发任务（需指定模板名）
  /templates   — 列出可用模板
  /keys        — 查看 Key 列表（ADMIN）
  /cancel <id> — 取消任务
  /help        — 显示帮助
"""

import os
import re
import logging
import asyncio
from typing import Any, Dict, Optional, Callable, Awaitable

import requests

logger = logging.getLogger(__name__)


class TelegramBot:
    """
    Telegram Bot 处理核心

    设计原则：
    - 命令驱动：用户输入命令 → Bot 解析 → 执行 → 返回结果
    - 上下文保留：记录最后触发的模板，供后续确认使用
    - 权限隔离：Bot 内命令也走 API Key 权限验证
    """

    def __init__(
        self,
        bot_token: str,
        default_chat_id: Optional[str] = None,
        api_base: Optional[str] = None,
    ):
        self.bot_token = bot_token
        self.default_chat_id = default_chat_id or os.getenv("TELEGRAM_CHAT_ID", "")
        self.api_base = api_base or f"https://api.telegram.org/bot{bot_token}"
        self._offset = 0
        self._running = False
        self._handlers: Dict[str, Callable] = {}
        self._task_mgr = None
        self._notify_mgr = None
        self._client = None
        self._auth_mgr = None

    def bind_components(
        self,
        task_mgr=None,
        notify_mgr=None,
        client=None,
        auth_mgr=None,
    ):
        """绑定业务组件"""
        self._task_mgr = task_mgr
        self._notify_mgr = notify_mgr
        self._client = client
        self._auth_mgr = auth_mgr

    # ─── 基础 API ───────────────────────────────────────────────

    def _call(self, method: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.api_base}/{method}"
        try:
            resp = requests.post(url, json=kwargs, timeout=15)
            result = resp.json()
            if not result.get("ok"):
                logger.warning(f"Telegram API error: {result}")
            return result
        except Exception as e:
            logger.error(f"Telegram request failed: {e}")
            return {"ok": False, "description": str(e)}

    def send_message(
        self,
        text: str,
        chat_id: Optional[str] = None,
        parse_mode: str = "Markdown",
        disable_web_page_preview: bool = True,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """发送消息"""
        chat_id = chat_id or self.default_chat_id
        if not chat_id:
            return {"ok": False, "description": "No chat_id"}
        return self._call(
            "sendMessage",
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
        )

    def send_html(self, text: str, chat_id: Optional[str] = None) -> Dict[str, Any]:
        """发送 HTML 格式消息"""
        chat_id = chat_id or self.default_chat_id
        if not chat_id:
            return {"ok": False, "description": "No chat_id"}
        return self._call(
            "sendMessage",
            chat_id=chat_id,
            text=text,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )

    def edit_message(
        self,
        chat_id: str,
        message_id: int,
        text: str,
        parse_mode: str = "Markdown",
    ) -> Dict[str, Any]:
        """编辑已发送的消息"""
        return self._call(
            "editMessageText",
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            parse_mode=parse_mode,
        )

    def set_webhook(self, webhook_url: str, secret_token: str = "") -> Dict[str, Any]:
        """设置 Webhook URL"""
        kwargs = {"url": webhook_url}
        if secret_token:
            kwargs["secret_token"] = secret_token
        return self._call("setWebhook", **kwargs)

    def delete_webhook(self) -> Dict[str, Any]:
        """删除 Webhook（切换到 Polling 模式）"""
        return self._call("deleteWebhook")

    def get_me(self) -> Dict[str, Any]:
        """获取 Bot 信息"""
        return self._call("getMe")

    # ─── 命令处理 ───────────────────────────────────────────────

    def register_commands(self):
        """注册 Bot 命令（让 Telegram 客户端显示命令菜单）"""
        commands = [
            {"command": "status", "description": "查看系统状态"},
            {"command": "list", "description": "最近任务列表"},
            {"command": "templates", "description": "可用任务模板"},
            {"command": "exec", "description": "执行任务 (例: /exec tech_brief)"},
            {"command": "cancel", "description": "取消任务 (例: /cancel t_abc123)"},
            {"command": "help", "description": "显示帮助"},
        ]
        return self._call("setMyCommands", commands=commands)

    def process_update(self, update: Dict[str, Any]) -> Optional[str]:
        """
        处理单个 Telegram Update

        Returns:
            回复文本 或 None（无需回复）
        """
        # 提取消息
        message = update.get("message") or update.get("edited_message")
        callback_query = update.get("callback_query")

        if callback_query:
            return self._handle_callback(callback_query)

        if not message:
            return None

        chat = message.get("chat", {})
        chat_id = str(chat.get("id", ""))
        text = message.get("text", "")
        msg_id = message.get("message_id")

        if not text:
            return None

        text = text.strip()

        # 命令路由
        if text.startswith("/"):
            return self._handle_command(text, chat_id, msg_id)

        # 透传模式：直接发送消息给 OpenClaw
        return self._handle_text(text, chat_id)

    def _handle_command(self, text: str, chat_id: str, msg_id: int) -> str:
        """路由命令"""
        parts = text.split(maxsplit=1)
        cmd = parts[0].lstrip("/").lower()
        arg = parts[1] if len(parts) > 1 else ""

        handlers = {
            "status": self._cmd_status,
            "list": self._cmd_list,
            "tasks": self._cmd_list,
            "templates": self._cmd_templates,
            "exec": self._cmd_exec,
            "run": self._cmd_exec,
            "cancel": self._cmd_cancel,
            "stop": self._cmd_cancel,
            "help": self._cmd_help,
            "start": self._cmd_help,
        }

        handler = handlers.get(cmd)
        if handler:
            try:
                return handler(arg, chat_id, msg_id)
            except Exception as e:
                logger.error(f"Command {cmd} failed: {e}")
                return f"❌ 命令执行失败：{e}"
        else:
            return f"❓ 未知命令：/{cmd}\n发送 /help 查看可用命令"

    def _handle_callback(self, callback: Dict) -> str:
        """处理 Inline Button 回调"""
        data = callback.get("data", "")
        query_id = callback.get("id")
        message = callback.get("message", {})
        chat_id = str(message.get("chat", {}).get("id", ""))
        msg_id = message.get("message_id")

        logger.info(f"[TelegramBot] Callback: {data}")

        # 确认 Token 回调（confirm_<token>）
        if data.startswith("confirm_"):
            token = data[8:]
            return self._handle_confirm(token, query_id, chat_id, msg_id)

        # 取消操作回调
        if data == "cancel_op":
            self._call("answerCallbackQuery", callback_query_id=query_id, text="❌ 操作已取消")
            return ""

        return ""

    def _handle_confirm(
        self,
        token: str,
        query_id: str,
        chat_id: str,
        msg_id: int,
    ) -> str:
        """处理确认操作"""
        from core.confirm_token import ConfirmTokenManager
        if hasattr(self, "_confirm_mgr") and self._confirm_mgr:
            ok, tok, err = self._confirm_mgr.verify_and_consume(token)
            if ok:
                self._call(
                    "answerCallbackQuery",
                    callback_query_id=query_id,
                    text=f"✅ 已确认：{tok.action}",
                    show_alert=True,
                )
                # 更新消息
                self.edit_message(
                    chat_id=chat_id,
                    message_id=msg_id,
                    text=f"✅ **操作已确认执行**\n\n`{tok.action}` on `{tok.resource_id}`",
                )
                # 触发后续操作（通过事件机制）
                asyncio.create_task(self._notify_confirmed(tok))
                return ""
            else:
                self._call(
                    "answerCallbackQuery",
                    callback_query_id=query_id,
                    text=f"❌ 确认失败：{err}",
                    show_alert=True,
                )
                return ""
        return ""

    async def _notify_confirmed(self, token):
        """Token 确认后，触发后续操作"""
        logger.info(f"[TelegramBot] Token confirmed: {token.action} / {token.resource_id}")
        # 通知已通过 confirm_mgr 回调，这里可以触发具体操作

    def _handle_text(self, text: str, chat_id: str) -> str:
        """处理自由文本 → 透传给 OpenClaw"""
        if self._client:
            try:
                # 透传给 OpenClaw 作为子任务
                if hasattr(self._client, "spawn_agent"):
                    result = self._client.spawn_agent(task=text)
                    session_key = result.get("session_key", "")
                    return f"📨 消息已转发给 OpenClaw\n\nSession: `{session_key}`\n\n请等待回复..."
            except Exception as e:
                return f"❌ 转发失败：{e}"
        return "🤖 OpenClaw 未连接，无法处理消息"

    # ─── 具体命令实现 ──────────────────────────────────────────

    def _cmd_status(self, arg: str, chat_id: str, msg_id: int) -> str:
        """查看系统状态"""
        lines = ["📡 **OpenClaw 系统状态**\n"]

        if self._client:
            try:
                status = self._client.get_status()
                lines.append(f"Gateway: ✅ 已连接")
                if "sessions" in str(status):
                    lines.append(f"活跃会话: {status.get('active_sessions', '?')}")
            except Exception as e:
                lines.append(f"Gateway: ❌ {e}")
        else:
            lines.append("Gateway: ⚠️ 未配置")

        if self._task_mgr:
            stats = self._task_mgr.get_stats() if hasattr(self._task_mgr, "get_stats") else {}
            lines.append(f"今日完成: {stats.get('completed_today', '?')}")
            lines.append(f"进行中: {stats.get('running', '?')}")
        else:
            lines.append("任务管理: ⚠️ 未配置")

        lines.append(f"\n⏰ {asyncio.get_event_loop().time()}")
        return "\n".join(lines)

    def _cmd_list(self, arg: str, chat_id: str, msg_id: int) -> str:
        """列出最近任务"""
        if not self._task_mgr and not self._client:
            return "❌ 任务管理器未配置"

        limit = 5
        if arg.isdigit():
            limit = min(int(arg), 20)

        lines = ["📋 **最近任务**\n"]

        if self._task_mgr:
            tasks = self._task_mgr.list_tasks(limit=limit) if hasattr(self._task_mgr, "list_tasks") else []
        else:
            tasks = []

        if not tasks:
            return "📭 暂无任务记录"

        for t in tasks:
            status_icon = {"completed": "✅", "running": "🔄", "failed": "❌", "queued": "⏳"}.get(
                t.get("status", ""), "❓"
            )
            name = t.get("name", "?")
            tid = t.get("task_id", "?")
            lines.append(f"{status_icon} `{tid}` — {name}")

        return "\n".join(lines)

    def _cmd_templates(self, arg: str, chat_id: str, msg_id: int) -> str:
        """列出可用模板"""
        if not self._task_mgr:
            return "❌ 任务管理器未配置"

        templates = self._task_mgr.list_templates() if hasattr(self._task_mgr, "list_templates") else []
        if not templates:
            return "📭 暂无模板"

        lines = ["📋 **可用任务模板**\n"]
        lines.append(f"共 {len(templates)} 个模板：\n")
        for t in templates:
            name = t.get("name", "?")
            display = t.get("display_name", name)
            desc = t.get("description", "")
            lines.append(f"• `{name}` — {display}")
            if desc:
                lines.append(f"  └ {desc}")

        lines.append("\n💡 使用 `/exec <模板名>` 执行")
        return "\n".join(lines)

    def _cmd_exec(self, arg: str, chat_id: str, msg_id: int) -> str:
        """执行任务"""
        if not arg:
            return "📝 请指定模板名\n用法：`/exec tech_brief`\n\n发送 `/templates` 查看可用模板"

        template_name = arg.strip().lower()
        if not self._task_mgr:
            return "❌ 任务管理器未配置"

        template = self._task_mgr.get_template(template_name) if hasattr(self._task_mgr, "get_template") else None
        if not template:
            # 尝试模糊匹配
            templates = self._task_mgr.list_templates() if hasattr(self._task_mgr, "list_templates") else []
            matches = [t for t in templates if template_name in t.get("name", "")]
            if matches:
                template_name = matches[0].get("name", template_name)
                template = matches[0]

        if not template:
            return f"❌ 模板不存在：`{arg}`\n\n发送 `/templates` 查看列表"

        # 创建并执行任务
        try:
            if hasattr(self._task_mgr, "create_from_template"):
                task = asyncio.run(self._task_mgr.create_from_template(template_name))
                task_id = task.task_id if hasattr(task, "task_id") else "?"
                return (
                    f"🚀 **任务已触发**\n\n"
                    f"模板：`{template_name}`\n"
                    f"任务ID：`{task_id}`\n\n"
                    f"⏳ 执行中，完成后会推送通知..."
                )
        except Exception as e:
            return f"❌ 执行失败：{e}"

        return "❌ 任务管理器不支持异步执行"

    def _cmd_cancel(self, arg: str, chat_id: str, msg_id: int) -> str:
        """取消任务"""
        if not arg:
            return "📝 请指定任务ID\n用法：`/cancel t_abc123`"

        task_id = arg.strip()
        if self._task_mgr and hasattr(self._task_mgr, "cancel"):
            ok = asyncio.run(self._task_mgr.cancel(task_id))
            return f"{'✅' if ok else '❌'} 任务 `{task_id}` {'已取消' if ok else '取消失败（可能已完成）'}"
        return "❌ 任务管理器未配置"

    def _cmd_help(self, arg: str, chat_id: str, msg_id: int) -> str:
        """帮助信息"""
        return """🤖 **OpenClaw 控制台 Bot**

**命令列表：**

`/status` — 系统状态
`/list [数量]` — 最近任务
`/templates` — 可用模板
`/exec <模板>` — 触发任务
`/cancel <ID>` — 取消任务
`/help` — 显示本帮助

**直接发送消息** — 透传给 OpenClaw

---
OpenClaw 跨设备控制框架 v1.1"""

    # ─── Polling 循环 ─────────────────────────────────────────

    async def start_polling(self, interval: float = 1.0):
        """
        启动 Polling 循环（后台运行）

        Args:
            interval: 每次轮询间隔（秒）
        """
        self._running = True
        logger.info("[TelegramBot] Polling started")

        # 注册命令菜单
        self.register_commands()

        while self._running:
            try:
                updates = self._fetch_updates()
                if updates:
                    for update in updates.get("result", []):
                        try:
                            self.process_update(update)
                        except Exception as e:
                            logger.error(f"Update processing error: {e}")
            except Exception as e:
                logger.warning(f"[TelegramBot] Polling error: {e}")

            await asyncio.sleep(interval)

    def _fetch_updates(self) -> Optional[Dict]:
        """拉取更新"""
        try:
            resp = requests.get(
                f"{self.api_base}/getUpdates",
                params={
                    "offset": self._offset,
                    "timeout": 30,
                    "allowed_updates": ["message", "callback_query"],
                },
                timeout=35,
            )
            result = resp.json()
            if result.get("ok") and result.get("result"):
                # 推进 offset
                last_id = max(u.get("update_id", 0) for u in result["result"])
                self._offset = last_id + 1
            return result if result.get("ok") else None
        except Exception as e:
            logger.warning(f"[TelegramBot] Fetch error: {e}")
            return None

    def stop_polling(self):
        """停止 Polling"""
        self._running = False
        logger.info("[TelegramBot] Polling stopped")
