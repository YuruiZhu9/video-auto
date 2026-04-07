"""任务定义与管理"""
import uuid
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass, field, asdict


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"      # 等待执行
    RUNNING = "running"      # 执行中
    SUCCESS = "success"      # 执行成功
    FAILED = "failed"        # 执行失败
    CANCELLED = "cancelled"  # 已取消
    TIMEOUT = "timeout"      # 超时


@dataclass
class Task:
    """任务定义"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    action: str = "spawn"    # spawn/send/exec
    agent: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout: float = 60.0    # 超时时间（秒）
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data["status"] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """从字典创建"""
        if "status" in data and isinstance(data["status"], str):
            data["status"] = TaskStatus(data["status"])
        return cls(**data)
    
    def mark_running(self):
        """标记为运行中"""
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.now()
    
    def mark_success(self, result: Dict[str, Any]):
        """标记为成功"""
        self.status = TaskStatus.SUCCESS
        self.completed_at = datetime.now()
        self.result = result
    
    def mark_failed(self, error: str):
        """标记为失败"""
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.now()
        self.error = error
    
    def mark_cancelled(self):
        """标记为取消"""
        self.status = TaskStatus.CANCELLED
        self.completed_at = datetime.now()
    
    @property
    def duration(self) -> Optional[float]:
        """执行耗时（秒）"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    @property
    def can_retry(self) -> bool:
        """是否可以重试"""
        return self.retry_count < self.max_retries and self.status == TaskStatus.FAILED


class TaskQueue:
    """任务队列管理器"""
    
    def __init__(self):
        self._tasks: Dict[str, Task] = {}
        self._pending: list[str] = []  # 待执行
        self._running: set[str] = set()  # 执行中
        self._callbacks: Dict[str, list[Callable]] = {}  # 回调函数
    
    def add(self, task: Task) -> str:
        """添加任务"""
        self._tasks[task.id] = task
        self._pending.append(task.id)
        return task.id
    
    def get(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        return self._tasks.get(task_id)
    
    def next(self) -> Optional[Task]:
        """获取下一个待执行任务"""
        if not self._pending:
            return None
        task_id = self._pending.pop(0)
        task = self._tasks.get(task_id)
        if task:
            self._running.add(task_id)
        return task
    
    def complete(self, task_id: str, result: Dict[str, Any]):
        """任务完成"""
        if task_id in self._running:
            self._running.remove(task_id)
        task = self._tasks.get(task_id)
        if task:
            task.mark_success(result)
            self._notify_callbacks(task_id, "complete", result)
    
    def fail(self, task_id: str, error: str):
        """任务失败"""
        if task_id in self._running:
            self._running.remove(task_id)
        task = self._tasks.get(task_id)
        if task:
            task.mark_failed(error)
            self._notify_callbacks(task_id, "failed", error)
    
    def cancel(self, task_id: str) -> bool:
        """取消任务"""
        task = self._tasks.get(task_id)
        if not task:
            return False
        if task.status == TaskStatus.RUNNING:
            return False  # 运行中无法取消
        if task_id in self._pending:
            self._pending.remove(task_id)
        task.mark_cancelled()
        return True
    
    def on_complete(self, task_id: str, callback: Callable):
        """注册完成回调"""
        if task_id not in self._callbacks:
            self._callbacks[task_id] = []
        self._callbacks[task_id].append(callback)
    
    def _notify_callbacks(self, task_id: str, event: str, data: Any):
        """触发回调"""
        for callback in self._callbacks.get(task_id, []):
            try:
                callback(event, data)
            except Exception:
                pass
    
    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        limit: int = 100
    ) -> list[Task]:
        """列出任务"""
        tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        return sorted(tasks, key=lambda t: t.created_at, reverse=True)[:limit]
    
    @property
    def stats(self) -> Dict[str, int]:
        """队列统计"""
        return {
            "total": len(self._tasks),
            "pending": len(self._pending),
            "running": len(self._running),
            "completed": sum(1 for t in self._tasks.values() if t.status == TaskStatus.SUCCESS),
            "failed": sum(1 for t in self._tasks.values() if t.status == TaskStatus.FAILED),
        }
