#!/usr/bin/env python3
"""
OpenClaw HTTP API 客户端
封装与 OpenClaw Gateway 的所有通信
"""

import json
import logging
import time
from typing import Any, Optional
from dataclasses import dataclass
from datetime import datetime

import requests

logger = logging.getLogger(__name__)


@dataclass
class ClawResponse:
    """OpenClaw API 响应"""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    status_code: int = 200


class OpenClawClient:
    """
    OpenClaw API 客户端
    
    支持：
    - 发送消息到指定渠道
    - 触发 Agent 执行任务
    - 查询系统状态
    - 获取会话历史
    """

    def __init__(
        self,
        base_url: str = "http://localhost:18789",
        api_key: Optional[str] = None,
        timeout: int = 30,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._session = requests.Session()
        if api_key:
            self._session.headers.update({"Authorization": f"Bearer {api_key}"})

    # ── 基础请求 ────────────────────────────────────────────────

    def _request(
        self,
        method: str,
        path: str,
        data: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> ClawResponse:
        """发送 HTTP 请求到 OpenClaw Gateway"""
        url = f"{self.base_url}{path}"
        try:
            resp = self._session.request(
                method,
                url,
                json=data,
                params=params,
                timeout=self.timeout,
            )
            if resp.status_code == 200:
                result = resp.json() if resp.content else {}
                return ClawResponse(success=True, data=result, status_code=200)
            else:
                return ClawResponse(
                    success=False,
                    error=resp.text,
                    status_code=resp.status_code,
                )
        except requests.exceptions.Timeout:
            return ClawResponse(success=False, error="请求超时", status_code=408)
        except requests.exceptions.ConnectionError:
            return ClawResponse(
                success=False,
                error=f"无法连接到 {self.base_url}，请确认 OpenClaw Gateway 运行中",
                status_code=503,
            )
        except Exception as e:
            logger.exception("OpenClaw API 请求失败")
            return ClawResponse(success=False, error=str(e), status_code=500)

    # ── 核心 API ────────────────────────────────────────────────

    def get_status(self) -> ClawResponse:
        """获取 OpenClaw 系统状态"""
        return self._request("GET", "/status")

    def get_sessions(self, limit: int = 10) -> ClawResponse:
        """获取会话列表"""
        return self._request("GET", "/sessions/list", params={"limit": limit})

    def get_session_history(
        self,
        session_key: str,
        limit: int = 20,
    ) -> ClawResponse:
        """获取指定会话的历史消息"""
        return self._request(
            "GET",
            f"/sessions/{session_key}/history",
            params={"limit": limit},
        )

    def send_message(
        self,
        channel: str,
        message: str,
        **kwargs,
    ) -> ClawResponse:
        """
        发送消息到指定渠道
        
        Args:
            channel: 渠道名称 (dingtalk/telegram/signal 等)
            message: 消息内容
            **kwargs: 额外参数
        """
        payload = {"channel": channel, "message": message, **kwargs}
        return self._request("POST", "/message/send", data=payload)

    def send_sessions_message(
        self,
        session_key: str,
        message: str,
    ) -> ClawResponse:
        """向指定会话发送消息（跨会话）"""
        payload = {"sessionKey": session_key, "message": message}
        return self._request("POST", "/sessions/send", data=payload)

    def spawn_agent(
        self,
        task: str,
        agent_id: Optional[str] = None,
        runtime: str = "subagent",
        run_timeout: int = 300,
        **kwargs,
    ) -> ClawResponse:
        """
        触发子 Agent 执行任务
        
        Args:
            task: 任务描述（prompt）
            agent_id: 指定 Agent ID（留空使用默认）
            runtime: subagent | acp
            run_timeout: 超时时间（秒）
            **kwargs: 额外参数
        """
        payload = {
            "task": task,
            "agentId": agent_id,
            "runtime": runtime,
            "runTimeoutSeconds": run_timeout,
            **kwargs,
        }
        return self._request("POST", "/sessions/spawn", data=payload)

    def trigger_template(
        self,
        template_name: str,
        params: Optional[dict] = None,
    ) -> ClawResponse:
        """触发预设任务模板"""
        payload = {"template": template_name, "params": params or {}}
        return self._request("POST", "/tasks/trigger", data=payload)

    # ── 便捷方法 ────────────────────────────────────────────────

    def quick_report(self, scope: str = "brief") -> ClawResponse:
        """快捷：生成简报"""
        task_map = {
            "brief": "生成今日 AI 资讯简报，重点关注大模型和推荐系统",
            "full": "执行全量信息抓取，生成详细分析报告",
            "market": "分析 AI 商业应用动态，发现新机会",
        }
        task = task_map.get(scope, task_map["brief"])
        return self.spawn_agent(task=task, runtime="subagent")

    def check_health(self) -> bool:
        """健康检查"""
        resp = self.get_status()
        return resp.success

    def __repr__(self) -> str:
        return f"<OpenClawClient base_url={self.base_url}>"
