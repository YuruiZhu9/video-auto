#!/usr/bin/env python3
"""
Webhook 回调系统
任务完成/失败/启动时自动向外部系统发送 HTTP POST 回调
支持：签名验证、重试机制、回调日志
"""

import asyncio
import hashlib
import hmac
import logging
import queue
import secrets
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import urlencode

import httpx

logger = logging.getLogger("clawctl.webhook")


class WebhookEvent(str, Enum):
    """支持的 Webhook 事件类型"""
    TASK_CREATED = "task.created"
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    TASK_CANCELLED = "task.cancelled"
    SYSTEM_ALERT = "system.alert"
    INSTANCE_UP = "instance.up"
    INSTANCE_DOWN = "instance.down"


@dataclass
class WebhookEndpoint:
    """Webhook 端点配置"""
    id: str
    url: str
    secret: str = ""                      # 签名密钥（可选）
    events: List[WebhookEvent] = field(default_factory=list)  # 订阅的事件
    enabled: bool = True
    retry_count: int = 3                 # 失败重试次数
    retry_delay: float = 5.0             # 重试间隔（秒）
    timeout: float = 10.0                 # 请求超时（秒）
    headers: Dict[str, str] = field(default_factory=dict)  # 自定义请求头
    tags: List[str] = field(default_factory=list)  # 标签（用于路由）
    description: str = ""
    total_calls: int = 0
    failed_calls: int = 0
    last_call_at: Optional[float] = None
    last_status_code: Optional[int] = None


@dataclass
class WebhookDelivery:
    """Webhook 投递记录"""
    id: str
    endpoint_id: str
    event: str
    payload: Dict[str, Any]
    status: str  # pending | success | failed | retrying
    attempts: int = 0
    response_code: Optional[int] = None
    response_body: Optional[str] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    delivered_at: Optional[float] = None


