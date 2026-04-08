"""
OpenClaw Cross-Device Control - FastAPI Server (v1.4.0)
高性能异步 Web 服务，替代 Flask
Phase 2 核心：APScheduler 集成、Web Admin API 贯通、任务持久化
"""

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger as APSchedulerCronTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from fastapi import FastAPI, HTTPException, Header, Depends, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from pathlib import Path

# ─── 路径设置 ───────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from core.auth import AuthManager, KeyLevel, APIKey
from core.client import OpenClawClient
from core.database import Database
from core.task import TaskManager, TaskStatus
from core.confirm_token import ConfirmTokenManager, ConfirmToken
from core.template_watcher import TemplateWatcher
from notify.notification import NotifyManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ─── 全局单例 ───────────────────────────────────────────────────
_db: Optional[Database] = None
_task_mgr: Optional[TaskManager] = None
_notify_mgr: Optional[NotifyManager] = None
_scheduler: Optional[AsyncIOScheduler] = None
_gateway_client: Optional[OpenClawClient] = None
_auth_mgr: AuthManager = AuthManager()
_confirm_mgr: Optional[ConfirmTokenManager] = None
_template_watcher: Optional[TemplateWatcher] = None
_telegram_bot = None  # Telegram Bot 实例（可选）

# ─── Web Session（简化版 Session，存 API Key）───────────────────
_web_sessions: Dict[str, Dict[str, Any]] = {}  # session_token -> {api_key, key_obj, expires}


# ═══════════════════════════════════════════════════════════════════
# 工具函数
# ═══════════════════════════════════════════════════════════════════

def get_openclaw_client() -> OpenClawClient:
    """获取或创建 OpenClaw Client"""
    global _gateway_client
    if _gateway_client is None:
        base_url = os.getenv("OPENCLAW_URL", "http://localhost:18789")
        api_key = os.getenv("OPENCLAW_TOKEN", "")
        _gateway_client = OpenClawClient(base_url=base_url, api_key=api_key)
    return _gateway_client


def _session_token() -> str:
    import secrets
    return secrets.token_urlsafe(32)


def _require_level(required: KeyLevel):
    """权限装饰器工厂"""
    def checker(authorization: Optional[str] = Header(None)) -> APIKey:
        if not authorization:
            raise HTTPException(status_code=401, detail="缺少认证：未提供 Authorization header")
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="认证格式错误：请使用 Bearer {api_key}")
        key = authorization[7:].strip()
        key_obj = _auth_mgr.validate_key(key)
        if not key_obj:
            raise HTTPException(status_code=401, detail="无效的 API Key")
        if not key_obj.is_valid():
            raise HTTPException(status_code=401, detail="API Key 已过期")
        if not _auth_mgr.check_permission(key, required):
            raise HTTPException(status_code=403, detail=f"权限不足：需要 {required.value} 级别")
        # 审计日志
        _auth_mgr.log_action("api_call", key_id=key_obj.key_id, detail=f"{required.value} action")
        return key_obj
    return checker


# ═══════════════════════════════════════════════════════════════════
# Pydantic 模型
# ═══════════════════════════════════════════════════════════════════

class LoginRequest(BaseModel):
    api_key: str

class TaskCreate(BaseModel):
    name: str
    action: str
    params: Dict[str, Any] = Field(default_factory=dict)
    template_id: Optional[str] = None
    description: Optional[str] = None

class TaskResponse(BaseModel):
    id: str
    name: str
    action: str
    params: Dict[str, Any]
    status: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_seconds: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class JobCreate(BaseModel):
    name: str
    template_id: Optional[str] = None
    cron_expr: str  # "hour=9,minute=30" 或 "0 9 * * *"
    enabled: bool = True
    description: Optional[str] = None

class JobResponse(BaseModel):
    job_id: str
    name: str
    template_id: Optional[str]
    cron_expr: str
    enabled: bool
    last_run: Optional[str]
    next_run: Optional[str]
    description: Optional[str]

class MessageRequest(BaseModel):
    channel: str = "dingtalk"
    message: str
    template: Optional[str] = None

class NotifyRequest(BaseModel):
    channel: str  # dingtalk | feishu | telegram | wecom
    message: str
    template: Optional[str] = None

class KeyCreate(BaseModel):
    name: str
    level: str = "readonly"
    expires_days: Optional[int] = None
    description: str = ""

class ConfirmCreate(BaseModel):
    action: str
    resource_id: str
    channel: str = "dingtalk"
    extra: Dict[str, Any] = Field(default_factory=dict)

class ConfirmVerify(BaseModel):
    token: str

class TelegramUpdate(BaseModel):
    """Telegram Webhook Update（可选，用于类型提示）"""
    update_id: Optional[int] = None
    message: Optional[Dict] = None
    callback_query: Optional[Dict] = None

# ═══════════════════════════════════════════════════════════════════
# 定时任务执行函数
# ═══════════════════════════════════════════════════════════════════

def _run_scheduled_job(job_id: str, template_id: str):
    """APScheduler 回调：执行定时任务"""
    global _task_mgr, _db, _scheduler, _notify_mgr
    logger.info(f"[Scheduler] 触发定时任务 {job_id} (template={template_id})")

    task = None
    if _task_mgr:
        task = _task_mgr.create_task_from_template(template_id)
        if task:
            task.start()
            _db.save_task(task.to_dict()) if _db else None

    # 发送通知
    if _notify_mgr:
        try:
            _notify_mgr.send("dingtalk", f"🚀 定时任务触发：{job_id}", template="task_start")
        except Exception as e:
            logger.warning(f"通知发送失败: {e}")

    # 异步触发 OpenClaw Agent
    if template_id and _gateway_client:
        try:
            client = get_openclaw_client()
            result = client.spawn_agent(task=f"执行定时任务: {job_id}")
            if task:
                task.complete({"spawn_result": result, "scheduled": True})
                if _db:
                    _db.save_task(task.to_dict())
        except Exception as e:
            logger.error(f"定时任务执行失败: {e}")
            if task:
                task.fail(str(e))
                if _db:
                    _db.save_task(task.to_dict())

    if _scheduler:
        job = _scheduler.get_job(job_id)
        if job and _db:
            _db.save_scheduled_job({
                "job_id": job_id,
                "name": job.name,
                "template_id": template_id,
                "cron_expr": str(job.trigger),
                "enabled": True,
                "last_run": datetime.now().isoformat(),
                "next_run": _get_next_run(job),
            })


