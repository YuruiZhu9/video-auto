#!/usr/bin/env python3
"""
clawctl 健康监控与指标收集系统
提供运行时指标、性能监控、告警管理
"""

import gc
import logging
import os
import platform
import psutil
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("clawctl.monitor")


@dataclass
class MetricsSnapshot:
    """指标快照"""
    timestamp: float
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    disk_percent: float
    network_sent_mb: float
    network_recv_mb: float
    open_connections: int
    active_threads: int
    gc_counts: tuple  # (gen0, gen1, gen2)


@dataclass
class Alert:
    """告警记录"""
    id: str
    level: str  # info | warning | critical
    title: str
    message: str
    metric: str
    value: Any
    threshold: Any
    created_at: float = field(default_factory=time.time)
    resolved_at: Optional[float] = None
    resolved: bool = False


class MetricsCollector:
    """
    运行时指标收集器

    收集：
    - 系统指标：CPU/内存/磁盘/网络
    - 应用指标：请求数/响应时间/错误率
    - OpenClaw 指标：会话数/活跃 Agent 数
    """

    # 指标保留窗口（秒）
    WINDOW_SIZE = 3600  # 1小时

    def __init__(self, history_seconds: int = 3600):
        self._history_seconds = history_seconds
        self._snapshots: deque = deque(maxlen=history_seconds)
        self._request_log: deque = deque(maxlen=10000)
        self._alerts: Dict[str, Alert] = {}
        self._alert_history: List[Alert] = []
        self._lock = threading.RLock()
        self._last_net_io = psutil.net_io_counters()
        self._last_net_time = time.time()
        self._process = psutil.Process(os.getpid())
        self._running = False
        self._collect_thread: Optional[threading.Thread] = None
        self._alert_callbacks: List[Callable[[Alert], None]] = []

        # 告警阈值配置
        self._thresholds = {
            "cpu_percent": 80.0,       # CPU > 80%
            "memory_percent": 85.0,    # 内存 > 85%
            "disk_percent": 90.0,      # 磁盘 > 90%
            "error_rate": 10.0,        # 错误率 > 10%
            "response_time_p95": 5.0,  # P95 响应时间 > 5s
            "queue_size": 100,         # 队列积压 > 100
        }

    # ─── 收集逻辑 ───────────────────────────────────────────────

    def _collect_snapshot(self) -> MetricsSnapshot:
        """采集一次系统指标快照"""
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        net = psutil.net_io_counters()

        now = time.time()
        elapsed = now - self._last_net_time
        net_sent_mb = (net.bytes_sent - self._last_net_io.bytes_sent) / elapsed / 1024 / 1024
        net_recv_mb = (net.bytes_recv - self._last_net_io.bytes_recv) / elapsed / 1024 / 1024
        self._last_net_io = net
        self._last_net_time = now

        try:
            proc_mem = self._process.memory_info()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            proc_mem = None

        gc_counts = gc.get_count()

        return MetricsSnapshot(
            timestamp=now,
            cpu_percent=self._process.cpu_percent(interval=0.1),
            memory_mb=proc_mem.rss / 1024 / 1024 if proc_mem else 0,
            memory_percent=mem.percent,
            disk_percent=disk.percent,
            network_sent_mb=net_sent_mb,
            network_recv_mb=net_recv_mb,
            open_connections=len(self._process.connections()),
            active_threads=self._process.num_threads(),
            gc_counts=gc_counts,
        )

    def _collect_loop(self, interval: int = 5):
        """定时收集线程"""
        while self._running:
            try:
                snap = self._collect_snapshot()
                with self._lock:
                    self._snapshots.append(snap)
                self._check_thresholds(snap)
            except Exception as e:
                logger.debug(f"指标收集异常: {e}")
            time.sleep(interval)

    def start(self, interval: int = 5):
        """启动指标收集"""
        if self._running:
            return
        self._running = True
        self._collect_thread = threading.Thread(
            target=self._collect_loop,
            args=(interval,),
            daemon=True,
            name="MetricsCollector",
        )
        self._collect_thread.start()
        logger.info(f"📊 指标收集器已启动（间隔 {interval}s，窗口 {self._history_seconds}s）")

    def stop(self):
        """停止收集"""
        self._running = False
        if self._collect_thread:
            self._collect_thread.join(timeout=10)

    # ─── 告警逻辑 ───────────────────────────────────────────────

    def _check_thresholds(self, snap: MetricsSnapshot):
        """检查告警阈值"""
        checks = {
            "cpu_percent": snap.cpu_percent,
            "memory_percent": snap.memory_percent,
            "disk_percent": snap.disk_percent,
        }
        for metric, value in checks.items():
            threshold = self._thresholds.get(metric, 100)
            if value > threshold:
                self._trigger_alert(
                    level="warning" if value < threshold * 1.2 else "critical",
                    title=f"{metric} 过高",
                    message=f"{metric} = {value:.1f}%（阈值: {threshold}%）",
                    metric=metric,
                    value=value,
                    threshold=threshold,
                )

        # 检查请求错误率
        with self._lock:
            recent = [r for r in self._request_log if time.time() - r["timestamp"] < 60]
            if recent:
                errors = sum(1 for r in recent if r["status"] >= 400)
                error_rate = errors / len(recent) * 100
                if error_rate > self._thresholds.get("error_rate", 10):
                    self._trigger_alert(
                        level="warning",
                        title="请求错误率过高",
                        message=f"近1分钟错误率 = {error_rate:.1f}%（{errors}/{len(recent)}）",
                        metric="error_rate",
                        value=error_rate,
                        threshold=self._thresholds["error_rate"],
                    )

    def _trigger_alert(self, level: str, title: str, message: str, metric: str, value: Any, threshold: Any):
        """触发告警"""
        import secrets
        alert_id = f"{metric}_{int(time.time())}"
        with self._lock:
            if alert_id in self._alerts:
                return  # 避免重复
            alert = Alert(
                id=alert_id,
                level=level,
                title=title,
                message=message,
                metric=metric,
                value=value,
                threshold=threshold,
            )
            self._alerts[alert_id] = alert
            self._alert_history.append(alert)
            # 只保留最近100条告警历史
            if len(self._alert_history) > 100:
                self._alert_history = self._alert_history[-100:]

        logger.warning(f"🚨 [{level.upper()}] {title}: {message}")
        for cb in self._alert_callbacks:
            try:
                cb(alert)
            except Exception:
                pass

    def resolve_alert(self, alert_id: str):
        """解除告警"""
        with self._lock:
            if alert_id in self._alerts:
                self._alerts[alert_id].resolved = True
                self._alerts[alert_id].resolved_at = time.time()

    def on_alert(self, callback: Callable[[Alert], None]):
        """订阅告警"""
        self._alert_callbacks.append(callback)

    # ─── 请求记录 ───────────────────────────────────────────────

    def record_request(self, endpoint: str, method: str, status: int, duration: float, error: str = None):
        """记录一次 API 请求"""
        with self._lock:
            self._request_log.append({
                "timestamp": time.time(),
                "endpoint": endpoint,
                "method": method,
                "status": status,
                "duration": duration,
                "error": error,
            })

    # ─── 数据查询 ───────────────────────────────────────────────

    def get_current(self) -> Dict[str, Any]:
        """获取当前指标"""
        with self._lock:
            if not self._snapshots:
                return {}
            snap = self._snapshots[-1]
            return {
                "timestamp": datetime.fromtimestamp(snap.timestamp).isoformat(),
                "cpu_percent": round(snap.cpu_percent, 1),
                "memory_mb": round(snap.memory_mb, 1),
                "memory_percent": round(snap.memory_percent, 1),
                "disk_percent": round(snap.disk_percent, 1),
                "network_sent_mb_s": round(snap.network_sent_mb, 2),
                "network_recv_mb_s": round(snap.network_recv_mb, 2),
                "open_connections": snap.open_connections,
                "active_threads": snap.active_threads,
                "gc_gen": snap.gc_counts,
            }

    def get_history(self, duration_seconds: int = 300) -> List[Dict[str, Any]]:
        """获取历史指标"""
        cutoff = time.time() - duration_seconds
        with self._lock:
            return [
                {
                    "timestamp": snap.timestamp,
                    "cpu_percent": snap.cpu_percent,
                    "memory_percent": snap.memory_percent,
                }
                for snap in self._snapshots
                if snap.timestamp >= cutoff
            ]

    def get_request_stats(self, duration_seconds: int = 300) -> Dict[str, Any]:
        """获取请求统计"""
        cutoff = time.time() - duration_seconds
        with self._lock:
            recent = [r for r in self._request_log if r["timestamp"] >= cutoff]
            if not recent:
                return {"total": 0, "errors": 0, "error_rate": 0, "avg_duration": 0, "p95_duration": 0}

            durations = sorted(r["duration"] for r in recent)
            errors = sum(1 for r in recent if r["status"] >= 400)
            p95_idx = int(len(durations) * 0.95)
            return {
                "total": len(recent),
                "errors": errors,
                "error_rate": round(errors / len(recent) * 100, 2),
                "avg_duration": round(sum(durations) / len(durations), 3),
                "p95_duration": round(durations[p95_idx] if durations else 0, 3),
                "max_duration": round(max(durations) if durations else 0, 3),
            }

    def get_alerts(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """获取告警列表"""
        with self._lock:
            alerts = list(self._alerts.values())
            if active_only:
                alerts = [a for a in alerts if not a.resolved]
            return [
                {
                    "id": a.id,
                    "level": a.level,
                    "title": a.title,
                    "message": a.message,
                    "metric": a.metric,
                    "value": a.value,
                    "threshold": a.threshold,
                    "created_at": datetime.fromtimestamp(a.created_at).isoformat(),
                    "resolved": a.resolved,
                    "resolved_at": datetime.fromtimestamp(a.resolved_at).isoformat() if a.resolved_at else None,
                }
                for a in sorted(alerts, key=lambda x: x.created_at, reverse=True)
            ]

    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        return {
            "hostname": platform.node(),
            "os": f"{platform.system()} {platform.release()}",
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(logical=True),
            "cpu_physical": psutil.cpu_count(logical=False),
            "total_memory_gb": round(psutil.virtual_memory().total / 1024**3, 1),
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            "process_uptime_seconds": round(time.time() - self._process.create_time()),
        }

    def get_full_report(self) -> Dict[str, Any]:
        """获取完整监控报告"""
        return {
            "current": self.get_current(),
            "request_stats_5m": self.get_request_stats(300),
            "request_stats_1h": self.get_request_stats(3600),
            "history_5m": self.get_history(300),
            "alerts_active": self.get_alerts(active_only=True),
            "system_info": self.get_system_info(),
        }

    def set_threshold(self, metric: str, value: float):
        """设置告警阈值"""
        self._thresholds[metric] = value


# ═══════════════════════════════════════════════════════════════════
# 全局单例
# ═══════════════════════════════════════════════════════════════════

_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector(history_seconds=3600)
        _metrics_collector.start(interval=5)
    return _metrics_collector
