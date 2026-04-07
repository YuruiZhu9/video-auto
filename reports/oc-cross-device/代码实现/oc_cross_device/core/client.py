"""OpenClaw API 客户端封装"""
import httpx
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class OpenClawClient:
    """OpenClaw Gateway HTTP API 客户端"""
    
    def __init__(
        self,
        base_url: str = "http://localhost:18789",
        api_key: Optional[str] = None,
        timeout: float = 60.0,
        retry: int = 3
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.retry = retry
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers=self._build_headers()
        )
    
    def _build_headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "oc-cross-device/1.0"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    async def _request(
        self,
        method: str,
        path: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict:
        url = f"{self.base_url}{path}"
        for attempt in range(self.retry):
            try:
                response = await self._client.request(
                    method=method, url=url, json=data, params=params
                )
                response.raise_for_status()
                return response.json()
            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                if attempt == self.retry - 1:
                    raise
                logger.warning(f"请求失败 (尝试 {attempt + 1}/{self.retry}): {e}")
        return {}
    
    async def send_message(self, channel: str, message: str, **kwargs) -> Dict:
        """发送消息到指定渠道"""
        return await self._request(
            "POST", "/api/send",
            data={"channel": channel, "message": message, **kwargs}
        )
    
    async def spawn_agent(
        self,
        task: str,
        agent: Optional[str] = None,
        runtime: str = "subagent",
        **kwargs
    ) -> Dict:
        """触发子 Agent 执行任务"""
        payload = {"task": task, "runtime": runtime, **kwargs}
        if agent:
            payload["agentId"] = agent
        return await self._request("POST", "/api/spawn", data=payload)
    
    async def get_status(self) -> Dict:
        """获取 OpenClaw 状态"""
        return await self._request("GET", "/api/status")
    
    async def get_sessions(self, limit: int = 10) -> List[Dict]:
        """获取会话列表"""
        result = await self._request("GET", "/api/sessions", params={"limit": limit})
        return result.get("sessions", [])
    
    async def get_session_history(self, session_key: str, limit: int = 50) -> List[Dict]:
        """获取会话历史"""
        result = await self._request(
            "GET", f"/api/sessions/{session_key}/history",
            params={"limit": limit}
        )
        return result.get("messages", [])
    
    async def send_to_session(self, session_key: str, message: str) -> Dict:
        """向指定会话发送消息"""
        return await self._request(
            "POST", f"/api/sessions/{session_key}/send",
            data={"message": message}
        )
    
    async def close(self):
        """关闭客户端连接"""
        await self._client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