def _get_next_run(job) -> Optional[str]:
    try:
        next_t = job.next_run_time
        return next_t.isoformat() if next_t else None
    except Exception:
        return None


def _parse_cron(cron_expr: str) -> Dict[str, Any]:
    """解析简化的 cron 表达式为 APScheduler 参数"""
    parts = cron_expr.strip().replace("，", ",").split(",")
    kw = {}
    for p in parts:
        p = p.strip()
        if "=" in p:
            k, v = p.split("=", 1)
            kw[k.strip()] = v.strip()
        elif ":" in p:
            k, v = p.split(":", 1)
            kw[k.strip()] = v.strip()
    return kw


# ═══════════════════════════════════════════════════════════════════
# 应用生命周期
# ═══════════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _db, _task_mgr, _notify_mgr, _scheduler

    logger.info("🚀 启动 OpenClaw Control FastAPI v1.4.0...")

    # ─── 数据库初始化 ──────────────────────────────────────────
    try:
        _db = Database()
        logger.info("✅ SQLite 数据库初始化成功")
    except Exception as e:
        logger.warning(f"⚠️ 数据库初始化失败（服务以有限模式运行）: {e}")
        _db = None

    # ─── 任务管理器初始化 ────────────────────────────────────────
    _task_mgr = TaskManager(db=_db)
    _task_mgr.load_default_templates()
    if _db:
        _task_mgr.load_templates_from_db()
    logger.info(f"✅ 任务管理器就绪，已加载 {len(_task_mgr.list_templates())} 个模板")

    # ─── 通知管理器初始化 ────────────────────────────────────────
    _notify_mgr = NotifyManager()
    logger.info("✅ 通知管理器就绪")

    # ─── APScheduler 初始化 ─────────────────────────────────────
    _scheduler = AsyncIOScheduler(jobstores={"default": MemoryJobStore()})
    _scheduler.start()
    # 从数据库恢复定时任务
    if _db:
        for row in _db.load_scheduled_jobs(enabled_only=True):
            try:
                _scheduler.add_job(
                    id=row["job_id"],
                    name=row["name"],
                    func=_run_scheduled_job,
                    trigger=APSchedulerCronTrigger(**_parse_cron(row["cron_expr"])),
                    args=[row["job_id"], row.get("template_id", "")],
                    replace_existing=True,
                )
                logger.info(f"  ↳ 恢复定时任务: {row['job_id']} - {row['name']}")
            except Exception as e:
                logger.warning(f"  ↳ 恢复定时任务失败 {row['job_id']}: {e}")
    logger.info("✅ APScheduler 调度器已启动")

    # ─── v1.5.0 新增：确认 Token 管理器初始化 ─────────────────────
    global _confirm_mgr
    _confirm_mgr = ConfirmTokenManager(notify_manager=_notify_mgr)
    logger.info("✅ 确认 Token 管理器已初始化")

    # ─── v1.5.0 新增：OpenClaw 多实例管理器 ─────────────────────
    from core.instance_manager import init_instance_manager, get_instance_manager
    from core.webhook_manager import init_webhook_manager, get_webhook_manager
    from core.monitor import get_metrics_collector
    from fastapi_server.routers.instances import set_instance_manager
    from fastapi_server.routers.webhooks import set_webhook_manager
    from fastapi_server.routers.monitor import set_metrics_collector

    _instances = init_instance_manager()
    set_instance_manager(_instances)
    logger.info(f"✅ OpenClaw 实例管理器已初始化（{len(_instances.list_instances())} 个实例）")

    # ─── v1.5.0 新增：Webhook 回调管理器 ─────────────────────────
    _webhooks = init_webhook_manager()
    set_webhook_manager(_webhooks)
    logger.info("✅ Webhook 回调管理器已初始化")

    # ─── v1.5.0 新增：指标收集器（监控） ─────────────────────────
    _monitor = get_metrics_collector()
    set_metrics_collector(_monitor)
    logger.info("✅ 系统监控指标收集器已启动")

    # ─── v2.5.0 新增：NL 自然语言解析路由 ─────────────────────────
    set_nl_components(
        task_mgr=_task_mgr,
        notify_mgr=_notify_mgr,
        gateway_client=_gateway_client,
        auth_mgr=_auth_mgr,
        llm_api_key=os.getenv("GLM_API_KEY", ""),
    )
    logger.info(
        f"✅ NL 自然语言解析路由已注册 "
        f"(LLM增强: {'已启用' if os.getenv('GLM_API_KEY') else '未启用（规则模式）'})"
    )

    # ─── 模板热加载初始化 ────────────────────────────────────────
    global _template_watcher
    yaml_path = os.getenv("TEMPLATES_YAML", str(ROOT.parent / "templates.yaml"))
    if os.path.exists(yaml_path):
        _template_watcher = TemplateWatcher(
            task_manager=_task_mgr,
            yaml_path=yaml_path,
            check_interval=15.0,
        )
        _template_watcher.start()
        logger.info(f"✅ 模板热加载监控已启动: {yaml_path}")
    else:
        logger.info(f"⚠️ 模板文件不存在，跳过热加载: {yaml_path}")

    # ─── Telegram Bot 初始化 ────────────────────────────────────
    _init_telegram_bot()

    # ─── 初始化默认 API Keys ─────────────────────────────────────
    _init_default_keys()

    yield

    # ─── 关闭 ───────────────────────────────────────────────────
    logger.info("🛑 关闭服务...")
    if _telegram_bot:
        _telegram_bot.stop_polling()
        logger.info("  ↳ Telegram Bot 已停止")
    if _template_watcher:
        _template_watcher.stop()
        logger.info("  ↳ 模板监控已停止")
    if _scheduler:
        _scheduler.shutdown(wait=False)
    # v1.5.0 新增：关闭各管理器
    try:
        from core.instance_manager import get_instance_manager
        get_instance_manager().stop_health_check()
        logger.info("  ↳ 实例健康检查线程已停止")
    except Exception:
        pass
    try:
        from core.webhook_manager import get_webhook_manager
        get_webhook_manager().shutdown()
        logger.info("  ↳ Webhook 管理器已关闭")
    except Exception:
        pass
    try:
        from core.monitor import get_metrics_collector
        get_metrics_collector().stop()
        logger.info("  ↳ 监控收集器已停止")
    except Exception:
        pass
    logger.info("✅ 服务已关闭")


