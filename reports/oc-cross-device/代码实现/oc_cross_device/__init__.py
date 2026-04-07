"""
OpenClaw Cross-Device Control Framework v1.0.0
轻量级、安全的 OpenClaw 远程控制框架
"""

__version__ = "1.0.0"

from .core.client import OpenClawClient
from .core.task import Task, TaskStatus
from .core.trigger import Trigger, HTTPTrigger, CronTrigger, WebhookTrigger
from .core.auth import Auth, APIKey, KeyLevel

__all__ = [
    "OpenClawClient",
    "Task", "TaskStatus",
    "Trigger", "HTTPTrigger", "CronTrigger", "WebhookTrigger",
    "Auth", "APIKey", "KeyLevel"
]
