#!/usr/bin/env python3
"""
HTTP API Handler - Flask 实现
RESTful API: /api/v1/*
"""

import logging
from flask import Flask, request, jsonify, g

from ..core.client import OpenClawClient
from ..core.task import Task, TaskManager, TaskStatus
from ..core.auth import AuthManager, KeyLevel
from ..core.database import TaskDatabase
from .sse_handler import SseManager, EventType

# Lazy import to avoid circular dependency
_nl_interpreter = None

def _get_nl():
    global _nl_interpreter
    if _nl_interpreter is None:
        try:
            from ..core.nl_interpreter import NLInterpreter
            _nl_interpreter = NLInterpreter()
        except ImportError:
            _nl_interpreter = None
    return _nl_interpreter

logger = logging.getLogger(__name__)

# 预定义快捷触发器
QUICK_TRIGGERS = {
    "quick-report":   {"action": "spawn", "params": {"task": "生成今日 AI 资讯简报", "runtime": "subagent"}},
    "tech-analyst":   {"action": "spawn", "params": {"task": "执行技术前沿分析", "runtime": "subagent"}},
    "market-insight": {"action": "spawn", "params": {"task": "分析 AI 商业机会", "runtime": "subagent"}},
    "full-scan":      {"action": "spawn", "params": {"task": "执行全量信息抓取", "runtime": "subagent"}},
}