def _init_default_keys():
    """初始化默认 API Keys（生产环境应从配置文件读取）"""
    defaults = [
        ("admin", KeyLevel.ADMIN, "默认管理员 Key"),
        ("executor", KeyLevel.EXECUTE, "默认执行 Key"),
        ("readonly", KeyLevel.READONLY, "默认只读 Key"),
    ]
    for name, level, desc in defaults:
        existing = [k for k in _auth_mgr.list_keys() if k.get("name") == name]
        if not existing:
            key = _auth_mgr.generate_key(name=name, level=level, description=desc)
            logger.info(f"📌 默认 API Key [{name}]({level.value}): {key}")


def _init_telegram_bot():
    """初始化 Telegram Bot（如果配置了）"""
    global _telegram_bot

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not bot_token:
        logger.info("⚠️ TELEGRAM_BOT_TOKEN 未配置，Telegram Bot 未启用")
        return

    try:
        from handlers.telegram_bot import TelegramBot

        _telegram_bot = TelegramBot(
            bot_token=bot_token,
            default_chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
        )
        _telegram_bot.bind_components(
            task_mgr=_task_mgr,
            notify_mgr=_notify_mgr,
            client=_gateway_client,
            auth_mgr=_auth_mgr,
        )
        if _confirm_mgr:
            _telegram_bot._confirm_mgr = _confirm_mgr

        me = _telegram_bot.get_me()
        if me.get("ok"):
            bot_name = me.get("result", {}).get("username", "unknown")
            logger.info(f"✅ Telegram Bot 初始化成功: @{bot_name}")
        else:
            logger.warning(f"⚠️ Telegram Bot 初始化失败: {me}")

        _telegram_bot.register_commands()

        webhook_url = os.getenv("TELEGRAM_WEBHOOK_URL", "")
        if not webhook_url:
            asyncio.create_task(_telegram_bot.start_polling(interval=1.0))
            logger.info("  ↳ Polling 模式已启动（后台）")
        else:
            secret = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
            result = _telegram_bot.set_webhook(webhook_url, secret)
            logger.info(f"  ↳ Webhook 模式已配置: {webhook_url} → {result}")

    except Exception as e:
        logger.error(f"❌ Telegram Bot 初始化失败: {e}")
        _telegram_bot = None


# ═══════════════════════════════════════════════════════════════════
# FastAPI 应用
# ═══════════════════════════════════════════════════════════════════

WEB_ADMIN_DIR = ROOT / "web_admin"
STATIC_DIR = ROOT.parent / "static"

# ─── v1.5.0 新增：路由器注册 ───────────────────────────────────
from fastapi_server.routers.instances import router as instances_router
from fastapi_server.routers.webhooks import router as webhooks_router
from fastapi_server.routers.monitor import router as monitor_router

# ─── v2.5.0 新增：NL 自然语言解析路由 ──────────────────────────
from handlers.nl_routes import router as nl_router, set_components as set_nl_components

app = FastAPI(
    title="OpenClaw Control API",
    description="OpenClaw 跨设备控制服务 API v2.5.0 | 多实例管理 · Webhook回调 · 实时监控 · 自然语言控制",
    version="2.5.0",
    lifespan=lifespan,
)

# 注册路由（v1.5.0）
app.include_router(instances_router)
app.include_router(webhooks_router)
app.include_router(monitor_router)

