"""
SSE (Server-Sent Events) 实时推送处理器

通过 SSE 协议向前端 Web 页面推送：
- 任务状态变化（新建/开始/完成/失败）
- 系统告警
- 定时任务触发通知
- OpenClaw 会话变化

前端使用 EventSource API 接收：
  const es = new EventSource('/api/v1/events?token=xxx');
  es.addEventListener('task_update', e => console.log(e.data));
"""

import json
import asyncio
import threading
from typing import Dict, Set, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class SseEvent:
    """SSE 事件"""
    event: str          # 事件类型：task_update / system_alert / heartbeat / scheduled_trigger
    data: Dict[str, Any]
    comment: str = ""   # 注释行（保持连接活跃）

    def to_sse(self) -> str:
        """序列化为 SSE 格式"""
        lines = []
        if self.comment:
            lines.append(f": {self.comment}")
        lines.append(f"event: {self.event}")
        lines.append(f"data: {json.dumps(self.data, ensure_ascii=False)}")
        lines.append("")  # 空行结束事件
        return "\n".join(lines) + "\n"


class SseConnection:
    """单个 SSE 连接"""

    def __init__(self, client_id: str, token: str, queue: asyncio.Queue):
        self.client_id = client_id
        self.token = token
        self.queue = queue
        self.closed = False
        self._lock = threading.Lock()

    async def send(self, event: SseEvent):
        if self.closed:
            return
        try:
            await asyncio.wait_for(self.queue.put(event), timeout=5)
        except asyncio.TimeoutError:
            logger.warning(f"SSE client {self.client_id} put timeout")

    def close(self):
        with self._lock:
            self.closed = True


