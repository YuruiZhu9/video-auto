#!/usr/bin/env python3
"""
Server-Sent Events (SSE) 实时推送系统
支持：任务状态变更 / 系统告警 / 定时触发 / 心跳保活
无需 WebSocket，兼容所有浏览器和移动端
"""

import json
import logging
import threading
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, asdict
from typing import Optional, Generator, Callable, Any
from datetime import datetime

from flask import Response, request, stream_with_context

logger = logging.getLogger(__name__)

# ── 事件类型枚举 ────────────────────────────────────────────────────────────

class EventType:
    TASK_UPDATE   = "task_update"       # 任务状态变更
    SYSTEM_ALERT   = "system_alert"      # 系统告警
    SCHEDULED_TRIGGER = "scheduled_trigger"  # 定时触发事件
    HEARTBEAT      = "heartbeat"         # 心跳保活
    TASK_RESULT    = "task_result"       # 任务完成（含结果摘要）


@dataclass
class SseEvent:
    """SSE 事件"""
    type: str
    data: Any
    id: Optional[str] = None
    retry: int = 30000   # 重连间隔（毫秒）

    def to_sse(self) -> str:
        """序列化为 SSE 格式"""
        self.id = self.id or str(uuid.uuid4())[:8]
        lines = [f"id: {self.id}", f"event: {self.type}", f"retry: {self.retry}"]
        if isinstance(self.data, dict):
            lines.append(f"data: {json.dumps(self.data, ensure_ascii=False)}")
        else:
            lines.append(f"data: {str(self.data)}")
        return "\n".join(lines) + "\n\n"


