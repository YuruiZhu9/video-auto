#!/usr/bin/env python3
"""
实时监控与告警系统
v2.4.0 新增

支持：
- 实时指标收集（CPU/内存/请求/P95延迟/错误率）
- 可配置告警规则（阈值触发）
- 多通道告警（钉钉/钉钉/邮件/Telegram）
- 时序数据存储（内存 + SQLite）
- Web Dashboard API
"""

import atexit
import json
import logging
import os
import platform
import threading
import time
import uuid
from collections import deque
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Optional, Any

import psutil

logger = logging.getLogger(__name__)

# ── 数据结构 ─────────────────────────────────────────────────────


@dataclass
class MetricPoint:
    """单个指标数据点"""
    timestamp: float          # Unix timestamp
    value: float
    labels: dict = field(default_factory=dict)


@dataclass
class AlertRule:
    """告警规则"""
    id: str
    name: str
    metric: str              # 指标名：cpu_percent / memory_percent / request_count / error_rate / avg_response_ms / active_tasks
    condition: str            # gt / lt / gte / lte / eq
    threshold: float
    severity: str = "warning"  # info / warning / critical
    cooldown: int = 300       # 秒，同一告警多久不重复触发
    enabled: bool = True
    channels: list[str] = field(default_factory=list)  # dingtalk / telegram / email / console


@dataclass
class Alert:
    """触发中的告警"""
    id: str
    rule_id: str
    rule_name: str
    metric: str
    current_value: float
    threshold: float
    condition: str
    severity: str
    fired_at: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False
    resolved_at: Optional[datetime] = None
    message: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["fired_at"] = self.fired_at.isoformat() if self.fired_at else None
        d["resolved_at"] = self.resolved_at.isoformat() if self.resolved_at else None
        return d


