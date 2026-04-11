#!/usr/bin/env python3
"""
clawctl FastAPI Server — OpenClaw 跨设备控制框架 v2.9.0
基于 FastAPI + Starlette，完全异步，WebSocket 原生支持

启动方式：
    cd /workspace/reports/oc-cross-device/code
    OPENCLAW_API_KEY=xxx /app/.venv/bin/python -m clawctl.fastapi_main --port 8081
    # 或直接运行
    OPENCLAW_API_KEY=xxx DINGTALK_TOKEN=xxx /app/.venv/bin/python fastapi_main.py --port 8081
"""

from __future__ import annotations

import os, sys, json, logging, asyncio
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

# ── 路径配置 ──────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent  # /workspace/reports/oc-cross-device/code
sys.path.insert(0, str(BASE_DIR))

from core.client import OpenClawClient
from core.task import TaskManager
from core.auth import AuthManager, KeyLevel
from core.database import TaskDatabase
from core.template_loader import TemplateLoader
from core.scheduler import Scheduler
from core.nl_interpreter import NLInterpreter
from core.multi_instance import get_multi_instance_manager
from core.monitor import MonitoringManager
from core.plugin_manager import PluginManager, Plugin

logger = logging.getLogger("clawctl.fastapi")

# ── 全局状态 ──────────────────────────────────────────────────────────────────
class AppState:
    client: OpenClawClient
    task_manager: TaskManager
    auth_manager: AuthManager
    db: TaskDatabase
    template_loader: TemplateLoader
    scheduler: Scheduler
    nl_interpreter: NLInterpreter
    plugin_manager: PluginManager
    monitoring: MonitoringManager
    sse_manager: SseManager
    ws_connections: list[WebSocket]

    def __init__(self):
        self.ws_connections = []
        self.client = None
        self.task_manager = None
        self.auth_manager = None
        self.db = None
        self.template_loader = None
        self.scheduler = None
        self.nl_interpreter = None
        self.plugin_manager = None
        self.monitoring = None
        self.sse_manager = None

state = AppState()


# ── SSE 管理器（复刻自 handlers/sse_handler.py，异步化）─────────────────────────

from dataclasses import dataclass, field
from collections import defaultdict
import uuid
import asyncio

@dataclass
class SseEvent:
    type: str
    data: dict
    id: Optional[str] = None
    retry: int = 30000

    def to_sse_bytes(self) -> bytes:
        eid = self.id or str(uuid.uuid4())[:8]
        lines = [
            f"id: {eid}",
            f"event: {self.type}",
            f"retry: {self.retry}",
            f"data: {json.dumps(self.data, ensure_ascii=False, default=str)}",
        ]
        return "\n".join(lines).encode() + b"\n\n"


