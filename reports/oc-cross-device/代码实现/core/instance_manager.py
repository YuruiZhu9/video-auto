#!/usr/bin/env python3
"""
OpenClaw 实例管理器 (InstanceManager)
支持多 OpenClaw 实例的注册、负载均衡、故障转移
"""

import asyncio
import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("clawctl.instances")


@dataclass
class InstanceInfo:
    """OpenClaw 实例信息"""
    id: str                          # 唯一标识符
    name: str                        # 显示名称
    base_url: str                    # Gateway URL
    api_key: str                     # API Key
    enabled: bool = True            # 是否启用
    is_alive: bool = False          # 健康状态
    is_master: bool = False         # 是否为主实例
    health_check_interval: int = 30 # 健康检查间隔（秒）
    last_check: float = 0           # 上次检查时间戳
    consecutive_failures: int = 0   # 连续失败次数
    max_failures: int = 3           # 最大连续失败次数（超过则标记为不可用）
    tags: List[str] = field(default_factory=list)  # 标签（用于路由）
    weight: int = 1                 # 负载均衡权重
    total_requests: int = 0         # 总请求数
    active_requests: int = 0        # 当前活跃请求数
    avg_response_time: float = 0.0  # 平均响应时间（秒）

    def mark_success(self, response_time: float):
        """标记请求成功"""
        self.is_alive = True
        self.consecutive_failures = 0
        self.total_requests += 1
        self.active_requests = max(0, self.active_requests - 1)
        # 滑动平均更新响应时间
        self.avg_response_time = 0.7 * self.avg_response_time + 0.3 * response_time
        self.last_check = time.time()

    def mark_failure(self):
        """标记请求失败"""
        self.consecutive_failures += 1
        self.active_requests = max(0, self.active_requests - 1)
        if self.consecutive_failures >= self.max_failures:
            self.is_alive = False
            logger.warning(f"实例 {self.id} 标记为不可用（连续失败 {self.consecutive_failures} 次）")
        self.last_check = time.time()

    def mark_alive(self, is_alive: bool):
        """直接设置存活状态（健康检查用）"""
        self.is_alive = is_alive
        if is_alive:
            self.consecutive_failures = 0
        self.last_check = time.time()


class InstanceClient:
    """单个 OpenClaw 实例的客户端封装"""

    def __init__(self, info: InstanceInfo):
        self.info = info
        self._client: Optional["OpenClawClient"] = None

    @property
    def client(self) -> "OpenClawClient":
        """延迟初始化客户端"""
        if self._client is None:
            from core.client import OpenClawClient
            self._client = OpenClawClient(
                base_url=self.info.base_url,
                api_key=self.info.api_key,
            )
        return self._client

    def health_check(self) -> bool:
        """健康检查"""
        try:
            result = self.client.health_check()
            alive = bool(result)
            self.info.mark_alive(alive)
            return alive
        except Exception as e:
            logger.debug(f"实例 {self.info.id} 健康检查失败: {e}")
            self.info.mark_alive(False)
            return False