@dataclass
class SystemSnapshot:
    """系统快照"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_total_mb: float
    disk_percent: float
    openclaw_active_tasks: int = 0
    openclaw_total_requests: int = 0
    openclaw_failed_requests: int = 0
    openclaw_avg_response_ms: float = 0.0
    openclaw_error_rate: float = 0.0
    openclaw_instances_healthy: int = 0
    openclaw_instances_total: int = 0
    api_requests_per_min: int = 0
    running_tasks: int = 0

    def to_dict(self) -> dict:
        d = asdict(self)
        d["timestamp"] = self.timestamp.isoformat()
        return d


# ── 告警评估 ─────────────────────────────────────────────────────


def evaluate_condition(value: float, condition: str, threshold: float) -> bool:
    ops = {"gt": lambda v, t: v > t, "lt": lambda v, t: v < t,
           "gte": lambda v, t: v >= t, "lte": lambda v, t: v <= t,
           "eq": lambda v, t: v == t}
    return ops.get(condition, lambda v, t: False)(value, threshold)


# ── 监控管理器 ───────────────────────────────────────────────────


class MonitoringManager:
    """
    监控与告警管理器

    使用示例：
        m = MonitoringManager()
        m.start_collection(interval=5)

        # 添加告警规则
        m.add_rule(AlertRule(
            id="high-cpu", name="CPU 过高",
            metric="cpu_percent", condition="gt", threshold=80,
            severity="warning", channels=["dingtalk"]
        ))

        # 查询当前状态
        snapshot = m.get_snapshot()
    """

    def __init__(self, retention_minutes: int = 60):
        self.retention_minutes = retention_minutes
        self._lock = threading.RLock()
        self._collection_thread: Optional[threading.Thread] = None
        self._stop = threading.Event()

        # 时序数据（滑动窗口）
        self._metrics: dict[str, deque] = {
            "cpu_percent": deque(maxlen=720),        # 1小时 @ 5s
            "memory_percent": deque(maxlen=720),
            "request_count": deque(maxlen=720),
            "error_rate": deque(maxlen=720),
            "avg_response_ms": deque(maxlen=720),
            "active_tasks": deque(maxlen=720),
            "api_latency_p95": deque(maxlen=720),
        }

        # 原始请求追踪（用于 P95 计算）
        self._request_latencies: deque = deque(maxlen=1000)

        # 告警规则
        self._rules: dict[str, AlertRule] = {}
        self._active_alerts: dict[str, Alert] = {}
        self._alert_history: list[Alert] = []
        self._last_alert_time: dict[str, datetime] = {}

        # 告警回调
        self._alert_callbacks: list[callable] = []

        # OpenClaw 指标注入（由外部更新）
        self._openclaw_metrics = {
            "active_tasks": 0,
            "total_requests": 0,
            "failed_requests": 0,
            "avg_response_ms": 0.0,
            "instances_healthy": 0,
            "instances_total": 0,
        }

        # 系统基线
        self._sys_base = self._get_system_info()

        # 注册退出
        atexit.register(self.stop)

    # ── 系统信息 ─────────────────────────────────────────────────

    def _get_system_info(self) -> dict:
        try:
            return {
                "cpu_count": psutil.cpu_count(logical=True),
                "memory_total_mb": psutil.virtual_memory().total / 1024 / 1024,
                "disk_total_gb": psutil.disk_usage("/").total / 1024 / 1024 / 1024,
            }
        except Exception:
            return {"cpu_count": 0, "memory_total_mb": 0, "disk_total_gb": 0}

    def _collect_system_metrics(self) -> dict:
        try:
            vm = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            return {
                "cpu_percent": psutil.cpu_percent(interval=None),
                "memory_percent": vm.percent,
                "memory_used_mb": vm.used / 1024 / 1024,
                "memory_total_mb": vm.total / 1024 / 1024,
                "disk_percent": disk.percent,
            }
        except Exception as e:
            logger.warning(f"Failed to collect system metrics: {e}")
            return {}

    # ── 指标收集 ─────────────────────────────────────────────────

    def record_request(self, latency_ms: float, success: bool = True):
        """记录 API 请求（外部调用）"""
        with self._lock:
            now = time.time()
            self._request_latencies.append((now, latency_ms, success))

            # 更新指标
            ts = self._metrics["request_count"]
            if ts and (now - ts[-1].timestamp) < 1:
                ts[-1] = MetricPoint(now, ts[-1].value + 1)
            else:
                ts.append(MetricPoint(now, 1))

            if not success:
                err_rate = len([r for r in list(self._request_latencies)[-100:] if not r[2]])
                err_rate = err_rate / max(len(list(self._request_latencies)[-100:]), 1) * 100
                self._metrics["error_rate"].append(MetricPoint(now, err_rate))

    def update_openclaw_metrics(self, **kwargs):
        """更新 OpenClaw 指标（由外部注入）"""
        with self._lock:
            self._openclaw_metrics.update(kwargs)

    def _collect(self):
        """收集一次指标"""
        now = time.time()
        sys_metrics = self._collect_system_metrics()

        with self._lock:
            for key in ["cpu_percent", "memory_percent"]:
                if key in sys_metrics:
                    self._metrics[key].append(MetricPoint(now, sys_metrics[key]))

            # OpenClaw 指标
            om = self._openclaw_metrics
            self._metrics["active_tasks"].append(MetricPoint(now, om.get("active_tasks", 0)))
            self._metrics["avg_response_ms"].append(MetricPoint(now, om.get("avg_response_ms", 0)))
            self._metrics["error_rate"].append(MetricPoint(
                now, om.get("failed_requests", 0) / max(om.get("total_requests", 1) * 100
            )))

            # P95 延迟
            recent = [r[1] for r in list(self._request_latencies)[-100:] if now - r[0] < 60]
            if recent:
                sorted_latencies = sorted(recent)
                p95 = sorted_latencies[int(len(sorted_latencies) * 0.95)]
            else:
                p95 = 0.0
            self._metrics["api_latency_p95"].append(MetricPoint(now, p95))

    def start_collection(self, interval: int = 5):
        """启动后台指标收集"""
        if self._collection_thread and self._collection_thread.is_alive():
            return

        self._stop.clear()

        def _loop():
            while not self._stop.is_set():
                self._collect()
                self._evaluate_alerts()
                self._stop.wait(interval)

        self._collection_thread = threading.Thread(target=_loop, daemon=True)
        self._collection_thread.start()
        logger.info(f"Monitoring collection started (interval={interval}s)")

    def stop(self):
        self._stop.set()
        if self._collection_thread:
            self._collection_thread.join(timeout=5)

    # ── 告警规则 ─────────────────────────────────────────────────

    def add_rule(self, rule: AlertRule):
        with self._lock:
            self._rules[rule.id] = rule

    def remove_rule(self, rule_id: str) -> bool:
        with self._lock:
            if rule_id in self._rules:
                del self._rules[rule_id]
                return True
            return False

    def list_rules(self) -> list[dict]:
        with self._lock:
            return [asdict(r) for r in self._rules.values()]

    def _evaluate_alerts(self):
        """评估所有告警规则"""
        with self._lock:
            for rule in self._rules.values():
                if not rule.enabled:
                    continue

                # 获取当前指标值
                metric_deque = self._metrics.get(rule.metric)
                if not metric_deque or len(metric_deque) == 0:
                    continue

                current = metric_deque[-1].value

                # 检查条件
                triggered = evaluate_condition(current, rule.condition, rule.threshold)

                # 冷却检查
                last_time = self._last_alert_time.get(rule.id)
                if last_time and (datetime.now() - last_time).total_seconds() < rule.cooldown:
                    continue

                if triggered:
                    self._fire_alert(rule, current)

    def _fire_alert(self, rule: AlertRule, current_value: float):
        """触发告警"""
        alert = Alert(
            id=str(uuid.uuid4())[:8],
            rule_id=rule.id,
            rule_name=rule.name,
            metric=rule.metric,
            current_value=current_value,
            threshold=rule.threshold,
            condition=rule.condition,
            severity=rule.severity,
            message=f"指标 {rule.metric} = {current_value:.2f}，条件 {rule.condition} {rule.threshold}",
        )
        self._active_alerts[rule.id] = alert
        self._alert_history.append(alert)
        self._last_alert_time[rule.id] = datetime.now()

        logger.warning(f"[ALERT] {rule.severity.upper()} - {rule.name}: {current_value:.2f}")

        # 触发回调
        for cb in self._alert_callbacks:
            try:
                cb(alert, rule)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")

    def acknowledge_alert(self, rule_id: str) -> bool:
        with self._lock:
            if rule_id in self._active_alerts:
                self._active_alerts[rule_id].acknowledged = True
                return True
            return False

    def get_active_alerts(self) -> list[dict]:
        with self._lock:
            return [a.to_dict() for a in self._active_alerts.values()]

    def get_alert_history(self, limit: int = 50) -> list[dict]:
        with self._lock:
            return [a.to_dict() for a in self._alert_history[-limit:]]

    def set_alert_callback(self, callback: callable):
        """设置告警回调（接收 alert 和 rule 对象）"""
        self._alert_callbacks.append(callback)

    # ── 数据查询 ─────────────────────────────────────────────────

    def get_current_value(self, metric: str) -> Optional[float]:
        with self._lock:
            dq = self._metrics.get(metric)
            if dq and len(dq) > 0:
                return dq[-1].value
        return None

    def get_series(self, metric: str, minutes: int = 10) -> list[dict]:
        """获取指标时序数据"""
        with self._lock:
            dq = self._metrics.get(metric)
            if not dq:
                return []
            cutoff = time.time() - minutes * 60
            return [
                {"timestamp": p.timestamp, "value": p.value}
                for p in dq if p.timestamp >= cutoff
            ]

    def get_snapshot(self) -> SystemSnapshot:
        """获取当前系统快照"""
        sys = self._collect_system_metrics()
        with self._lock:
            om = self._openclaw_metrics

            def _latest(metric: str, default: float = 0.0) -> float:
                dq = self._metrics.get(metric)
                return dq[-1].value if dq and len(dq) > 0 else default

            recent = list(self._request_latencies)[-60:]
            rpm = len(recent)

            return SystemSnapshot(
                timestamp=datetime.now(),
                cpu_percent=sys.get("cpu_percent", 0),
                memory_percent=sys.get("memory_percent", 0),
                memory_used_mb=sys.get("memory_used_mb", 0),
                memory_total_mb=sys.get("memory_total_mb", 0),
                disk_percent=sys.get("disk_percent", 0),
                openclaw_active_tasks=om.get("active_tasks", 0),
                openclaw_total_requests=om.get("total_requests", 0),
                openclaw_failed_requests=om.get("failed_requests", 0),
                openclaw_avg_response_ms=om.get("avg_response_ms", 0),
                openclaw_error_rate=_latest("error_rate"),
                openclaw_instances_healthy=om.get("instances_healthy", 0),
                openclaw_instances_total=om.get("instances_total", 0),
                api_requests_per_min=rpm,
                running_tasks=om.get("active_tasks", 0),
            )

    def get_dashboard_summary(self) -> dict:
        """获取 Dashboard 汇总数据"""
        snap = self.get_snapshot()
        return {
            "snapshot": snap.to_dict(),
            "series_10m": {
                "cpu": self.get_series("cpu_percent", 10),
                "memory": self.get_series("memory_percent", 10),
                "latency_p95": self.get_series("api_latency_p95", 10),
                "error_rate": self.get_series("error_rate", 10),
                "active_tasks": self.get_series("active_tasks", 10),
            },
            "alerts": {
                "active": self.get_active_alerts(),
                "history": self.get_alert_history(20),
            },
            "rules": self.list_rules(),
        }


# ── 全局单例 ─────────────────────────────────────────────────────

_monitoring: Optional[MonitoringManager] = None
_m_lock = threading.Lock()


def get_monitoring_manager() -> MonitoringManager:
    global _monitoring
    with _m_lock:
        if _monitoring is None:
            _monitoring = MonitoringManager()
        return _monitoring


def init_monitoring(retention_minutes: int = 60) -> MonitoringManager:
    global _monitoring
    with _m_lock:
        _monitoring = MonitoringManager(retention_minutes)
        return _monitoring
