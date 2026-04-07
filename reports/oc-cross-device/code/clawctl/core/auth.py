#!/usr/bin/env python3
"""
认证与安全模块
- API Key 管理
- 请求签名验证
- 操作审计
- 速率限制
"""

import os, time, hmac, hashlib, logging, threading
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from functools import wraps

logger = logging.getLogger(__name__)


class KeyLevel(Enum):
    READ = "read"
    EXEC = "exec"
    ADMIN = "admin"


@dataclass
class APIKey:
    id: str
    key: str
    level: KeyLevel
    name: str = ""
    ip_whitelist: Optional[list] = None
    rate_limit: int = 60
    enabled: bool = True


class AuditLogger:
    def __init__(self, log_file: str = "logs/audit.log"):
        self.log_file = log_file
        self._lock = threading.Lock()

    def log(self, key_id: str, action: str, path: str, ip: str, status: str, detail: str = ""):
        entry = f"{datetime.now().isoformat()} | key={key_id} | action={action} | path={path} | ip={ip} | status={status} | detail={detail}"
        with self._lock:
            try:
                os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(entry + "\n")
            except Exception:
                pass
        logger.info(entry)


class RateLimiter:
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._records: dict = {}
        self._lock = threading.RLock()

    def is_allowed(self, key_id: str) -> bool:
        now = time.time()
        window_start = now - self.window_seconds
        with self._lock:
            if key_id not in self._records:
                self._records[key_id] = []
            self._records[key_id] = [t for t in self._records[key_id] if t > window_start]
            if len(self._records[key_id]) >= self.max_requests:
                return False
            self._records[key_id].append(now)
            return True


class AuthManager:
    LEVEL_HIERARCHY = {KeyLevel.READ: 1, KeyLevel.EXEC: 2, KeyLevel.ADMIN: 3}

    def __init__(self):
        self._keys: dict = {}
        self._limiter = RateLimiter()
        self._audit = AuditLogger()
        self._lock = threading.RLock()
        self._webhook_secret: Optional[str] = None

    def add_key(self, key: APIKey):
        with self._lock:
            self._keys[key.key] = key

    def set_webhook_secret(self, secret: str):
        self._webhook_secret = secret

    def authenticate(self, key: str, required_level: KeyLevel = KeyLevel.READ) -> Optional[APIKey]:
        api_key = self._keys.get(key)
        if not api_key or not api_key.enabled:
            return None
        if self.LEVEL_HIERARCHY.get(api_key.level, 0) < self.LEVEL_HIERARCHY.get(required_level, 0):
            return None
        if not self._limiter.is_allowed(api_key.id):
            return None
        return api_key

    def verify_webhook_signature(self, body: bytes, signature: str) -> bool:
        if not self._webhook_secret:
            return False
        expected = hmac.new(self._webhook_secret.encode(), body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(f"sha256={expected}", signature)

    def audit(self, key_id: str, action: str, path: str, ip: str, status: str, detail: str = ""):
        self._audit.log(key_id, action, path, ip, status, detail)
