"""HTTP Server — FastAPI 主入口"""

import asyncio
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from core.client import OpenClawClient
from core.task import TaskManager, TaskTemplate
from core.trigger import HTTPTrigger, WebhookTrigger, CronTrigger, RateLimiter
from core.auth import AuthManager, get_api_key, require_level, KeyLevel
from notify.notify_manager import NotifyManager
from notify.dingtalk import DingTalkChannel


# ─── NL 辅助函数 ────────────────────────────────────────────

_ESTIMATE_TIME = {
    "tech_brief": "2-3分钟",
    "market_insight": "2-4分钟",
    "full_scan": "5-10分钟",
    "quick_fetch": "1-2分钟",
    "deep_analysis": "5-8分钟",
    "status_query": "<1秒",
    "help": "<1秒",
    "passthrough": "取决于内容",
}

_SUGGESTIONS = {
    "tech_brief": [
        "📊 详细技术分析（深度）",
        "🔍 带大模型专项分析",
        "⏰ 聚焦近24小时最新动态",
    ],
    "market_insight": [
        "💰 带商业化案例分析",
        "🏢 特定行业垂直分析",
        "📈 附投资机会评估",
    ],
    "quick_fetch": [
        "🔥 仅热点资讯（5分钟）",
        "🌍 全量来源扫描",
        "📱 推送到手机",
    ],
}


def _estimate_time(intent: str) -> str:
    return _ESTIMATE_TIME.get(intent, "1-3分钟")


def _get_suggestions(plan) -> list:
    suggestions = _SUGGESTIONS.get(plan.intent, [])
    if plan.scope == "detailed":
        suggestions.append("✅ 已设置为详细模式")
    if plan.time_range != "today":
        suggestions.append(f"⏰ 时间范围: {plan.time_range}")
    if plan.topics:
        suggestions.append(f"🏷️ 话题: {', '.join(plan.topics)}")
    return suggestions


# ─── Pydantic 模型 ───────────────────────────────────────────

class TaskCreateRequest(BaseModel):
    template: Optional[str] = None
    task: Optional[dict] = None
    params: Optional[dict] = None
    notify: bool = True
    notify_channels: Optional[list] = None


class TaskListRequest(BaseModel):
    status: Optional[str] = None
    limit: int = 20


class TemplateCreateRequest(BaseModel):
    name: str
    display_name: str
    description: str = ""
    action: str = "spawn"
    agent: Optional[str] = None
    params: dict = {}
    params_schema: dict = {}
    notify_on_complete: bool = True


# ─── Lifespan ────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化所有组件
    config = app.state.config
    
    # OpenClaw Client
    app.state.oc = OpenClawClient(config["openclaw"])
    
    # 通知管理器
    app.state.notify = NotifyManager()
    if config["notify"]["dingtalk"]["enabled"]:
        dt = DingTalkChannel(
            config["notify"]["dingtalk"]["webhook_url"],
            config["notify"]["dingtalk"].get("secret"),
        )
        app.state.notify.register(dt)
    
    # 任务管理器
    app.state.tm = TaskManager(
        oc_client=app.state.oc,
        notify_manager=app.state.notify,
        templates=config.get("templates", {}),
    )
    
    # 认证管理器
    app.state.auth = AuthManager()
    
    # 频率限制器
    limits = config.get("auth", {}).get("rate_limit", {})
    app.state.rate_limiter = RateLimiter(limits or {"READ_ONLY": 30, "EXECUTE": 20, "ADMIN": 60})
    
    # HTTP 触发器
    app.state.http_trigger = HTTPTrigger(app.state.tm, app.state.auth, app.state.rate_limiter)
    
    # Webhook 触发器
    webhook_secret = config.get("triggers", {}).get("webhook", {}).get("secret")
    app.state.webhook_trigger = WebhookTrigger(app.state.tm, webhook_secret)
    
    # Cron 触发器
    if config.get("triggers", {}).get("cron", {}).get("enabled"):
        app.state.cron_trigger = CronTrigger(app.state.tm)
        schedules = config.get("triggers", {}).get("cron", {}).get("schedules", [])
        for s in schedules:
            app.state.cron_trigger.add_schedule(s["template"], s["cron"])
        await app.state.cron_trigger.start()
    
    print("[ClawRemote] 所有组件初始化完成")
    yield
    
    # 关闭时清理
    if hasattr(app.state, "cron_trigger"):
        await app.state.cron_trigger.stop()
    await app.state.oc.close()
    print("[ClawRemote] 已关闭")


