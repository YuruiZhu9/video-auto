#!/usr/bin/env python3
"""
StreamManager - 流式任务执行管理器
负责将子 Agent 的输出实时流式推送到所有订阅者（SSE）
"""

import json
import time
import uuid
import logging
import threading
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Callable
from collections import defaultdict, deque
from datetime import datetime

logger = logging.getLogger(__name__)


class StreamLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    SUCCESS = "success"
    SECTION = "section"  # 分节标题


@dataclass
class StreamEvent:
    """流事件"""
    event: str          # event type name
    data: dict          # payload
    stream_id: str      # 流 ID
    task_id: str        # 关联任务 ID
    timestamp: str       # ISO 时间戳

    def to_sse(self) -> str:
        """序列化为 SSE 格式"""
        lines = [f"event: {self.event}", f"data: {json.dumps(self.data, ensure_ascii=False)}"]
        return "\n".join(lines) + "\n\n"


@dataclass
class StreamSession:
    """单个流会话"""
    stream_id: str
    task_id: str
    agent_name: str
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    status: str = "running"  # running / completed / failed / cancelled
    chunks: deque = field(default_factory=lambda: deque(maxlen=500))
    result: Optional[dict] = None
    error: Optional[str] = None
    subscribers: List = field(default_factory=list)  # SSE response objects
    lock: threading.Lock = field(default_factory=threading.Lock)

    def add_subscriber(self, resp):
        with self.lock:
            self.subscribers.append(resp)

    def remove_subscriber(self, resp):
        with self.lock:
            if resp in self.subscribers:
                self.subscribers.remove(resp)

    def broadcast(self, event: StreamEvent):
        """向所有订阅者推送事件"""
        dead = []
        sse_text = event.to_sse()
        with self.lock:
            for sub in self.subscribers:
                try:
                    sub.write(sse_text)
                    sub.flush()
                except Exception:
                    dead.append(sub)
            for d in dead:
                self.subscribers.remove(d)

    def to_dict(self) -> dict:
        return {
            "stream_id": self.stream_id,
            "task_id": self.task_id,
            "agent_name": self.agent_name,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "status": self.status,
            "chunk_count": len(self.chunks),
            "result": self.result,
            "error": self.error,
            "duration_ms": int((self.ended_at - self.started_at).total_seconds() * 1000) if self.ended_at else None,
        }


