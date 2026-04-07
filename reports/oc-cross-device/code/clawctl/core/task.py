#!/usr/bin/env python3
"""
任务管理与执行模块
支持：即时任务 / 定时任务 / 模板任务
"""

import uuid
import time
import logging
import threading
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Callable, Any

from .client import OpenClawClient, ClawResponse

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3


@dataclass
class Task:
    """
    任务对象
    
    Attributes:
        name:        任务名称/描述
        action:      动作类型 (spawn|send|trigger)
        params:      动作参数
        status:      当前状态
        priority:    优先级
        notify:      执行完成后是否通知
        notify_channel: 通知渠道
        result:      执行结果
        created_at:  创建时间
        started_at:  开始时间
        completed_at: 完成时间
    """
    name: str
    action: str
    params: dict
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL
    notify: bool = True
    notify_channel: str = "dingtalk"
    id: str = field(default_factory=lambda: f"task_{int(time.time())}_{uuid.uuid4().hex[:6]}")
    result: Optional[dict] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    tags: list = field(default_factory=list)

    def duration_ms(self) -> Optional[int]:
        """计算执行耗时（毫秒）"""
        if self.started_at and self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds() * 1000)
        return None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "action": self.action,
            "status": self.status.value,
            "priority": self.priority.name,
            "notify": self.notify,
            "notify_channel": self.notify_channel,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_ms": self.duration_ms(),
            "tags": self.tags,
        }


class TaskManager:
    """
    任务管理器
    
    功能：
    - 任务注册与执行
    - 任务队列（优先级排序）
    - 执行状态跟踪
    - 结果回调通知
    """

    def __init__(self, client: OpenClawClient):
        self.client = client
        self._tasks: dict[str, Task] = {}
        self._lock = threading.RLock()
        self._executing: set[str] = set()
        self._done_callbacks: list[Callable[[Task], None]] = []
        self.templates: dict = {}  # 由 TemplateLoader 填充

    def submit(self, task: Task) -> Task:
        """提交任务到队列"""
        with self._lock:
            self._tasks[task.id] = task
            task.status = TaskStatus.QUEUED
        logger.info(f"任务已提交: {task.id} | {task.name}")
        return task

    def execute(self, task: Task) -> Task:
        """
        执行单个任务（同步）
        """
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        self._executing.add(task.id)

        try:
            if task.action == "spawn":
                resp = self.client.spawn_agent(
                    task=task.params.get("task", task.name),
                    agent_id=task.params.get("agent_id"),
                    runtime=task.params.get("runtime", "subagent"),
                    run_timeout=task.params.get("timeout", 300),
                )
            elif task.action == "send":
                resp = self.client.send_message(
                    channel=task.params.get("channel", "dingtalk"),
                    message=task.params.get("message", ""),
                )
            elif task.action == "trigger":
                resp = self.client.trigger_template(
                    template_name=task.params.get("template"),
                    params=task.params.get("params"),
                )
            else:
                raise ValueError(f"未知动作类型: {task.action}")

            task.completed_at = datetime.now()
            if resp.success:
                task.status = TaskStatus.SUCCESS
                task.result = resp.data
                logger.info(f"任务成功: {task.id} | 耗时: {task.duration_ms()}ms")
            else:
                task.status = TaskStatus.FAILED
                task.error = resp.error
                logger.error(f"任务失败: {task.id} | 错误: {resp.error}")

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
            logger.exception(f"任务异常: {task.id}")

        finally:
            self._executing.discard(task.id)
            self._notify_done(task)

        return task

    def execute_async(self, task: Task) -> Task:
        """异步执行任务（后台线程）"""
        t = threading.Thread(target=self.execute, args=(task,), daemon=True)
        t.start()
        return task

    def get(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)

    def list(self, status: Optional[TaskStatus] = None, limit: int = 50) -> list[Task]:
        """列出任务"""
        tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        tasks.sort(key=lambda t: (t.priority.value, t.created_at), reverse=True)
        return tasks[:limit]

    def cancel(self, task_id: str) -> bool:
        """取消任务（仅限排队中）"""
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False
            if task.status == TaskStatus.QUEUED:
                task.status = TaskStatus.CANCELLED
                task.completed_at = datetime.now()
                return True
            return False

    def on_done(self, callback: Callable[[Task], None]):
        """注册任务完成回调"""
        self._done_callbacks.append(callback)

    def _notify_done(self, task: Task):
        for cb in self._done_callbacks:
            try:
                cb(task)
            except Exception:
                logger.exception("任务回调异常")
