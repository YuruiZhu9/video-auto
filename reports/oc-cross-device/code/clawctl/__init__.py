#!/usr/bin/env python3
"""
clawctl - OpenClaw 跨设备控制框架
"""

from .core.client import OpenClawClient
from .core.task import TaskManager, TaskStatus
from .core.auth import AuthManager, APIKey, KeyLevel
from .core.config import Config
from .core.scheduler import Scheduler
from .core.template_loader import TemplateLoader
from .core.database import TaskDatabase, TaskRecord
from .core.multi_instance import (
    MultiInstanceManager, InstanceInfo, InstanceStatus,
    MultiInstanceClient, CircuitBreaker, LoadBalanceStrategy,
    get_multi_instance_manager, init_multi_instance_manager,
)
from .core.monitor import (
    MonitoringManager, AlertRule, Alert, SystemSnapshot, MetricPoint,
    get_monitoring_manager, init_monitoring,
)

__version__ = "2.4.0"
__all__ = [
    "OpenClawClient",
    "TaskManager", "TaskStatus",
    "AuthManager", "APIKey", "KeyLevel",
    "Config", "Scheduler", "TemplateLoader", "TaskDatabase", "TaskRecord",
    "MultiInstanceManager", "InstanceInfo", "InstanceStatus",
    "MultiInstanceClient", "CircuitBreaker", "LoadBalanceStrategy",
    "MonitoringManager", "AlertRule", "Alert", "SystemSnapshot", "MetricPoint",
    "get_multi_instance_manager", "init_multi_instance_manager",
    "get_monitoring_manager", "init_monitoring",
]
