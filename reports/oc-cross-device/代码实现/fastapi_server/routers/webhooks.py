#!/usr/bin/env python3
"""
FastAPI 路由：Webhook 回调管理 API
/api/v1/webhook/* — Webhook 端点注册、投递日志
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

logger = logging.getLogger("clawctl.routes.webhooks")

router = APIRouter(prefix="/api/v1/webhook", tags=["Webhook管理"])


class WebhookEndpointCreate(BaseModel):
    id: str
    url: str
    secret: str = ""
    events: list[str] = Field(default_factory=list)  # 事件列表
    enabled: bool = True
    retry_count: int = 3
    retry_delay: float = 5.0
    timeout: float = 10.0
    headers: dict[str, str] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    description: str = ""


class WebhookEndpointUpdate(BaseModel):
    url: Optional[str] = None
    secret: Optional[str] = None
    events: Optional[list[str]] = None
    enabled: Optional[bool] = None
    retry_count: Optional[int] = None
    retry_delay: Optional[float] = None
    timeout: Optional[float] = None
    headers: Optional[dict[str, str]] = None
    tags: Optional[list[str]] = None
    description: Optional[str] = None


class WebhookTestRequest(BaseModel):
    endpoint_id: str
    event: str = "system.alert"
    payload: dict = Field(default_factory=dict)


# 全局引用
_webhook_manager = None


def set_webhook_manager(mgr):
    global _webhook_manager
    _webhook_manager = mgr


def get_mgr():
    global _webhook_manager
    if _webhook_manager is None:
        from core.webhook_manager import get_webhook_manager
        _webhook_manager = get_webhook_manager()
    return _webhook_manager


@router.get("/", summary="列出所有 Webhook 端点")
async def list_endpoints():
    mgr = get_mgr()
    return {
        "total": mgr._endpoints.__len__() if hasattr(mgr, "_endpoints") else 0,
        **mgr.get_stats(),
    }


@router.get("/{endpoint_id}", summary="获取端点详情")
async def get_endpoint(endpoint_id: str):
    ep = get_mgr().get_endpoint(endpoint_id)
    if not ep:
        raise HTTPException(status_code=404, detail=f"端点不存在: {endpoint_id}")
    return {
        "id": ep.id,
        "url": ep.url,
        "events": [e.value for e in ep.events],
        "enabled": ep.enabled,
        "retry_count": ep.retry_count,
        "retry_delay": ep.retry_delay,
        "timeout": ep.timeout,
        "headers": ep.headers,
        "tags": ep.tags,
        "description": ep.description,
        "total_calls": ep.total_calls,
        "failed_calls": ep.failed_calls,
        "last_call_at": ep.last_call_at,
        "last_status_code": ep.last_status_code,
    }


@router.post("/", summary="注册 Webhook 端点")
async def create_endpoint(body: WebhookEndpointCreate):
    from core.webhook_manager import WebhookEndpoint as WHEndpoint
    from core.webhook_manager import WebhookEvent
    mgr = get_mgr()
    try:
        events = [WebhookEvent(e) for e in body.events if e in [ev.value for ev in WebhookEvent]]
        ep = mgr.add_endpoint(WHEndpoint(
            id=body.id,
            url=body.url,
            secret=body.secret,
            events=events,
            enabled=body.enabled,
            retry_count=body.retry_count,
            retry_delay=body.retry_delay,
            timeout=body.timeout,
            headers=body.headers,
            tags=body.tags,
            description=body.description,
        ))
        return {
            "message": "Webhook 端点注册成功",
            "endpoint_id": ep.id,
            "events": [e.value for e in ep.events],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{endpoint_id}", summary="更新 Webhook 端点")
async def update_endpoint(endpoint_id: str, body: WebhookEndpointUpdate):
    from core.webhook_manager import WebhookEvent
    updates = body.model_dump(exclude_unset=True)
    # 转换事件字符串为枚举
    if "events" in updates:
        updates["events"] = [WebhookEvent(e) for e in updates["events"] if e in [ev.value for ev in WebhookEvent]]
    ep = get_mgr().update_endpoint(endpoint_id, **updates)
    if not ep:
        raise HTTPException(status_code=404, detail=f"端点不存在: {endpoint_id}")
    return {"message": "更新成功", "endpoint_id": endpoint_id}


@router.delete("/{endpoint_id}", summary="删除 Webhook 端点")
async def delete_endpoint(endpoint_id: str):
    ok = get_mgr().remove_endpoint(endpoint_id)
    if not ok:
        raise HTTPException(status_code=404, detail=f"端点不存在: {endpoint_id}")
    return {"message": "端点已删除", "endpoint_id": endpoint_id}


@router.post("/{endpoint_id}/test", summary="测试 Webhook 端点")
async def test_endpoint(endpoint_id: str):
    from core.webhook_manager import WebhookEvent
    import datetime
    mgr = get_mgr()
    ep = mgr.get_endpoint(endpoint_id)
    if not ep:
        raise HTTPException(status_code=404, detail=f"端点不存在: {endpoint_id}")

    test_payload = {
        "event": "test",
        "timestamp": datetime.datetime.now().isoformat(),
        "message": "🔔 这是一条来自 clawctl 的测试消息",
        "test": True,
    }
    mgr.emit(WebhookEvent.TASK_COMPLETED, test_payload, target_endpoint_id=endpoint_id)
    return {"message": "测试事件已投递", "endpoint_id": endpoint_id}


@router.get("/{endpoint_id}/deliveries", summary="查询投递日志")
async def get_deliveries(endpoint_id: str, limit: int = Query(50, le=200)):
    deliveries = get_mgr().get_delivery_log(endpoint_id=endpoint_id, limit=limit)
    return {
        "total": len(deliveries),
        "deliveries": [
            {
                "id": d.id,
                "endpoint_id": d.endpoint_id,
                "event": d.event,
                "status": d.status,
                "attempts": d.attempts,
                "response_code": d.response_code,
                "error": d.error,
                "created_at": d.created_at,
                "delivered_at": d.delivered_at,
            }
            for d in deliveries
        ],
    }


@router.post("/{endpoint_id}/enable", summary="启用端点")
async def enable_endpoint(endpoint_id: str):
    get_mgr().enable_endpoint(endpoint_id, True)
    return {"message": "端点已启用", "endpoint_id": endpoint_id}


@router.post("/{endpoint_id}/disable", summary="禁用端点")
async def disable_endpoint(endpoint_id: str):
    get_mgr().enable_endpoint(endpoint_id, False)
    return {"message": "端点已禁用", "endpoint_id": endpoint_id}