# 注册路由（v2.5.0）：NL 自然语言解析
app.include_router(nl_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件（如果存在）
if WEB_ADMIN_DIR.exists():
    app.mount("/admin", StaticFiles(directory=str(WEB_ADMIN_DIR), html=True), name="web_admin")
    logger.info(f"✅ Web Admin 静态文件已挂载: {WEB_ADMIN_DIR}")

# ─── 首页重定向 ──────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def root():
    if WEB_ADMIN_DIR.exists():
        return RedirectResponse(url="/admin/", status_code=302)
    return {"message": "OpenClaw Control API v1.2.0", "docs": "/docs"}


# ═══════════════════════════════════════════════════════════════════
# 健康检查
# ═══════════════════════════════════════════════════════════════════

@app.get("/health", tags=["健康检查"])
async def health_check():
    gw_ok = False
    try:
        client = get_openclaw_client()
        client.get_status()
        gw_ok = True
    except Exception:
        pass

    stats = _db.get_stats() if _db else {}
    job_count = len(_scheduler.get_jobs()) if _scheduler else 0

    # v1.5.0 新增：实例+Webhook+监控状态
    try:
        from core.instance_manager import get_instance_manager
        inst_stats = get_instance_manager().get_stats()
    except Exception:
        inst_stats = {}
    try:
        from core.webhook_manager import get_webhook_manager
        wh_stats = get_webhook_manager().get_stats()
    except Exception:
        wh_stats = {}
    try:
        from core.monitor import get_metrics_collector
        current_metrics = get_metrics_collector().get_current()
    except Exception:
        current_metrics = {}

    return {
        "status": "healthy" if gw_ok else "degraded",
        "gateway": "connected" if gw_ok else "disconnected",
        "server_time": datetime.now().isoformat(),
        "version": "1.5.0",
        "stats": {
            **stats,
            "active_jobs": job_count,
        },
        # v1.5.0
        "instances": inst_stats,
        "webhooks": wh_stats,
        "metrics": current_metrics,
    }


# ═══════════════════════════════════════════════════════════════════
# Web Admin 登录 API（Session 模式，简化认证）
# ═══════════════════════════════════════════════════════════════════

@app.post("/api/v1/web-login", tags=["Web登录"], include_in_schema=False)
async def web_login(req: LoginRequest):
    """Web Admin 登录接口：通过 API Key 获取 Session Token"""
    key_obj = _auth_mgr.validate_key(req.api_key)
    if not key_obj or not key_obj.is_valid():
        raise HTTPException(status_code=401, detail="API Key 无效或已过期")

    token = _session_token()
    _web_sessions[token] = {
        "api_key": req.api_key,
        "key_obj": key_obj,
        "expires": datetime.now() + timedelta(hours=24),
        "key_id": key_obj.key_id,
        "key_name": key_obj.name,
        "level": key_obj.level.value,
    }

    logger.info(f"Web 登录成功: {key_obj.name} ({key_obj.level.value})")
    _auth_mgr.log_action("web_login", key_id=key_obj.key_id, detail=f"用户 {key_obj.name} Web 登录")

    return {
        "token": token,
        "key_name": key_obj.name,
        "level": key_obj.level.value,
        "expires_in": 86400,
    }


@app.post("/api/v1/web-logout", tags=["Web登录"], include_in_schema=False)
async def web_logout(token: str = Query(...)):
    session = _web_sessions.pop(token, None)
    if session:
        _auth_mgr.log_action("web_logout", key_id=session.get("key_id", ""), detail="Web 登出")
    return {"success": True}


# ═══════════════════════════════════════════════════════════════════
# 状态 API
# ═══════════════════════════════════════════════════════════════════

@app.get("/api/v1/status", tags=["状态"])
async def get_status(
    api_key: APIKey = Depends(_require_level(KeyLevel.READONLY)),
):
    stats = _db.get_stats() if _db else {}
    job_count = len(_scheduler.get_jobs()) if _scheduler else 0
    next_jobs = []
    if _scheduler:
        for job in _scheduler.get_jobs()[:5]:
            next_jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": _get_next_run(job),
            })

    gw_ok = False
    sessions = []
    try:
        client = get_openclaw_client()
        client.get_status()
        gw_ok = True
        sessions = client.get_sessions(active_only=True)
    except Exception:
        pass

    return {
        "gateway_connected": gw_ok,
        "server_time": datetime.now().isoformat(),
        "active_sessions": len(sessions),
        "queue_size": stats.get("running_tasks", 0),
        "stats": stats,
        "scheduler": {
            "active_jobs": job_count,
            "next_jobs": next_jobs,
        }
    }


# ═══════════════════════════════════════════════════════════════════
# 消息推送 API
# ═══════════════════════════════════════════════════════════════════

@app.post("/api/v1/notify", tags=["消息推送"])
async def send_notification(
    req: NotifyRequest,
    api_key: APIKey = Depends(_require_level(KeyLevel.EXECUTE)),
):
    """向指定渠道发送通知"""
    if not _notify_mgr:
        raise HTTPException(status_code=503, detail="通知管理器未初始化")

    result = _notify_mgr.send(req.channel, req.message)
    if not result.get("success", False):
        raise HTTPException(status_code=500, detail=result.get("error", "发送失败"))

    _auth_mgr.log_action("notify", key_id=api_key.key_id, detail=f"向 {req.channel} 发送消息")
    return {"success": True, "result": result}


@app.get("/api/v1/notify/channels", tags=["消息推送"])
async def list_channels(
    api_key: APIKey = Depends(_require_level(KeyLevel.READONLY)),
):
    """列出已配置的通知渠道"""
    channels = list(_notify_mgr.notifiers.keys()) if _notify_mgr else []
    return {"channels": channels}


class WeComSendRequest(BaseModel):
    msgtype: str = "text"  # text | markdown | news
    content: str
    mentioned_list: Optional[List[str]] = None
    mentioned_mobile_list: Optional[List[str]] = None


@app.post("/api/v1/notify/wecom", tags=["企业微信"])
async def send_wecom_notification(
    req: WeComSendRequest,
    api_key: APIKey = Depends(_require_level(KeyLevel.EXECUTE)),
):
    """
    向企业微信发送消息（原生接口）

    支持 msgtype:
    - text: 纯文本，mentioned_list / mentioned_mobile_list 可 @ 成员
    - markdown: Markdown 格式（支持加粗、代码、列表等）
    - news: 图文消息（content 字段传入 JSON 数组 articles）
    """
    import os, json as _json
    from notify.wecom import WeComNotifier as WCN

    webhook_url = os.getenv("WECOM_WEBHOOK_URL", "")
    if not webhook_url:
        raise HTTPException(status_code=503, detail="WECOM_WEBHOOK_URL 环境变量未配置")

    notifier = WCN(webhook_url=webhook_url)

    if req.msgtype == "markdown":
        result = notifier.send_markdown(req.content)
    elif req.msgtype == "news":
        try:
            articles = _json.loads(req.content) if isinstance(req.content, str) else req.content
        except Exception:
            raise HTTPException(status_code=400, detail="news 类型需传入 articles JSON 数组")
        result = notifier.send_news(articles)
    else:
        result = notifier.send_text(
            req.content,
            mentioned_list=req.mentioned_list,
            mentioned_mobile_list=req.mentioned_mobile_list,
        )

    if not result.get("success", False):
        raise HTTPException(status_code=500, detail=result.get("error", "发送失败"))

    _auth_mgr.log_action("notify", key_id=api_key.key_id, detail="向企业微信发送消息")
    return {"success": True, "result": result}