# ─── App Factory ──────────────────────────────────────────────

def create_app(config: dict) -> FastAPI:
    app = FastAPI(title="ClawRemote API", version="1.0.0")
    app.state.config = config

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.router.lifespan_context = lifespan

    # ─── 异常处理 ────────────────────────────────────────────

    @app.exception_handler(PermissionError)
    async def permission_error(request: Request, exc: PermissionError):
        return JSONResponse(status_code=403, content={
            "error": {"code": "FORBIDDEN", "message": str(exc)}
        })

    @app.exception_handler(ValueError)
    async def value_error(request: Request, exc: ValueError):
        return JSONResponse(status_code=400, content={
            "error": {"code": "INVALID_REQUEST", "message": str(exc)}
        })

    # ─── 健康检查 ────────────────────────────────────────────

    @app.get("/health")
    async def health():
        oc_healthy = await app.state.oc.health_check()
        return {"status": "ok", "openclaw": "healthy" if oc_healthy else "unreachable"}

    # ─── 任务接口 ────────────────────────────────────────────

    @app.post("/api/v1/tasks", summary="创建任务")
    async def create_task(
        req: Request,
        body: TaskCreateRequest,
        api_key=Depends(get_api_key),
    ):
        data = body.model_dump(exclude_none=True)
        result = await app.state.http_trigger.handle_create_task(data, api_key)
        await app.state.auth.audit(api_key, "task.create", result.get("task_id", ""), "success", ip=req.client.host if req.client else "unknown")
        return result

    @app.get("/api/v1/tasks/{task_id}", summary="查询任务状态")
    async def get_task(task_id: str, api_key=Depends(get_api_key)):
        return await app.state.http_trigger.handle_get_task(task_id, api_key)

    @app.get("/api/v1/tasks", summary="列出任务")
    async def list_tasks(
        status: Optional[str] = None,
        limit: int = 20,
        api_key=Depends(get_api_key),
    ):
        return await app.state.http_trigger.handle_list_tasks(status, limit, api_key)

    @app.delete("/api/v1/tasks/{task_id}", summary="取消任务")
    async def cancel_task(task_id: str, req: Request, api_key=Depends(get_api_key)):
        result = await app.state.http_trigger.handle_cancel_task(task_id, api_key)
        await app.state.auth.audit(api_key, "task.cancel", task_id, "success", ip=req.client.host if req.client else "unknown")
        return result

    @app.post("/api/v1/tasks/trigger", summary="快捷触发（GET/POST 均可）")
    async def trigger_task(
        req: Request,
        name: Optional[str] = None,
        api_key=Depends(get_api_key),
    ):
        """用于快捷指令/IFTTT 的简化触发接口"""
        if req.method == "GET":
            template = name
            params = {}
        else:
            body = await req.json()
            template = body.get("template") or name
            params = body.get("params", {})
        if not template:
            raise HTTPException(400, "缺少 template 参数")
        task = await app.state.tm.create_from_template(template, params)
        return {"task_id": task.task_id, "status": task.status.value}

    # ─── 模板接口 ────────────────────────────────────────────

    @app.get("/api/v1/templates", summary="列出模板")
    async def list_templates(api_key=Depends(require_level(KeyLevel.READ_ONLY))):
        return {"templates": app.state.tm.list_templates()}

    @app.post("/api/v1/templates", summary="创建模板", dependencies=[Depends(require_level(KeyLevel.ADMIN))])
    async def create_template(body: TemplateCreateRequest, req: Request, api_key=Depends(get_api_key)):
        template = TaskTemplate(**body.model_dump())
        app.state.tm.add_template(template)
        await app.state.auth.audit(api_key, "template.create", template.name, "success", ip=req.client.host if req.client else "unknown")
        return {"name": template.name, "status": "created"}

    @app.delete("/api/v1/templates/{name}", summary="删除模板", dependencies=[Depends(require_level(KeyLevel.ADMIN))])
    async def delete_template(name: str, req: Request, api_key=Depends(get_api_key)):
        ok = app.state.tm.remove_template(name)
        if not ok:
            raise HTTPException(404, f"模板不存在: {name}")
        await app.state.auth.audit(api_key, "template.delete", name, "success", ip=req.client.host if req.client else "unknown")
        return {"name": name, "status": "deleted"}

    # ─── 状态接口 ────────────────────────────────────────────

    @app.get("/api/v1/status", summary="系统状态")
    async def get_status(api_key=Depends(require_level(KeyLevel.READ_ONLY))):
        oc_status = await app.state.oc.get_status()
        sessions = await app.state.oc.sessions_list(kinds=["subagent"])
        task_stats = app.state.tm.get_stats()
        return {
            "server": {"version": "1.0.0", "uptime": "N/A"},
            "openclaw": {
                "gateway_reachable": True,
                "active_sessions": len(sessions.get("sessions", [])),
                "agents": oc_status.get("agents", []),
            },
            "tasks": task_stats,
        }

    # ─── Webhook 接口 ────────────────────────────────────────

    @app.post("/api/v1/webhook", summary="通用 Webhook 入口")
    async def webhook(req: Request):
        body = await req.body()
        signature = req.headers.get("x-signature-256")
        if not app.state.webhook_trigger.verify_signature(body, signature):
            raise HTTPException(401, "签名验证失败")
        data = await req.json()
        return await app.state.webhook_trigger.handle(data)

    @app.post("/api/v1/webhook/dingtalk", summary="钉钉 Webhook 入口")
    async def webhook_dingtalk(req: Request):
        data = await req.json()
        timestamp = req.headers.get("timestamp", "")
        sign = req.headers.get("sign", "")
        secret = app.state.config.get("notify", {}).get("dingtalk", {}).get("secret")
        if secret:
            from core.trigger import DingTalkTrigger
            dt_trigger = DingTalkTrigger(app.state.tm, secret)
            if not dt_trigger.verify_signature(timestamp, sign):
                raise HTTPException(401, "签名验证失败")
            result = await dt_trigger.handle(data)
            if result:
                return result
        return {"ok": True}

    # ─── 自然语言任务接口 ────────────────────────────────────

    class NLParseRequest(BaseModel):
        text: str
        execute: bool = False

    @app.post("/api/v1/nl/parse", summary="解析自然语言命令")
    async def nl_parse(
        req: Request,
        body: NLParseRequest,
        api_key=Depends(require_level(KeyLevel.EXECUTE)),
    ):
        """
        解析自然语言命令，返回 TaskPlan（不执行）
        """
        plan = app.state.nl_interpreter.parse(body.text)

        # 状态查询 / 帮助 — 直接响应，无需执行
        if plan.intent in ("status_query", "help", "unknown"):
            await app.state.auth.audit(
                api_key, "nl.parse", plan.intent, "success",
                ip=req.client.host if req.client else "unknown"
            )
            return {
                "type": "direct_response",
                "intent": plan.intent,
                "confidence": plan.confidence,
                "description": plan.description,
                "plan": plan.to_dict(),
            }

        await app.state.auth.audit(
            api_key, "nl.parse", plan.intent, "success",
            ip=req.client.host if req.client else "unknown"
        )
        return {
            "type": "plan",
            "intent": plan.intent,
            "confidence": plan.confidence,
            "description": plan.description,
            "estimated_time": _estimate_time(plan.intent),
            "agent": plan.agent,
            "suggestions": _get_suggestions(plan),
            "params": {
                "scope": plan.scope,
                "time_range": plan.time_range,
                "topics": plan.topics,
                "template_id": f"{plan.agent}-{plan.intent}",
            },
        }

    @app.post("/api/v1/nl/execute", summary="解析并执行自然语言命令")
    async def nl_execute(
        req: Request,
        body: NLParseRequest,
        api_key=Depends(require_level(KeyLevel.EXECUTE)),
    ):
        """
        解析自然语言命令并立即执行
        """
        plan = app.state.nl_interpreter.parse(body.text)

        # 状态查询 — 直接返回系统状态
        if plan.intent == "status_query":
            oc_status = await app.state.oc.get_status()
            sessions = await app.state.oc.sessions_list(kinds=["subagent"])
            return {
                "type": "status",
                "intent": "status_query",
                "status": {
                    "openclaw": "✅ 在线" if oc_status.get("ok") else "⚠️ 离线",
                    "活跃会话": len(sessions.get("sessions", [])),
                    "可用Agent": [a.get("name") or a.get("id", "未知") for a in oc_status.get("agents", [])],
                },
            }

        # 帮助 — 返回命令参考
        if plan.intent == "help":
            return {
                "type": "help",
                "intent": "help",
                "reference": app.state.nl_interpreter.get_reference(),
            }

        # 透传命令 — 直接发给 OpenClaw
        if plan.intent == "passthrough":
            try:
                result = await app.state.oc.send_message(
                    channel="dingtalk",
                    message=body.text,
                )
                return {
                    "type": "passthrough",
                    "task_id": result.get("message_id", ""),
                    "intent": "passthrough",
                    "description": "已透传给 OpenClaw 处理",
                }
            except Exception as e:
                return {"type": "error", "message": str(e)}

        # 正常任务执行
        template_id = f"{plan.agent}-{plan.intent}"
        task_data = {
            "template": template_id,
            "params": {
                "scope": plan.scope,
                "time_range": plan.time_range,
                "topics": plan.topics,
                **plan.params,
            },
            "notify": True,
        }
        task_result = await app.state.http_trigger.handle_create_task(task_data, api_key)

        await app.state.auth.audit(
            api_key, "nl.execute", plan.intent, "success",
            ip=req.client.host if req.client else "unknown"
        )
        return {
            "type": "task_executed",
            "task_id": task_result.get("task_id", ""),
            "intent": plan.intent,
            "confidence": plan.confidence,
            "description": plan.description,
            "estimated_time": _estimate_time(plan.intent),
            "suggestions": _get_suggestions(plan),
            "params": task_data["params"],
        }

    @app.get("/api/v1/nl/reference", summary="获取命令参考")
    async def nl_reference(api_key=Depends(require_level(KeyLevel.READ_ONLY))):
        return app.state.nl_interpreter.get_reference()

    @app.get("/api/v1/nl/stats", summary="NL 解析统计", dependencies=[Depends(require_level(KeyLevel.ADMIN))])
    async def nl_stats(api_key=Depends(get_api_key)):
        return app.state.nl_interpreter.stats()

    # ─── 审计日志 ────────────────────────────────────────────

    @app.get("/api/v1/audit_logs", summary="操作审计日志", dependencies=[Depends(require_level(KeyLevel.ADMIN))])
    async def get_audit_logs(
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        limit: int = 100,
        api_key=Depends(get_api_key),
    ):
        logs = app.state.auth.get_audit_logs(from_date, to_date, limit)
        return {"logs": logs, "total": len(logs)}

    return app
