"""
ClawRemote - OpenClaw 跨设备远程控制核心模块

Core 模块提供：
- OpenClawClient: OpenClaw API 客户端
- Task: 任务定义
- Trigger: 触发器基类
- Auth: 认证模块
"""

from .client import OpenClawClient
from .task import Task, TaskManager, TaskStatus
from .trigger import Trigger, HTTPTrigger, CronTrigger, WebhookTrigger
from .auth import AuthManager, APIKey, KeyLevel

__all__ = [
    "OpenClawClient",
    "Task",
    "TaskManager",
    "TaskStatus",
    "Trigger",
    "HTTPTrigger",
    "CronTrigger",
    "WebhookTrigger",
    "AuthManager",
    "APIKey",
    "KeyLevel",
]