class StreamManager:
    """
    全局流管理器 — 管理所有活动任务的流式输出

    使用方式：
        stream_mgr = StreamManager()

        # 1. 启动一个流的会话
        stream_id = stream_mgr.start_stream(task_id="task-001", agent_name="tech-analyst")

        # 2. 推送输出片段（子 agent 运行时持续调用）
        stream_mgr.push(task_id="task-001", content="正在搜索 arXiv 论文...", level="info")
        stream_mgr.push(task_id="task-001", content="找到 23 篇相关论文", level="success")

        # 3. Markdown 格式内容（前端渲染 Markdown）
        stream_mgr.push_markdown(task_id="task-001", content="## 分析结论\n- GPT-5 参数量约 1.8T")

        # 4. 进度更新
        stream_mgr.push_progress(task_id="task-001", progress=60, message="正在生成报告...")

        # 5. 流结束
        stream_mgr.end(task_id="task-001", result={"report_url": "..."})

        # 6. SSE 订阅（在 Flask 路由中）
        return stream_mgr.subscribe(task_id="task-001", response)
    """

    def __init__(self, max_streams: int = 100, max_history: int = 50):
        self._streams: Dict[str, StreamSession] = {}
        self._task_stream_map: Dict[str, str] = {}  # task_id -> stream_id
        self._history: deque = deque(maxlen=max_history)  # 保留最近 N 个完成流
        self._lock = threading.Lock()
        self._max_streams = max_streams
        self._callbacks: Dict[str, List[Callable]] = defaultdict(list)

    # ── 公开 API ──────────────────────────────────────────────────────────────

    def start_stream(self, task_id: str, agent_name: str = "unknown") -> str:
        """
        为一个任务启动新的流会话。
        如果该 task_id 已有活动流，返回已有 stream_id。
        """
        with self._lock:
            # 已有活跃流则复用
            if task_id in self._task_stream_map:
                sid = self._task_stream_map[task_id]
                if sid in self._streams:
                    return sid

            # 清理过多活跃流
            if len(self._streams) >= self._max_streams:
                self._prune_old_streams()

            stream_id = f"stream-{uuid.uuid4().hex[:12]}"
            session = StreamSession(
                stream_id=stream_id,
                task_id=task_id,
                agent_name=agent_name,
            )
            self._streams[stream_id] = session
            self._task_stream_map[task_id] = stream_id

            logger.info(f"[StreamManager] 启动流: task={task_id} stream={stream_id}")
            return stream_id

    def push(
        self,
        task_id: str,
        content: str,
        level: str = "info",
        timestamp: Optional[datetime] = None,
    ) -> bool:
        """
        推送一个输出片段到指定任务的流。
        自动处理 Markdown 渲染：代码块 / 标题 / 列表 自动识别。
        """
        ts = timestamp or datetime.now()
        with self._lock:
            if task_id not in self._task_stream_map:
                return False
            stream_id = self._task_stream_map[task_id]
            if stream_id not in self._streams:
                return False

        session = self._streams[stream_id]
        ts_str = ts.isoformat()

        # 保存到历史
        session.chunks.append({
            "content": content,
            "level": level,
            "timestamp": ts_str,
        })

        # 构造 SSE 事件
        auto_event = self._detect_event_type(content, level)
        event = StreamEvent(
            event=auto_event,
            data={
                "task_id": task_id,
                "content": content,
                "level": level,
                "timestamp": ts_str,
            },
            stream_id=stream_id,
            task_id=task_id,
            timestamp=ts_str,
        )

        session.broadcast(event)
        return True

    def push_markdown(self, task_id: str, content: str, timestamp: Optional[datetime] = None) -> bool:
        """推送 Markdown 内容片段（前端渲染）"""
        return self.push(task_id, content, level="markdown", timestamp=timestamp)

    def push_section(self, task_id: str, title: str, timestamp: Optional[datetime] = None) -> bool:
        """推送分节标题"""
        ts = timestamp or datetime.now()
        return self.push(task_id, f"【{title}】", level="section", timestamp=ts)

    def push_progress(
        self,
        task_id: str,
        progress: int,
        message: str = "",
        timestamp: Optional[datetime] = None,
    ) -> bool:
        """推送进度更新（0-100）"""
        ts = timestamp or datetime.now()
        ts_str = ts.isoformat()
        with self._lock:
            if task_id not in self._task_stream_map:
                return False
            stream_id = self._task_stream_map[task_id]

        session = self._streams[stream_id]
        event = StreamEvent(
            event="stream_progress",
            data={
                "task_id": task_id,
                "progress": progress,
                "message": message,
                "timestamp": ts_str,
            },
            stream_id=stream_id,
            task_id=task_id,
            timestamp=ts_str,
        )
        session.broadcast(event)
        return True

    def push_result(self, task_id: str, result: dict, timestamp: Optional[datetime] = None) -> bool:
        """推送结构化结果（JSON 展示用）"""
        ts = timestamp or datetime.now()
        ts_str = ts.isoformat()
        with self._lock:
            if task_id not in self._task_stream_map:
                return False
            stream_id = self._task_stream_map[task_id]

        session = self._streams[stream_id]
        event = StreamEvent(
            event="stream_result",
            data={
                "task_id": task_id,
                "result": result,
                "timestamp": ts_str,
            },
            stream_id=stream_id,
            task_id=task_id,
            timestamp=ts_str,
        )
        session.broadcast(event)
        return True

    def end(
        self,
        task_id: str,
        result: Optional[dict] = None,
        error: Optional[str] = None,
        status: str = "completed",
        timestamp: Optional[datetime] = None,
    ) -> bool:
        """标记流结束"""
        ts = timestamp or datetime.now()
        ts_str = ts.isoformat()
        with self._lock:
            if task_id not in self._task_stream_map:
                return False
            stream_id = self._task_stream_map[task_id]
            if stream_id not in self._streams:
                return False

        session = self._streams[stream_id]
        session.ended_at = ts
        session.status = status
        session.result = result
        session.error = error

        # 推送结束事件
        duration_ms = int((ts - session.started_at).total_seconds() * 1000)
        event = StreamEvent(
            event="stream_complete",
            data={
                "task_id": task_id,
                "stream_id": stream_id,
                "status": status,
                "duration_ms": duration_ms,
                "result_summary": str(result)[:300] if result else None,
                "error": error,
                "timestamp": ts_str,
            },
            stream_id=stream_id,
            task_id=task_id,
            timestamp=ts_str,
        )
        session.broadcast(event)

        # 移到历史
        with self._lock:
            self._history.append(session.to_dict())
            del self._streams[stream_id]
            del self._task_stream_map[task_id]

        logger.info(f"[StreamManager] 流结束: task={task_id} status={status} duration={duration_ms}ms")
        return True

    def subscribe(self, task_id: str, response):
        """
        将 Flask response 对象订阅到指定任务的流。
        首次订阅时发送 stream_start 事件（包含历史 chunks）。
        """
        with self._lock:
            if task_id not in self._task_stream_map:
                return None
            stream_id = self._task_stream_map[task_id]
            if stream_id not in self._streams:
                return None
            session = self._streams[stream_id]

        session.add_subscriber(response)

        # 发送历史 chunks（让新连接能看回放）
        for chunk in session.chunks:
            start_event = StreamEvent(
                event="stream_history",
                data={
                    "task_id": task_id,
                    "content": chunk["content"],
                    "level": chunk["level"],
                    "timestamp": chunk["timestamp"],
                },
                stream_id=stream_id,
                task_id=task_id,
                timestamp=chunk["timestamp"],
            )
            try:
                response.write(start_event.to_sse())
                response.flush()
            except Exception:
                break

        return stream_id

    def unsubscribe(self, task_id: str, response):
        """取消订阅"""
        with self._lock:
            if task_id not in self._task_stream_map:
                return
            stream_id = self._task_stream_map[task_id]
            if stream_id in self._streams:
                self._streams[stream_id].remove_subscriber(response)

    # ── 查询 API ──────────────────────────────────────────────────────────────

    def get_active_streams(self) -> List[dict]:
        """获取所有活跃流"""
        with self._lock:
            return [s.to_dict() for s in self._streams.values()]

    def get_stream(self, task_id: str) -> Optional[dict]:
        """获取指定任务的流信息"""
        with self._lock:
            if task_id not in self._task_stream_map:
                # 查历史
                for h in self._history:
                    if h["task_id"] == task_id:
                        return h
                return None
            sid = self._task_stream_map[task_id]
            if sid in self._streams:
                return self._streams[sid].to_dict()
        return None

    def get_history(self, limit: int = 20) -> List[dict]:
        """获取最近完成的历史流"""
        with self._lock:
            return list(self._history)[-limit:]

    # ── 内部方法 ──────────────────────────────────────────────────────────────

    def _detect_event_type(self, content: str, level: str) -> str:
        """根据内容自动检测 SSE 事件类型"""
        if level in ("error", "warn"):
            return "stream_chunk"
        stripped = content.strip()
        if stripped.startswith("# ") or stripped.startswith("## "):
            return "stream_section"
        if "```" in stripped:
            return "stream_code"
        if stripped.startswith("-" ) or stripped.startswith("* "):
            return "stream_list"
        return "stream_chunk"

    def _prune_old_streams(self):
        """清理最老的已完成流（不超过 max_streams）"""
        to_remove = [sid for sid, s in self._streams.items() if s.status != "running"]
        for sid in to_remove[:5]:
            task_id = self._streams[sid].task_id
            self._history.append(self._streams[sid].to_dict())
            del self._streams[sid]
            if task_id in self._task_stream_map:
                del self._task_stream_map[task_id]
        logger.warning(f"[StreamManager] 清理旧流: 移除 {min(5, len(to_remove))} 个")


# ── 全局单例 ──────────────────────────────────────────────────────────────────
_stream_manager: Optional[StreamManager] = None
_stream_lock = threading.Lock()


def get_stream_manager() -> StreamManager:
    global _stream_manager
    with _stream_lock:
        if _stream_manager is None:
            _stream_manager = StreamManager()
        return _stream_manager


def init_stream_manager(**kwargs) -> StreamManager:
    global _stream_manager
    with _stream_lock:
        _stream_manager = StreamManager(**kwargs)
        return _stream_manager
