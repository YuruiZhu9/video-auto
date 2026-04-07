"""ClawRemote — OpenClaw 跨设备远程控制框架"""

from .cli import main
from .server import main as server_main

__version__ = "1.0.0"
__all__ = ["main", "server_main"]
