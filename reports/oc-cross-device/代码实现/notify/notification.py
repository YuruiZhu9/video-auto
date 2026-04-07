"""消息通知模块"""

import os
import json
import requests
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


class Notifier(ABC):
    """通知器基类"""
    
    @abstractmethod
    def send(self, message: str, **kwargs) -> Dict[str, Any]:
        """发送消息"""
        pass


@dataclass
class DingTalkNotifier(Notifier):
    """钉钉通知器"""
    webhook: str = ""
    secret: str = ""
    
    def __post_init__(self):
        if not self.webhook:
            self.webhook = os.getenv("DINGTALK_WEBHOOK", "")
        if not self.secret:
            self.secret = os.getenv("DINGTALK_SECRET", "")
    
    def send(self, message: str, **kwargs) -> Dict[str, Any]:
        """发送钉钉消息"""
        if not self.webhook:
            return {"success": False, "error": "Webhook not configured"}
        
        import hmac
        import hashlib
        import base64
        import urllib.parse
        import time
        
        # 签名计算
        timestamp = str(round(time.time() * 1000))
        secret_enc = self.secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, self.secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        
        url = f"{self.webhook}&timestamp={timestamp}&sign={sign}"
        
        payload = {
            "msgtype": "text",
            "text": {
                "content": message
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            result = response.json()
            return {
                "success": result.get("errcode") == 0,
                "response": result
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


@dataclass
class TelegramNotifier(Notifier):
    """Telegram 通知器"""
    bot_token: str = ""
    chat_id: str = ""
    
    def __post_init__(self):
        if not self.bot_token:
            self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        if not self.chat_id:
            self.chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    
    def send(self, message: str, **kwargs) -> Dict[str, Any]:
        """发送 Telegram 消息"""
        if not self.bot_token or not self.chat_id:
            return {"success": False, "error": "Bot token or chat_id not configured"}
        
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": kwargs.get("parse_mode", "Markdown")
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            result = response.json()
            return {
                "success": result.get("ok", False),
                "response": result
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


@dataclass
class EmailNotifier(Notifier):
    """邮件通知器"""
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    from_addr: str = ""
    to_addrs: str = ""
    
    def send(self, message: str, **kwargs) -> Dict[str, Any]:
        """发送邮件"""
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        subject = kwargs.get("subject", "OpenClaw 通知")
        
        msg = MIMEMultipart()
        msg["From"] = self.from_addr
        msg["To"] = self.to_addrs
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "html" if kwargs.get("html") else "plain"))
        
        try:
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)
            server.quit()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}


@dataclass
class WeComNotifier(Notifier):
    """企业微信通知器"""
    webhook_url: str = ""

    def __post_init__(self):
        if not self.webhook_url:
            self.webhook_url = os.getenv("WECOM_WEBHOOK_URL", "")

    def send(self, message: str, **kwargs) -> Dict[str, Any]:
        """发送企业微信消息"""
        if not self.webhook_url:
            return {"success": False, "error": "Webhook URL 未配置"}
        from notify.wecom import WeComNotifier as WCN
        notifier = WCN(webhook_url=self.webhook_url)
        channel = kwargs.get("channel", "")
        if channel in ("markdown", "wecom_md"):
            return notifier.send_markdown(message)
        elif channel in ("card", "wecom_card"):
            return notifier.send_card(message, **kwargs)
        elif channel in ("news", "wecom_news"):
            return notifier.send_news(kwargs.get("articles", []))
        return notifier.send_text(message)


# 消息模板
class MessageTemplate:
    """消息模板"""
    
    TEMPLATES = {
        "task_start": """
🚀 **任务开始**
- 任务：{task_name}
- 执行者：{agent}
- 时间：{timestamp}
        """,
        
        "task_complete": """
✅ **任务完成**
- 任务：{task_name}
- 耗时：{duration}秒
- 结果：{result_summary}
        """,
        
        "task_failed": """
❌ **任务失败**
- 任务：{task_name}
- 错误：{error}
- 时间：{timestamp}
        """,
        
        "alert": """
⚠️ **告警**
- 类型：{alert_type}
- 详情：{message}
- 时间：{timestamp}
        """,
        
        "status_report": """
📊 **状态报告**
- 运行时间：{uptime}
- 活跃任务：{active_tasks}
- 内存使用：{memory}
        """
    }
    
    @classmethod
    def format(cls, template_name: str, **kwargs) -> str:
        """格式化模板"""
        template = cls.TEMPLATES.get(template_name, "")
        return template.format(**kwargs)


# 通知管理器
class NotifyManager:
    """通知管理器"""
    
    def __init__(self):
        self.notifiers: Dict[str, Notifier] = {}
        self._register_default_notifiers()
    
    def _register_default_notifiers(self):
        """注册默认通知器"""
        self.register("dingtalk", DingTalkNotifier())
        self.register("telegram", TelegramNotifier())
        self.register("email", EmailNotifier())
        self.register("wecom", WeComNotifier())
    
    def register(self, name: str, notifier: Notifier):
        """注册通知器"""
        self.notifiers[name] = notifier
    
    def send(self, channel: str, message: str, **kwargs) -> Dict[str, Any]:
        """发送消息（同步）"""
        notifier = self.notifiers.get(channel)
        if not notifier:
            return {"success": False, "error": f"Channel {channel} not found"}
        return notifier.send(message, **kwargs)

    async def send_async(self, channel: str, message: str, **kwargs) -> Dict[str, Any]:
        """发送消息（异步，适配 ConfirmTokenManager）"""
        # 直接调用同步版本（通知器本身是同步IO，不阻塞事件循环）
        return self.send(channel, message, **kwargs)
    
    def broadcast(self, message: str, channels: list = None, **kwargs) -> Dict[str, Any]:
        """广播消息"""
        results = {}
        channels = channels or list(self.notifiers.keys())
        for channel in channels:
            results[channel] = self.send(channel, message, **kwargs)
        return results
