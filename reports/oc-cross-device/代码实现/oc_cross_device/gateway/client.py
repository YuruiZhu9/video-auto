"""
OpenClaw Gateway WebSocket Protocol Client
基于 OpenClaw Gateway Protocol v3 实现
文档: /app/openclaw/docs/gateway/protocol.md
"""

import asyncio
import json
import logging
import uuid
import hashlib
import hmac
import time
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Callable, List
from enum import Enum
import websockets
from websockets.asyncio.client import connect as ws_connect

logger = logging.getLogger(__name__)


class ClientRole(Enum):
    OPERATOR = "operator"
    NODE = "node"


class ClientMode(Enum):
    OPERATOR = "operator"
    WEB = "web"
    CLI = "cli"


@dataclass
class GatewayConfig:
    """Gateway 连接配置"""
    host: str = "localhost"
    port: int = 18789
    token: str = ""           # Operator token from config
    use_tls: bool = False
    timeout: int = 30


class GatewayProtocol:
    """
    OpenClaw Gateway WebSocket 协议客户端
    
    支持的操作:
    - operator.read: 读取状态、会话、配置
    - operator.write: 发送消息、触发任务
    """
    
    def __init__(self, config: GatewayConfig):
        self.config = config
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.connected = False
        self._pending: Dict[str, asyncio.Future] = {}
        self._ listeners: List[Callable] = []
        self._receive_task: Optional[asyncio.Task] = None
        self.protocol_version: int = 3
        self._id_counter = 0
    
    def _next_id(self) -> str:
        self._id_counter += 1
        return f"req-{self._id_counter}-{int(time.time() * 1000)}"
    
    async def connect(self) -> bool:
        """建立 WebSocket 连接并完成握手"""
        scheme = "wss" if self.config.use_tls else "ws"
        url = f"{scheme}://{self.config.host}:{self.config.port}/"
        
        try:
            self.ws = await ws_connect(
                url,
                ping_interval=20,
                ping_timeout=10,
                open_timeout=self.config.timeout
            )
            logger.info(f"WebSocket 连接已建立: {url}")
            
            # 启动接收循环
            self._receive_task = asyncio.create_task(self._receive_loop())
            
            # 处理握手挑战
            connected = await self._wait_for_hello()
            self.connected = connected
            return connected
            
        except Exception as e:
            logger.error(f"连接失败: {e}")
            return False
    
    async def _wait_for_hello(self) -> bool:
        """等待并处理 hello-ok 响应"""
        try:
            msg = await asyncio.wait_for(self.ws.get(), timeout=self.config.timeout)
            data = json.loads(msg)
            
            if data.get("type") == "event" and data.get("event") == "connect.challenge":
                # 收到挑战，发送 connect 请求
                nonce = data.get("payload", {}).get("nonce", "")
                await self._send_connect(nonce)
                
                # 等待 hello-ok
                hello_msg = await asyncio.wait_for(self.ws.get(), timeout=self.config.timeout)
                hello_data = json.loads(hello_msg)
                
                if hello_data.get("type") == "res" and hello_data.get("payload", {}).get("type") == "hello-ok":
                    self.protocol_version = hello_data.get("payload", {}).get("protocol", 3)
                    logger.info(f"握手成功，协议版本: {self.protocol_version}")
                    return True
            
            return False
            
        except asyncio.TimeoutError:
            logger.error("握手超时")
            return False
    
    async def _send_connect(self, nonce: str):
        """发送 connect 请求"""
        req_id = self._next_id()
        
        connect_params = {
            "minProtocol": 3,
            "maxProtocol": 3,
            "client": {
                "id": "clawctl",
                "version": "1.0.0",
                "platform": "linux",
                "mode": "operator"
            },
            "role": "operator",
            "scopes": ["operator.read", "operator.write"],
            "caps": [],
            "commands": [],
            "permissions": {},
            "locale": "zh-CN",
            "userAgent": "clawctl/1.0.0"
        }
        
        # 如果有 token，添加到 auth
        if self.config.token:
            connect_params["auth"] = {"token": self.config.token}
        
        payload = {
            "type": "req",
            "id": req_id,
            "method": "connect",
            "params": connect_params
        }
        
        await self.ws.send(json.dumps(payload))
    
    async def _receive_loop(self):
        """接收消息循环"""
        try:
            async for msg in self.ws:
                await self._handle_message(json.loads(msg))
        except websockets.ConnectionClosed:
            logger.warning("WebSocket 连接已关闭")
        except Exception as e:
            logger.error(f"接收消息异常: {e}")
        finally:
            self.connected = False
    
    async def _handle_message(self, msg: Dict[str, Any]):
        """处理接收到的消息"""
        msg_type = msg.get("type")
        
        if msg_type == "res":
            # 响应消息
            req_id = msg.get("id")
            if req_id in self._pending:
                fut = self._pending.pop(req_id)
                if not fut.done():
                    fut.set_result(msg)
        
        elif msg_type == "event":
            # 事件消息
            event = msg.get("event", "")
            payload = msg.get("payload", {})
            logger.debug(f"收到事件: {event}")
            
            # 通知所有监听器
            for listener in self._listeners:
                try:
                    await listener(event, payload)
                except Exception as e:
                    logger.error(f"事件监听器异常: {e}")
        
        elif msg_type == "error":
            req_id = msg.get("id")
            if req_id in self._pending:
                fut = self._pending.pop(req_id)
                if not fut.done():
                    fut.set_exception(Exception(msg.get("error", "Unknown error")))
    
    async def _send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """发送请求并等待响应"""
        if not self.connected or not self.ws:
            raise ConnectionError("Gateway 未连接")
        
        req_id = self._next_id()
        payload = {
            "type": "req",
            "id": req_id,
            "method": method,
            "params": params or {}
        }
        
        fut = asyncio.Future()
        self._pending[req_id] = fut
        
        try:
            await self.ws.send(json.dumps(payload))
            result = await asyncio.wait_for(fut, timeout=self.config.timeout)
            return result
        except asyncio.TimeoutError:
            self._pending.pop(req_id, None)
            raise TimeoutError(f"请求 {method} 超时")
    
    def add_listener(self, listener: Callable):
        """添加事件监听器"""
        self._listeners.append(listener)
    
    # ========== Gateway API 方法 ==========
    
    async def status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return await self._send_request("gateway.status")
    
    async def sessions_list(self, active_minutes: int = None) -> Dict[str, Any]:
        """列出会话"""
        params = {}
        if active_minutes:
            params["activeMinutes"] = active_minutes
        return await self._send_request("sessions.list", params)
    
    async def sessions_history(self, session_key: str, limit: int = 20) -> Dict[str, Any]:
        """获取会话历史"""
        return await self._send_request("sessions.history", {
            "sessionKey": session_key,
            "limit": limit
        })
    
    async def message_send(self, channel: str, message: str, target: str = None,
                           channel_id: str = None) -> Dict[str, Any]:
        """发送消息"""
        params = {
            "channel": channel,
            "message": message
        }
        if target:
            params["target"] = target
        if channel_id:
            params["channelId"] = channel_id
        return await self._send_request("message.send", params)
    
    async def agent_spawn(self, task: str, agent_id: str = None,
                          runtime: str = "subagent", **kwargs) -> Dict[str, Any]:
        """触发 Agent"""
        params = {
            "task": task,
            "runtime": runtime
        }
        if agent_id:
            params["agentId"] = agent_id
        params.update(kwargs)
        return await self._send_request("agent.spawn", params)
    
    async def agent_send(self, session_key: str, message: str) -> Dict[str, Any]:
        """向会话发送消息"""
        return await self._send_request("agent.send", {
            "sessionKey": session_key,
            "message": message
        })
    
    async def exec_run(self, command: str, workdir: str = "/workspace") -> Dict[str, Any]:
        """执行命令"""
        return await self._send_request("exec.run", {
            "command": command,
            "workdir": workdir
        })
    
    async def config_get(self) -> Dict[str, Any]:
        """获取配置"""
        return await self._send_request("config.get")
    
    async def close(self):
        """关闭连接"""
        if self._receive_task:
            self._receive_task.cancel()
        if self.ws:
            await self.ws.close()
        self.connected = False
        logger.info("Gateway 连接已关闭")


