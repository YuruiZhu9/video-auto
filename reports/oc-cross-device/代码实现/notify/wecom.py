"""企业微信（WeCom）群机器人推送模块

官方文档：https://developer.work.weixin.qq.com/document/path/91770
支持的消息类型：文本、Markdown、图文（news）、卡片（template_card）

使用方式：
    notifier = WeComNotifier(
        webhook_url="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxx"
    )
    notifier.send_text("Hello 企业微信!")
    notifier.send_markdown("**加粗** 和 `代码` 支持")
    notifier.send_card("task_complete", task_name="测试", duration=3.2)
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ─── 消息模板 ─────────────────────────────────────────────────

TEMPLATES: Dict[str, Dict] = {
    "task_start": {
        "msgtype": "markdown",
        "markdown": {
            "content": (
                "### 🚀 任务开始\n"
                "**任务名称**：{task_name}\n"
                "**执行 Agent**：{agent}\n"
                "**开始时间**：{timestamp}\n"
            )
        },
    },
    "task_complete": {
        "msgtype": "markdown",
        "markdown": {
            "content": (
                "### ✅ 任务完成\n"
                "**任务名称**：{task_name}\n"
                "**耗时**：{duration} 秒\n"
                "**结果摘要**：{result_summary}\n"
            )
        },
    },
    "task_failed": {
        "msgtype": "markdown",
        "markdown": {
            "content": (
                "### ❌ 任务失败\n"
                "**任务名称**：{task_name}\n"
                "**失败原因**：{error}\n"
                "**发生时间**：{timestamp}\n"
            )
        },
    },
    "alert": {
        "msgtype": "markdown",
        "markdown": {
            "content": (
                "### ⚠️ 系统告警\n"
                "**告警类型**：{alert_type}\n"
                "**告警详情**：{message}\n"
                "**触发时间**：{timestamp}\n"
            )
        },
    },
    "status_report": {
        "msgtype": "markdown",
        "markdown": {
            "content": (
                "### 📊 系统状态报告\n"
                "**运行时间**：{uptime}\n"
                "**活跃任务**：{active_tasks}\n"
                "**定时任务**：{scheduled_jobs}\n"
                "**报告时间**：{timestamp}\n"
            )
        },
    },
    "daily_brief": {
        "msgtype": "markdown",
        "markdown": {
            "content": (
                "### 📰 今日简报\n"
                "{content}\n"
                "—— 由 OpenClaw 于 {timestamp} 推送"
            )
        },
    },
}

# WeCom 支持的消息类型
SUPPORTED_TYPES = ["text", "markdown", "image", "news", "file", "template_card"]


def _fill(text: str, vars_: Dict) -> str:
    """替换模板中的 {key} 占位符"""
    try:
        return text.format(**vars_)
    except KeyError:
        return text


class WeComNotifier:
    """
    企业微信群机器人推送

    支持：
    - 文本消息（text）
    - Markdown 消息（markdown）
    - 图文消息（news）— 通过 send_news() 方法

    限制：
    - Markdown 仅支持有限子集：<h1-h6>/**bold**/`code`/`code block`/
      > / - 无序列表 / 1. 有序列表 / [超链接](url)
    - 每条消息最长 4096 字节（超出自动截断）
    """

    def __init__(self, webhook_url: str, timeout: int = 10):
        """
        Args:
            webhook_url: 企业微信群机器人 Webhook URL
                        格式：https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxx
            timeout: 请求超时时间（秒）
        """
        self.webhook_url = webhook_url
        self.timeout = timeout

    def _post(self, payload: Dict) -> Dict[str, Any]:
        """发送 POST 请求到企业微信 Webhook"""
        import requests

        try:
            resp = requests.post(
                self.webhook_url,
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"},
            )
            result = resp.json()
            errcode = result.get("errcode", 0)
            if errcode == 0:
                return {"success": True, "data": result}
            logger.warning(f"WeCom 推送失败: errcode={errcode}, errmsg={result.get('errmsg')}")
            return {"success": False, "error": result.get("errmsg", f"errcode={errcode}")}
        except Exception as e:
            logger.exception("WeCom 推送异常")
            return {"success": False, "error": str(e)}

    # ── 基础方法 ────────────────────────────────────────────────

    def send_text(self, content: str, mentioned_list: List[str] = None,
                  mentioned_mobile_list: List[str] = None) -> Dict[str, Any]:
        """
        发送纯文本消息（支持 @ 成员）

        Args:
            content: 消息内容（最长 2048 字节，超出截断）
            mentioned_list: 被 @ 的 userid 列表（单人时填 userid，多人时填 userid 的 JSON 串）
            mentioned_mobile_list: 被 @ 的手机号列表（通过手机号 @ 成员）
        """
        payload = {
            "msgtype": "text",
            "text": {
                "content": content[:2048],
                "mentioned_list": mentioned_list or [],
                "mentioned_mobile_list": mentioned_mobile_list or [],
            },
        }
        return self._post(payload)

    def send_markdown(self, content: str) -> Dict[str, Any]:
        """
        发送 Markdown 消息

        支持的 Markdown 语法：
        - 标题：# / ## / ### / #### / ##### / ######
        - 粗体：**bold**
        - 斜体：*italic*（企业微信部分版本支持）
        - 行内代码：`code`
        - 链接：[text](url)
        - 有序列表：1. a  2. b
        - 无序列表：- a / · a / • a
        - 引用：> quote

        注意：content 超出 4096 字节会报错，降级为截断文本
        """
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "content": content[:4096],
            },
        }
        return self._post(payload)

    def send_news(self, articles: List[Dict]) -> Dict[str, Any]:
        """
        发送图文消息（每个卡片最多展示 8 条）

        Args:
            articles: 图文列表，每项包含：
                - title: 标题（最长 128 字节）
                - description: 描述（可选，最长 512 字节）
                - url: 点击后跳转的链接
                - picurl: 封面图片 URL（可选，建议尺寸 200x200）
        """
        if not articles:
            return {"success": False, "error": "articles 不能为空"}
        payload = {
            "msgtype": "news",
            "news": {
                "articles": [
                    {
                        "title": a.get("title", "")[:128],
                        "description": a.get("description", "")[:512],
                        "url": a.get("url", ""),
                        "picurl": a.get("picurl", ""),
                    }
                    for a in articles[:8]
                ]
            },
        }
        return self._post(payload)

    def send_file(self, media_id: str) -> Dict[str, Any]:
        """发送文件消息（需先通过 /cgi-bin/webhook/upload_media 上传文件）"""
        payload = {
            "msgtype": "file",
            "file": {"media_id": media_id},
        }
        return self._post(payload)

    # ── 模板方法 ────────────────────────────────────────────────

    def send_card(self, template_name: str, **kwargs) -> Dict[str, Any]:
        """
        使用预定义模板发送消息

        Args:
            template_name: TEMPLATES 中的模板名称，如 "task_complete"
            **kwargs: 模板变量（自动填充 {key} 占位符）
        """
        template = TEMPLATES.get(template_name)
        if not template:
            logger.warning(f"未知 WeCom 模板: {template_name}，降级为文本")
            return self.send_text(str(kwargs))

        # 填充时间戳默认值
        if "timestamp" not in kwargs:
            from datetime import datetime
            kwargs["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        msg_type = template.get("msgtype", "text")

        if msg_type == "markdown":
            content = _fill(template["markdown"]["content"], kwargs)
            return self.send_markdown(content)
        elif msg_type == "text":
            content = _fill(template.get("text", {}).get("content", ""), kwargs)
            return self.send_text(content)
        else:
            return self.send_text(str(kwargs))

    def send_custom(self, msg_type: str, content: Dict) -> Dict[str, Any]:
        """
        发送自定义消息（直接传入消息体）

        Args:
            msg_type: 消息类型，见 SUPPORTED_TYPES
            content: 消息内容结构
        """
        if msg_type not in SUPPORTED_TYPES:
            return {"success": False, "error": f"不支持的消息类型: {msg_type}"}
        payload = {"msgtype": msg_type, msg_type: content}
        return self._post(payload)


# ─── 快捷函数 ─────────────────────────────────────────────────

def send(
    webhook_url: str,
    message: str,
    channel: str = "wecom",
    **kwargs,
) -> Dict[str, Any]:
    """
    send() 统一入口，用于 NotifyManager 集成

    channel="wecom": 发送纯文本
    channel="wecom_md": 发送 Markdown
    channel="wecom_card": 使用模板发送
    """
    notifier = WeComNotifier(webhook_url=webhook_url)

    if channel == "wecom_md":
        return notifier.send_markdown(message)
    elif channel == "wecom_card":
        return notifier.send_card(message, **kwargs)
    elif channel == "wecom_news":
        return notifier.send_news(kwargs.get("articles", []))
    else:
        return notifier.send_text(message)


# ─── NotifyManager 集成用的 Notifier 类 ──────────────────────

class WeComNotifierV2:
    """
    适配 NotifyManager 的通知器类

    配置项（环境变量）：
        WECOM_WEBHOOK_URL  — Webhook 地址
        WECOM_MENTION_USERS — @ 用户列表，逗号分隔 userid
        WECOM_MENTION_MOBILES — @ 手机号列表，逗号分隔
    """

    def __init__(
        self,
        webhook_url: str = "",
        mentioned_list: List[str] = None,
        mentioned_mobile_list: List[str] = None,
    ):
        import os
        self.webhook_url = webhook_url or os.getenv("WECOM_WEBHOOK_URL", "")
        self.mentioned_list = mentioned_list or []
        self.mentioned_mobile_list = mentioned_mobile_list or []

        if not self.webhook_url:
            logger.warning("WeCom Webhook URL 未配置，WECOM_WEBHOOK_URL 环境变量为空")

    def send(self, message: str, **kwargs) -> Dict[str, Any]:
        """发送消息（NotifyManager 接口）"""
        if not self.webhook_url:
            return {"success": False, "error": "Webhook URL 未配置"}

        notifier = WeComNotifier(webhook_url=self.webhook_url)

        channel = kwargs.get("channel", "")
        if channel == "markdown" or channel == "wecom_md":
            return notifier.send_markdown(message)
        elif channel == "card" or channel == "wecom_card":
            return notifier.send_card(message, **kwargs)
        elif channel == "news" or channel == "wecom_news":
            return notifier.send_news(kwargs.get("articles", []))
        else:
            # 尝试解析为 Markdown 发送
            return notifier.send_text(message)
