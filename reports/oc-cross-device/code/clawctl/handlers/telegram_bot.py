#!/usr/bin/env python3
"""
clawctl - Telegram Bot 处理器
支持 Polling 和 Webhook 两种模式
"""

import os
import re
import logging
import threading
from dataclasses import dataclass, field
from typing import Optional, Callable, Dict, Any

import requests

logger = logging.getLogger(__name__)


@dataclass
class TelegramCommand:
    """命令定义"""
    name: str
    handler: Callable
    description: str = ""
    usage: str = ""


class TelegramBot:
    """
    Telegram Bot - Polling 实现
    
    用法:
        bot = TelegramBot(token="...", chat_id="...")
        bot.register("status", cmd_status, "查看状态")
        bot.register("exec", cmd_exec, "执行任务")
        bot.start_polling()
    """

    def __init__(
        self,
        token: str,
        chat_id: Optional[str] = None,
        admin_ids: Optional[list] = None,
        notify_mgr=None,
        task_manager=None,
        client=None,
    ):
        self.token = token
        self.chat_id = chat_id
        self.admin_ids = set(str(a) for a in (admin_ids or []))
        self.api_url = f"https://api.telegram.org/bot{token}"
        self._commands: Dict[str, TelegramCommand] = {}
        self._offset = 0
        self._running = False
        self._lock = threading.RLock()
        self._polling_thread: Optional[threading.Thread] = None
        self.notify_mgr = notify_mgr
        self.task_manager = task_manager
        self.client = client

    def register(
        self,
        name: str,
        handler: Callable[["TelegramBot", dict], Any],
        description: str = "",
        usage: str = "",
    ):
        """注册命令"""
        self._commands[name] = TelegramCommand(name, handler, description, usage)

    def _send_message(self, chat_id: str, text: str, parse_mode: str = "Markdown", **kwargs) -> bool:
        """发送消息"""
        try:
            resp = requests.post(
                f"{self.api_url}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": parse_mode,
                    **kwargs,
                },
                timeout=10,
            )
            return resp.json().get("ok", False)
        except Exception as e:
            logger.error(f"Telegram 发送失败: {e}")
            return False

    def _reply(self, update: dict, text: str, parse_mode: str = "Markdown", **kwargs):
        """回复用户消息"""
        chat_id = str(update.get("message", {}).get("chat", {}).get("id", ""))
        if not chat_id:
            return
        self._send_message(chat_id, text, parse_mode, **kwargs)

    def _is_admin(self, update: dict) -> bool:
        """检查是否是管理员"""
        user_id = str(update.get("message", {}).get("from", {}).get("id", ""))
        return user_id in self.admin_ids

    def _cmd_status(self, update: dict, args: list) -> str:
        """处理 /status 命令"""
        try:
            health = self.client.check_health() if self.client else False
            sessions = self.client.get_sessions() if self.client else None
            session_count = len(sessions.data.get("sessions", [])) if sessions and sessions.success else 0
            tasks = self.task_manager.list() if self.task_manager else []
            running = sum(1 for t in tasks if t.status.value == "running")

            status_emoji = "🟢" if health else "🔴"
            return (
                f"{status_emoji} *OpenClaw 状态*\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"Gateway: *{'在线' if health else '离线'}*\n"
                f"活跃会话: *{session_count}*\n"
                f"运行任务: *{running}*\n"
                f"总任务数: *{len(tasks)}*"
            )
        except Exception as e:
            return f"❌ 状态查询失败: {e}"

    def _cmd_list(self, update: dict, args: list) -> str:
        """处理 /list 命令"""
        limit = int(args[0]) if args and args[0].isdigit() else 5
        tasks = self.task_manager.list() if self.task_manager else []
        recent = tasks[:limit]
        if not recent:
            return "📋 暂无任务记录"
        lines = ["📋 *最近任务*\n━━━━━━━━━━━━━━━━━━━"]
        for t in recent:
            emoji = {"pending": "⏳", "queued": "📋", "running": "🔄",
                     "success": "✅", "failed": "❌"}.get(t.status.value, "❓")
            lines.append(f"{emoji} `{t.id}` {t.name}")
            lines.append(f"   └─ {t.status.value} | {t.duration_ms() or 0}ms\n")
        return "\n".join(lines)

    def _cmd_templates(self, update: dict, args: list) -> str:
        """处理 /templates 命令"""
        return (
            "📋 *可用任务模板*\n━━━━━━━━━━━━━━━━━━━\n"
            "• `/exec quick-report` - 快速报告\n"
            "• `/exec tech-analyst` - 技术分析\n"
            "• `/exec market-insight` - 商业洞察\n"
            "• `/exec full-scan` - 全量扫描\n\n"
            "直接发消息 → 透传给 OpenClaw 执行"
        )

    def _cmd_exec(self, update: dict, args: list) -> str:
        """处理 /exec <模板> 命令"""
        if not args:
            return "用法: `/exec <模板名>`\n示例: `/exec quick-report`"
        template_name = args[0]
        from ..core.task import Task
        task = Task(name=f"telegram:{template_name}", action="spawn",
                    params={"task": template_name})
        self.task_manager.submit(task)
        self.task_manager.execute_async(task)
        return (
            f"🚀 *任务已触发*\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"模板: `{template_name}`\n"
            f"任务ID: `{task.id}`\n"
            f"⏳ 执行中，完成后将推送通知..."
        )

    def _cmd_cancel(self, update: dict, args: list) -> str:
        """处理 /cancel <ID> 命令"""
        if not args:
            return "用法: `/cancel <task_id>`"
        task_id = args[0]
        ok = self.task_manager.cancel(task_id) if self.task_manager else False
        return f"{'✅ 任务已取消' if ok else '❌ 取消失败，任务可能已执行或不存在'}: `{task_id}`"

    def _cmd_help(self, update: dict, args: list) -> str:
        """处理 /help 命令"""
        lines = [
            "🤖 *OpenClaw 控制 Bot*\n━━━━━━━━━━━━━━━━━━━",
            "/status - 系统状态",
            "/list [n] - 任务列表",
            "/templates - 可用模板",
            "/exec <模板> - 触发任务",
            "/cancel <id> - 取消任务",
            "/help - 显示本帮助",
            "━━━━━━━━━━━━━━━━━━━",
            "直接发消息 → 透传给 OpenClaw",
        ]
        return "\n".join(lines)

    def _handle_message(self, update: dict):
        """处理单条消息"""
        try:
            text = (update.get("message", {}).get("text") or "").strip()
            if not text:
                return

            # 命令匹配
            m = re.match(r"/(\w+)(@.+?)?(?:\s+(.*))?$", text, re.DOTALL)
            if m:
                cmd = m.group(1).lower()
                args = (m.group(3) or "").split() if m.group(3) else []
            else:
                # 非命令消息 → 透传给 OpenClaw
                if self.task_manager:
                    from ..core.task import Task
                    task = Task(name="telegram:prompt", action="spawn",
                                params={"task": text})
                    self.task_manager.submit(task)
                    self.task_manager.execute_async(task)
                    self._reply(update, f"🚀 已提交任务: `{task.id}`，完成后将推送结果")
                return

            # 内置命令
            handlers = {
                "status": self._cmd_status,
                "list": self._cmd_list,
                "templates": self._cmd_templates,
                "exec": self._cmd_exec,
                "cancel": self._cmd_cancel,
                "help": self._cmd_help,
                "start": lambda u, a: self._cmd_help(u, a),
            }
            handler = handlers.get(cmd)
            if handler:
                reply = handler(update, args)
                self._reply(update, reply)
            else:
                self._reply(update, f"❓ 未知命令: /{cmd}\n发送 /help 查看可用命令")

        except Exception as e:
            logger.exception(f"处理消息异常: {e}")
            self._reply(update, f"❌ 处理失败: {e}")

    def _poll_once(self) -> list:
        """拉取一次更新"""
        try:
            resp = requests.get(
                f"{self.api_url}/getUpdates",
                params={"offset": self._offset, "timeout": 30},
                timeout=35,
            )
            data = resp.json()
            if not data.get("ok"):
                return []
            updates = data.get("result", [])
            if updates:
                self._offset = max(u["update_id"] for u in updates) + 1
            return updates
        except Exception as e:
            logger.warning(f"Polling 异常: {e}")
            return []

    def start_polling(self, daemon: bool = True):
        """启动 Polling 循环"""
        self._running = True
        def _loop():
            logger.info("🤖 Telegram Bot Polling 启动")
            while self._running:
                updates = self._poll_once()
                for u in updates:
                    self._handle_message(u)
        self._polling_thread = threading.Thread(target=_loop, daemon=daemon)
        self._polling_thread.start()

    def stop_polling(self):
        """停止 Polling"""
        self._running = False
        logger.info("🤖 Telegram Bot Polling 停止")

    def send_to_admin(self, text: str) -> bool:
        """向管理员发送消息"""
        if self.chat_id:
            return self._send_message(self.chat_id, text)
        return False

    def set_webhook(self, webhook_url: str, secret: str = "") -> bool:
        """设置 Webhook（生产模式）"""
        try:
            params = {"url": webhook_url, "secret_token": secret} if secret else {"url": webhook_url}
            resp = requests.post(f"{self.api_url}/setWebhook", json=params, timeout=10)
            return resp.json().get("ok", False)
        except Exception as e:
            logger.error(f"设置 Webhook 失败: {e}")
            return False
