"""钉钉通知渠道"""
import time
import hmac
import hashlib
import base64
import httpx
from typing import Optional
from .notify_manager import NotifyChannel


class DingTalkChannel(NotifyChannel):
    """
    钉钉自定义机器人通知渠道
    
    支持：文本消息、Markdown 消息、加签签名校验
    
    用法：
    ```python
    dt = DingTalkChannel(
        webhook_url="https://oapi.dingtalk.com/robot/send?access_token=xxx",
        secret="SECxxxx"          # 可选，开启加签
    )
    await nm.register(dt)
    ```
    """

    name = "dingtalk"

    def __init__(self, webhook_url: str, secret: Optional[str] = None):
        self.webhook_url = webhook_url
        self.secret = secret
        self._client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        await self._client.aclose()

    def _make_sign(self) -> tuple[str, str]:
        """生成加签"""
        timestamp = str(round(time.time() * 1000))
        s = f"{timestamp}\n{self.secret}"
        sign = base64.b64encode(
            hmac.new(self.secret.encode(), s.encode(), hashlib.sha256).digest()
        ).decode()
        return timestamp, sign

    def _build_payload(self, message: str, is_markdown: bool = False) -> dict:
        if is_markdown:
            return {
                "msgtype": "markdown",
                "markdown": {"title": "ClawRemote", "text": message},
            }
        return {"msgtype": "text", "text": {"content": message}}

    async def send(self, message: str, context: dict) -> bool:
        url = self.webhook_url
        if self.secret:
            ts, sign = self._make_sign()
            url = f"{self.webhook_url}&timestamp={ts}&sign={sign}"

        payload = self._build_payload(message, is_markdown=True)
        resp = await self._client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data.get("errcode", 0) == 0
