"""统一通知管理器"""
from abc import ABC, abstractmethod
from typing import Optional
import asyncio


class NotifyChannel(ABC):
    name: str = "base"

    @abstractmethod
    async def send(self, message: str, context: dict) -> bool:
        raise NotImplementedError


class NotifyManager:
    """
    统一通知管理器
    
  用法：
    ```python
    nm = NotifyManager()
    nm.register(DingTalkChannel(webhook_url, secret))
    nm.register(TelegramChannel(bot_token, chat_id))
    
    # 发送任务完成通知
    await nm.send("task_complete", {
        "task_name": "每日简报",
        "duration": 45,
    }, channels=["dingtalk", "telegram"])
    ```
    """

    def __init__(self):
        self._channels: dict[str, NotifyChannel] = {}
        self._lock = asyncio.Lock()

    def register(self, channel: NotifyChannel):
        self._channels[channel.name] = channel

    def unregister(self, name: str):
        self._channels.pop(name, None)

    async def send(
        self,
        template: str,
        context: dict,
        channels: Optional[list] = None,
    ) -> dict:
        """
        向指定渠道发送通知
        
        Args:
            template: 模板名称（task_start/task_complete/task_failed/alert）
            context: 模板变量上下文
            channels: 目标渠道列表（None = 所有已注册渠道）
        """
        message = self._render_template(template, context)
        targets = channels or list(self._channels.keys())
        results = {}
        for name in targets:
            channel = self._channels.get(name)
            if not channel:
                results[name] = {"ok": False, "error": "channel not registered"}
                continue
            try:
                ok = await channel.send(message, context)
                results[name] = {"ok": ok}
            except Exception as e:
                results[name] = {"ok": False, "error": str(e)}
        return results

    # ─── 消息模板 ───────────────────────────────────────────

    TEMPLATES = {
        "task_start": """🚀 任务已接收
━━━━━━━━━━━━━━━
📋 任务：{display_name}
🆔 ID：{task_id}
⏰ 时间：{timestamp}
━━━━━━━━━━━━━━━
正在执行中...
""",
        "task_complete": """✅ 任务完成
━━━━━━━━━━━━━━━
📋 任务：{display_name}
🆔 ID：{task_id}
⏱ 耗时：{duration}秒
📌 结果：{result_summary}
""",
        "task_failed": """❌ 任务失败
━━━━━━━━━━━━━━━
📋 任务：{display_name}
🆔 ID：{task_id}
⚠️ 错误：{error}
""",
        "alert": """⚠️ 告警
━━━━━━━━━━━━━━━
{message}
""",
        "server_status": """🖥 OpenClaw 状态
━━━━━━━━━━━━━━━
🟢 Gateway：在线
📊 活跃会话：{active_sessions}
📋 运行中任务：{running_tasks}
✅ 今日完成：{completed_today}
❌ 今日失败：{failed_today}
"""
    }

    def _render_template(self, template: str, context: dict) -> str:
        tpl = self.TEMPLATES.get(template, "{message}")
        # 安全替换：只替换存在的键
        for k, v in context.items():
            tpl = tpl.replace(f"{{{k}}}", str(v))
        return tpl
