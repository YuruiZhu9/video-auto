"""
触发器引擎

支持多种触发方式：
- HTTPTrigger: HTTP 请求触发（FastAPI route）
- CronTrigger: 定时任务触发
- WebhookTrigger: 外部 Webhook 触发
"""

import asyncio
import hmac
import hashlib
import base64
import time
from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime
import croniter


class Trigger(ABC):
    """触发器基类"""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    async def stop(self):
        pass


class HTTPTrigger(Trigger):
    """HTTP 触发器 — 提供 FastAPI 路由处理函数"""

    def __init__(self, task_manager, auth_manager, rate_limiter=None):
        super().__init__("http")
        self.task_manager = task_manager
        self.auth_manager = auth_manager
        self.rate_limiter = rate_limiter

    async def start(self):
        pass

    async def stop(self):
        pass

    async def handle_create_task(self, request_data: dict, api_key_obj) -> dict:
        from .task import TaskStatus
        if api_key_obj.level.value < 20:
            raise PermissionError("EXECUTE 权限不足")
        if self.rate_limiter:
            await self.rate_limiter.check(api_key_obj.key_id, api_key_obj.level.name)

        if "template" in request_data:
            task = await self.task_manager.create_from_template(
                template_name=request_data["template"],
                params=request_data.get("params", {}),
                notify_channels=request_data.get("notify_channels"),
            )
        elif "task" in request_data:
            td = request_data["task"]
            task = await self.task_manager.create(
                name=td.get("name", "manual_task"),
                action=td.get("action", "spawn"),
                params=td.get("params", {}),
                notify_channels=request_data.get("notify_channels"),
            )
        else:
            raise ValueError("必须提供 template 或 task 字段")

        return {"task_id": task.task_id, "name": task.name,
                "status": task.status.value, "created_at": task.created_at}

    async def handle_get_task(self, task_id: str, api_key_obj) -> dict:
        if api_key_obj.level.value < 10:
            raise PermissionError("READ_ONLY 权限不足")
        task = self.task_manager.get_task(task_id)
        if not task:
            raise ValueError(f"任务不存在: {task_id}")
        return task.to_dict()

    async def handle_list_tasks(self, status: Optional[str], limit: int, api_key_obj) -> dict:
        if api_key_obj.level.value < 10:
            raise PermissionError("READ_ONLY 权限不足")
        from .task import TaskStatus
        status_enum = TaskStatus(status) if status else None
        tasks = self.task_manager.list_tasks(status=status_enum, limit=limit)
        return {"tasks": [t.to_dict() for t in tasks], "total": len(tasks), "limit": limit}

    async def handle_cancel_task(self, task_id: str, api_key_obj) -> dict:
        if api_key_obj.level.value < 20:
            raise PermissionError("EXECUTE 权限不足")
        await self.task_manager.cancel(task_id)
        return {"task_id": task_id, "status": "cancelled"}


class CronTrigger(Trigger):
    """定时触发器 — 基于 cron 表达式定时触发模板任务"""

    def __init__(self, task_manager):
        super().__init__("cron")
        self.task_manager = task_manager
        self._schedules: dict[str, str] = {}
        self._running = False
        self._task: Optional[asyncio.Task] = None

    def add_schedule(self, template_name: str, cron_expr: str):
        croniter.validate(cron_expr)
        self._schedules[template_name] = cron_expr

    def remove_schedule(self, template_name: str):
        self._schedules.pop(template_name, None)

    async def start(self):
        self._running = True
        self._task = asyncio.create_task(self._run())

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _run(self):
        last_check = 0
        while self._running:
            now = time.time()
            if now - last_check >= 30:  # 每 30 秒检查一次
                last_check = now
                for template_name, cron_expr in list(self._schedules.items()):
                    cron = croniter.croniter(cron_expr, datetime.now())
                    prev = cron.get_prev()
                    if now - prev.timestamp() < 60:
                        try:
                            task = await self.task_manager.create_from_template(template_name)
                            print(f"[CronTrigger] 触发: {template_name} -> {task.task_id}")
                        except Exception as e:
                            print(f"[CronTrigger] 失败: {e}")
            await asyncio.sleep(5)


class WebhookTrigger(Trigger):
    """外部 Webhook 触发器 — 支持 HMAC-SHA256 签名验证"""

    def __init__(self, task_manager, secret: Optional[str] = None):
        super().__init__("webhook")
        self.task_manager = task_manager
        self.secret = secret

    async def start(self):
        pass

    async def stop(self):
        pass

    def verify_signature(self, body: bytes, signature: Optional[str]) -> bool:
        if not self.secret or not signature:
            return bool(self.secret)
        expected = "sha256=" + hmac.new(
            self.secret.encode(), body, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

    async def handle(self, payload: dict) -> dict:
        template = payload.get("template")
        if not template:
            raise ValueError("必须提供 template 字段")
        task = await self.task_manager.create_from_template(
            template_name=template,
            params=payload.get("params", {}),
        )
        return {"task_id": task.task_id, "status": task.status.value}


class DingTalkTrigger(Trigger):
    """钉钉消息触发器 — 支持加签签名校验 + 命令解析"""

    def __init__(self, task_manager, secret: Optional[str] = None, keywords: Optional[list] = None):
        super().__init__("dingtalk")
        self.task_manager = task_manager
        self.secret = secret
        self.keywords = keywords or ["/任务", "/执行"]

    async def start(self):
        pass

    async def stop(self):
        pass

    def verify_signature(self, timestamp: str, sign: str, secret: Optional[str] = None) -> bool:
        secret = secret or self.secret
        if not secret or not sign:
            return False
        s = f"{timestamp}\n{secret}"
        expected = base64.b64encode(
            hmac.new(s.encode(), s.encode(), hashlib.sha256).digest()
        ).decode()
        return hmac.compare_digest(expected, sign)

    def parse_command(self, text: str) -> Optional[dict]:
        text = text.strip()
        for kw in self.keywords:
            if text.startswith(kw):
                cmd = text[len(kw):].strip()
                parts = cmd.split(maxsplit=1)
                if not parts:
                    return None
                template = parts[0]
                params = {}
                if len(parts) > 1:
                    for pair in parts[1].split():
                        if "=" in pair:
                            k, v = pair.split("=", 1)
                            params[k] = v
                return {"template": template, "params": params}
        return None

    async def handle(self, payload: dict) -> Optional[dict]:
        text = payload.get("text", {}).get("content", "")
        cmd = self.parse_command(text)
        if not cmd:
            return None
        task = await self.task_manager.create_from_template(**cmd)
        return {"task_id": task.task_id, "name": task.name, "status": task.status.value}


class RateLimiter:
    """滑动窗口频率限制器"""

    def __init__(self, limits: dict[str, int]):
        self.limits = limits
        self._windows: dict[str, list[float]] = {}
        self._lock = asyncio.Lock()

    async def check(self, key_id: str, level: str):
        limit = self.limits.get(level, 30)
        window = 60.0
        async with self._lock:
            now = time.time()
            if key_id not in self._windows:
                self._windows[key_id] = []
            self._windows[key_id] = [t for t in self._windows[key_id] if now - t < window]
            if len(self._windows[key_id]) >= limit:
                raise PermissionError(f"频率超限：{level} 每分钟最多 {limit} 次")
            self._windows[key_id].append(now)
