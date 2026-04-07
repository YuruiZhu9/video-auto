"""
OpenClaw API 客户端

封装对 OpenClaw Gateway 的所有 API 调用：
- 会话管理（spawn/send/list）
- 消息发送
- 状态查询
- 配置管理
"""

import os
import httpx
import asyncio
from typing import Optional, Any
from dataclasses import dataclass


@dataclass
class OpenClawConfig:
    """OpenClaw 连接配置"""
    gateway_url: str = "http://localhost:18789"
    api_key: Optional[str] = None  # 从环境变量 OPENCLAW_API_KEY 读取

    def __post_init__(self):
        if self.api_key is None:
            self.api_key = os.environ.get("OPENCLAW_API_KEY", "")


class OpenClawClient:
    """
    OpenClaw Gateway API 客户端
    
    用法示例：
    
    ```python
    client = OpenClawClient(
        gateway_url="http://localhost:18789",
        api_key="your-api-key"
    )
    
    # 发送消息到钉钉
    result = await client.send_message(
        channel="dingtalk",
        target="03003745585526383319",
        message="Hello from ClawRemote!"
    )
    
    # 触发子 Agent
    result = await client.spawn_agent(
        task="帮我生成今日技术简报",
        agent="tech-analyst"
    )
    ```
    """

    def __init__(self, config: Optional[OpenClawConfig] = None, **kwargs):
        self.config = config or OpenClawConfig(**kwargs)
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def base_url(self) -> str:
        return self.config.gateway_url.rstrip("/")

    @property
    def headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.headers,
                timeout=60.0,
            )
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def send_message(
        self,
        channel: str,
        message: str,
        target: Optional[str] = None,
        **kwargs
    ) -> dict:
        """发送消息到指定渠道"""
        client = await self._get_client()
        payload = {
            "action": "send",
            "channel": channel,
            "message": message,
            **{k: v for k, v in kwargs.items() if v is not None},
        }
        if target:
            payload["target"] = target
        resp = await client.post("/message", json=payload)
        resp.raise_for_status()
        return resp.json()

    async def spawn_agent(
        self,
        task: str,
        agent: Optional[str] = None,
        runtime: str = "subagent",
        timeout_seconds: int = 300,
        label: Optional[str] = None,
        **kwargs
    ) -> dict:
        """触发一个新的子 Agent 会话"""
        client = await self._get_client()
        payload = {
            "task": task,
            "runtime": runtime,
            "runTimeoutSeconds": timeout_seconds,
            **{k: v for k, v in kwargs.items() if v is not None},
        }
        if agent:
            payload["agentId"] = agent
        if label:
            payload["label"] = label
        resp = await client.post("/sessions/spawn", json=payload)
        resp.raise_for_status()
        return resp.json()

    async def sessions_list(
        self,
        kinds: Optional[list] = None,
        limit: int = 20,
        message_limit: int = 0,
    ) -> dict:
        """列出当前会话"""
        client = await self._get_client()
        params = {"limit": limit, "messageLimit": message_limit}
        if kinds:
            params["kinds"] = ",".join(kinds)
        resp = await client.get("/sessions/list", params=params)
        resp.raise_for_status()
        return resp.json()

    async def sessions_history(
        self,
        session_key: str,
        limit: int = 50,
        include_tools: bool = False,
    ) -> dict:
        """获取会话历史"""
        client = await self._get_client()
        resp = await client.get(
            f"/sessions/{session_key}/history",
            params={"limit": limit, "includeTools": include_tools},
        )
        resp.raise_for_status()
        return resp.json()

    async def sessions_send(
        self,
        session_key: str,
        message: str,
        timeout_seconds: int = 60,
    ) -> dict:
        """向指定会话发送消息"""
        client = await self._get_client()
        payload = {
            "sessionKey": session_key,
            "message": message,
            "timeoutSeconds": timeout_seconds,
        }
        resp = await client.post("/sessions/send", json=payload)
        resp.raise_for_status()
        return resp.json()

    async def get_status(self) -> dict:
        """获取 Gateway 状态"""
        client = await self._get_client()
        resp = await client.get("/status")
        resp.raise_for_status()
        return resp.json()

    async def health_check(self) -> bool:
        """检查 Gateway 是否可达"""
        try:
            await self.get_status()
            return True
        except Exception:
            return False

    async def config_get(self) -> dict:
        """获取 Gateway 配置"""
        client = await self._get_client()
        resp = await client.get("/gateway/config")
        resp.raise_for_status()
        return resp.json()

    async def config_patch(self, raw: dict, note: str = "") -> dict:
        """更新 Gateway 配置"""
        client = await self._get_client()
        payload = {"raw": raw, "note": note}
        resp = await client.post("/gateway/config/patch", json=payload)
        resp.raise_for_status()
        return resp.json()

    async def subagents_list(self) -> dict:
        """列出正在运行的子 Agent"""
        client = await self._get_client()
        resp = await client.get("/subagents/list")
        resp.raise_for_status()
        return resp.json()

    async def subagents_steer(self, target: str, message: str) -> dict:
        """向子 Agent 发送指令"""
        client = await self._get_client()
        payload = {"target": target, "message": message}
        resp = await client.post("/subagents/steer", json=payload)
        resp.raise_for_status()
        return resp.json()

    async def subagents_kill(self, target: str) -> dict:
        """终止子 Agent"""
        client = await self._get_client()
        payload = {"target": target}
        resp = await client.post("/subagents/kill", json=payload)
        resp.raise_for_status()
        return resp.json()
