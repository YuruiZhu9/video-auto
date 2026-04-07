#!/usr/bin/env python3
"""
FastAPI 路由：实例管理 API
/instance/* — 多 OpenClaw 实例管理
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

logger = logging.getLogger("clawctl.routes.instances")

router = APIRouter(prefix="/api/v1/instance", tags=["实例管理"])


class InstanceCreate(BaseModel):
    id: str
    name: str
    base_url: str
    api_key: str
    enabled: bool = True
    is_master: bool = False
    tags: list[str] = Field(default_factory=list)
    weight: int = 1


class InstanceUpdate(BaseModel):
    name: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    enabled: Optional[bool] = None
    is_master: Optional[bool] = None
    tags: Optional[list[str]] = None
    weight: Optional[int] = None
    health_check_interval: Optional[int] = None
    max_failures: Optional[int] = None


class SelectRequest(BaseModel):
    strategy: str = "round_robin"  # round_robin | weighted | fastest | least_active
    tag: Optional[str] = None
    exclude: Optional[str] = None


# 全局引用（由 main.py 设置）
_instance_manager = None


def set_instance_manager(mgr):
    global _instance_manager
    _instance_manager = mgr


def get_mgr():
    if _instance_manager is None:
        from core.instance_manager import get_instance_manager
        mgr = get_instance_manager()
        set_instance_manager(mgr)
    return _instance_manager


@router.get("/", summary="列出所有实例")
async def list_instances(enabled_only: bool = Query(False)):
    mgr = get_mgr()
    instances = mgr.list_instances(enabled_only=enabled_only)
    return {
        "total": len(instances),
        "instances": [
            {
                "id": i.id,
                "name": i.name,
                "base_url": i.base_url,
                "enabled": i.enabled,
                "is_alive": i.is_alive,
                "is_master": i.is_master,
                "tags": i.tags,
                "weight": i.weight,
                "total_requests": i.total_requests,
                "active_requests": i.active_requests,
                "avg_response_time": round(i.avg_response_time, 3),
                "last_check": i.last_check,
                "consecutive_failures": i.consecutive_failures,
            }
            for i in instances
        ],
    }


@router.get("/stats", summary="集群统计")
async def instance_stats():
    return get_mgr().get_stats()


@router.get("/{instance_id}", summary="获取实例详情")
async def get_instance(instance_id: str):
    ic = get_mgr().get_instance(instance_id)
    if not ic:
        raise HTTPException(status_code=404, detail=f"实例不存在: {instance_id}")
    i = ic.info
    return {
        "id": i.id,
        "name": i.name,
        "base_url": i.base_url,
        "enabled": i.enabled,
        "is_alive": i.is_alive,
        "is_master": i.is_master,
        "tags": i.tags,
        "weight": i.weight,
        "health_check_interval": i.health_check_interval,
        "max_failures": i.max_failures,
        "consecutive_failures": i.consecutive_failures,
        "total_requests": i.total_requests,
        "active_requests": i.active_requests,
        "avg_response_time": round(i.avg_response_time, 3),
        "last_check": i.last_check,
    }


@router.post("/", summary="注册新实例")
async def create_instance(body: InstanceCreate):
    from core.instance_manager import InstanceInfo
    mgr = get_mgr()
    try:
        info = mgr.add_instance(InstanceInfo(
            id=body.id,
            name=body.name,
            base_url=body.base_url,
            api_key=body.api_key,
            enabled=body.enabled,
            is_master=body.is_master,
            tags=body.tags,
            weight=body.weight,
        ))
        return {"message": "实例注册成功", "instance": {"id": info.id, "name": info.name}}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{instance_id}", summary="更新实例配置")
async def update_instance(instance_id: str, body: InstanceUpdate):
    updates = body.model_dump(exclude_unset=True)
    info = get_mgr().update_instance(instance_id, **updates)
    if not info:
        raise HTTPException(status_code=404, detail=f"实例不存在: {instance_id}")
    return {"message": "更新成功", "instance_id": instance_id}


@router.delete("/{instance_id}", summary="注销实例")
async def delete_instance(instance_id: str):
    ok = get_mgr().remove_instance(instance_id)
    if not ok:
        raise HTTPException(status_code=404, detail=f"实例不存在: {instance_id}")
    return {"message": "实例已注销", "instance_id": instance_id}


@router.post("/health-check", summary="立即执行健康检查")
async def trigger_health_check():
    get_mgr().force_health_check()
    return {"message": "健康检查已触发"}


@router.post("/select", summary="负载均衡选择实例")
async def select_instance(body: SelectRequest):
    ic = get_mgr().select_instance(
        strategy=body.strategy,
        tag=body.tag,
        exclude=body.exclude,
    )
    if not ic:
        raise HTTPException(status_code=503, detail="无可用实例")
    i = ic.info
    return {
        "instance_id": i.id,
        "name": i.name,
        "base_url": i.base_url,
        "is_master": i.is_master,
        "avg_response_time": round(i.avg_response_time, 3),
        "active_requests": i.active_requests,
    }
