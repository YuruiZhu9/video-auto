"""
确认 Token（Confirm Token）机制

用于敏感操作的二次确认：
- 删除模板/任务
- 新建/删除 API Key
- 修改安全配置

流程：
1. 发起操作 → Server 生成 6 位 Token（有效期 5 分钟）
2. 向用户发送确认卡片（钉钉/Telegram）
3. 用户点击"确认" → Server 验证 Token → 执行操作
4. Token 一次性使用，过期自动失效
"""

import secrets
import asyncio
import logging
from dataclasses import dataclass, field
from typing import Optional, Callable, Awaitable
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class ConfirmToken:
    """确认 Token"""
    token: str               # 6位随机字符串
    action: str              # 操作类型（如 "template_delete"）
    resource_id: str         # 资源ID（如模板名）
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    expires_at: str = field(default_factory=lambda: (
        datetime.now() + timedelta(minutes=5)
    ).isoformat())
    confirmed: bool = False
    confirmed_at: Optional[str] = None
    request_ip: str = "unknown"
    key_name: str = ""
    extra: dict = field(default_factory=dict)  # 额外参数

    def is_valid(self) -> bool:
        if self.confirmed:
            return False
        if datetime.fromisoformat(self.expires_at) < datetime.now():
            return False
        return True

    def confirm(self):
        self.confirmed = True
        self.confirmed_at = datetime.now().isoformat()


class ConfirmTokenManager:
    """
    确认 Token 管理器

    使用示例：
    ```python
    ctm = ConfirmTokenManager(notify_manager)

    # 1. 创建 Token（危险操作前）
    token = ctm.create_token(
        action="template_delete",
        resource_id="daily_brief",
        key_name="admin_key",
        request_ip="12.34.56.78",
        extra={"template_name": "daily_brief"},
    )
    # 发送确认卡片
    await ctm.send_confirm_request(token, channel="dingtalk")

    # 2. 验证 Token（用户点击确认后）
    result = ctm.verify_and_consume(token.token)
    if result.success:
        await perform_dangerous_action(token)
    ```

    确认卡片示例（钉钉）：
    ┌─────────────────────────────────┐
    │ ⚠️ 确认操作                      │
    │                                │
    │ 操作：删除模板「daily_brief」    │
    │ 来源：admin_key（12.34.56.78）  │
    │ 有效期：5 分钟                  │
    │                                │
    │ [✅ 确认执行]  [❌ 取消]          │
    └─────────────────────────────────┘
    """

    def __init__(
        self,
        notify_manager,
        token_ttl_minutes: int = 5,
        max_pending: int = 50,
    ):
        self._tokens: dict[str, ConfirmToken] = {}
        self._notify = notify_manager
        self._ttl = token_ttl_minutes
        self._max_pending = max_pending
        self._lock = asyncio.Lock()

    def create_token(
        self,
        action: str,
        resource_id: str,
        key_name: str = "",
        request_ip: str = "unknown",
        extra: Optional[dict] = None,
    ) -> ConfirmToken:
        """
        创建确认 Token

        Args:
            action: 操作类型（action_resource 格式，如 template_delete）
            resource_id: 资源标识
            key_name: 发起操作的 Key 名称
            request_ip: 请求来源 IP
            extra: 额外参数（用于渲染确认卡片）

        Returns:
            ConfirmToken 对象
        """
        raw_token = secrets.token_hex(3)[:6].upper()  # 6位大写字母数字
        token = ConfirmToken(
            token=raw_token,
            action=action,
            resource_id=resource_id,
            key_name=key_name,
            request_ip=request_ip,
            extra=extra or {},
            expires_at=(datetime.now() + timedelta(minutes=self._ttl)).isoformat(),
        )
        self._tokens[raw_token] = token

        # 清理过期 token
        self._cleanup_expired()

        logger.info(f"[ConfirmToken] Created token {raw_token} for {action}/{resource_id}")
        return token

    async def send_confirm_request(
        self,
        token: ConfirmToken,
        channel: str = "dingtalk",
    ) -> dict:
        """
        发送确认请求卡片

        Args:
            token: 确认 Token
            channel: 推送渠道（dingtalk / telegram / feishu）

        Returns:
            发送结果
        """
        # 格式化确认卡片内容
        if token.action == "template_delete":
            title = "⚠️ 确认删除模板"
            detail = f"模板：**{token.resource_id}**"
        elif token.action == "task_cancel":
            title = "⚠️ 确认取消任务"
            detail = f"任务ID：**{token.resource_id}**"
        elif token.action == "key_create":
            title = "⚠️ 确认创建 API Key"
            detail = f"Key名：**{token.resource_id}**"
        elif token.action == "key_revoke":
            title = "⚠️ 确认撤销 API Key"
            detail = f"Key：**{token.resource_id}**"
        elif token.action == "job_delete":
            title = "⚠️ 确认删除定时任务"
            detail = f"任务：**{token.resource_id}**"
        else:
            title = "⚠️ 确认执行操作"
            detail = f"资源：**{token.resource_id}**"

        expires_min = self._ttl
        content = f"""**{title}**

**操作类型：** `{token.action}`
{detail}
**发起人：** {token.key_name or "未知"}
**来源IP：** `{token.request_ip}`
**Token：** `{token.token}`
**有效期：** {expires_min} 分钟内有效

⚠️ 此操作不可逆，请确认是否继续"""

        button_text = (
            f"✅ 确认执行 | Token: {token.token} | 请回复 same"
        )

        result = await self._notify.send_async(
            channel,
            content,
            extra={
                "confirm_token": token.token,
                "action": token.action,
                "resource_id": token.resource_id,
            }
        )

        logger.info(f"[ConfirmToken] Sent confirm request via {channel} for token {token.token}")
        return result

    def verify_token(self, token_str: str) -> Optional[ConfirmToken]:
        """
        验证 Token（不消费，用于查询状态）
        """
        token = self._tokens.get(token_str.upper())
        if not token:
            return None
        if not token.is_valid():
            return None
        return token

    def verify_and_consume(self, token_str: str) -> tuple[bool, Optional[ConfirmToken], str]:
        """
        验证并消费 Token

        Returns:
            (success, token_obj, error_message)
        """
        token_str = token_str.upper()
        token = self._tokens.get(token_str)

        if not token:
            return False, None, "Token 不存在"

        if not token.is_valid():
            if token.confirmed:
                return False, None, "Token 已使用"
            return False, None, "Token 已过期"

        token.confirm()
        logger.info(f"[ConfirmToken] Token {token_str} consumed for {token.action}/{token.resource_id}")
        return True, token, ""

    def get_pending(self, action: Optional[str] = None) -> list[ConfirmToken]:
        """获取当前待确认的 Token"""
        tokens = [t for t in self._tokens.values() if t.is_valid()]
        if action:
            tokens = [t for t in tokens if t.action == action]
        return tokens

    def _cleanup_expired(self):
        """清理过期 Token"""
        now = datetime.now()
        expired = [
            k for k, t in self._tokens.items()
            if datetime.fromisoformat(t.expires_at) < now
        ]
        for k in expired:
            del self._tokens[k]
        # 限制总数
        if len(self._tokens) > self._max_pending:
            sorted_tokens = sorted(
                self._tokens.items(),
                key=lambda x: x[1].created_at
            )
            for k, _ in sorted_tokens[:len(self._tokens) - self._max_pending]:
                del self._tokens[k]
