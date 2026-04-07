"""
认证与权限管理

- API Key 的创建、校验、权限分级
- 操作审计日志
"""

import os
import re
import uuid
import hashlib
import secrets
import asyncio
from enum import IntEnum
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


class KeyLevel(IntEnum):
    READ_ONLY = 10
    EXECUTE = 20
    ADMIN = 30

    @classmethod
    def from_str(cls, s: str) -> "KeyLevel":
        mapping = {
            "read_only": cls.READ_ONLY,
            "READ_ONLY": cls.READ_ONLY,
            "execute": cls.EXECUTE,
            "EXECUTE": cls.EXECUTE,
            "admin": cls.ADMIN,
            "ADMIN": cls.ADMIN,
        }
        return mapping.get(s.upper(), cls.READ_ONLY)


@dataclass
class APIKey:
    """API Key 数据结构"""
    key_id: str          # 哈希值（用于索引）
    key_prefix: str      # 前4位明文（用于识别）
    key_suffix: str      # 后4位明文（用于识别）
    level: KeyLevel
    name: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    expires_at: Optional[str] = None
    ip_whitelist: Optional[list] = None
    enabled: bool = True

    @property
    def display_key(self) -> str:
        return f"{self.key_prefix}...{self.key_suffix}"

    @property
    def is_expired(self) -> bool:
        if not self.expires_at:
            return False
        return datetime.fromisoformat(self.expires_at) < datetime.now()


def _hash_key(raw_key: str) -> str:
    """对原始 Key 做 SHA256 哈希"""
    return hashlib.sha256(raw_key.encode()).hexdigest()[:32]


def generate_api_key(level: KeyLevel = KeyLevel.EXECUTE) -> tuple[str, APIKey]:
    """
    生成一对 API Key
    
    Returns:
        (raw_key, APIKey对象) — raw_key 只在生成时返回一次，之后不再能获取
    """
    random_bytes = secrets.token_hex(16)
    raw_key = f"sk-{random_bytes}-{level.name}"
    key_id = _hash_key(raw_key)
    api_key = APIKey(
        key_id=key_id,
        key_prefix=raw_key[:8],
        key_suffix=raw_key[-6:],
        level=level,
        name="",
    )
    return raw_key, api_key


class AuthManager:
    """
    认证管理器
    
    负责：
    - API Key 存储与校验
    - 请求认证中间件
    - 操作审计日志
    """

    def __init__(self, storage_path: Optional[str] = None):
        self._keys: dict[str, APIKey] = {}
        self._audit_logs: list[dict] = []
        self._lock = asyncio.Lock()
        self._storage_path = storage_path
        self._load_keys()

    def _load_keys(self):
        """从环境变量/文件加载已有 Key"""
        # 可以扩展为从 SQLite/JSON 文件加载
        pass

    def create_key(
        self,
        level: KeyLevel,
        name: str,
        ip_whitelist: Optional[list] = None,
        expires_at: Optional[str] = None,
    ) -> tuple[str, APIKey]:
        """创建新的 API Key"""
        raw_key, api_key = generate_api_key(level)
        api_key.name = name
        api_key.ip_whitelist = ip_whitelist
        api_key.expires_at = expires_at
        self._keys[api_key.key_id] = api_key
        return raw_key, api_key

    def revoke_key(self, key_id: str) -> bool:
        api_key = self._keys.get(key_id)
        if not api_key:
            return False
        api_key.enabled = False
        return True

    def validate_key(self, raw_key: str) -> Optional[APIKey]:
        """
        校验 API Key
        
        检查项：
        1. 格式是否合法
        2. 是否存在于存储
        3. 是否已启用
        4. 是否未过期
        """
        if not raw_key or not raw_key.startswith("sk-"):
            return None

        key_id = _hash_key(raw_key)
        api_key = self._keys.get(key_id)

        if not api_key or not api_key.enabled:
            return None
        if api_key.is_expired:
            return None

        return api_key

    def check_ip(self, api_key: APIKey, client_ip: str) -> bool:
        """检查 IP 白名单"""
        if not api_key.ip_whitelist:
            return True  # 无白名单则允许
        return client_ip in api_key.ip_whitelist

    def list_keys(self) -> list[dict]:
        """列出所有 Key（非敏感）"""
        return [
            {
                "key_id": k.key_id,
                "display_key": k.display_key,
                "level": k.level.name,
                "name": k.name,
                "created_at": k.created_at,
                "expires_at": k.expires_at,
                "enabled": k.enabled,
            }
            for k in self._keys.values()
        ]

    async def audit(
        self,
        api_key: APIKey,
        action: str,
        resource: str,
        result: str,
        params: Optional[dict] = None,
        ip: str = "unknown",
    ):
        """记录审计日志"""
        log = {
            "timestamp": datetime.now().isoformat(),
            "api_key_id": api_key.key_id,
            "api_key_name": api_key.name,
            "level": api_key.level.name,
            "action": action,
            "resource": resource,
            "result": result,
            "ip": ip,
            "params": params,
        }
        async with self._lock:
            self._audit_logs.append(log)
            # 只保留最近 10000 条
            if len(self._audit_logs) > 10000:
                self._audit_logs = self._audit_logs[-5000:]

    def get_audit_logs(
        self,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict]:
        logs = self._audit_logs
        if from_date:
            logs = [l for l in logs if l["timestamp"] >= from_date]
        if to_date:
            logs = [l for l in logs if l["timestamp"] <= to_date]
        return logs[-limit:]


# ── 请求认证装饰器（适配 FastAPI）─────────────────────────────

from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

_bearer = HTTPBearer(auto_error=False)


async def get_api_key(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    auth_manager: AuthManager = Depends(),
) -> APIKey:
    """
    FastAPI 依赖注入：获取并验证当前请求的 API Key
    
    用法：
    ```python
    @app.post("/api/v1/tasks")
    async def create_task(
        req: Request,
        api_key: APIKey = Depends(get_api_key),
    ):
        ...
    ```
    """
    # 优先从 Authorization Header 获取
    raw_key = None
    if credentials:
        raw_key = credentials.credentials
    # 备选：从 query 参数获取
    if not raw_key:
        raw_key = request.query_params.get("api_key")

    if not raw_key:
        raise HTTPException(401, "缺少 API Key")

    api_key = auth_manager.validate_key(raw_key)
    if not api_key:
        raise HTTPException(401, "无效或已停用的 API Key")

    # IP 检查
    client_ip = request.client.host if request.client else "unknown"
    if not auth_manager.check_ip(api_key, client_ip):
        raise HTTPException(403, "IP 不在白名单中")

    # 注入到 request state 供后续使用
    request.state.api_key = api_key
    return api_key


def require_level(min_level: KeyLevel):
    """权限等级依赖工厂"""
    async def checker(api_key: APIKey = Depends(get_api_key)) -> APIKey:
        if api_key.level.value < min_level.value:
            raise HTTPException(403, f"需要 {min_level.name} 权限")
        return api_key
    return checker
