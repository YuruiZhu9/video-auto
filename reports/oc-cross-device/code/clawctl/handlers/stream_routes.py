#!/usr/bin/env python3
"""
Stream Routes - Flask 流式 API
提供流式任务执行端点 + SSE 订阅
"""

import json
import logging
import time
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from flask import (
    Response, request, stream_with_context,
    jsonify, g, current_app,
)
from ..core.stream_manager import get_stream_manager, StreamLevel
from ..core.task import Task, TaskStatus
from ..core.auth import KeyLevel

logger = logging.getLogger(__name__)

_executor = ThreadPoolExecutor(max_workers=4)


def require_auth(level: KeyLevel = KeyLevel.READ):
    """权限装饰器（复制自 http_handler）"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            auth = request.headers.get("Authorization", "")
            if not auth.startswith("Bearer "):
                return jsonify({"error": "缺少认证信息"}), 401
            api_key = g.auth_mgr.authenticate(auth[7:], level)
            if not api_key:
                return jsonify({"error": "认证失败或权限不足"}), 403
            g.api_key = api_key
            g.auth_mgr.audit(api_key.id, request.method, request.path, request.remote_addr, "ok")
            if g.db:
                g.db.log_audit(api_key.id, request.method, request.path, request.remote_addr, "ok")
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator


def _build_stream_blueprint(
    client, task_manager, auth_manager,
    db=None, notify_mgr=None, stream_mgr=None,
):
    """构建流式路由 Blueprint"""
    from flask import Blueprint
    bp = Blueprint("stream", __name__, url_prefix="/api/v1/stream")

    def _get_stream():
        return stream_mgr or get_stream_manager()

    def _get_notify():
        return notify_mgr

    # ── SSE 订阅端点 ────────────────────────────────────────────────────────

    @bp.route("/subscribe/<task_id>", methods=["GET"])
    def sse_subscribe(task_id):
        """
        SSE 流订阅 — 订阅指定任务的实时输出
        支持查询参数 all=1 订阅所有活动流
        """
        # auth optional for SSE (token in query param)
        auth_header = request.headers.get("Authorization", "")
        token = request.args.get("token", "")
        effective_token = auth_header[7:] if auth_header.startswith("Bearer ") else token

        if effective_token:
            key = auth_manager.authenticate(effective_token, KeyLevel.READ)
            if not key:
                return jsonify({"error": "认证失败"}), 403
            if db:
                db.log_audit(key.id, "GET", f"/stream/subscribe/{task_id}", request.remote_addr, "ok")

        def generate():
            sm = _get_stream()

            if task_id == "all":
                # 订阅所有活跃流
                active = sm.get_active_streams()
                yield f"event: stream_list\ndata: {json.dumps({'streams': active}, ensure_ascii=False)}\n\n"

                # 持续发送活跃流列表
                while True:
                    time.sleep(5)
                    try:
                        active = sm.get_active_streams()
                        yield f"event: heartbeat\ndata: {json.dumps({'active_streams': len(active)}, ensure_ascii=False)}\n\n"
                    except GeneratorExit:
                        break
            else:
                # 订阅单个任务流
                def on_disconnect():
                    sm.unsubscribe(task_id, None)  # cleanup if needed

                # 先发送 start 事件
                info = sm.get_stream(task_id)
                if info:
                    yield f"event: stream_start\ndata: {json.dumps(info, ensure_ascii=False)}\n\n"

                # 保持连接，定期发送心跳
                while True:
                    time.sleep(25)
                    try:
                        info = sm.get_stream(task_id)
                        if not info or info.get("status") != "running":
                            break
                        yield f"event: heartbeat\ndata: {json.dumps({'task_id': task_id, 'status': 'alive'}, ensure_ascii=False)}\n\n"
                    except GeneratorExit:
                        break

        resp = Response(
            stream_with_context(generate()),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Nginx SSE fix
            },
        )
        return resp

    # ── 流式执行 ──────────────────────────────────────────────────────────

    @bp.route("/execute", methods=["POST"])
    @require_auth(KeyLevel.EXECUTE)
    def stream_execute():
        """
        启动流式任务执行
        与普通 execute 不同，这里返回 stream_id 并在后台流式推送输出
        """
        data = request.get_json() or {}
        action = data.get("action", "spawn")
        params = data.get("params", {})
        task_name = data.get("name", "流式任务")
        agent = params.get("agent", params.get("runtime", "tech-analyst"))

        # 1. 创建任务
        task = Task(
            name=task_name,
            action=action,
            params=params,
            priority=Task.Priority.NORMAL,
            notify=data.get("notify", True),
            notify_channel=data.get("notify_channel"),
        )
        task_manager.add(task)

        # 2. 启动流
        sm = _get_stream()
        stream_id = sm.start_stream(task_id=task.id, agent_name=agent)

        # 3. 推送开始事件
        sm.push(task_id=task.id, content=f"🚀 任务已启动：{task_name}", level="section")
        sm.push(task_id=task.id, content=f"执行者：{agent} | 开始时间：{datetime.now().strftime('%H:%M:%S')}", level="info")

        # 4. 后台异步执行任务（不阻塞 HTTP 响应）
        def _execute_in_background():
            try:
                sm.push_progress(task_id=task.id, progress=5, message="正在初始化执行环境...")
                task_manager.execute(task.id)

                # 监控任务状态，流式推送更新
                max_wait = 300  # 最多等 5 分钟
                elapsed = 0
                while elapsed < max_wait:
                    time.sleep(2)
                    elapsed += 2
                    t = task_manager.get(task.id)
                    if not t:
                        sm.end(task_id=task.id, error="任务丢失", status="failed")
                        break
                    if t.status == TaskStatus.RUNNING:
                        pct = min(95, 5 + int(elapsed / max_wait * 85))
                        sm.push_progress(task_id=task.id, progress=pct, message=f"执行中... ({elapsed}s)")
                    elif t.status == TaskStatus.SUCCESS:
                        sm.push_progress(task_id=task.id, progress=100, message="执行完成")
                        result_preview = str(t.result)[:500] if t.result else "完成"
                        sm.push(task_id=task.id, content=f"\n✅ 任务完成 | 耗时: {t.duration_ms() or elapsed * 1000}ms", level="success")
                        if t.result:
                            sm.push_result(task_id=task.id, result=t.result)
                        sm.end(task_id=task.id, result=t.result, status="completed")
                        # 通知
                        nm = _get_notify()
                        if nm and task.notify:
                            nm.send_task_complete(task.name, t.duration_ms() or 0, result_preview, channel=task.notify_channel)
                        break
                    elif t.status == TaskStatus.FAILED:
                        sm.push(task_id=task.id, content=f"\n❌ 任务失败: {t.error}", level="error")
                        sm.end(task_id=task.id, error=t.error, status="failed")
                        nm = _get_notify()
                        if nm and task.notify:
                            nm.send_alert("任务失败", f"{task.name}: {t.error}", channel=task.notify_channel)
                        break
            except Exception as e:
                logger.exception(f"[StreamManager] 后台执行异常 task={task.id}")
                sm.end(task_id=task.id, error=str(e), status="failed")

        _executor.submit(_execute_in_background)

        return jsonify({
            "type": "stream_started",
            "stream_id": stream_id,
            "task_id": task.id,
            "task_name": task.name,
            "subscribe_url": f"/api/v1/stream/subscribe/{task.id}?token={request.headers.get('Authorization', '')[7:]}",
            "message": "任务已启动，流式输出可在 subscribe_url 订阅",
        })

    # ── 直接透传 NL 命令的流式执行 ─────────────────────────────────────────

    @bp.route("/nl/execute", methods=["POST"])
    @require_auth(KeyLevel.EXECUTE)
    def nl_stream_execute():
        """
        自然语言命令 → 流式执行
        结合 NLInterpreter，直接用自然语言触发流式任务
        """
        data = request.get_json() or {}
        text = data.get("text", "").strip()
        if not text:
            return jsonify({"error": "text 不能为空"}), 400

        # 获取 NL interpreter
        nl = None
        try:
            from ..core.nl_interpreter import NLInterpreter
            nl = NLInterpreter()
        except ImportError:
            pass

        if nl is None:
            return jsonify({"error": "NL Interpreter 未加载"}), 500

        result = nl.parse_natural_command(text)
        plan = result.get("plan")

        if plan and plan.get("intent") in ("status_query", "help"):
            # 直接响应
            return jsonify({
                "type": "direct_response",
                "intent": plan["intent"],
                "response": plan.get("response", ""),
            })

        if not plan:
            # 透传给 OpenClaw
            plan = {
                "intent": "unknown",
                "action": "spawn",
                "params": {"task": text, "runtime": "subagent"},
            }

        # 启动流式执行
        task = Task(
            name=f"自然语言命令: {text[:30]}",
            action=plan.get("action", "spawn"),
            params=plan.get("params", {"task": text, "runtime": "subagent"}),
            priority=Task.Priority.NORMAL,
            notify=True,
        )
        task_manager.add(task)

        sm = _get_stream()
        stream_id = sm.start_stream(task_id=task.id, agent_name=plan.get("params", {}).get("agent", "subagent"))
        sm.push(task_id=task.id, content=f"💬 {text}", level="section")
        sm.push(task_id=task.id, content=f"识别意图: {plan.get('intent', 'unknown')} | 置信度: {result.get('confidence', 0):.0%}", level="info")

        def _execute():
            try:
                task_manager.execute(task.id)
                max_wait = 300
                elapsed = 0
                while elapsed < max_wait:
                    time.sleep(2)
                    elapsed += 2
                    t = task_manager.get(task.id)
                    if not t:
                        sm.end(task_id=task.id, error="任务丢失", status="failed")
                        break
                    if t.status == TaskStatus.SUCCESS:
                        sm.push_progress(task_id=task.id, progress=100)
                        if t.result:
                            sm.push_result(task_id=task.id, result=t.result)
                        sm.end(task_id=task.id, result=t.result)
                        break
                    elif t.status == TaskStatus.FAILED:
                        sm.end(task_id=task.id, error=t.error, status="failed")
                        break
            except Exception as e:
                logger.exception(f"[StreamManager] NL 执行异常 task={task.id}")
                sm.end(task_id=task.id, error=str(e), status="failed")

        _executor.submit(_execute)

        return jsonify({
            "type": "stream_started",
            "stream_id": stream_id,
            "task_id": task.id,
            "intent": plan.get("intent"),
            "confidence": result.get("confidence"),
            "subscribe_url": f"/api/v1/stream/subscribe/{task.id}",
        })

    # ── 活跃流列表 ─────────────────────────────────────────────────────────

    @bp.route("/active", methods=["GET"])
    @require_auth(KeyLevel.READ)
    def list_active():
        """列出所有活跃流"""
        sm = _get_stream()
        return jsonify({
            "active_streams": sm.get_active_streams(),
            "count": len(sm.get_active_streams()),
        })

    # ── 历史流 ─────────────────────────────────────────────────────────────

    @bp.route("/history", methods=["GET"])
    @require_auth(KeyLevel.READ)
    def stream_history():
        """获取最近完成的流历史"""
        sm = _get_stream()
        limit = request.args.get("limit", 20, type=int)
        return jsonify({"history": sm.get_history(limit=limit)})

    # ── 单条流详情 ─────────────────────────────────────────────────────────

    @bp.route("/<task_id>", methods=["GET"])
    @require_auth(KeyLevel.READ)
    def get_stream(task_id):
        """获取指定流的详情"""
        sm = _get_stream()
        info = sm.get_stream(task_id)
        if not info:
            return jsonify({"error": "流不存在或已过期"}), 404
        return jsonify(info)

    return bp