def create_app(
    client: OpenClawClient,
    task_manager: TaskManager,
    auth_manager: AuthManager,
    scheduler=None,
    template_loader=None,
    db: TaskDatabase = None,
    sse_manager: SseManager = None,
) -> Flask:
    app = Flask(__name__)

    @app.before_request
    def inject_globals():
        g.client = client
        g.task_mgr = task_manager
        g.auth_mgr = auth_manager
        g.scheduler = scheduler
        g.tpl_loader = template_loader
        g.db = db
        g.sse = sse_manager

    def require_auth(level: KeyLevel = KeyLevel.READ):
        def decorator(f):
            def wrapper(*args, **kwargs):
                auth = request.headers.get("Authorization", "")
                if not auth.startswith("Bearer "):
                    return jsonify({"error": "缺少认证信息"}), 401
                api_key = auth_manager.authenticate(auth[7:], level)
                if not api_key:
                    return jsonify({"error": "认证失败或权限不足"}), 403
                g.api_key = api_key
                auth_manager.audit(api_key.id, request.method, request.path, request.remote_addr, "ok")
                if g.db:
                    g.db.log_audit(api_key.id, request.method, request.path, request.remote_addr, "ok")
                return f(*args, **kwargs)
            wrapper.__name__ = f.__name__
            return wrapper
        return decorator

    # ── 公开接口 ────────────────────────────────────────────────

    @app.route("/api/v1/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "service": "clawctl", "version": "1.0.0"})

    # ── 状态查询 (Read) ─────────────────────────────────────────

    @app.route("/api/v1/status", methods=["GET"])
    @require_auth(KeyLevel.READ)
    def status():
        claw_status = client.get_status()
        all_tasks = task_manager.list()
        return jsonify({
            "clawctl": "running",
            "openclaw_connected": claw_status.success,
            "tasks": {
                "total": len(all_tasks),
                "running": sum(1 for t in all_tasks if t.status == TaskStatus.RUNNING),
                "queued": sum(1 for t in all_tasks if t.status == TaskStatus.QUEUED),
                "success": sum(1 for t in all_tasks if t.status == TaskStatus.SUCCESS),
                "failed": sum(1 for t in all_tasks if t.status == TaskStatus.FAILED),
            },
        })

    @app.route("/api/v1/tasks", methods=["GET"])
    @require_auth(KeyLevel.READ)
    def list_tasks():
        status_str = request.args.get("status")
        status = TaskStatus(status_str) if status_str else None
        limit = int(request.args.get("limit", 50))
        tasks = task_manager.list(status=status, limit=limit)
        return jsonify({"tasks": [t.to_dict() for t in tasks]})

    @app.route("/api/v1/tasks/<task_id>", methods=["GET"])
    @require_auth(KeyLevel.READ)
    def get_task(task_id):
        task = task_manager.get(task_id)
        if not task:
            return jsonify({"error": "任务不存在"}), 404
        return jsonify(task.to_dict())

    @app.route("/api/v1/sessions", methods=["GET"])
    @require_auth(KeyLevel.READ)
    def list_sessions():
        resp = client.get_sessions()
        return jsonify({"success": resp.success, "data": resp.data or []})

    # ── 任务执行 (Exec) ─────────────────────────────────────────

    @app.route("/api/v1/tasks", methods=["POST"])
    @require_auth(KeyLevel.EXEC)
    def create_task():
        body = request.get_json() or {}
        task = Task(
            name=body.get("name", "unnamed"),
            action=body.get("action", "spawn"),
            params=body.get("params", {}),
            notify=body.get("notify", True),
            notify_channel=body.get("notify_channel", "dingtalk"),
        )
        task_manager.submit(task)
        task_manager.execute_async(task)

        # 持久化到 SQLite
        if g.db:
            from ..core.database import TaskRecord
            import json as _json
            record = TaskRecord(
                id=task.id, name=task.name, action=task.action,
                params=_json.dumps(task.params, ensure_ascii=False),
                status=task.status.value, priority=task.priority.name,
                notify=task.notify, notify_channel=task.notify_channel,
                result=None, error=None,
                created_at=task.created_at.isoformat(),
                started_at=None, completed_at=None, duration_ms=None,
                api_key_id=g.api_key.id if g.api_key else None,
                source_ip=request.remote_addr,
            )
            g.db.save_task(record)
        return jsonify(task.to_dict()), 201

    @app.route("/api/v1/trigger/<name>", methods=["POST"])
    @require_auth(KeyLevel.EXEC)
    def trigger_template(name):
        if name not in QUICK_TRIGGERS:
            return jsonify({"error": f"未知模板: {name}", "available": list(QUICK_TRIGGERS.keys())}), 404
        cfg = QUICK_TRIGGERS[name]
        task = Task(name=name, action=cfg["action"], params=cfg["params"])
        task_manager.submit(task)
        task_manager.execute_async(task)
        return jsonify(task.to_dict()), 201

    @app.route("/api/v1/send", methods=["POST"])
    @require_auth(KeyLevel.EXEC)
    def send_message():
        body = request.get_json() or {}
        resp = client.send_message(
            channel=body.get("channel", "dingtalk"),
            message=body.get("message", ""),
        )
        return jsonify({"success": resp.success, "error": resp.error})

    # ── 管理接口 (Admin) ────────────────────────────────────────

    @app.route("/api/v1/tasks/<task_id>", methods=["DELETE"])
    @require_auth(KeyLevel.ADMIN)
    def delete_task(task_id):
        ok = task_manager.cancel(task_id)
        if not ok:
            return jsonify({"error": "无法取消任务（可能已执行或不存在）"}), 400
        return jsonify({"ok": True})

    # ── Webhook 入口 ────────────────────────────────────────────

    @app.route("/api/v1/webhook", methods=["POST"])
    def webhook():
        if auth_manager._webhook_secret:
            sig = request.headers.get("X-Signature", "")
            if not auth_manager.verify_webhook_signature(request.data, sig):
                return jsonify({"error": "签名验证失败"}), 401
        body = request.get_json() or {}
        # 兼容钉钉格式
        msg = body.get("text", {}).get("content", "") or body.get("message", "")
        task = Task(name=f"webhook:{msg[:60]}", action="spawn", params={"task": msg or "处理 webhook 事件"})
        task_manager.submit(task)
        task_manager.execute_async(task)
        return jsonify({"ok": True, "task_id": task.id})

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "未找到"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "服务器内部错误"}), 500

    # ── 任务模板 API ────────────────────────────────────────────

    @app.route("/api/v1/templates", methods=["GET"])
    @require_auth(KeyLevel.READ)
    def list_templates():
        if g.tpl_loader:
            pattern = request.args.get("q", "")
            return jsonify({"templates": g.tpl_loader.list(pattern)})
        # 降级：使用内置 QUICK_TRIGGERS
        return jsonify({"templates": QUICK_TRIGGERS})

    @app.route("/api/v1/templates/<name>", methods=["GET"])
    @require_auth(KeyLevel.READ)
    def get_template(name):
        if g.tpl_loader:
            tpl = g.tpl_loader.get(name)
            if tpl:
                return jsonify(tpl)
        tpl = QUICK_TRIGGERS.get(name)
        if tpl:
            return jsonify(tpl)
        return jsonify({"error": "模板不存在"}), 404

    @app.route("/api/v1/templates/reload", methods=["POST"])
    @require_auth(KeyLevel.ADMIN)
    def reload_templates():
        if g.tpl_loader:
            g.tpl_loader.reload()
            return jsonify({"ok": True, "count": len(g.tpl_loader.list())})
        return jsonify({"error": "模板加载器未启用"}), 400

    @app.route("/api/v1/templates/<name>/execute", methods=["POST"])
    @require_auth(KeyLevel.EXEC)
    def execute_template(name):
        body = request.get_json() or {}
        if g.tpl_loader:
            tpl_cfg = g.tpl_loader.render_task(name, body.get("params"))
            if not tpl_cfg:
                return jsonify({"error": f"模板不存在: {name}"}), 404
            task = Task(
                name=body.get("name", name),
                action=tpl_cfg.get("action", "spawn"),
                params=tpl_cfg.get("params", {}),
                notify=tpl_cfg.get("notify", {}).get("on_start", True),
                notify_channel=body.get("notify_channel", "dingtalk"),
            )
        else:
            cfg = QUICK_TRIGGERS.get(name, {})
            if not cfg:
                return jsonify({"error": f"模板不存在: {name}"}), 404
            task = Task(
                name=name,
                action=cfg.get("action", "spawn"),
                params=cfg.get("params", {}),
            )
        g.task_mgr.submit(task)
        g.task_mgr.execute_async(task)
        return jsonify(task.to_dict()), 201

    # ── 定时任务 API ────────────────────────────────────────────

    @app.route("/api/v1/schedules", methods=["GET"])
    @require_auth(KeyLevel.READ)
    def list_schedules():
        if not g.scheduler:
            return jsonify({"error": "调度器未启用", "schedules": []})
        return jsonify({"schedules": g.scheduler.list_jobs()})

    @app.route("/api/v1/schedules", methods=["POST"])
    @require_auth(KeyLevel.EXEC)
    def create_schedule():
        if not g.scheduler:
            return jsonify({"error": "调度器未启用"}), 400
        body = request.get_json() or {}
        required = ["name", "template_id", "cron"]
        for f in required:
            if f not in body:
                return jsonify({"error": f"缺少必需字段: {f}"}), 400
        try:
            job = g.scheduler.add_job(
                name=body["name"],
                cron_expr=body["cron"],
                template_id=body["template_id"],
                timezone=body.get("timezone", "Asia/Shanghai"),
                enabled=body.get("enabled", True),
                notify_on_complete=body.get("notify", {}).get("on_complete", True),
                notify_channel=body.get("notify", {}).get("channel", "dingtalk"),
                params=body.get("params", {}),
            )
            return jsonify(job.to_dict()), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @app.route("/api/v1/schedules/<job_id>", methods=["GET"])
    @require_auth(KeyLevel.READ)
    def get_schedule(job_id):
        if not g.scheduler:
            return jsonify({"error": "调度器未启用"}), 400
        job = g.scheduler.get_job(job_id)
        if not job:
            return jsonify({"error": "定时任务不存在"}), 404
        return jsonify(job.to_dict())

    @app.route("/api/v1/schedules/<job_id>", methods=["PATCH"])
    @require_auth(KeyLevel.EXEC)
    def update_schedule(job_id):
        if not g.scheduler:
            return jsonify({"error": "调度器未启用"}), 400
        body = request.get_json() or {}
        job = g.scheduler.get_job(job_id)
        if not job:
            return jsonify({"error": "定时任务不存在"}), 404
        if "enabled" in body:
            if body["enabled"]:
                g.scheduler.resume_job(job_id)
            else:
                g.scheduler.pause_job(job_id)
        return jsonify(g.scheduler.get_job(job_id).to_dict())

    @app.route("/api/v1/schedules/<job_id>", methods=["DELETE"])
    @require_auth(KeyLevel.ADMIN)
    def delete_schedule(job_id):
        if not g.scheduler:
            return jsonify({"error": "调度器未启用"}), 400
        ok = g.scheduler.remove_job(job_id)
        if not ok:
            return jsonify({"error": "删除失败"}), 400
        return jsonify({"ok": True})

    @app.route("/api/v1/schedules/<job_id>/trigger", methods=["POST"])
    @require_auth(KeyLevel.EXEC)
    def trigger_schedule_now(job_id):
        if not g.scheduler:
            return jsonify({"error": "调度器未启用"}), 400
        jid = g.scheduler.trigger_now(job_id)
        if not jid:
            return jsonify({"error": "定时任务不存在"}), 404
        return jsonify({"ok": True, "job_id": jid})


    # ═══════════════════════════════════════════════════════════════
    #  SQLite 历史数据 API（v1.4 新增）
    # ═══════════════════════════════════════════════════════════════

    @app.route("/api/v1/history", methods=["GET"])
    @require_auth(KeyLevel.READ)
    def task_history():
        """任务历史查询（来自 SQLite 持久化）"""
        if not g.db:
            return jsonify({"error": "数据库未启用"}), 400
        status_str = request.args.get("status")
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))
        since = request.args.get("since")   # ISO datetime
        records = g.db.list_tasks(status=status_str, limit=limit, offset=offset, since=since)
        return jsonify({
            "tasks": [r.to_dict() for r in records],
            "total": g.db.count_tasks(status=status_str, since=since),
        })

    @app.route("/api/v1/history/<task_id>", methods=["GET"])
    @require_auth(KeyLevel.READ)
    def history_detail(task_id):
        """任务历史详情"""
        if not g.db:
            return jsonify({"error": "数据库未启用"}), 400
        record = g.db.get_task(task_id)
        if not record:
            return jsonify({"error": "任务不存在"}), 404
        return jsonify(record.to_dict())

    @app.route("/api/v1/stats", methods=["GET"])
    @require_auth(KeyLevel.READ)
    def task_stats():
        """任务统计报表"""
        if not g.db:
            return jsonify({"error": "数据库未启用"}), 400
        days = int(request.args.get("days", 7))
        return jsonify(g.db.stats(days=min(days, 90)))

    @app.route("/api/v1/audit", methods=["GET"])
    @require_auth(KeyLevel.ADMIN)
    def audit_log():
        """审计日志查询（Admin 权限）"""
        if not g.db:
            return jsonify({"error": "数据库未启用"}), 400
        limit = int(request.args.get("limit", 100))
        key_id = request.args.get("api_key_id")
        records = g.db.list_audit(limit=limit, api_key_id=key_id)
        return jsonify({"records": [vars(r) for r in records]})

    @app.route("/api/v1/history/cleanup", methods=["DELETE"])
    @require_auth(KeyLevel.ADMIN)
    def cleanup_history():
        """清理过期任务历史（Admin 权限）"""
        if not g.db:
            return jsonify({"error": "数据库未启用"}), 400
        days = int(request.args.get("days", 30))
        deleted = g.db.delete_old_tasks(days=days)
        return jsonify({"deleted": deleted, "ok": True})

    @app.route("/api/v1/history/export", methods=["GET"])
    @require_auth(KeyLevel.READ)
    def export_history():
        """导出任务历史（JSON，可用于备份）"""
        if not g.db:
            return jsonify({"error": "数据库未启用"}), 400
        import json as _json
        records = g.db.list_tasks(limit=10000)
        return jsonify({
            "exported_at": __import__("datetime").datetime.now().isoformat(),
            "count": len(records),
            "tasks": [r.to_dict() for r in records],
        })

    # ═══════════════════════════════════════════════════════════════
    #  SSE 事件流状态 API
    # ═══════════════════════════════════════════════════════════════

    @app.route("/api/v1/events/count", methods=["GET"])
    @require_auth(KeyLevel.READ)
    def events_count():
        """当前 SSE 连接数"""
        if not g.sse:
            return jsonify({"connected": 0})
        return jsonify({"connected": g.sse.client_count()})

    # ═══════════════════════════════════════════════════════════════
    #  自然语言解析 API（v2.0.0 新增）
    # ═══════════════════════════════════════════════════════════════

    @app.route("/api/v1/nl/parse", methods=["POST"])
    @require_auth(KeyLevel.EXEC)
    def nl_parse():
        """
        自然语言 → 任务计划
        POST /api/v1/nl/parse
        Body: {"text": "帮我生成今日技术简报"}
        Returns: TaskPlan JSON（含 intent / confidence / params）
        """
        body = request.get_json() or {}
        text = body.get("text", "").strip()
        if not text:
            return jsonify({"error": "text 字段不能为空"}), 400

        nl = _get_nl()
        if not nl:
            return jsonify({"error": "NLInterpreter 未安装，请检查依赖"}), 500

        plan = nl.parse(text)
        return jsonify(plan.to_dict())

    @app.route("/api/v1/nl/execute", methods=["POST"])
    @require_auth(KeyLevel.EXEC)
    def nl_execute():
        """
        自然语言 → 解析 → 直接执行（一步到位）
        POST /api/v1/nl/execute
        Body: {"text": "帮我生成今日技术简报"}
        Returns: 任务对象
        """
        body = request.get_json() or {}
        text = body.get("text", "").strip()
        if not text:
            return jsonify({"error": "text 字段不能为空"}), 400

        nl = _get_nl()
        if not nl:
            return jsonify({"error": "NLInterpreter 未安装"}), 500

        plan = nl.parse(text)
        plan_dict = plan.to_dict()

        # 特殊 Intent 直接处理
        if plan.intent.value == "help":
            return jsonify({
                "type": "help",
                "reference": nl.get_command_reference(),
                "plan": plan_dict,
            })

        if plan.intent.value == "status_query":
            # 状态查询：直接调 client 返回
            claw_status = g.client.get_status()
            all_tasks = g.task_mgr.list()
            return jsonify({
                "type": "status_query",
                "result": {
                    "openclaw_connected": claw_status.success,
                    "tasks": {
                        "running": sum(1 for t in all_tasks if t.status == TaskStatus.RUNNING),
                        "queued": sum(1 for t in all_tasks if t.status == TaskStatus.QUEUED),
                        "success": sum(1 for t in all_tasks if t.status == TaskStatus.SUCCESS),
                        "failed": sum(1 for t in all_tasks if t.status == TaskStatus.FAILED),
                    },
                },
                "plan": plan_dict,
            })

        # 构建并提交任务
        params = plan.to_execute_params()
        task = Task(
            name=f"nl:{plan.intent.value}",
            action="spawn",
            params=params,
            notify=body.get("notify", True),
            notify_channel=body.get("notify_channel", "dingtalk"),
        )
        g.task_mgr.submit(task)
        g.task_mgr.execute_async(task)

        # SSE 广播
        if g.sse:
            g.sse.broadcast(
                event=EventType.TASK_UPDATE,
                data={
                    "task_id": task.id,
                    "intent": plan.intent.value,
                    "original_text": text,
                    "status": task.status.value,
                },
            )

        return jsonify({
            "type": "task_executed",
            "task_id": task.id,
            "intent": plan.intent.value,
            "confidence": plan.confidence,
            "description": plan.description,
            "estimated_time": plan.estimated_time,
            "suggestions": plan.suggestions,
            "params": params,
        }), 201

    @app.route("/api/v1/nl/reference", methods=["GET"])
    @require_auth(KeyLevel.READ)
    def nl_reference():
        """获取自然语言命令参考（帮助信息）"""
        nl = _get_nl()
        if not nl:
            return jsonify({"error": "NLInterpreter 未安装"}), 500
        return jsonify(nl.get_command_reference())

    @app.route("/api/v1/nl/stats", methods=["GET"])
    @require_auth(KeyLevel.READ)
    def nl_stats():
        """解析统计（调试）"""
        nl = _get_nl()
        if not nl:
            return jsonify({})
        return jsonify(nl.stats())

    return app