class WebhookSigner:
    """Webhook 签名工具"""

    @staticmethod
    def sign(payload: bytes, secret: str, timestamp: Optional[int] = None) -> str:
        """生成 HMAC-SHA256 签名"""
        if not secret:
            return ""
        if timestamp is None:
            timestamp = int(time.time())
        signed_payload = f"{timestamp}.{payload.decode('utf-8')}"
        signature = hmac.new(
            secret.encode("utf-8"),
            signed_payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return f"t={timestamp},v1={signature}"

    @staticmethod
    def verify(signature: str, payload: bytes, secret: str) -> bool:
        """验证 Webhook 签名"""
        if not signature or not secret:
            return True
        parts = dict(p.split("=", 1) for p in signature.split(",") if "=" in p)
        ts = int(parts.get("t", 0))
        # 5 分钟内的签名有效
        if abs(time.time() - ts) > 300:
            return False
        expected = WebhookSigner.sign(payload, secret, ts)
        return hmac.compare_digest(signature, expected)


class WebhookManager:
    """
    Webhook 管理器

    功能：
    - 注册/管理多个 Webhook 端点
    - 根据事件类型自动路由
    - HMAC-SHA256 签名
    - 异步投递 + 重试机制
    - 投递日志（内存 + 可选数据库）
    """

    def __init__(self, max_workers: int = 4):
        self._endpoints: Dict[str, WebhookEndpoint] = {}
        self._lock = threading.RLock()
        self._delivery_queue: queue.Queue = queue.Queue()
        self._worker_threads: List[threading.Thread] = []
        self._stop_workers = threading.Event()
        self._delivery_log: List[WebhookDelivery] = []
        self._max_log_size = 500
        self._async_client: Optional[httpx.AsyncClient] = None
        self._event_handlers: Dict[WebhookEvent, List[Callable]] = {}

        # 启动投递线程
        for i in range(max_workers):
            t = threading.Thread(target=self._delivery_worker, daemon=True, name=f"WebhookWorker-{i}")
            t.start()
            self._worker_threads.append(t)
        logger.info(f"🪝 Webhook 管理器已启动（{max_workers} 个投递线程）")

    # ─── 端点管理 ───────────────────────────────────────────────

    def add_endpoint(self, endpoint: WebhookEndpoint) -> WebhookEndpoint:
        """注册 Webhook 端点"""
        with self._lock:
            if endpoint.id in self._endpoints:
                raise ValueError(f"Endpoint ID 已存在: {endpoint.id}")
            self._endpoints[endpoint.id] = endpoint
            logger.info(f"✅ 注册 Webhook 端点: {endpoint.id} → {endpoint.url} [{', '.join(e.value for e in endpoint.events)}]")
        return endpoint

    def remove_endpoint(self, endpoint_id: str) -> bool:
        """移除 Webhook 端点"""
        with self._lock:
            if endpoint_id in self._endpoints:
                del self._endpoints[endpoint_id]
                logger.info(f"🗑️ 移除 Webhook 端点: {endpoint_id}")
                return True
            return False

    def update_endpoint(self, endpoint_id: str, **kwargs) -> Optional[WebhookEndpoint]:
        """更新端点配置"""
        with self._lock:
            ep = self._endpoints.get(endpoint_id)
            if not ep:
                return None
            for k, v in kwargs.items():
                if hasattr(ep, k):
                    setattr(ep, k, v)
            return ep

    def get_endpoint(self, endpoint_id: str) -> Optional[WebhookEndpoint]:
        with self._lock:
            return self._endpoints.get(endpoint_id)

    def list_endpoints(self) -> List[WebhookEndpoint]:
        with self._lock:
            return list(self._endpoints.values())

    def enable_endpoint(self, endpoint_id: str, enabled: bool = True):
        ep = self.get_endpoint(endpoint_id)
        if ep:
            ep.enabled = enabled
            logger.info(f"{'✅ 启用' if enabled else '⏸ 禁用'} Webhook 端点: {endpoint_id}")

    # ─── 投递 ───────────────────────────────────────────────────

    def _deliver_sync(self, endpoint: WebhookEndpoint, event: WebhookEvent, payload: Dict[str, Any]) -> WebhookDelivery:
        """同步投递（由投递线程调用）"""
        import json
        body = json.dumps(payload, ensure_ascii=False, indent=2)
        delivery = WebhookDelivery(
            id=secrets.token_urlsafe(16),
            endpoint_id=endpoint.id,
            event=event.value,
            payload=payload,
            status="pending",
        )

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "clawctl-webhook/1.0",
            "X-Webhook-Event": event.value,
            "X-Webhook-Delivery": delivery.id,
            **endpoint.headers,
        }

        # 签名
        if endpoint.secret:
            headers["X-Webhook-Signature"] = WebhookSigner.sign(body.encode("utf-8"), endpoint.secret)

        endpoint.total_calls += 1
        endpoint.last_call_at = time.time()

        try:
            resp = httpx.post(
                endpoint.url,
                content=body,
                headers=headers,
                timeout=endpoint.timeout,
                follow_redirects=True,
            )
            endpoint.last_status_code = resp.status_code
            delivery.response_code = resp.status_code
            delivery.response_body = resp.text[:500] if resp.text else ""

            if 200 <= resp.status_code < 300:
                delivery.status = "success"
                delivery.delivered_at = time.time()
                logger.debug(f"✅ Webhook 投递成功: {endpoint.id} [{event.value}] {resp.status_code}")
            else:
                delivery.status = "failed"
                delivery.error = f"HTTP {resp.status_code}"
                endpoint.failed_calls += 1
                logger.warning(f"⚠️ Webhook 投递失败: {endpoint.id} [{event.value}] {resp.status_code}")

        except Exception as e:
            delivery.status = "failed"
            delivery.error = str(e)
            endpoint.failed_calls += 1
            endpoint.last_status_code = None
            logger.warning(f"⚠️ Webhook 投递异常: {endpoint.id} [{event.value}] {e}")

        return delivery

    def _delivery_worker(self):
        """Webhook 投递工作线程"""
        while not self._stop_workers.is_set():
            try:
                item = self._delivery_queue.get(timeout=1)
                endpoint, event, payload = item
                delivery = self._deliver_sync(endpoint, event, payload)

                # 重试逻辑
                if delivery.status == "failed" and endpoint.retry_count > 0:
                    for attempt in range(endpoint.retry_count):
                        time.sleep(endpoint.retry_delay * (attempt + 1))
                        delivery = self._deliver_sync(endpoint, event, payload)
                        if delivery.status == "success":
                            break
                        delivery.status = "retrying"
                        delivery.attempts = attempt + 2

                # 记录到日志
                with self._lock:
                    self._delivery_log.append(delivery)
                    if len(self._delivery_log) > self._max_log_size:
                        self._delivery_log = self._delivery_log[-self._max_log_size:]

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Webhook 投递线程异常: {e}")

    def emit(self, event: WebhookEvent, payload: Dict[str, Any], target_endpoint_id: Optional[str] = None):
        """
        触发 Webhook 投递

        Args:
            event: 事件类型
            payload: 投递数据
            target_endpoint_id: 指定端点（None = 所有订阅该事件的端点）
        """
        with self._lock:
            if target_endpoint_id:
                endpoints = [self._endpoints.get(target_endpoint_id)]
            else:
                endpoints = [
                    ep for ep in self._endpoints.values()
                    if ep.enabled and event in ep.events
                ]

        for endpoint in endpoints:
            if endpoint:
                self._delivery_queue.put((endpoint, event, payload))

    def trigger_task_event(self, event: WebhookEvent, task_data: Dict[str, Any]):
        """快捷方法：触发任务相关事件，自动补充元数据"""
        import datetime
        payload = {
            "event": event.value,
            "timestamp": datetime.datetime.now().isoformat(),
            "task": task_data,
        }
        self.emit(event, payload)

    def trigger_instance_event(self, event: WebhookEvent, instance_id: str, instance_data: Dict[str, Any]):
        """快捷方法：触发实例相关事件"""
        import datetime
        payload = {
            "event": event.value,
            "timestamp": datetime.datetime.now().isoformat(),
            "instance_id": instance_id,
            "instance": instance_data,
        }
        self.emit(event, payload)

    # ─── 日志查询 ───────────────────────────────────────────────

    def get_delivery_log(self, endpoint_id: Optional[str] = None, limit: int = 50) -> List[WebhookDelivery]:
        with self._lock:
            log = self._delivery_log
            if endpoint_id:
                log = [d for d in log if d.endpoint_id == endpoint_id]
            return log[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            total_calls = sum(ep.total_calls for ep in self._endpoints.values())
            failed_calls = sum(ep.failed_calls for ep in self._endpoints.values())
            return {
                "total_endpoints": len(self._endpoints),
                "enabled_endpoints": sum(1 for ep in self._endpoints.values() if ep.enabled),
                "total_calls": total_calls,
                "failed_calls": failed_calls,
                "success_rate": round((total_calls - failed_calls) / max(total_calls, 1) * 100, 1),
                "queue_size": self._delivery_queue.qsize(),
                "endpoints": [
                    {
                        "id": ep.id,
                        "url": ep.url,
                        "events": [e.value for e in ep.events],
                        "enabled": ep.enabled,
                        "total_calls": ep.total_calls,
                        "failed_calls": ep.failed_calls,
                        "success_rate": round((ep.total_calls - ep.failed_calls) / max(ep.total_calls, 1) * 100, 1),
                        "last_call_at": ep.last_call_at,
                        "last_status_code": ep.last_status_code,
                    }
                    for ep in self._endpoints.values()
                ],
            }

    def shutdown(self):
        """优雅关闭"""
        self._stop_workers.set()
        for t in self._worker_threads:
            t.join(timeout=5)
        logger.info("🪝 Webhook 管理器已关闭")


# ═══════════════════════════════════════════════════════════════════
# 全局单例
# ═══════════════════════════════════════════════════════════════════

_webhook_manager: Optional[WebhookManager] = None


def get_webhook_manager() -> WebhookManager:
    global _webhook_manager
    if _webhook_manager is None:
        _webhook_manager = WebhookManager(max_workers=4)
    return _webhook_manager


def init_webhook_manager(configs: List[Dict[str, Any]] = None) -> WebhookManager:
    """初始化 Webhook 管理器"""
    mgr = get_webhook_manager()
    if configs:
        for cfg in configs:
            events = [WebhookEvent(e) for e in cfg.get("events", []) if e in [ev.value for ev in WebhookEvent]]
            ep = WebhookEndpoint(
                id=cfg["id"],
                url=cfg["url"],
                secret=cfg.get("secret", ""),
                events=events,
                enabled=cfg.get("enabled", True),
                retry_count=cfg.get("retry_count", 3),
                retry_delay=cfg.get("retry_delay", 5.0),
                timeout=cfg.get("timeout", 10.0),
                headers=cfg.get("headers", {}),
                tags=cfg.get("tags", []),
                description=cfg.get("description", ""),
            )
            mgr.add_endpoint(ep)
    return mgr


# ─── 快捷模板 ───────────────────────────────────────────────────────

WEBHOOK_TASK_PAYLOAD_TEMPLATE = """{{
  "event": "{event}",
  "timestamp": "{timestamp}",
  "task": {{
    "id": "{task_id}",
    "name": "{task_name}",
    "action": "{task_action}",
    "status": "{task_status}",
    "duration_ms": {duration_ms},
    "result_summary": "{result_summary}",
    "error": {error}
  }},
  "meta": {{
    "source": "clawctl",
    "version": "1.5.0"
  }}
}}"""