# ═══════════════════════════════════════════════════════════════════
# 任务 API
# ═══════════════════════════════════════════════════════════════════

@app.post("/api/v1/tasks", response_model=TaskResponse, tags=["任务"])
async def create_task(
    req: TaskCreate,
    api_key: APIKey = Depends(_require_level(KeyLevel.EXECUTE)),
):
    """创建新任务"""
    if not _task_mgr:
        raise HTTPException(status_code=503, detail="任务管理器未初始化")

    # 如果指定了模板，从模板创建
    if req.template_id:
        task = _task_mgr.create_task_from_template(req.template_id, overrides=req.params)
        if not task:
            raise HTTPException(status_code=404, detail=f"模板不存在: {req.template_id}")
    else:
        task = _task_mgr.create_task(
            name=req.name,
            action=req.action,
            params=req.params,
            description=req.description,
        )

    logger.info(f"任务创建: [{task.id}] {task.name}")
    _auth_mgr.log_action("task_create", key_id=api_key.key_id, detail=f"创建任务 {task.name}")
    return TaskResponse(**task.to_dict())


@app.get("/api/v1/tasks", tags=["任务"])
async def list_tasks(
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    api_key: APIKey = Depends(_require_level(KeyLevel.READONLY)),
):
    """列出任务历史"""
    if not _db:
        return {"tasks": [], "total": 0, "stats": {}}

    tasks = _db.load_tasks(status=status, limit=limit, offset=offset)
    total = _db.count_tasks(status=status)
    stats = _db.get_stats()

    return {"tasks": tasks, "total": total, "stats": stats}


@app.get("/api/v1/tasks/{task_id}", tags=["任务"])
async def get_task(
    task_id: str,
    api_key: APIKey = Depends(_require_level(KeyLevel.READONLY)),
):
    """获取单个任务详情"""
    if not _db:
        raise HTTPException(status_code=503, detail="数据库未初始化")

    task = _db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")
    return task


@app.delete("/api/v1/tasks/{task_id}", tags=["任务"])
async def cancel_task(
    task_id: str,
    api_key: APIKey = Depends(_require_level(KeyLevel.EXECUTE)),
):
    """取消任务"""
    if not _task_mgr:
        raise HTTPException(status_code=503, detail="任务管理器未初始化")

    ok = _task_mgr.cancel_task(task_id)
    if not ok:
        raise HTTPException(status_code=404, detail=f"任务不存在或无法取消: {task_id}")

    _auth_mgr.log_action("task_cancel", key_id=api_key.key_id, detail=f"取消任务 {task_id}")
    return {"success": True, "task_id": task_id}


# ═══════════════════════════════════════════════════════════════════
# 任务模板 API
# ═══════════════════════════════════════════════════════════════════

@app.get("/api/v1/templates", tags=["模板"])
async def list_templates(
    api_key: APIKey = Depends(_require_level(KeyLevel.READONLY)),
):
    """列出所有任务模板"""
    if not _task_mgr:
        return {"templates": []}
    templates = _task_mgr.list_templates()
    return {"templates": [t.to_dict() for t in templates]}


@app.post("/api/v1/templates", tags=["模板"])
async def create_template(
    name: str = Query(...),
    action: str = Query(...),
    template_id: str = Query(...),
    description: str = Query(""),
    params: str = Query("{}"),  # JSON string
    api_key: APIKey = Depends(_require_level(KeyLevel.EXECUTE)),
):
    """创建任务模板"""
    import json
    if not _task_mgr:
        raise HTTPException(status_code=503, detail="任务管理器未初始化")

    try:
        params_dict = json.loads(params)
    except Exception:
        raise HTTPException(status_code=400, detail="params 必须是有效的 JSON")

    from core.task import TaskTemplate
    tmpl = TaskTemplate(
        template_id=template_id,
        name=name,
        description=description,
        action=action,
        params=params_dict,
    )
    _task_mgr.register_template(tmpl)
    _auth_mgr.log_action("template_create", key_id=api_key.key_id, detail=f"创建模板 {name}")
    return {"success": True, "template": tmpl.to_dict()}


class TemplateUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    action: Optional[str] = None
    params: Optional[Dict[str, Any]] = None


@app.put("/api/v1/templates/{template_id}", tags=["模板"])
async def update_template(
    template_id: str,
    req: TemplateUpdateRequest,
    api_key: APIKey = Depends(_require_level(KeyLevel.EXECUTE)),
):
    """更新任务模板"""
    if not _task_mgr:
        raise HTTPException(status_code=503, detail="任务管理器未初始化")
    tmpl = _task_mgr.update_template(
        template_id=template_id,
        name=req.name,
        description=req.description,
        action=req.action,
        params=req.params,
    )
    if not tmpl:
        raise HTTPException(status_code=404, detail=f"模板不存在: {template_id}")
    _auth_mgr.log_action("template_update", key_id=api_key.key_id, detail=f"更新模板 {template_id}")
    return {"success": True, "template": tmpl.to_dict()}


@app.delete("/api/v1/templates/{template_id}", tags=["模板"])
async def delete_template(
    template_id: str,
    api_key: APIKey = Depends(_require_level(KeyLevel.ADMIN)),
):
    """删除任务模板"""
    if not _task_mgr:
        raise HTTPException(status_code=503, detail="任务管理器未初始化")
    ok = _task_mgr.delete_template(template_id)
    if not ok:
        raise HTTPException(status_code=404, detail=f"模板不存在: {template_id}")
    _auth_mgr.log_action("template_delete", key_id=api_key.key_id, detail=f"删除模板 {template_id}")
    return {"success": True}


# ═══════════════════════════════════════════════════════════════════
# 定时任务调度 API（APScheduler 集成）
# ═══════════════════════════════════════════════════════════════════

