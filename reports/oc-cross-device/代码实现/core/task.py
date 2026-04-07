"""
任务定义与任务管理器

Task: 单个任务的抽象定义
TaskManager: 任务队列管理 + 执行引擎
TaskStatus: 任务状态枚举
TaskTemplate: 任务模板
"""

import uuid
import time
import asyncio
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Optional, Callable, Awaitable
from datetime import datetime


class TaskStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """
    任务单元
    
    Attributes:
        name: 任务名称（来自模板或手动指定）
        action: 执行动作（spawn/send/message/...)
        params: 执行参数
        status: 当前状态
        task_id: 唯一标识
        created_at: 创建时间
        started_at: 开始执行时间
        completed_at: 完成时间
        result: 执行结果
        session_key: 关联的 OpenClaw 会话
        notify_channels: 结果推送渠道
    """
    name: str
    action: str
    params: dict = field(default_factory=dict)
    status: TaskStatus = TaskStatus.QUEUED
    task_id: str = field(default_factory=lambda: f"t_{uuid.uuid4().hex[:12]}")
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[dict] = None
    session_key: Optional[str] = None
    notify_channels: list = field(default_factory=lambda: ["dingtalk"])
    error: Optional[str] = None
    progress: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["status"] = self.status.value
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        data = data.copy()
        if "status" in data and isinstance(data["status"], str):
            data["status"] = TaskStatus(data["status"])
        return cls(**data)


@dataclass
class TaskTemplate:
    """任务模板"""
    name: str
    display_name: str
    description: str = ""
    action: str = "spawn"
    agent: Optional[str] = None
    params_schema: dict = field(default_factory=dict)
    params: dict = field(default_factory=dict)
    notify_on_complete: bool = True
    notify_channels: list = field(default_factory=lambda: ["dingtalk"])

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "TaskTemplate":
        return cls(**data)


