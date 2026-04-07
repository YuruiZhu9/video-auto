"""Telegram Bot 推送"""
import logging
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Telegram Bot 推送"""

    def __init__(self, bot_token: str, default_chat_id: Optional[str] = None):
        self.bot_token = bot_token
        self.default_chat_id = default_chat_id
        self.api_base = f"https://api.telegram.org/bot{bot_token}"

    def send_message(
        self,
        text: str,
        chat_id: Optional[str] = None,
        parse_mode: str = "Markdown",
        disable_notification: bool = False,
    ) -> Dict[str, Any]:
        """发送消息"""
        chat_id = chat_id or self.default_chat_id
        if not chat_id:
            raise ValueError("chat_id is required")
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_notification": disable_notification,
        }
        try:
            resp = requests.post(
                f"{self.api_base}/sendMessage",
                json=payload,
                timeout=10,
            )
            result = resp.json()
            if not result.get("ok"):
                logger.error(f"Telegram send failed: {result}")
            return result
        except Exception as e:
            logger.error(f"Telegram request error: {e}")
            return {"ok": False, "description": str(e)}

    def send_photo(self, photo_url: str, caption: str = "", chat_id: Optional[str] = None) -> Dict[str, Any]:
        chat_id = chat_id or self.default_chat_id
        payload = {"chat_id": chat_id, "photo": photo_url, "caption": caption}
        try:
            resp = requests.post(f"{self.api_base}/sendPhoto", json=payload, timeout=10)
            return resp.json()
        except Exception as e:
            return {"ok": False, "description": str(e)}

    def send_template(self, template_key: str, **kwargs) -> Dict[str, Any]:
        from .dingtalk import TEMPLATES
        template = TEMPLATES.get(template_key, "{message}").format(**kwargs)
        return self.send_message(template)
