#!/usr/bin/env python3
"""FastAPI 路由：监控指标 API"""
import logging
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
logger = logging.getLogger("clawctl.routes.monitor")
router = APIRouter(prefix="/api/v1/monitor", tags=["监控指标"])
_metrics_collector = None
def set_metrics_collector(collector):
    global _metrics_collector
    _metrics_collector = collector
def get_collector():
    global _metrics_collector
    if _metrics_collector is None:
        from core.monitor import get_metrics_collector
        _metrics_collector = get_metrics_collector()
    return _metrics_collector
@router.get("/current", summary="当前系统指标")
async def get_current_metrics():
    return get_collector().get_current()
@router.get("/history", summary="历史指标")
async def get_history_metrics(duration_seconds: int = Query(300, le=3600)):
    return {"duration_seconds": duration_seconds, "data": get_collector().get_history(duration_seconds=duration_seconds)}
@router.get("/requests", summary="API请求统计")
async def get_request_stats(duration_seconds: int = Query(300, le=3600)):
    stats = get_collector().get_request_stats(duration_seconds=duration_seconds)
    return {"duration_seconds": duration_seconds, **stats}
@router.get("/alerts", summary="告警列表")
async def get_alerts(active_only: bool = Query(True)):
    alerts = get_collector().get_alerts(active_only=active_only)
    return {"total": len(alerts), "active_count": sum(1 for a in alerts if not a.get("resolved")), "alerts": alerts}
@router.delete("/alerts/{alert_id}", summary="解除告警")
async def resolve_alert(alert_id: str):
    get_collector().resolve_alert(alert_id)
    return {"message": "告警已解除", "alert_id": alert_id}
@router.get("/system", summary="系统信息")
async def get_system_info():
    return get_collector().get_system_info()
@router.get("/report", summary="完整监控报告")
async def get_full_report():
    return get_collector().get_full_report()
class ThresholdUpdate(BaseModel):
    metric: str
    value: float
@router.patch("/thresholds", summary="更新告警阈值")
async def update_threshold(body: ThresholdUpdate):
    VALID_METRICS = ["cpu_percent", "memory_percent", "disk_percent", "error_rate", "response_time_p95", "queue_size"]
    if body.metric not in VALID_METRICS:
        raise HTTPException(status_code=400, detail=f"无效的 metric: {body.metric}")
    get_collector().set_threshold(body.metric, body.value)
    return {"message": "阈值已更新", "metric": body.metric, "value": body.value}
@router.get("/thresholds", summary="查看告警阈值")
async def get_thresholds():
    c = get_collector()
    return {k: c._thresholds.get(k) for k in ["cpu_percent", "memory_percent", "disk_percent", "error_rate", "response_time_p95", "queue_size"]}