class TaskManager:
    """
    任务管理器
    
    负责任务的：
    - 入队与调度
    - 状态跟踪
    - OpenClaw Client 执行
    - 结果收集与推送
    
    用法：
    ```python
    tm = TaskManager(oc_client, notify_manager)
    
    # 创建任务（从模板）
    task = await tm.create_from_template("daily_brief", {"scope": "tech"})
    
    # 直接创建
    task = await tm.create(name="my_task", action="spawn", 
                            params={"task": "生成报告", "agent": "tech-analyst"})
    
    # 查询状态
    status = await tm.get_status("t_abc123")
    
    # 取消
    await tm.cancel("t_abc123")
    
    # 列出最近任务
    tasks = await tm.list_tasks(limit=20)
    ```
    """

    def __init__(
        self,
        oc_client,
        notify_manager,
        templates: Optional[dict] = None,
    ):
        self.oc_client = oc_client
        self.notify = notify_manager
        self.templates: dict[str, TaskTemplate] = {}
        self.tasks: dict[str, Task] = {}
        self._lock = asyncio.Lock()
        self._running_tasks: dict[str, asyncio.Task] = {}

        if templates:
            for name, data in templates.items():
                self.templates[name] = TaskTemplate(name=name, **data)

    # ─── 模板管理 ───────────────────────────────────────────

    def list_templates(self) -> list[dict]:
        return [t.to_dict() for t in self.templates.values()]

    def get_template(self, name: str) -> Optional[TaskTemplate]:
        return self.templates.get(name)

    def add_template(self, template: TaskTemplate):
        self.templates[template.name] = template

    def remove_template(self, name: str) -> bool:
        return self.templates.pop(name, None) is not None

    # ─── 任务创建 ───────────────────────────────────────────

    async def create_from_template(
        self,
        template_name: str,
        params: Optional[dict] = None,
        notify_channels: Optional[list] = None,
    ) -> Task:
        """从模板创建任务"""
        template = self.templates.get(template_name)
        if not template:
            raise ValueError(f"模板不存在: {template_name}")

        merged_params = {**template.params, **(params or {})}
        task = Task(
            name=template_name,
            action=template.action,
            params=merged_params,
            notify_channels=notify_channels or template.notify_channels,
        )
        if template.agent:
            task.params["agent"] = template.agent

        await self._enqueue(task)
        return task

    async def create(
        self,
        name: str,
        action: str,
        params: dict,
        notify_channels: Optional[list] = None,
    ) -> Task:
        """直接创建任务"""
        task = Task(
            name=name,
            action=action,
            params=params,
            notify_channels=notify_channels or ["dingtalk"],
        )
        await self._enqueue(task)
        return task

    async def _enqueue(self, task: Task):
        """任务入队"""
        async with self._lock:
            self.tasks[task.task_id] = task
        await self._schedule(task)

    async def _schedule(self, task: Task):
        """调度任务执行"""
        async def run():
            await self._execute(task)

        coro = asyncio.create_task(run())
        self._running_tasks[task.task_id] = coro

    # ─── 任务执行 ───────────────────────────────────────────

    async def _execute(self, task: Task):
        """执行单个任务"""
        try:
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now().isoformat()

            await self._notify_task_start(task)

            if task.action == "spawn":
                result = await self._execute_spawn(task)
            elif task.action == "send":
                result = await self._execute_send(task)
            elif task.action == "message":
                result = await self._execute_message(task)
            else:
                raise ValueError(f"未知动作: {task.action}")

            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now().isoformat()
            task.result = result

            await self._notify_task_complete(task)

        except asyncio.CancelledError:
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.now().isoformat()
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now().isoformat()
            task.error = str(e)
            await self._notify_task_failed(task)
        finally:
            self._running_tasks.pop(task.task_id, None)

    async def _execute_spawn(self, task: Task) -> dict:
        """执行 spawn 动作：触发子 Agent"""
        params = task.params.copy()
        task_text = params.pop("task", params.pop("prompt", ""))
        agent = params.pop("agent", None)
        runtime = params.pop("runtime", "subagent")
        timeout = params.pop("timeout", 300)

        result = await self.oc_client.spawn_agent(
            task=task_text,
            agent=agent,
            runtime=runtime,
            timeout_seconds=timeout,
            label=f"clawremote:{task.task_id}",
            **params
        )
        task.session_key = result.get("session_key")
        return result

    async def _execute_send(self, task: Task) -> dict:
        """执行 send 动作：向会话发送消息"""
        params = task.params.copy()
        session_key = params.pop("session_key")
        message = params.pop("message", "")
        return await self.oc_client.sessions_send(
            session_key=session_key,
            message=message,
            **params
        )

    async def _execute_message(self, task: Task) -> dict:
        """执行 message 动作：直接发消息"""
        params = task.params.copy()
        channel = params.pop("channel", "dingtalk")
        message = params.pop("message", "")
        target = params.pop("target", None)
        return await self.oc_client.send_message(
            channel=channel,
            message=message,
            target=target,
            **params
        )

    # ─── 通知 ───────────────────────────────────────────────

    async def _notify_task_start(self, task: Task):
        try:
            await self.notify.send("task_start", {
                "task_name": task.name,
                "task_id": task.task_id,
                "display_name": self.templates.get(task.name, {}).display_name or task.name,
                "timestamp": task.started_at,
            }, channels=task.notify_channels)
        except Exception:
            pass

    async def _notify_task_complete(self, task: Task):
        try:
            duration = None
            if task.started_at and task.completed_at:
                start = datetime.fromisoformat(task.started_at)
                end = datetime.fromisoformat(task.completed_at)
                duration = round((end - start).total_seconds())

            await self.notify.send("task_complete", {
                "task_name": task.name,
                "task_id": task.task_id,
                "display_name": self.templates.get(task.name, {}).display_name or task.name,
                "duration": duration,
                "result_summary": str(task.result)[:200] if task.result else "无",
            }, channels=task.notify_channels)
        except Exception:
            pass

    async def _notify_task_failed(self, task: Task):
        try:
            await self.notify.send("task_failed", {
                "task_name": task.name,
                "task_id": task.task_id,
                "display_name": self.templates.get(task.name, {}).display_name or task.name,
                "error": task.error,
            }, channels=task.notify_channels)
        except Exception:
            pass

    # ─── 任务查询 ───────────────────────────────────────────

    def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)

    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        limit: int = 20,
    ) -> list[Task]:
        tasks = list(self.tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        return tasks[:limit]

    async def cancel(self, task_id: str) -> bool:
        """取消任务"""
        task = self.tasks.get(task_id)
        if not task:
            return False
        if task.status == TaskStatus.RUNNING:
            coro = self._running_tasks.get(task_id)
            if coro:
                coro.cancel()
                return True
        elif task.status == TaskStatus.QUEUED:
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.now().isoformat()
            return True
        return False

    def get_stats(self) -> dict:
        """获取统计信息"""
        tasks = list(self.tasks.values())
        today = datetime.now().date().isoformat()
        today_tasks = [t for t in tasks if t.created_at.startswith(today)]
        return {
            "total": len(tasks),
            "queued": sum(1 for t in tasks if t.status == TaskStatus.QUEUED),
            "running": sum(1 for t in tasks if t.status == TaskStatus.RUNNING),
            "completed_today": sum(1 for t in today_tasks if t.status == TaskStatus.COMPLETED),
            "failed_today": sum(1 for t in today_tasks if t.status == TaskStatus.FAILED),
        }