class InstanceManager:
    """
    OpenClaw 多实例管理器

    功能：
    - 注册/注销多个 OpenClaw 实例
    - 故障检测与自动移除
    - 负载均衡（轮询/加权/最快响应）
    - 实例亲和性（按标签路由）
    - 健康检查守护线程
    """

    def __init__(self):
        self._instances: Dict[str, InstanceClient] = {}
        self._lock = threading.RLock()
        self._health_thread: Optional[threading.Thread] = None
        self._stop_health_check = threading.Event()
        self._event_callbacks: List[Callable[[str, str, Any], None]] = []  # (event, instance_id, data)
        # 轮询计数器
        self._round_robin_counter: Dict[str, int] = {}  # tag -> counter

    # ─── 实例管理 ───────────────────────────────────────────────

    def add_instance(self, info: InstanceInfo) -> InstanceInfo:
        """注册新实例"""
        with self._lock:
            if info.id in self._instances:
                raise ValueError(f"实例 ID 已存在: {info.id}")
            ic = InstanceClient(info)
            self._instances[info.id] = ic
            # 如果是第一个实例，自动设为主
            if len(self._instances) == 1:
                info.is_master = True
            logger.info(f"✅ 注册实例: {info.id} ({info.name}) @ {info.base_url}")
        return info

    def remove_instance(self, instance_id: str) -> bool:
        """注销实例"""
        with self._lock:
            if instance_id not in self._instances:
                return False
            inst = self._instances.pop(instance_id)
            # 如果移除的是主实例，升级一个从实例
            if inst.info.is_master:
                self._promote_next_master()
            logger.info(f"🗑️ 注销实例: {instance_id}")
            return True

    def get_instance(self, instance_id: str) -> Optional[InstanceClient]:
        """获取指定实例"""
        with self._lock:
            return self._instances.get(instance_id)

    def list_instances(self, enabled_only: bool = False) -> List[InstanceInfo]:
        """列出所有实例"""
        with self._lock:
            instances = [ic.info for ic in self._instances.values()]
            if enabled_only:
                instances = [i for i in instances if i.enabled]
            return instances

    def update_instance(self, instance_id: str, **kwargs) -> Optional[InstanceInfo]:
        """更新实例配置"""
        with self._lock:
            ic = self._instances.get(instance_id)
            if not ic:
                return None
            for k, v in kwargs.items():
                if hasattr(ic.info, k):
                    setattr(ic.info, k, v)
            return ic.info

    # ─── 负载均衡 ───────────────────────────────────────────────

    def _promote_next_master(self):
        """将下一个可用实例升级为主"""
        with self._lock:
            candidates = [ic for ic in self._instances.values() if ic.info.enabled and ic.info.is_alive]
            if candidates:
                candidates[0].info.is_master = True
                logger.info(f"⭐ 新主实例: {candidates[0].info.id}")

    def select_instance(
        self,
        strategy: str = "round_robin",
        tag: Optional[str] = None,
        exclude: Optional[str] = None,
    ) -> Optional[InstanceClient]:
        """
        选择最优实例

        Args:
            strategy: round_robin | weighted | fastest | least_active
            tag: 标签过滤（只选有该标签的实例）
            exclude: 排除的实例ID
        Returns:
            InstanceClient 或 None
        """
        with self._lock:
            instances = [
                ic for ic in self._instances.values()
                if ic.info.enabled and ic.info.is_alive
                and (tag is None or tag in ic.info.tags)
                and (exclude is None or ic.info.id != exclude)
            ]
            if not instances:
                return None

            if strategy == "round_robin":
                key = tag or "__all__"
                counter = self._round_robin_counter.get(key, 0)
                idx = counter % len(instances)
                self._round_robin_counter[key] = counter + 1
                return instances[idx]

            elif strategy == "weighted":
                total_weight = sum(i.info.weight for i in instances)
                import random
                r = random.uniform(0, total_weight)
                cum = 0
                for ic in instances:
                    cum += ic.info.weight
                    if r <= cum:
                        return ic
                return instances[-1]

            elif strategy == "fastest":
                return min(instances, key=lambda ic: ic.info.avg_response_time)

            elif strategy == "least_active":
                return min(instances, key=lambda ic: ic.info.active_requests)

            else:
                return instances[0]

    def get_default_client(self) -> Optional[InstanceClient]:
        """获取主实例客户端"""
        with self._lock:
            for ic in self._instances.values():
                if ic.info.is_master and ic.info.enabled:
                    return ic
            # fallback 到任意可用实例
            for ic in self._instances.values():
                if ic.info.enabled and ic.info.is_alive:
                    return ic
            return None

    # ─── 健康检查 ───────────────────────────────────────────────

    def start_health_check(self, interval: int = 30):
        """启动健康检查守护线程"""
        if self._health_thread and self._health_thread.is_alive():
            logger.warning("健康检查线程已在运行")
            return

        self._stop_health_check.clear()
        def _check_loop():
            while not self._stop_health_check.wait(interval):
                self._do_health_check()
        self._health_thread = threading.Thread(target=_check_loop, daemon=True, name="InstanceHealthCheck")
        self._health_thread.start()
        logger.info(f"🫀 健康检查线程已启动（间隔 {interval}s）")

    def stop_health_check(self):
        """停止健康检查"""
        self._stop_health_check.set()
        if self._health_thread:
            self._health_thread.join(timeout=5)

    def _do_health_check(self):
        """执行一轮健康检查"""
        with self._lock:
            instance_ids = list(self._instances.keys())

        for iid in instance_ids:
            ic = self.get_instance(iid)
            if not ic:
                continue
            try:
                alive = ic.health_check()
                status = "✅" if alive else "❌"
                logger.debug(f"{status} 实例 {iid} 健康检查: {'UP' if alive else 'DOWN'}")
                # 自动故障转移
                if not alive and ic.info.is_master:
                    logger.warning(f"⚠️ 主实例 {iid} 不可用，触发故障转移")
                    self._promote_next_master()
            except Exception as e:
                logger.debug(f"实例 {iid} 健康检查异常: {e}")

    def force_health_check(self):
        """立即执行一次健康检查"""
        self._do_health_check()

    # ─── 统计信息 ───────────────────────────────────────────────

    def get_stats(self) -> Dict[str, Any]:
        """获取集群统计信息"""
        with self._lock:
            instances = list(self._instances.values())
            total = len(instances)
            alive = sum(1 for ic in instances if ic.info.is_alive and ic.info.enabled)
            return {
                "total_instances": total,
                "alive_instances": alive,
                "dead_instances": total - alive,
                "total_requests": sum(ic.info.total_requests for ic in instances),
                "active_requests": sum(ic.info.active_requests for ic in instances),
                "instances": [
                    {
                        "id": ic.info.id,
                        "name": ic.info.name,
                        "base_url": ic.info.base_url,
                        "is_alive": ic.info.is_alive,
                        "is_master": ic.info.is_master,
                        "enabled": ic.info.enabled,
                        "tags": ic.info.tags,
                        "total_requests": ic.info.total_requests,
                        "active_requests": ic.info.active_requests,
                        "avg_response_time": round(ic.info.avg_response_time, 3),
                        "last_check": ic.info.last_check,
                    }
                    for ic in instances
                ],
            }

    # ─── 事件订阅 ───────────────────────────────────────────────

    def on_event(self, callback: Callable[[str, str, Any], None]):
        """订阅实例事件（up/down/change）"""
        self._event_callbacks.append(callback)

    def _emit(self, event: str, instance_id: str, data: Any = None):
        for cb in self._event_callbacks:
            try:
                cb(event, instance_id, data)
            except Exception:
                pass


# ═══════════════════════════════════════════════════════════════════
# 全局单例
# ═══════════════════════════════════════════════════════════════════

_instance_manager: Optional[InstanceManager] = None


def get_instance_manager() -> InstanceManager:
    global _instance_manager
    if _instance_manager is None:
        _instance_manager = InstanceManager()
    return _instance_manager


def init_instance_manager(instances: List[Dict[str, Any]] = None) -> InstanceManager:
    """初始化实例管理器并注册实例"""
    mgr = get_instance_manager()
    if instances:
        for cfg in instances:
            info = InstanceInfo(
                id=cfg["id"],
                name=cfg.get("name", cfg["id"]),
                base_url=cfg["base_url"],
                api_key=cfg.get("api_key", ""),
                enabled=cfg.get("enabled", True),
                is_master=cfg.get("is_master", False),
                tags=cfg.get("tags", []),
                weight=cfg.get("weight", 1),
                max_failures=cfg.get("max_failures", 3),
            )
            mgr.add_instance(info)
    mgr.start_health_check(interval=30)
    return mgr