class SseManager:
    def __init__(self):
        self._conns: list[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        async with self._lock:
            self._conns.append(ws)

    async def disconnect(self, ws: WebSocket):
        async with self._lock:
            self._conns = [c for c in self._conns if c != ws]

    async def broadcast(self, event: SseEvent):
        dead = []
        async with self._lock:
            conns = list(self._conns)
        for ws in conns:
            try:
                await ws.send_bytes(event.to_sse_bytes())
            except Exception:
                dead.append(ws)
        if dead:
            async with self._lock:
                self._conns = [c for c in self._conns if c not in dead]


# ── 生命周期 ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI 生命周期管理：启动初始化 + 关闭清理"""
    setup_logging()
    logger.info("🚀 clawctl FastAPI Server v2.9.0 启动中...")

    # ── 初始化核心组件 ──────────────────────────────────────────────────────
    oc_cfg = load_oc_config()
    state.client = OpenClawClient(
        base_url=oc_cfg.get("base_url", "http://localhost:18789"),
        api_key=oc_cfg.get("api_key") or os.environ.get("OPENCLAW_API_KEY", ""),
        timeout=oc_cfg.get("timeout", 30),
    )
    state.auth_manager = AuthManager(str(BASE_DIR / "clawctl" / "auth_keys.json"))
    state.db = TaskDatabase(os.environ.get("CLAWCTL_DB_PATH", str(BASE_DIR / "data" / "tasks.db")))
    state.template_loader = TemplateLoader(str(BASE_DIR / "clawctl" / "templates" / "schedules.yaml"))
    state.task_manager = TaskManager(state.client, db=state.db)
    state.sse_manager = SseManager()
    state.plugin_manager = PluginManager()
    state.nl_interpreter = NLInterpreter()

    # 注入插件系统支持
    try:
        from clawctl.core.nl_plugin_ext import patch_nl_interpreter
        patch_nl_interpreter(state.nl_interpreter, state.plugin_manager)
        logger.info(f"✅ NL Interpreter 插件扩展已注入，已注册 {len(state.plugin_manager.plugins)} 个插件")
    except ImportError:
        logger.warning("⚠️ nl_plugin_ext 未找到，插件扩展跳过")

    # 定时调度器
    state.scheduler = Scheduler(state.task_manager, state.template_loader)
    state.template_loader.start()
    state.scheduler.load_tasks()
    state.scheduler.start()

    # 监控 + 健康检查
    state.monitoring = MonitoringManager(
        collectors=[],
        interval=5,
        retention_minutes=60,
    )
    state.monitoring.start()

    logger.info("✅ 所有组件初始化完成")

    # ── 启动后注册到 OpenClaw 回调 ───────────────────────────────────────────
    # NL interpreter 执行完成后广播 SSE 事件
    def on_task_done(task_id: str, result: dict):
        asyncio.create_task(state.sse_manager.broadcast(SseEvent(
            type="task_result",
            data={"task_id": task_id, "result": result},
        )))

    yield

    # ── 关闭清理 ─────────────────────────────────────────────────────────────
    logger.info("🛑 关闭 clawctl FastAPI Server...")
    state.scheduler.stop()
    state.monitoring.stop()
    state.template_loader.stop()
    for ws in list(state.sse_manager._conns):
        try:
            await ws.close()
        except Exception:
            pass


def load_oc_config() -> dict:
    cfg = {}
    for path in [
        BASE_DIR / "clawctl" / "config.yaml",
        Path(os.environ.get("CLAWCTL_CONFIG", "")),
        Path("/workspace/reports/oc-cross-device/config.yaml"),
    ]:
        if path.exists():
            import yaml
            cfg = yaml.safe_load(open(path)) or {}
            break
    return cfg.get("openclaw", {})


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


# ── FastAPI 应用 ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="clawctl API",
    version="2.9.0",
    description="OpenClaw 跨设备控制框架 — FastAPI 原生实现",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件（Web Admin v3）
WEB_ADMIN_V3 = BASE_DIR / "clawctl" / "web_admin" / "v3"
if WEB_ADMIN_V3.exists():
    app.mount("/admin_v3", StaticFiles(directory=str(WEB_ADMIN_V3), html=True), name="admin_v3")

STATIC_ROOT = BASE_DIR / "clawctl" / "web_admin"
if STATIC_ROOT.exists():
    app.mount("/admin", StaticFiles(directory=str(STATIC_ROOT), html=True), name="admin")


# ── 认证依赖 ──────────────────────────────────────────────────────────────────

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
security = HTTPBearer(auto_error=False)


async def get_current_key(cred: HTTPAuthorizationCredentials = Depends(security)):
    """认证：支持 Bearer token 或 API Key query 参数"""
    key = None
    level = None

    if cred:
        key = cred.credentials
    elif "api_key" in dict(request.__dict__.get("_query_params", {})):
        # FastAPI 从 request 无法直接访问 query_params
        pass

    if not key:
        # 允许无认证访问健康检查
        return None

    if hasattr(state, 'auth_manager') and state.auth_manager:
        level = state.auth_manager.verify_key(key)
    return key if level else None


def require_level(level: KeyLevel):
    async def dep(key=Depends(get_current_key)):
        if key is None:
            raise HTTPException(401, "Unauthorized")
        # level check would go here
        return key
    return dep


# ── SSE WebSocket 端点 ─────────────────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """WebSocket 实时通道 — 双向通信"""
    await state.sse_manager.connect(ws)
    try:
        while True:
            data = await ws.receive_text()
            # 解析客户端消息
            try:
                msg = json.loads(data)
                cmd = msg.get("type")
                if cmd == "ping":
                    await ws.send_json({"type": "pong"})
                elif cmd == "subscribe":
                    # 订阅特定事件类型
                    await ws.send_json({"type": "subscribed", "channels": msg.get("channels", [])})
                elif cmd == "trigger":
                    task_text = msg.get("task")
                    if task_text:
                        result = await asyncio.to_thread(
                            state.nl_interpreter.execute, task_text, "dingtalk"
                        )
                        await ws.send_json({"type": "trigger_result", "result": result})
            except json.JSONDecodeError:
                await ws.send_json({"type": "error", "message": "invalid JSON"})
    except WebSocketDisconnect:
        await state.sse_manager.disconnect(ws)


@app.get("/api/v1/events")
async def sse_stream(request: Request):
    """SSE 实时推送端点（兼容旧版客户端）"""
    from fastapi.responses import StreamingResponse

    async def event_generator():
        q = asyncio.Queue()

        async def on_event(event: SseEvent):
            await q.put(event.to_sse_bytes())

        # 订阅
        async with state.sse_manager._lock:
            # 创建一个虚拟 WS 连接用于 SSE
            pass

        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    data = await asyncio.wait_for(q.get(), timeout=30)
                    yield data
                except asyncio.TimeoutError:
                    yield b": heartbeat\n\n"
        except Exception:
            pass

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ── 核心 API 端点 ──────────────────────────────────────────────────────────────

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    task: str
    runtime: Optional[str] = "subagent"
    params: Optional[dict] = {}
    channel: Optional[str] = "dingtalk"


class NLRequest(BaseModel):
    text: str
    channel: Optional[str] = "dingtalk"
    preview_only: Optional[bool] = False


class PluginRegister(BaseModel):
    id: str
    name: str
    description: str
    intents: list[dict] = []  # [{intent: str, keywords: list[str], handler: str}]


class ScheduleCreate(BaseModel):
    """创建定时任务的请求模型"""
    name: str = Field(..., description="任务名称")
    template_id: str = Field(..., description="模板 ID")
    cron_expr: str = Field(..., description="Cron 表达式，如 0 9 * * *")
    timezone: str = Field(default="Asia/Shanghai", description="时区")
    enabled: bool = Field(default=True, description="是否启用")
    notify_on_complete: bool = Field(default=True, description="完成后通知")
    notify_channel: str = Field(default="dingtalk", description="通知渠道")
    params: dict = Field(default_factory=dict, description="模板参数覆盖")


@app.get("/api/v1/health")
async def health():
    """健康检查"""
    return {"status": "ok", "version": "2.9.0", "service": "clawctl-fastapi"}


@app.get("/api/v1/status")
async def status():
    """系统状态"""
    try:
        oc_status = await asyncio.to_thread(state.client.get_status)
    except Exception as e:
        oc_status = {"error": str(e)}
    return {
        "openclaw": oc_status,
        "active_tasks": state.task_manager.count_running() if state.task_manager else 0,
        "schedules": len(state.scheduler.jobs) if state.scheduler else 0,
        "plugins": len(state.plugin_manager.plugins) if state.plugin_manager else 0,
        "ws_clients": len(state.sse_manager._conns),
    }


@app.post("/api/v1/tasks", response_model=dict)
async def create_task(body: TaskCreate):
    """触发新任务"""
    task_id = f"api-{uuid.uuid4().hex[:8]}"
    result = await asyncio.to_thread(
        state.task_manager.create_task,
        name=body.task,
        action="spawn",
        params={"task": body.task, "runtime": body.runtime, **body.params},
        channel=body.channel or "dingtalk",
    )
    return {"task_id": result.get("task_id", task_id), "status": "submitted", "result": result}


@app.get("/api/v1/tasks", response_model=list)
async def list_tasks(limit: int = Query(20, le=100), status: Optional[str] = None):
    """列出最近任务"""
    records = state.db.get_recent(limit=limit) if state.db else []
    if status:
        records = [r for r in records if r.get("status") == status]
    return records


@app.get("/api/v1/tasks/{task_id}", response_model=dict)
async def get_task(task_id: str):
    record = state.db.get(task_id) if state.db else None
    if not record:
        raise HTTPException(404, "Task not found")
    return record


@app.delete("/api/v1/tasks/{task_id}")
async def cancel_task(task_id: str):
    success = state.task_manager.cancel(task_id) if state.task_manager else False
    if not success:
        raise HTTPException(404, "Task not found or cannot cancel")
    return {"task_id": task_id, "status": "cancelled"}


# ── 自然语言解析端点 ───────────────────────────────────────────────────────────

@app.post("/api/v1/nl", response_model=dict)
async def nl_execute(body: NLRequest):
    """自然语言 → 自动解析执行"""
    result = await asyncio.to_thread(
        state.nl_interpreter.execute, body.text, body.channel or "dingtalk"
    )
    return result


@app.post("/api/v1/nl/preview", response_model=dict)
async def nl_preview(body: NLRequest):
    """预览自然语言解析结果（不执行）"""
    parsed = state.nl_interpreter.parse(body.text)
    return parsed


@app.get("/api/v1/nl/intents", response_model=dict)
async def nl_intents():
    """列出支持的意图"""
    return {
        "intents": [
            {"id": k, "keywords": v.get("keywords", [])}
            for k, v in state.nl_interpreter.INTENT_PATTERNS.items()
        ]
    }


@app.get("/api/v1/nl/cmd")
async def nl_cmd(
    q: str = Query(..., description="自然语言指令"),
    channel: str = Query("dingtalk"),
    intent_only: bool = Query(False),
    api_key: Optional[str] = Query(None),
):
    """快捷指令 GET 端点（兼容 iOS 快捷指令）"""
    # 认证检查
    if api_key and hasattr(state, 'auth_manager') and state.auth_manager:
        if not state.auth_manager.verify_key(api_key):
            return JSONResponse({"success": False, "error": "Invalid API key"}, status_code=401)

    if intent_only:
        parsed = state.nl_interpreter.parse(q)
        return parsed

    result = await asyncio.to_thread(
        state.nl_interpreter.execute, q, channel
    )
    return result


# ── 任务模板 ──────────────────────────────────────────────────────────────────

@app.get("/api/v1/templates", response_model=list)
async def list_templates():
    if not state.template_loader:
        return []
    return [{"id": tid, **tpl} for tid, tpl in state.template_loader.list().items()]


@app.post("/api/v1/templates/{name}/execute", response_model=dict)
async def execute_template(name: str, channel: str = Query("dingtalk")):
    """执行指定模板"""
    tpl = state.template_loader.get(name) if state.template_loader else None
    if not tpl:
        raise HTTPException(404, f"Template '{name}' not found")
    result = await asyncio.to_thread(
        state.task_manager.execute_template, name, tpl, channel=channel
    )
    return result


# ── 定时任务 ──────────────────────────────────────────────────────────────────

@app.get("/api/v1/schedules", response_model=list)
async def list_schedules():
    if not state.scheduler:
        return []
    return state.scheduler.list_jobs()


@app.post("/api/v1/schedules/{schedule_id}/trigger")
async def trigger_schedule(schedule_id: str):
    """立即触发定时任务"""
    job = state.scheduler.get_job(schedule_id) if state.scheduler else None
    if not job:
        raise HTTPException(404, "Schedule not found")
    state.scheduler.trigger_now(schedule_id)
    return {"schedule_id": schedule_id, "status": "triggered"}


@app.post("/api/v1/schedules")
async def create_schedule(body: ScheduleCreate):
    """创建新的定时任务"""
    if not state.scheduler:
        raise HTTPException(503, "Scheduler not available")
    try:
        import uuid
        job_id = str(uuid.uuid4())[:8]
        state.scheduler.add_job(
            name=body.name,
            template_id=body.template_id,
            cron_expr=body.cron_expr,
            timezone=body.timezone,
            enabled=body.enabled,
            notify_on_complete=body.notify_on_complete,
            notify_channel=body.notify_channel,
            params=body.params,
            job_id=body.name,
        )
        return {"success": True, "job_id": body.name}
    except Exception as e:
        raise HTTPException(400, str(e))


@app.delete("/api/v1/schedules/{schedule_id}")
async def delete_schedule(schedule_id: str):
    """删除定时任务"""
    if not state.scheduler:
        raise HTTPException(503, "Scheduler not available")
    removed = state.scheduler.remove_job(schedule_id)
    if not removed:
        raise HTTPException(404, "Schedule not found")
    return {"success": True, "schedule_id": schedule_id}


@app.patch("/api/v1/schedules/{schedule_id}/toggle")
async def toggle_schedule(schedule_id: str):
    """切换定时任务启用状态"""
    if not state.scheduler:
        raise HTTPException(503, "Scheduler not available")
    job = state.scheduler.get_job(schedule_id)
    if not job:
        raise HTTPException(404, "Schedule not found")
    if job.enabled:
        state.scheduler.pause_job(schedule_id)
    else:
        state.scheduler.resume_job(schedule_id)
    job = state.scheduler.get_job(schedule_id)
    return {"schedule_id": schedule_id, "enabled": job.enabled if job else False}


@app.get("/api/v1/templates/{template_id}")
async def get_template(template_id: str):
    """获取指定模板详情"""
    if not state.template_loader:
        raise HTTPException(503, "Template loader not available")
    tpl = state.template_loader.get(template_id)
    if not tpl:
        raise HTTPException(404, "Template not found")
    return {"id": template_id, **tpl}


# ── Plugin 系统 ────────────────────────────────────────────────────────────────

@app.get("/api/v1/plugins", response_model=list)
async def list_plugins():
    """列出已注册插件"""
    return [
        {"id": p.id, "name": p.name, "description": p.description, "intents": p.intents}
        for p in (state.plugin_manager.plugins.values() if state.plugin_manager else [])
    ]


@app.post("/api/v1/plugins")
async def register_plugin(body: PluginRegister):
    """注册新插件"""
    plugin = Plugin(
        id=body.id,
        name=body.name,
        description=body.description,
        intents=body.intents,
        enabled=True,
    )
    state.plugin_manager.register(plugin)
    # 将插件意图合并到 NL interpreter
    for intent_cfg in body.intents:
        state.nl_interpreter.add_custom_intent(
            intent_cfg["intent"],
            intent_cfg.get("keywords", []),
            intent_cfg.get("handler"),
        )
    return {"success": True, "plugin_id": body.id}


@app.delete("/api/v1/plugins/{plugin_id}")
async def unregister_plugin(plugin_id: str):
    """卸载插件"""
    state.plugin_manager.unregister(plugin_id)
    return {"success": True, "plugin_id": plugin_id}


# ── 监控端点 ──────────────────────────────────────────────────────────────────

@app.get("/api/v1/monitor/snapshot", response_model=dict)
async def monitor_snapshot():
    if not state.monitoring:
        return {"error": "monitoring not initialized"}
    return state.monitoring.get_snapshot()


@app.get("/api/v1/monitor/instances", response_model=list)
async def list_instances():
    mgr = get_multi_instance_manager()
    if not mgr:
        return []
    return [
        {"id": i.id, "name": i.name, "status": i.status, "group": i.group}
        for i in mgr.instances.values()
    ]


@app.get("/api/v1/monitor/alerts/active", response_model=list)
async def active_alerts():
    if not state.monitoring:
        return []
    return state.monitoring.get_active_alerts()


@app.get("/api/v1/monitor/alerts/rules", response_model=list)
async def alert_rules():
    if not state.monitoring:
        return []
    return [
        {"id": r.id, "name": r.name, "metric": r.metric, "threshold": r.threshold}
        for r in state.monitoring.alert_rules
    ]


# ── 快捷触发（兼容旧版）────────────────────────────────────────────────────────

@app.post("/api/v1/trigger/{name}", response_model=dict)
async def quick_trigger(name: str, channel: str = Query("dingtalk")):
    """快捷触发器：/api/v1/trigger/quick-report"""
    tpl_name = name.replace("-", "_")
    tpl = state.template_loader.get(tpl_name) if state.template_loader else None
    if not tpl:
        raise HTTPException(404, f"Template '{tpl_name}' not found")
    result = await asyncio.to_thread(
        state.task_manager.execute_template, tpl_name, tpl, channel=channel
    )
    return result


# ── 主入口 ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8081)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()

    uvicorn.run(
        "fastapi_main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info",
    )