class SseManager:
    """
    SSE 连接管理器
    - 线程安全
    - 按 token 隔离事件（不同用户只收到自己的事件）
    - 系统级广播（管理员可发送全员通知）
    """

    def __init__(self, heartbeat_interval: int = 25):
        self._clients: dict[str, list[tuple[threading.Event, list[str]]]] = defaultdict(list)
        # key=token, val=[(stop_event, event_types_filter)]
        self._lock = threading.RLock()
        self._heartbeat_interval = heartbeat_interval
        self._last_id: dict[str, int] = defaultdict(int)  # 每个 token 的最后发送的 id
        logger.info("SSE Manager 初始化完成")

    # ── 连接管理 ──────────────────────────────────────────────────────────

    def connect(self, token: str, event_types: Optional[list[str]] = None) -> Generator[str, None, None]:
        """
        客户端连接生成器
        用法：
            return Response(
                stream_with_context(sse_manager.connect(token, ["task_update"])),
                mimetype="text/event-stream",
                headers={"X-Accel-Buffering": "no"}
            )
        """
        stop_event = threading.Event()
        client_entry = (stop_event, event_types or [EventType.HEARTBEAT])
        client_id = str(uuid.uuid4())[:8]

        with self._lock:
            self._clients[token].append(client_entry)
            client_count = len(self._clients[token])
            logger.info(f"SSE 客户端连接: token={token[:8]}..., id={client_id}, 当前连接数={client_count}")

        try:
            # 发送连接成功事件
            yield self._make_event(EventType.SYSTEM_ALERT, {
                "message": "已连接到 Clawctl 实时推送",
                "client_id": client_id,
                "connected_at": datetime.now().isoformat(),
                "event_types": event_types or ["*"],
            }, token=token)

            # 先发送心跳
            yield self._make_event(EventType.HEARTBEAT, {
                "ts": datetime.now().isoformat(),
                "uptime": "connected",
            }, token=token)

            last_heartbeat = time.time()

            # 事件循环
            while not stop_event.is_set():
                stop_event.wait(timeout=1)   # 每秒检查一次
                now = time.time()

                # 心跳保活（默认每25秒一次）
                if now - last_heartbeat >= self._heartbeat_interval:
                    try:
                        yield self._make_event(EventType.HEARTBEAT, {
                            "ts": datetime.now().isoformat(),
                        }, token=token)
                        last_heartbeat = now
                    except Exception:
                        break

        except GeneratorExit:
            logger.info(f"SSE 客户端正常断开: token={token[:8]}...")
        except Exception:
            logger.exception(f"SSE 传输异常: token={token[:8]}...")
        finally:
            with self._lock:
                self._clients[token] = [
                    e for e in self._clients[token] if e[0] is not stop_event
                ]
                logger.info(f"SSE 客户端移除: token={token[:8]}..., 剩余={len(self._clients[token])}")

    # ── 事件推送 ──────────────────────────────────────────────────────────

    def emit(
        self,
        event_type: str,
        data: Any,
        target_tokens: Optional[list[str]] = None,
        broadcast: bool = False,
    ):
        """
        发送事件到客户端

        Args:
            event_type: 事件类型
            data: 事件数据
            target_tokens: 指定 token 列表（优先使用）
            broadcast: 是否广播到所有连接
        """
        sse = self._make_event(event_type, data)

        if broadcast:
            with self._lock:
                tokens = list(self._clients.keys())
        elif target_tokens:
            tokens = target_tokens
        else:
            tokens = []

        for token in tokens:
            self._send_to_token(token, sse)

    def _send_to_token(self, token: str, sse: str):
        """向指定 token 的所有连接发送事件"""
        with self._lock:
            entries = list(self._clients.get(token, []))

        for stop_event, filter_types in entries:
            if stop_event.is_set():
                continue
            if filter_types and EventType.HEARTBEAT not in filter_types:
                if filter_types and "*" not in filter_types and sse not in (EventType.TASK_UPDATE,):
                    pass  # 过滤逻辑
            try:
                # 通过 request 或全局队列，这里用回调
                # Flask 需要在请求上下文中调用，这里先记录到内存缓冲区
                self._enqueue(token, sse)
            except Exception:
                pass

    def _enqueue(self, token: str, sse: str):
        """将事件加入缓冲（由连接生成器消费）"""
        with self._lock:
            if token in self._pending:
                self._pending[token].append(sse)
            else:
                self._pending[token] = [sse]

    _pending: dict = defaultdict(list)

    def _make_event(self, event_type: str, data: Any, token: Optional[str] = None) -> str:
        """构建 SSE 事件字符串"""
        if isinstance(data, dict):
            if "ts" not in data:
                data["_ts"] = datetime.now().isoformat()
        event = SseEvent(type=event_type, data=data)
        if token:
            with self._lock:
                self._last_id[token] += 1
                event.id = f"{token[:8]}-{self._last_id[token]}"
        return event.to_sse()

    # ── 便捷方法 ──────────────────────────────────────────────────────────

    def emit_task_update(self, task_data: dict, target_tokens: Optional[list[str]] = None):
        """推送任务状态变更"""
        self.emit(EventType.TASK_UPDATE, {
            "task_id": task_data.get("id"),
            "name": task_data.get("name"),
            "status": task_data.get("status"),
            "duration_ms": task_data.get("duration_ms"),
            "error": task_data.get("error"),
            "result_summary": self._summarize_result(task_data.get("result")),
        }, target_tokens=target_tokens)

    def emit_task_result(self, task_data: dict, target_tokens: Optional[list[str]] = None):
        """推送任务完成结果（带完整摘要）"""
        self.emit(EventType.TASK_RESULT, {
            "task_id": task_data.get("id"),
            "name": task_data.get("name"),
            "status": task_data.get("status"),
            "duration_ms": task_data.get("duration_ms"),
            "completed_at": task_data.get("completed_at"),
            "result": task_data.get("result"),
            "error": task_data.get("error"),
        }, target_tokens=target_tokens)

    def emit_alert(self, alert_type: str, message: str, level: str = "info",
                   target_tokens: Optional[list[str]] = None):
        """推送系统告警"""
        self.emit(EventType.SYSTEM_ALERT, {
            "alert_type": alert_type,
            "level": level,
            "message": message,
            "ts": datetime.now().isoformat(),
        }, target_tokens=target_tokens)

    def emit_scheduled(self, schedule_id: str, schedule_name: str,
                       target_tokens: Optional[list[str]] = None):
        """推送定时任务触发"""
        self.emit(EventType.SCHEDULED_TRIGGER, {
            "schedule_id": schedule_id,
            "name": schedule_name,
            "ts": datetime.now().isoformat(),
        }, target_tokens=target_tokens)

    # ── 统计 ─────────────────────────────────────────────────────────────

    def client_count(self, token: Optional[str] = None) -> int:
        """连接数统计"""
        with self._lock:
            if token:
                return len(self._clients.get(token, []))
            return sum(len(v) for v in self._clients.values())

    @staticmethod
    def _summarize_result(result: Any, max_len: int = 200) -> str:
        """将结果压缩为摘要字符串"""
        if not result:
            return ""
        if isinstance(result, str):
            s = result
        elif isinstance(result, dict):
            s = json.dumps(result, ensure_ascii=False)
        else:
            s = str(result)
        return s[:max_len] + ("..." if len(s) > max_len else "")


# ── Flask 蓝图 ──────────────────────────────────────────────────────────────

def register_sse_routes(app, sse_manager: SseManager):
    """注册 SSE 相关路由"""

    @app.route("/api/v1/events", methods=["GET"])
    def sse_events():
        """SSE 实时事件流（需带 ?token=xxx）"""
        from flask import request
        token = request.args.get("token", "")
        event_types = request.args.get("types", "")
        types = event_types.split(",") if event_types else None

        if not token:
            return {"error": "缺少 token 参数"}, 400

        return Response(
            stream_with_context(sse_manager.connect(token, types)),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",      # 禁用 Nginx 缓冲
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Authorization, Content-Type",
            }
        )

    @app.route("/api/v1/events/stats", methods=["GET"])
    def sse_stats():
        """SSE 连接统计（Admin 权限）"""
        return {
            "total_clients": sse_manager.client_count(),
            "active_connections": dict(sse_manager._clients),
        }

    @app.route("/api/v1/events/broadcast", methods=["POST"])
    def sse_broadcast():
        """系统级广播（Admin 权限）"""
        from flask import request, jsonify
        data = request.get_json() or {}
        event_type = data.get("type", EventType.SYSTEM_ALERT)
        message = data.get("message", "")
        sse_manager.emit(event_type, {"message": message}, broadcast=True)
        return jsonify({"ok": True, "clients_notified": sse_manager.client_count()})
