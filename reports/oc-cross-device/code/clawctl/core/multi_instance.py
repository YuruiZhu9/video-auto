#!/usr/bin/env python3
"""
多 OpenClaw 实例管理器 (Multi-Instance Manager)
v2.4.0 新增

支持：
- 注册多个 OpenClaw 实例（不同机器/端口/用途）
- 实例健康检查（心跳 + 响应时间）
- 智能路由：round-robin / least-loaded / failover
- 实例分组（不同用途：info-fetcher / tech-analyst / 等）
- 熔断器模式：连续失败自动摘除
"""

import json
import logging
import threading
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Callable, Any

import requests

logger = logging.getLogger(__name__)


class InstanceStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"    # 慢但可用
    FAILED = "failed"         # 熔断器打开
    UNKNOWN = "unknown"


class LoadBalanceStrategy(Enum):
    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    FAILOVER = "failover"     # 主备切换


@dataclass
class InstanceInfo:
    """OpenClaw 实例信息"""
    id: str
    name: str                         # 显示名称，如 "主实例-北京"
    base_url: str                      # Gateway URL
    api_key: str
    group: str = "default"            # 实例分组
    tags: list[str] = field(default_factory=list)
    max_concurrent: int = 5           # 最大并发任务数
    enabled: bool = True

    # 健康状态（运行时计算）
    status: InstanceStatus = InstanceStatus.UNKNOWN
    active_tasks: int = 0
    total_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0     # ms
    last_heartbeat: Optional[datetime] = None
    last_error: Optional[str] = None

    # 熔断器
    consecutive_failures: int = 0
    circuit_open_at: Optional[datetime] = None   # 熔断器打开时间

    def to_dict(self) -> dict:
        d = asdict(self)
        d["status"] = self.status.value
        return d

    @property
    def failure_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.failed_requests / self.total_requests


@dataclass
class HealthCheckResult:
    """健康检查结果"""
    instance_id: str
    success: bool
    response_time_ms: float
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class CircuitBreaker:
    """熔断器：连续失败 N 次后自动摘除实例"""

    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout: int = 60,
        half_open_requests: int = 1,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout      # 秒
        self.half_open_requests = half_open_requests
        self._failures = 0
        self._open_at: Optional[datetime] = None
        self._half_open_tested = 0
        self._lock = threading.Lock()

    def record_success(self):
        with self._lock:
            self._failures = 0
            self._open_at = None
            self._half_open_tested = 0

    def record_failure(self) -> bool:
        """记录失败，返回是否触发熔断"""
        with self._lock:
            self._failures += 1
            if self._failures >= self.failure_threshold:
                self._open_at = datetime.now()
                return True
            return False

    def is_open(self) -> bool:
        with self._lock:
            if self._open_at is None:
                return False
            elapsed = (datetime.now() - self._open_at).total_seconds()
            if elapsed >= self.recovery_timeout:
                # 进入半开状态
                self._half_open_tested = 0
                return False
            return True

    def try_half_open(self) -> bool:
        """尝试半开，返回是否放行一个测试请求"""
        with self._lock:
            if self._open_at is None:
                return True
            elapsed = (self._open_at - datetime.now()).total_seconds()
            if elapsed >= self.recovery_timeout:
                self._half_open_tested += 1
                return self._half_open_tested <= self.half_open_requests
            return False