# ========== 便捷客户端 ==========

class OpenClawGateway:
    """
    OpenClaw Gateway 高级客户端
    封装常见操作，自动处理连接管理
    """
    
    def __init__(self, config: GatewayConfig):
        self.config = config
        self.protocol = GatewayProtocol(config)
        self._connected = False
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, *args):
        await self.close()
    
    async def connect(self) -> bool:
        self._connected = await self.protocol.connect()
        return self._connected
    
    async def close(self):
        await self.protocol.close()
        self._connected = False
    
    @property
    def is_connected(self) -> bool:
        return self._connected and self.protocol.connected
    
    async def send_message(self, channel: str, message: str, **kwargs) -> Dict[str, Any]:
        """发送消息"""
        return await self.protocol.message_send(channel, message, **kwargs)
    
    async def spawn(self, task: str, agent_id: str = None, **kwargs) -> Dict[str, Any]:
        """触发 Agent"""
        return await self.protocol.agent_spawn(task, agent_id=agent_id, **kwargs)
    
    async def status(self) -> Dict[str, Any]:
        """获取状态"""
        return await self.protocol.status()
    
    async def sessions(self, active_minutes: int = 60) -> Dict[str, Any]:
        """列出会话"""
        return await self.protocol.sessions_list(active_minutes)
    
    async def exec(self, command: str, workdir: str = "/workspace") -> Dict[str, Any]:
        """执行命令"""
        return await self.protocol.exec_run(command, workdir)
    
    async def chat_send(self, session_key: str, message: str) -> Dict[str, Any]:
        """向会话发送消息"""
        return await self.protocol.agent_send(session_key, message)


async def create_gateway(host: str = "localhost", port: int = 18789,
                          token: str = "") -> OpenClawGateway:
    """创建 Gateway 客户端的便捷函数"""
    config = GatewayConfig(host=host, port=port, token=token)
    return OpenClawGateway(config)