@app.get("/api/v1/scheduler/jobs", tags=["定时任务"])
async def list_jobs(
    api_key: APIKey = Depends(_require_level(KeyLevel.READONLY)),
):
    """列出所有定时任务"""
    if not _scheduler:
        return {"jobs": []}

    jobs = []
    for job in _scheduler.get_jobs():
        jobs.append({
            "job_id": job.id,
            "name": job.name,
            "cron_expr": str(job.trigger),
            "next_run": _get_next_run(job),
            "enabled": True,
        })

    # 合并数据库记录（包含未在内存中的任务）
    if _db:
        for row in _db.load_scheduled_jobs():
            if not any(j["job_id"] == row["job_id"] for j in jobs):
                jobs.append({
                    "job_id": row["job_id"],
                    "name": row["name"],
                    "cron_expr": row.get("cron_expr", ""),
                    "next_run": row.get("next_run"),
                    "enabled": bool(row.get("enabled", 1)),
                })

    return {"jobs": jobs, "total": len(jobs)}


@app.post("/api/v1/scheduler/jobs", tags=["定时任务"])
async def create_job(
    req: JobCreate,
    api_key: APIKey = Depends(_require_level(KeyLevel.EXECUTE)),
):
    """创建定时任务"""
    import uuid
    if not _scheduler:
        raise HTTPException(status_code=503, detail="调度器未初始化")
    if not req.template_id:
        raise HTTPException(status_code=400, detail="必须指定 template_id")

    job_id = f"job_{uuid.uuid4().hex[:8]}"
    try:
        cron_kwargs = _parse_cron(req.cron_expr)
        trigger = APSchedulerCronTrigger(**cron_kwargs)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cron 表达式解析失败: {e}")

    _scheduler.add_job(
        id=job_id,
        name=req.name,
        func=_run_scheduled_job,
        trigger=trigger,
        args=[job_id, req.template_id],
        replace_existing=True,
    )

    if _db:
        _db.save_scheduled_job({
            "job_id": job_id,
            "name": req.name,
            "template_id": req.template_id,
            "cron_expr": req.cron_expr,
            "enabled": 1 if req.enabled else 0,
            "next_run": _get_next_run(_scheduler.get_job(job_id)),
        })

    logger.info(f"定时任务创建: {job_id} - {req.name} ({req.cron_expr})")
    _auth_mgr.log_action("job_create", key_id=api_key.key_id, detail=f"创建定时任务 {req.name}")
    return {"success": True, "job_id": job_id}


@app.delete("/api/v1/scheduler/jobs/{job_id}", tags=["定时任务"])
async def delete_job(
    job_id: str,
    api_key: APIKey = Depends(_require_level(KeyLevel.EXECUTE)),
):
    """删除定时任务"""
    if not _scheduler:
        raise HTTPException(status_code=503, detail="调度器未初始化")

    try:
        _scheduler.remove_job(job_id)
    except Exception:
        pass  # 任务可能不在内存中

    if _db:
        _db.delete_scheduled_job(job_id)

    logger.info(f"定时任务删除: {job_id}")
    _auth_mgr.log_action("job_delete", key_id=api_key.key_id, detail=f"删除定时任务 {job_id}")
    return {"success": True, "job_id": job_id}


@app.post("/api/v1/scheduler/jobs/{job_id}/run", tags=["定时任务"])
async def run_job_now(
    job_id: str,
    api_key: APIKey = Depends(_require_level(KeyLevel.EXECUTE)),
):
    """立即执行定时任务（手动触发）"""
    if not _scheduler:
        raise HTTPException(status_code=503, detail="调度器未初始化")

    job = _scheduler.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"定时任务不存在: {job_id}")

    # 直接调用 job.func
    asyncio.create_task(asyncio.to_thread(job.func, *job.args))
    logger.info(f"手动触发定时任务: {job_id}")
    _auth_mgr.log_action("job_run", key_id=api_key.key_id, detail=f"手动触发 {job_id}")
    return {"success": True, "job_id": job_id}


@app.post("/api/v1/scheduler/jobs/{job_id}/toggle", tags=["定时任务"])
async def toggle_job(
    job_id: str,
    enabled: bool = Query(...),
    api_key: APIKey = Depends(_require_level(KeyLevel.EXECUTE)),
):
    """启用/禁用定时任务"""
    if not _scheduler:
        raise HTTPException(status_code=503, detail="调度器未初始化")

    job = _scheduler.get_job(job_id)
    if enabled and job is None:
        # 从数据库恢复
        if _db:
            rows = _db.load_scheduled_jobs()
            row = next((r for r in rows if r["job_id"] == job_id), None)
            if row:
                cron_kwargs = _parse_cron(row["cron_expr"])
                _scheduler.add_job(
                    id=job_id, name=row["name"], func=_run_scheduled_job,
                    trigger=APSchedulerCronTrigger(**cron_kwargs),
                    args=[job_id, row.get("template_id", "")],
                    replace_existing=True,
                )
    elif not enabled and job is not None:
        _scheduler.remove_job(job_id)

    if _db:
        for row in _db.load_scheduled_jobs():
            if row["job_id"] == job_id:
                row["enabled"] = 1 if enabled else 0
                _db.save_scheduled_job(row)
                break

    logger.info(f"定时任务 {job_id} {'启用' if enabled else '禁用'}")
    return {"success": True, "job_id": job_id, "enabled": enabled}


# ═══════════════════════════════════════════════════════════════════
# OpenClaw Gateway 代理 API
# ═══════════════════════════════════════════════════════════════════

