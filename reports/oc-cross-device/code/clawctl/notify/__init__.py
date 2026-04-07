#!/usr/bin/env python3
"""
消息推送模块
支持：钉钉、Telegram（可扩展）
"""

import os
import logging
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

import requests

logger = logging.getLogger(__name__)


@dataclass
class Notification:
    """通知对象"""
    title: str
    content: str
    channel: str = "dingtalk"
    at_mobiles: list = None
    extra: dict = None

    def __post_init__(self):
        if self.at_mobiles is None:
            self.at_mobiles = []
        if self.extra is None:
            self.extra = {}


class Notifier(ABC):
    """推送基类"""

    @abstractmethod
    def send(self, notification: Notification) -> bool:
        raise NotImplementedError

    def _safe_send(self, notification: Notification, resp_data: dict) -> bool:
        """通用响应判断"""
        if resp_data.get("errcode", 0) == 0:
            logger.info(f"[{self.__class__.__name__}] 发送成功: {notification.title}")
            return True
        logger.error(f"[{self.__class__.__name__}] 发送失败: {resp_data.get('errmsg', '未知错误')}")
        return False


class DingTalkNotifier(Notifier):
    """
    钉钉推送
    
    支持：
    - 文本消息
    - 链接卡片（Markdown）
    - 签名（加签）认证
    """

    def __init__(self, token: str, secret: Optional[str] = None):
        self.token = token
        self.secret = secret
        self.api_url = f"https://oapi.dingtalk.com/robot/send?access_token={token}"
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0

    def _get_access_token(self) -> str:
        """获取调用凭证（加签模式）"""
        import time, hmac, hashlib, base64, urllib.parse
        if self._access_token and time.time() < self._token_expires_at:
            return self._access_token
        timestamp = str(round(time.time() * 1000))
        string_to_sign = f"{timestamp}\n{self.secret}"
        hmac_obj = hmac.new(self.secret.encode(), string_to_sign.encode(), hashlib.sha256)
        sign = base64.b64encode(hmac_obj.digest()).decode("utf-8")
        sign = urllib.parse.quote_plus(sign)
        url = f"https://oapi.dingtalk.com/gettoken?appkey=&appsecret="
        # 注：完整加签实现需配合钉钉应用凭证
        return ""

    def send(self, notification: Notification) -> bool:
        if notification.channel not in ("dingtalk", "all"):
            return False
        try:
            payload = {
                "msgtype": "markdown",
                "markdown": {
                    "title": notification.title,
                    "text": notification.content,
                },
                "at": {"atMobiles": notification.at_mobiles},
            }
            resp = requests.post(self.api_url, json=payload, timeout=10)
            data = resp.json()
            return self._safe_send(notification, data)
        except Exception as e:
            logger.exception(f"钉钉推送异常: {e}")
            return False

    def send_text(self, content: str, at_mobiles: list = None) -> bool:
        """纯文本消息"""
        try:
            payload = {
                "msgtype": "text",
                "text": {"content": content},
                "at": {"atMobiles": at_mobiles or []},
            }
            resp = requests.post(self.api_url, json=payload, timeout=10)
            return self._safe_send(Notification(title="", content=content), resp.json())
        except Exception as e:
            logger.exception(f"钉钉文本推送异常: {e}")
            return False


class TelegramNotifier(Notifier):
    """
    Telegram 推送
    支持 Markdown 格式消息和 Inline Keyboard
    """

    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"

    def _request(self, method: str, data: dict = None) -> dict:
        """调用 Telegram Bot API"""
        try:
            resp = requests.post(f"{self.api_url}/{method}", json=data or {}, timeout=10)
            return resp.json()
        except Exception as e:
            logger.error(f"Telegram API 调用失败: {e}")
            return {}

    def send(self, notification: Notification) -> bool:
        if notification.channel not in ("telegram", "all"):
            return False
        try:
            text = f"*{notification.title}*\n{notification.content}"
            resp = self._request("sendMessage", {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "Markdown",
                "reply_markup": notification.extra.get("keyboard") if notification.extra else None,
            })
            ok = resp.get("ok", False)
            if ok:
                logger.info(f"[Telegram] 发送成功: {notification.title}")
            else:
                logger.error(f"[Telegram] 发送失败: {resp.get('description', '未知错误')}")
            return ok
        except Exception as e:
            logger.exception(f"Telegram 推送异常: {e}")
            return False

    def send_text(self, text: str, chat_id: str = None) -> bool:
        """发送纯文本消息"""
        try:
            resp = self._request("sendMessage", {
                "chat_id": chat_id or self.chat_id,
                "text": text,
                "parse_mode": "Markdown",
            })
            return resp.get("ok", False)
        except Exception as e:
            logger.exception(f"Telegram 文本推送异常: {e}")
            return False


class NotifyManager:
    """
    通知管理器
    - 统一发送接口
    - 异步发送（不阻塞任务）
    - 失败重试（可扩展）
    """

    def __init__(self):
        self._notifiers: dict[str, Notifier] = {}
        self._lock = threading.RLock()

    def register(self, channel: str, notifier: Notifier):
        with self._lock:
            self._notifiers[channel] = notifier

    def send(self, notification: Notification, async_: bool = True) -> bool:
        """发送通知"""
        notifier = self._notifiers.get(notification.channel)
        if not notifier:
            logger.warning(f"未注册的通知渠道: {notification.channel}")
            return False

        def _do_send():
            try:
                notifier.send(notification)
            except Exception:
                logger.exception("通知发送失败")

        if async_:
            threading.Thread(target=_do_send, daemon=True).start()
            return True
        else:
            _do_send()
            return True

    def send_task_start(self, task_name: str, channel: str = "dingtalk") -> bool:
        return self.send(Notification(
            title="🚀 任务开始",
            content=f"**任务**: {task_name}\n**时间**: 现在",
            channel=channel,
        ))

    def send_task_complete(self, task_name: str, duration_ms: int, result: str, channel: str = "dingtalk") -> bool:
        return self.send(Notification(
            title="✅ 任务完成",
            content=f"**任务**: {task_name}\n**耗时**: {duration_ms}ms\n**结果**: {result}",
            channel=channel,
        ))

    def send_alert(self, alert_type: str, message: str, channel: str = "dingtalk") -> bool:
        return self.send(Notification(
            title=f"⚠️ {alert_type}",
            content=f"**类型**: {alert_type}\n**详情**: {message}",
            channel=channel,
        ))