class MultiInstanceManager:
    """
    多实例管理器

    使用示例：
        mgr = MultiInstanceManager()
        mgr.register_instance(InstanceInfo(
            id="prod-1", name="生产实例", base_url="http://192.168.1.10:18789", api_key="xxx"
        ))
        mgr.register_instance(InstanceInfo(
            id="prod-2", name="灾备实例", base_url="http://192.168.1.11:18789", api_key="xxx"
        ))
        mgr.start_health_check(interval=15)

        # 智能选择最优实例
        client = mgr.get_client(group="default", strategy=LoadBalanceStrategy.FAILOVER)
        resp = client.get_status()
    """

    def __init__(self):
        self._instances: dict[str, InstanceInfo] = {}
        self._circuits: dict[str, CircuitBreaker] = {}
        self._lock = threading.RLock()
        self._health_check_thread: Optional[threading.Thread] = None
        self._stop_health_check = threading.Event()
        self._health_check_interval = 15      # 秒
        self._round_robin_index: dict[str, int] = {}  # per-group round-robin 计数器

        # 健康检查回调
        self._on_instance_unhealthy: Optional[Callable[[str, str], None]] = None
        self._on_instance_recovered: Optional[Callable[[str], None]] = None

    # ── 实例管理 ─────────────────────────────────────────────────

    def register_instance(self, info: InstanceInfo) -> bool:
        """注册一个 OpenClaw 实例"""
        with self._lock:
            if info.id in self._instances:
                logger.warning(f"Instance {info.id} already registered, updating")
            self._instances[info.id] = info
            self._circuits[info.id] = CircuitBreaker()
            self._round_robin_index.setdefault(info.group, 0)
            logger.info(f"Registered OpenClaw instance: {info.name} ({info.base_url})")
            return True

    def unregister_instance(self, instance_id: str) -> bool:
        """注销实例"""
        with self._lock:
            if instance_id in self._instances:
                del self._instances[instance_id]
                if instance_id in self._circuits:
                    del self._circuits[instance_id]
                logger.info(f"Unregistered instance: {instance_id}")
                return True
            return False

    def get_instance(self, instance_id: str) -> Optional[InstanceInfo]:
        return self._instances.get(instance_id)

    def list_instances(self, group: Optional[str] = None, enabled_only: bool = False) -> list[dict]:
        """列出所有实例"""
        with self._lock:
            result = []
            for info in self._instances.values():
                if group and info.group != group:
                    continue
                if enabled_only and not info.enabled:
                    continue
                result.append(info.to_dict())
            return result

    def update_instance(self, instance_id: str, **kwargs) -> bool:
        """更新实例配置（部分字段）"""
        with self._lock:
            info = self._instances.get(instance_id)
            if not info:
                return False
            for key, value in kwargs.items():
                if hasattr(info, key):
                    setattr(info, key, value)
            return True

    # ── 实例选择策略 ─────────────────────────────────────────────

    def get_best_instance(
        self,
        group: str = "default",
        strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUND_ROBIN,
        required_capability: Optional[str] = None,
    ) -> Optional[InstanceInfo]:
        """
        根据策略选择最优实例

        Args:
            group: 实例分组
            strategy: 负载均衡策略
            required_capability: 需要的标签（如 "vision", "code"）
        """
        with self._lock:
            candidates = [
                i for i in self._instances.values()
                if i.group == group and i.enabled
                and i.status not in (InstanceStatus.FAILED, InstanceStatus.UNKNOWN)
                and (not required_capability or required_capability in i.tags)
            ]

            if not candidates:
                # 降级：尝试未检查的实例
                candidates = [
                    i for i in self._instances.values()
                    if i.group == group and i.enabled
                ]
                if not candidates:
                    return None

            if strategy == LoadBalanceStrategy.ROUND_ROBIN:
                idx = self._round_robin_index.get(group, 0) % len(candidates)
                self._round_robin_index[group] = idx + 1
                return candidates[idx]

            elif strategy == LoadBalanceStrategy.LEAST_LOADED:
                return min(candidates, key=lambda i: i.active_tasks)

            elif strategy == LoadBalanceStrategy.FAILOVER:
                # 优先选主实例（id 排序第一个，或标记 primary 的）
                primaries = [i for i in candidates if "primary" in i.tags or "main" in i.tags]
                if primaries:
                    return min(primaries, key=lambda i: i.active_tasks)
                return min(candidates, key=lambda i: i.active_tasks)

        return None

    def get_client_for_instance(
        self,
        instance_id: str,
    ) -> Optional["MultiInstanceClient"]:
        """获取指定实例的客户端"""
        info = self._instances.get(instance_id)
        if not info:
            return None
        return MultiInstanceClient(info, self)

    # ── 任务执行（自动路由）────────────────────────────────────────

    def execute_task(
        self,
        task_name: str,
        task_params: dict,
        group: str = "default",
        strategy: LoadBalanceStrategy = LoadBalanceStrategy.FAILOVER,
        required_capability: Optional[str] = None,
    ) -> dict:
        """在最优实例上执行任务（自动选择实例）"""
        info = self.get_best_instance(group, strategy, required_capability)
        if not info:
            return {"success": False, "error": f"No healthy instance in group '{group}'"}

        client = MultiInstanceClient(info, self)
        return client.execute_task(task_name, task_params)

    # ── 健康检查 ─────────────────────────────────────────────────

    def start_health_check(self, interval: int = 15):
        """启动后台健康检查线程"""
        self._health_check_interval = interval
        self._stop_health_check.clear()
        if self._health_check_thread and self._health_check_thread.is_alive():
            logger.info("Health check already running")
            return

        def _check_loop():
            while not self._stop_health_check.is_set():
                self._run_health_check()
                self._stop_health_check.wait(self._health_check_interval)

        self._health_check_thread = threading.Thread(target=_check_loop, daemon=True)
        self._health_check_thread.start()
        logger.info(f"Health check started (interval={interval}s)")

    def stop_health_check(self):
        self._stop_health_check.set()
        if self._health_check_thread:
            self._health_check_thread.join(timeout=5)

    def _run_health_check(self):
        """执行健康检查"""
        now = datetime.now()
        for instance_id, info in list(self._instances.items()):
            result = self._health_check_instance(info)
            self._process_health_result(instance_id, result, now)

    def _health_check_instance(self, info: InstanceInfo) -> HealthCheckResult:
        """检查单个实例"""
        start = time.time()
        try:
            resp = requests.get(
                f"{info.base_url}/api/status",
                headers={"Authorization": f"Bearer {info.api_key}"},
                timeout=5,
            )
            elapsed_ms = (time.time() - start) * 1000
            if resp.status_code == 200:
                return HealthCheckResult(
                    instance_id=info.id, success=True, response_time_ms=elapsed_ms
                )
            else:
                return HealthCheckResult(
                    instance_id=info.id, success=False,
                    response_time_ms=elapsed_ms,
                    error=f"HTTP {resp.status_code}",
                )
        except Exception as e:
            return HealthCheckResult(
                instance_id=info.id, success=False,
                response_time_ms=(time.time() - start) * 1000,
                error=str(e),
            )

    def _process_health_result(self, instance_id: str, result: HealthCheckResult, now: datetime):
        """处理健康检查结果，更新实例状态"""
        with self._lock:
            info = self._instances.get(instance_id)
            if not info:
                return

            circuit = self._circuits.get(instance_id, CircuitBreaker())

            if result.success:
                circuit.record_success()
                # 更新指标
                info.total_requests += 1
                info.last_heartbeat = now
                info.last_error = None

                # 计算移动平均响应时间
                if info.avg_response_time == 0:
                    info.avg_response_time = result.response_time_ms
                else:
                    info.avg_response_time = info.avg_response_time * 0.7 + result.response_time_ms * 0.3

                # 判断是否恢复
                if info.status == InstanceStatus.FAILED:
                    if self._on_instance_recovered:
                        self._on_instance_recovered(instance_id)

                # 判断降级
                if result.response_time_ms > 3000 or info.failure_rate > 0.3:
                    info.status = InstanceStatus.DEGRADED
                else:
                    info.status = InstanceStatus.HEALTHY

            else:
                info.failed_requests += 1
                info.total_requests += 1
                info.last_error = result.error
                circuit_open = circuit.record_failure()

                if circuit_open:
                    info.status = InstanceStatus.FAILED
                    info.circuit_open_at = now
                    if self._on_instance_unhealthy:
                        self._on_instance_unhealthy(instance_id, result.error)

    def set_health_callbacks(
        self,
        on_unhealthy: Optional[Callable[[str, str], None]] = None,
        on_recovered: Optional[Callable[[str], None]] = None,
    ):
        """设置健康状态变更回调"""
        self._on_instance_unhealthy = on_unhealthy
        self._on_instance_recovered = on_recovered