@app.post("/api/v1/gateway/message", tags=["Gateway代理"])
async def gateway_send_message(
    channel: str = Query(...),
    message: str = Query(...),
    api_key: APIKey = Depends(_require_level(KeyLevel.EXECUTE)),
):
    """通过 OpenClaw Gateway 发送消息"""
    try:
        client = get_openclaw_client()
        result = client.send_message(channel=channel, message=message)
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/gateway/spawn", tags=["Gateway代理"])
async def gateway_spawn(
    task: str = Query(...),
    runtime: str = Query("subagent"),
    api_key: APIKey = Depends(_require_level(KeyLevel.EXECUTE)),
):
    """通过 OpenClaw Gateway 触发 Agent"""
    try:
        client = get_openclaw_client()
        result = client.spawn_agent(task=task, runtime=runtime)
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/gateway/sessions", tags=["Gateway代理"])
async def gateway_sessions(
    active_only: bool = Query(True),
    api_key: APIKey = Depends(_require_level(KeyLevel.READONLY)),
):
    """获取 OpenClaw 会话列表"""
    try:
        client = get_openclaw_client()
        sessions = client.get_sessions(active_only=active_only)
        return {"sessions": sessions, "total": len(sessions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/gateway/status", tags=["Gateway代理"])
async def gateway_status(
    api_key: APIKey = Depends(_require_level(KeyLevel.READONLY)),
):
    """获取 OpenClaw Gateway 状态"""
    try:
        client = get_openclaw_client()
        status = client.get_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════
# OpenClaw 配置热重载 API（v1.4.0 新增）
# ═══════════════════════════════════════════════════════════════════

@app.get("/api/v1/gateway/config", tags=["Gateway配置"])
async def gateway_config_get(
    api_key: APIKey = Depends(_require_level(KeyLevel.READONLY)),
):
    """获取 OpenClaw Gateway 当前配置（只读）"""
    try:
        client = get_openclaw_client()
        config = await client.config_get()
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ConfigPatchRequest(BaseModel):
    raw: Dict[str, Any]
    note: Optional[str] = ""


@app.patch("/api/v1/gateway/config", tags=["Gateway配置"])
async def gateway_config_patch(
    req: ConfigPatchRequest,
    api_key: APIKey = Depends(_require_level(KeyLevel.ADMIN)),
):
    """
    热重载 OpenClaw Gateway 配置（Admin 权限）

    注意：此操作会修改 Gateway 配置，请确认后再执行。
    不支持的字段变更需要重启 Gateway 生效。
    """
    try:
        client = get_openclaw_client()
        result = await client.config_patch(req.raw, note=req.note)
        _auth_mgr.log_action(
            "config_patch",
            key_id=api_key.key_id,
            detail=f"配置更新: {req.note or '手动更新'}"
        )
        # 通知
        if _notify_mgr:
            try:
                await _notify_mgr.send(
                    "dingtalk",
                    f"⚙️ Gateway 配置已更新\n操作者：{api_key.name}\n说明：{req.note or '无'}",
                )
            except Exception:
                pass
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════
# 认证 API
# ═══════════════════════════════════════════════════════════════════

@app.get("/api/v1/keys", tags=["认证"])
async def list_keys(
    api_key: APIKey = Depends(_require_level(KeyLevel.ADMIN)),
):
    """列出所有 API Keys（不包含明文）"""
    keys = _auth_mgr.list_keys()
    return {"keys": keys, "total": len(keys)}


@app.post("/api/v1/keys", tags=["认证"])
async def create_key(
    req: KeyCreate,
    api_key: APIKey = Depends(_require_level(KeyLevel.ADMIN)),
):
    """创建新的 API Key"""
    level = KeyLevel(req.level) if req.level in [e.value for e in KeyLevel] else KeyLevel.READONLY
    new_key = _auth_mgr.generate_key(
        name=req.name,
        level=level,
        expires_days=req.expires_days,
        description=req.description,
    )
    _auth_mgr.log_action("key_create", key_id=api_key.key_id, detail=f"创建 Key {req.name}")
    return {"key": new_key, "name": req.name, "level": req.level}


@app.delete("/api/v1/keys/{key_id}", tags=["认证"])
async def revoke_key(
    key_id: str,
    api_key: APIKey = Depends(_require_level(KeyLevel.ADMIN)),
):
    """撤销 API Key"""
    ok = _auth_mgr.revoke_key(key_id)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Key 不存在: {key_id}")
    _auth_mgr.log_action("key_revoke", key_id=api_key.key_id, detail=f"撤销 Key {key_id}")
    return {"success": True}


# ═══════════════════════════════════════════════════════════════════
# 审计日志 API
# ═══════════════════════════════════════════════════════════════════

@app.get("/api/v1/audit", tags=["审计"])
async def get_audit_log(
    limit: int = Query(100, ge=1, le=1000),
    action: Optional[str] = Query(None),
    api_key: APIKey = Depends(_require_level(KeyLevel.ADMIN)),
):
    """获取审计日志"""
    if not _db:
        logs = _auth_mgr.get_audit_log(limit)
        return {"logs": logs, "total": len(logs)}
    logs = _db.load_audit_logs(limit=limit, action=action)
    return {"logs": logs, "total": len(logs)}


# ═══════════════════════════════════════════════════════════════════
# 确认 Token API（v1.1.0 新增）
# ═══════════════════════════════════════════════════════════════════

@app.post("/api/v1/confirm/request", tags=["确认Token"])
async def request_confirm(
    req: ConfirmCreate,
    api_key: APIKey = Depends(_require_level(KeyLevel.EXECUTE)),
):
    """
    请求确认 Token（用于敏感操作二次确认）

    流程：创建 Token → Server 向指定渠道推送确认卡片 → 用户确认 → verify
    """
    global _confirm_mgr, _notify_mgr
    if not _confirm_mgr:
        raise HTTPException(status_code=503, detail="确认管理器未初始化")

    client_ip = "unknown"  # TODO: 从 request 获取
    token = _confirm_mgr.create_token(
        action=req.action,
        resource_id=req.resource_id,
        key_name=api_key.name,
        request_ip=client_ip,
        extra=req.extra,
    )

    # 发送确认卡片
    try:
        await _notify_mgr.send(req.channel, f"确认请求: {req.action} / {req.resource_id}")
    except Exception:
        pass  # 通知失败不影响 token 创建

    _auth_mgr.log_action("confirm_request", key_id=api_key.key_id,
                         detail=f"请求确认 {req.action}/{req.resource_id}")

    return {
        "success": True,
        "token": token.token,
        "expires_at": token.expires_at,
        "message": f"确认请求已发送到 {req.channel}，请在 {5} 分钟内确认",
    }


@app.post("/api/v1/confirm/verify", tags=["确认Token"])
async def verify_confirm(
    req: ConfirmVerify,
    api_key: APIKey = Depends(_require_level(KeyLevel.EXECUTE)),
):
    """验证并消费确认 Token"""
    global _confirm_mgr
    if not _confirm_mgr:
        raise HTTPException(status_code=503, detail="确认管理器未初始化")

    ok, token, err = _confirm_mgr.verify_and_consume(req.token)
    if not ok:
        raise HTTPException(status_code=400, detail=err)

    _auth_mgr.log_action("confirm_verify", key_id=api_key.key_id,
                         detail=f"确认 Token {req.token} 验证成功: {token.action}")

    return {
        "success": True,
        "action": token.action,
        "resource_id": token.resource_id,
        "extra": token.extra,
    }


@app.get("/api/v1/confirm/pending", tags=["确认Token"])
async def list_pending_confirms(
    action: Optional[str] = Query(None),
    api_key: APIKey = Depends(_require_level(KeyLevel.ADMIN)),
):
    """列出当前待确认的 Token（Admin）"""
    global _confirm_mgr
    if not _confirm_mgr:
        return {"pending": []}

    tokens = _confirm_mgr.get_pending(action=action)
    return {
        "pending": [
            {
                "token": t.token,
                "action": t.action,
                "resource_id": t.resource_id,
                "key_name": t.key_name,
                "expires_at": t.expires_at,
                "created_at": t.created_at,
            }
            for t in tokens
        ],
        "total": len(tokens),
    }


# ═══════════════════════════════════════════════════════════════════
# Telegram Bot Webhook 端点（v1.1.0 新增）
# ═══════════════════════════════════════════════════════════════════

@app.post("/api/v1/telegram/webhook", tags=["Telegram Bot"], include_in_schema=False)
async def telegram_webhook(request: Request):
    """
    Telegram Bot Webhook 入口

    当使用 Webhook 模式时，Telegram 服务器会 POST 更新到这个端点
    必须响应 200 OK（否则 Telegram 会重复推送）
    """
    global _telegram_bot
    if not _telegram_bot:
        return {"ok": False, "description": "Bot not configured"}

    try:
        body = await request.json()
        _telegram_bot.process_update(body)
    except Exception as e:
        logger.error(f"Telegram webhook 处理失败: {e}")

    # Telegram 要求立即返回 200
    return {"ok": True}


@app.get("/api/v1/telegram/status", tags=["Telegram Bot"])
async def telegram_status(
    api_key: APIKey = Depends(_require_level(KeyLevel.READONLY)),
):
    """查看 Telegram Bot 状态"""
    global _telegram_bot
    if not _telegram_bot:
        return {
            "enabled": False,
            "mode": None,
            "message": "TELEGRAM_BOT_TOKEN 未配置",
        }

    me = _telegram_bot.get_me()
    bot_info = me.get("result", {}) if me.get("ok") else {}
    return {
        "enabled": True,
        "username": bot_info.get("username", ""),
        "first_name": bot_info.get("first_name", ""),
        "mode": "webhook" if os.getenv("TELEGRAM_WEBHOOK_URL") else "polling",
        "default_chat_id": _telegram_bot.default_chat_id,
    }


@app.post("/api/v1/telegram/send", tags=["Telegram Bot"])
async def telegram_send_message(
    message: str = Query(...),
    chat_id: Optional[str] = Query(None),
    api_key: APIKey = Depends(_require_level(KeyLevel.EXECUTE)),
):
    """通过 Telegram Bot 发送消息"""
    global _telegram_bot
    if not _telegram_bot:
        raise HTTPException(status_code=503, detail="Telegram Bot 未启用")

    result = _telegram_bot.send_message(text=message, chat_id=chat_id)
    if not result.get("ok"):
        raise HTTPException(status_code=500, detail=result.get("description", "发送失败"))

    _auth_mgr.log_action("telegram_send", key_id=api_key.key_id, detail=f"TG 消息: {message[:50]}")
    return {"success": True, "message_id": result.get("result", {}).get("message_id")}


# ═══════════════════════════════════════════════════════════════════
# 模板热加载 API（v1.1.0 新增）
# ═══════════════════════════════════════════════════════════════════

@app.post("/api/v1/templates/reload", tags=["模板"])
async def reload_templates(
    api_key: APIKey = Depends(_require_level(KeyLevel.ADMIN)),
):
    """手动触发模板热加载（Admin）"""
    global _template_watcher
    if not _template_watcher:
        raise HTTPException(status_code=503, detail="热加载未启用（templates.yaml 不存在）")

    success, failed = _template_watcher.load()
    _auth_mgr.log_action("template_reload", key_id=api_key.key_id,
                         detail=f"热加载: {success} 成功, {failed} 失败")
    return {"success": True, "loaded": success, "failed": failed}


# ═══════════════════════════════════════════════════════════════════
# 入口
# ═══════════════════════════════════════════════════════════════════

def run_server(host: str = "0.0.0.0", port: int = 8081, reload: bool = False):
    uvicorn.run(
        "fastapi_server.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="OpenClaw Control FastAPI Server v1.2.0")
    parser.add_argument("--host", default="0.0.0.0", help="监听地址")
    parser.add_argument("--port", type=int, default=8081, help="监听端口")
    parser.add_argument("--reload", action="store_true", help="开发模式（代码热重载）")
    args = parser.parse_args()
    run_server(host=args.host, port=args.port, reload=args.reload)
