"""飞书消息推送模块

支持：
- 文本消息（text）
- Markdown 卡片消息（interactive card）
- 富文本消息（post）
"""

import logging
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ─── 消息模板 ───────────────────────────────────────────────

TEMPLATES = {
    "task_start": {
        "header": {"title": {"tag": "plain_text", "content": "🚀 任务开始"}},
        "elements": [
            {"tag": "markdown", "content": "**任务名称**\n{task_name}"},
            {"tag": "markdown", "content": "**执行 Agent**\n{agent}"},
            {"tag": "markdown", "content": "**开始时间**\n{timestamp}"},
        ],
    },
    "task_complete": {
        "header": {"title": {"tag": "plain_text", "content": "✅ 任务完成"}},
        "elements": [
            {"tag": "markdown", "content": "**任务名称**\n{task_name}"},
            {"tag": "markdown", "content": "**耗时**\n{duration} 秒"},
            {"tag": "markdown", "content": "**结果摘要**\n{result_summary}"},
        ],
    },
    "task_failed": {
        "header": {"title": {"tag": "plain_text", "content": "❌ 任务失败"}},
        "elements": [
            {"tag": "markdown", "content": "**任务名称**\n{task_name}"},
            {"tag": "markdown", "content": "**失败原因**\n{error}"},
            {"tag": "markdown", "content": "**发生时间**\n{timestamp}"},
        ],
    },
    "alert": {
        "header": {"title": {"tag": "plain_text", "content": "⚠️ 系统告警"}},
        "elements": [
            {"tag": "markdown", "content": "**告警类型**\n{alert_type}"},
            {"tag": "markdown", "content": "**告警详情**\n{message}"},
            {"tag": "markdown", "content": "**触发时间**\n{timestamp}"},
        ],
    },
    "status_report": {
        "header": {"title": {"tag": "plain_text", "content": "📊 系统状态报告"}},
        "elements": [
            {"tag": "markdown", "content": "**运行时间**\n{uptime}"},
            {"tag": "markdown", "content": "**活跃任务**\n{active_tasks}"},
            {"tag": "markdown", "content": "**定时任务**\n{scheduled_jobs}"},
            {"tag": "markdown", "content": "**报告时间**\n{timestamp}"},
        ],
    },
    "daily_brief": {
        "header": {"title": {"tag": "plain_text", "content": "📰 今日简报"}},
        "elements": [
            {"tag": "markdown", "content": "{content}"},
        ],
    },
}


def _build_card(template: Dict, **kwargs) -> Dict:
    """用模板变量填充飞书卡片"""
    card = {
        "msg_type": "interactive",
        "card": {
            "header": _fill_obj(template.get("header", {}), kwargs),
            "elements": [
                _fill_obj(el, kwargs) if isinstance(el, dict) else el
                for el in template.get("elements", [])
            ],
        },
    }
    # 添加底部时间戳
    if kwargs.get("timestamp"):
        ts = kwargs["timestamp"]
    else:
        from datetime import datetime
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    card["card"].setdefault("elements", []).append(
        {"tag": "hr"},
        {"tag": "note", "elements": [{"tag": "plain_text", "content": f"由 OpenClaw 于 {ts} 推送"}]},
    )
    return card


def _fill_obj(obj: Any, vars_: Dict) -> Any:
    """递归替换模板中的 {key} 占位符"""
    if isinstance(obj, dict):
        return {k: _fill_obj(v, vars_) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_fill_obj(item, vars_) for item in obj]
    elif isinstance(obj, str):
        try:
            return obj.format(**vars_)
        except KeyError:
            return obj
    return obj


class FeishuNotifier:
    """
    飞书群机器人推送

    使用方式：
        notifier = FeishuNotifier(
            webhook_url="https://open.feishu.cn/open-apis/bot/v2/hook/xxxxx"
        )
        # 发送文本
        notifier.send_text("Hello 飞书!")
        # 发送卡片
        notifier.send_card("task_complete", task_name="测试", duration=3.2, result_summary="成功")
    """

    def __init__(
        self,
        webhook_url: str,
        timeout: int = 10,
    ):
        self.webhook_url = webhook_url
        self.timeout = timeout

    def send_text(self, content: str) -> Dict[str, Any]:
        """发送纯文本消息"""
        payload = {
            "msg_type": "text",
            "content": {"text": content},
        }
        return self._post(payload)

    def send_card(
        self,
        template_name: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        发送卡片消息

        Args:
            template_name: TEMPLATES 中的模板名称，如 "task_complete"
            **kwargs: 模板变量
        """
        template = TEMPLATES.get(template_name)
        if not template:
            logger.warning(f"未知飞书模板: {template_name}，降级为文本")
            return self.send_text(str(kwargs))

        payload = _build_card(template, **kwargs)
        return self._post(payload)

    def send_custom_card(self, card: Dict) -> Dict[str, Any]:
        """发送自定义卡片（直接传入 card 结构）"""
        payload = {"msg_type": "interactive", "card": card}
        return self._post(payload)

    def send_markdown(self, content: str, title: str = "OpenClaw 通知") -> Dict[str, Any]:
        """发送 Markdown 富文本卡片"""
        card = {
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": "blue",
            },
            "elements": [
                {"tag": "markdown", "content": content},
            ],
        }
        return self.send_custom_card(card)

    def _post(self, payload: Dict) -> Dict[str, Any]:
        """发送 POST 请求到飞书 webhook"""
        import requests

        try:
            resp = requests.post(
                self.webhook_url,
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"},
            )
            result = resp.json()
            if result.get("code") == 0 or result.get("StatusCode") == 0:
                return {"success": True, "data": result}
            logger.warning(f"飞书推送失败: {result}")
            return {"success": False, "error": result}
        except Exception as e:
            logger.exception("飞书推送异常")
            return {"success": False, "error": str(e)}


# ─── 快捷函数 ────────────────────────────────────────────────

def send(
    webhook_url: str,
    message: str,
    channel: str = "feishu",
    **kwargs,
) -> Dict[str, Any]:
    """send() 统一入口，用于 NotifyManager"""
    notifier = FeishuNotifier(webhook_url=webhook_url)
    if channel == "feishu_card":
        return notifier.send_card(message, **kwargs)
    return notifier.send_text(message)