class SseManager:
    """
    SSE 连接管理器

    支持：
    - 多客户端订阅（按 token 区分）
    - 按事件类型过滤
    - 心跳保活（每 25 秒发送 comment）
    - 优雅关闭
    """

    HEARTBEAT_INTERVAL = 25  # 秒

    def __init__(self):
        # client_id -> SseConnection
        self._connections: Dict[str, SseConnection] = {}
        # token -> set of client_ids（支持多标签页）
        self._tokens: Dict[str, Set[str]] = defaultdict(set)
        self._lock = threading.RLock()
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._running = False

    # ─── 连接管理 ─────────────────────────────────────────────────

    def add_connection(self, client_id: str, token: str) -> SseConnection:
        """注册新的 SSE 连接"""
        queue: asyncio.Queue[Optional[SseEvent]] = asyncio.Queue(maxsize=50)
        conn = SseConnection(client_id, token, queue)
        with self._lock:
            self._connections[client_id] = conn
            self._tokens[token].add(client_id)
        logger.info(f"[SSE] Client connected: {client_id} (token={token[:8]}...)")
        return conn

    def remove_connection(self, client_id: str):
        """移除 SSE 连接"""
        with self._lock:
            conn = self._connections.pop(client_id, None)
            if conn:
                conn.close()
                self._tokens[conn.token].discard(client_id)
                if not self._tokens[conn.token]:
                    self._tokens.pop(conn.token, None)
                logger.info(f"[SSE] Client disconnected: {client_id}")

    def is_token_valid(self, token: str) -> bool:
        with self._lock:
            return token in self._tokens

    # ─── 事件广播 ─────────────────────────────────────────────────

    def _broadcast(self, event: SseEvent, token_filter: Optional[str] = None):
        """同步广播事件到所有连接"""
        dead_clients = []
        with self._lock:
            clients = list(self._connections.values())

        for conn in clients:
            if token_filter and conn.token != token_filter:
                continue
            if conn.closed:
                dead_clients.append(conn.client_id)
                continue
            try:
                # 在新线程中异步发送（避免阻塞）
                threading.Thread(
                    target=_async_send_wrapper,
                    args=(conn, event),
                    daemon=True
                ).start()
            except Exception as e:
                logger.error(f"[SSE] Broadcast error: {e}")

        # 清理死连接
        for cid in dead_clients:
            self.remove_connection(cid)

    def emit_task_update(self, task_data: Dict[str, Any]):
        """发布任务状态更新"""
        event = SseEvent(
            event="task_update",
            data=task_data,
            comment=f"task {task_data.get('task_id', '')} {task_data.get('status', '')}"
        )
        self._broadcast(event)

    def emit_task_completed(
        self,
        task_id: str,
        db_id: int,
        status: str,
        result_summary: str,
        duration: float,
        error: str = ""
    ):
        self.emit_task_update({
            "type": "task_completed",
            "task_id": task_id,
            "db_id": db_id,
            "status": status,
            "result_summary": result_summary,
            "duration_seconds": duration,
            "error": error,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def emit_system_alert(self, level: str, title: str, message: str, detail: str = ""):
        """发布系统告警"""
        event = SseEvent(
            event="system_alert",
            data={
                "level": level,  # info / warning / error / critical
                "title": title,
                "message": message,
                "detail": detail,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        self._broadcast(event)

    def emit_scheduled_trigger(self, job_id: str, job_name: str, template_id: str):
        """发布定时任务触发通知"""
        self.emit_task_update({
            "type": "scheduled_trigger",
            "job_id": job_id,
            "job_name": job_name,
            "template_id": template_id,
            "status": "running",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def emit_heartbeat(self):
        """发送心跳（保活）"""
        event = SseEvent(
            event="heartbeat",
            data={"timestamp": datetime.now(timezone.utc).isoformat()},
            comment="pong"
        )
        self._broadcast(event)

    # ─── SSE 事件流生成器 ──────────────────────────────────────────

    async def stream(self, client_id: str, token: str) -> SseConnection:
        """
        获取 SSE 连接，开始推送循环
        在 FastAPI/Starlette 路由中调用：
            async def get():
                conn = sse_manager.stream(client_id, token)
                return EventSourceResponse(conn.queue.put, ...)
        """
        conn = self.add_connection(client_id, token)
        return conn

    async def event_generator(self, client_id: str, token: str):
        """
        异步生成器，供 Starlette/FastAPI EventSourceResponse 使用
        """
        conn = self.add_connection(client_id, token)
        queue: asyncio.Queue[Optional[SseEvent]] = conn.queue

        # 先发送连接成功事件
        yield SseEvent(
            event="connected",
            data={"client_id": client_id, "timestamp": datetime.now(timezone.utc).isoformat()}
        ).to_sse()

        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=self.HEARTBEAT_INTERVAL)
                except asyncio.TimeoutError:
                    # 超时 → 发送 comment 心跳保活
                    yield f": heartbeat {datetime.now(timezone.utc).isoformat()}\n\n"
                    continue

                if event is None:  # None = 关闭信号
                    break
                yield event.to_sse()

        except asyncio.CancelledError:
            pass
        finally:
            self.remove_connection(client_id)

    # ─── 生命周期 ─────────────────────────────────────────────────

    def start(self):
        """启动心跳定时器"""
        if self._running:
            return
        self._running = True
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        logger.info("[SSE] Manager started")

    async def _heartbeat_loop(self):
        while self._running:
            await asyncio.sleep(self.HEARTBEAT_INTERVAL)
            if self._running:
                self.emit_heartbeat()

    async def stop(self):
        """停止 SSE 服务"""
        self._running = False
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        with self._lock:
            for conn in list(self._connections.values()):
                conn.close()
        self._connections.clear()
        self._tokens.clear()
        logger.info("[SSE] Manager stopped")

    @property
    def connection_count(self) -> int:
        with self._lock:
            return len(self._connections)


def _async_send_wrapper(conn: SseConnection, event: SseEvent):
    """线程安全的异步发送包装"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(conn.send(event))
        loop.close()
    except Exception as e:
        logger.error(f"[SSE] Send error: {e}")