class MultiInstanceClient:
    """
    多实例客户端（绑定到特定实例）
    线程安全，支持自动重试
    """

    def __init__(self, instance: InstanceInfo, manager: MultiInstanceManager):
        self.instance = instance
        self._manager = manager
        self._session = requests.Session()
        self._session.headers.update({"Authorization": f"Bearer {instance.api_key}"})
        self._session.headers["Content-Type"] = "application/json"

    @property
    def base_url(self) -> str:
        return self.instance.base_url

    def _request(self, method: str, path: str, **kwargs) -> dict:
        url = f"{self.instance.base_url}{path}"
        resp = self._session.request(method, url, timeout=self.instance.timeout if hasattr(self.instance, 'timeout') else 30, **kwargs)
        if resp.status_code == 200:
            return resp.json()
        raise Exception(f"HTTP {resp.status_code}: {resp.text}")

    def get_status(self) -> dict:
        try:
            return {"success": True, "data": self._request("GET", "/api/status")}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def send_message(self, channel: str, message: str, **kwargs) -> dict:
        try:
            return {"success": True, "data": self._request("POST", "/api/message/send", json={"channel": channel, "message": message, **kwargs})}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def spawn_agent(self, task: str, **kwargs) -> dict:
        try:
            return {"success": True, "data": self._request("POST", "/api/agent/spawn", json={"task": task, **kwargs})}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def execute_task(self, task_name: str, params: dict) -> dict:
        """执行任务并记录活跃任务数"""
        try:
            with self._manager._lock:
                self.instance.active_tasks += 1
            result = self.spawn_agent(task_name, **params)
            return result
        finally:
            with self._manager._lock:
                self.instance.active_tasks = max(0, self.instance.active_tasks - 1)


# ── 全局单例 ─────────────────────────────────────────────────────

_manager: Optional[MultiInstanceManager] = None
_lock = threading.Lock()


def get_multi_instance_manager() -> MultiInstanceManager:
    global _manager
    with _lock:
        if _manager is None:
            _manager = MultiInstanceManager()
        return _manager


def init_multi_instance_manager() -> MultiInstanceManager:
    global _manager
    with _lock:
        _manager = MultiInstanceManager()
        return _manager
