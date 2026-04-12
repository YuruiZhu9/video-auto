#!/usr/bin/env python3
"""
dag_market.py — 工作流模板市场
内置 5 个黄金工作流 + 用户自定义工作流注册/发现/执行

API:
  GET  /api/v1/workflows              列出所有工作流（含 Mermaid）
  GET  /api/v1/workflows/{id}        工作流详情
  POST /api/v1/workflows/{id}/execute 执行工作流
  GET  /api/v1/workflows/{id}/runs   历史执行记录
  GET  /api/v1/workflows/{id}/visualize 获取 Mermaid 图
  POST /api/v1/workflows              注册自定义工作流（YAML/JSON）
  DELETE /api/v1/workflows/{id}       删除工作流
"""

from __future__ import annotations

import logging
import json
import time
import threading
import os
from pathlib import Path
from typing import Any, Optional

from core.task_dag_engine import (
    DAG, DAGEngine, DAGVisualizer, DAGSerializer,
    NodeType, NodeStatus, quick_dag, build_dag_from_yaml,
)

logger = logging.getLogger("clawctl.dag_market")


# ─────────────────────────────────────────────────────────────────────────────
# 内置黄金工作流模板
# ─────────────────────────────────────────────────────────────────────────────

BUILTIN_WORKFLOWS: dict[str, dict] = {
    "ai-daily-report": {
        "name": "AI 日报生成流水线",
        "description": "信息抓取 → 技术分析 → 报告生成 → 钉钉推送，全自动完成",
        "icon": "📋",
        "tags": ["日常", "自动化", "推荐系统"],
        "dag": quick_dag(
            "AI 日报生成流水线",
            ("fetch",    "agent",         "info-fetcher",    []),
            ("analyze",  "agent",         "tech-analyst",    ["fetch"]),
            ("report",   "agent",         "quick-report",   ["analyze"]),
            ("notify",   "notification",  "钉钉通知",       ["report"]),
        ),
    },

    "market-full-scan": {
        "name": "市场全网扫描",
        "description": "全量信息抓取 → 竞品分析 → 商机发现 → 报告",
        "icon": "🔭",
        "tags": ["市场分析", "商机发现"],
        "dag": quick_dag(
            "市场全网扫描",
            ("scan",     "agent",         "info-fetcher",    []),
            ("analyze",  "agent",         "market-insight",  ["scan"]),
            ("compete",  "agent",         "tech-analyst",    ["scan"]),
            ("report",   "agent",         "quick-report",    ["analyze", "compete"]),
            ("notify",   "notification",  "钉钉通知",        ["report"]),
        ),
    },

    "job-market-weekly": {
        "name": "推荐算法就业市场周报",
        "description": "招聘数据抓取 → 薪资分析 → 技能图谱 → 趋势报告",
        "icon": "💼",
        "tags": ["求职", "推荐系统", "数据分析"],
        "dag": quick_dag(
            "推荐算法就业市场周报",
            ("fetch_jobs",   "agent",    "info-fetcher",    []),
            ("salary",       "agent",    "tech-analyst",    ["fetch_jobs"]),
            ("skills",       "agent",    "market-insight", ["fetch_jobs"]),
            ("report",       "agent",    "quick-report",   ["salary", "skills"]),
            ("notify",       "notification", "钉钉通知",   ["report"]),
        ),
    },

    "tech-deep-research": {
        "name": "技术深度研究",
        "description": "arXiv 论文 → 技术解析 → 趋势研判 → 深度报告",
        "icon": "🔬",
        "tags": ["技术研究", "论文", "深度分析"],
        "dag": quick_dag(
            "技术深度研究",
            ("fetch_papers", "agent",   "info-fetcher",    []),
            ("analyze",      "agent",   "tech-analyst",    ["fetch_papers"]),
            ("trends",       "agent",   "market-insight",  ["analyze"]),
            ("deep_report",  "agent",   "quick-report",    ["analyze", "trends"]),
            ("notify",       "notification", "钉钉通知",    ["deep_report"]),
        ),
    },

    "multi-agent-debate": {
        "name": "多 Agent 辩论分析",
        "description": "多路 Agent 同时分析 → 对抗式辩论 → 综合结论",
        "icon": "⚔️",
        "tags": ["多Agent", "深度思考", "综合分析"],
        "dag": quick_dag(
            "多 Agent 辩论分析",
            ("analyst_a",   "agent",    "tech-analyst",    []),
            ("analyst_b",   "agent",    "market-insight",  []),
            ("analyst_c",   "agent",    "info-fetcher",    []),
            ("debate",      "agent",    "quick-report",    ["analyst_a", "analyst_b", "analyst_c"]),
            ("conclusion",  "agent",    "quick-report",    ["debate"]),
            ("notify",      "notification", "钉钉通知",    ["conclusion"]),
        ),
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# 工作流市场
# ─────────────────────────────────────────────────────────────────────────────

class WorkflowMarket:
    """
    工作流模板市场

    提供：
      - 内置 5 个黄金工作流
      - 用户自定义工作流注册
      - 执行记录追踪
      - Mermaid 可视化
    """

    def __init__(self, dag_engine: DAGEngine = None):
        self.dag_engine = dag_engine or DAGEngine()
        self._workflows: dict[str, dict] = {}
        self._runs: dict[str, list[dict]] = {}   # workflow_id → 执行历史
        self._runs_lock = threading.Lock()
        self._load_builtin()
        self._load_user_workflows()

    def _load_builtin(self):
        for wid, w in BUILTIN_WORKFLOWS.items():
            self._workflows[wid] = {
                "id": wid,
                "name": w["name"],
                "description": w["description"],
                "icon": w["icon"],
                "tags": w["tags"],
                "dag": w["dag"],
                "builtin": True,
            }

    def _load_user_workflows(self):
        wf_dir = Path(__file__).parent.parent / "workflows"
        if not wf_dir.exists():
            wf_dir.mkdir(parents=True, exist_ok=True)
            return
        for f in wf_dir.glob("*.yaml"):
            try:
                dag = build_dag_from_yaml(str(f))
                wid = f.stem
                self._workflows[wid] = {
                    "id": wid,
                    "name": dag.name,
                    "description": dag.description,
                    "icon": "📦",
                    "tags": [],
                    "dag": dag,
                    "builtin": False,
                    "path": str(f),
                }
                logger.info(f"[WorkflowMarket] 加载用户工作流: {wid}")
            except Exception as e:
                logger.warning(f"[WorkflowMarket] 加载 {f} 失败: {e}")

    # ── 核心 API ───────────────────────────────────────────────────────────

    def list_workflows(self) -> list[dict]:
        """列出所有工作流（不含 DAG 详情，用于列表页）"""
        result = []
        for wid, w in self._workflows.items():
            dag = w["dag"]
            result.append({
                "id": wid,
                "name": w["name"],
                "description": w["description"],
                "icon": w["icon"],
                "tags": w["tags"],
                "builtin": w.get("builtin", False),
                "node_count": len(dag.nodes),
                "layer_count": len(dag.topological_sort()),
                "mermaid": DAGVisualizer.to_mermaid(dag),
            })
        return result

    def get_workflow(self, workflow_id: str) -> Optional[dict]:
        w = self._workflows.get(workflow_id)
        if not w:
            return None
        dag = w["dag"]
        return {
            **w,
            "dag": {
                "nodes": [
                    {
                        "id": n.id,
                        "type": n.type.value,
                        "name": n.name,
                        "params": n.params,
                        "depends_on": n.depends_on,
                        "retry": n.retry,
                        "timeout": n.timeout,
                    }
                    for n in dag.nodes
                ],
                "edges": [
                    {"from": e.from_node, "to": e.to_node, "condition": e.condition}
                    for e in dag.edges
                ],
                "variables": dag.variables,
            },
            "mermaid": DAGVisualizer.to_mermaid(dag),
            "ascii": DAGVisualizer.to_ascii(dag),
            "json": DAGVisualizer.to_json(dag),
        }

    async def execute_workflow(
        self,
        workflow_id: str,
        params: dict = None,
        notify_channel: str = "dingtalk",
    ) -> dict:
        """执行工作流"""
        w = self._workflows.get(workflow_id)
        if not w:
            raise ValueError(f"工作流不存在: {workflow_id}")

        dag = w["dag"]
        if params:
            dag.variables.update(params)

        logger.info(f"[WorkflowMarket] 执行工作流: {workflow_id}")
        exec_result = await self.dag_engine.execute(dag)

        # 记录执行历史
        record = {
            "execution_id": exec_result.execution_id,
            "workflow_id": workflow_id,
            "status": exec_result.status.value,
            "start_time": exec_result.start_time,
            "end_time": exec_result.end_time,
            "duration_ms": exec_result.duration_ms,
            "total_nodes": exec_result.total_nodes,
            "success_nodes": exec_result.success_nodes,
            "failed_nodes": exec_result.failed_nodes,
            "node_results": {
                k: str(v)[:200] for k, v in exec_result.node_results.items()
            },
        }

        with self._runs_lock:
            if workflow_id not in self._runs:
                self._runs[workflow_id] = []
            self._runs[workflow_id].insert(0, record)
            # 只保留最近 100 条
            self._runs[workflow_id] = self._runs[workflow_id][:100]

        return record

    def get_runs(self, workflow_id: str, limit: int = 20) -> list[dict]:
        with self._runs_lock:
            return list(self._runs.get(workflow_id, [])[:limit])

    def visualize_workflow(self, workflow_id: str, format: str = "mermaid") -> Optional[str]:
        w = self._workflows.get(workflow_id)
        if not w:
            return None
        dag = w["dag"]
        if format == "mermaid":
            return DAGVisualizer.to_mermaid(dag)
        elif format == "ascii":
            return DAGVisualizer.to_ascii(dag)
        elif format == "json":
            return json.dumps(DAGVisualizer.to_json(dag), indent=2, ensure_ascii=False)
        return DAGVisualizer.to_mermaid(dag)

    def register_workflow(self, workflow_data: dict) -> dict:
        """注册用户自定义工作流"""
        try:
            dag = DAGSerializer().from_dict(workflow_data)
        except Exception as e:
            raise ValueError(f"DAG 格式错误: {e}")

        wid = workflow_data.get("id") or dag.name.lower().replace(" ", "-")
        wf_path = Path(__file__).parent.parent / "workflows" / f"{wid}.yaml"
        wf_path.parent.mkdir(parents=True, exist_ok=True)
        wf_path.write_text(DAGSerializer().to_yaml(dag), encoding="utf-8")

        self._workflows[wid] = {
            "id": wid,
            "name": dag.name,
            "description": dag.description,
            "icon": "📦",
            "tags": workflow_data.get("tags", []),
            "dag": dag,
            "builtin": False,
            "path": str(wf_path),
        }
        logger.info(f"[WorkflowMarket] 注册工作流: {wid}")
        return {"id": wid, "name": dag.name, "status": "registered"}

    def delete_workflow(self, workflow_id: str) -> bool:
        w = self._workflows.get(workflow_id)
        if not w or w.get("builtin"):
            return False
        path = w.get("path")
        if path and os.path.exists(path):
            os.remove(path)
        del self._workflows[workflow_id]
        logger.info(f"[WorkflowMarket] 删除工作流: {workflow_id}")
        return True


# ─────────────────────────────────────────────────────────────────────────────
# 全局单例
# ─────────────────────────────────────────────────────────────────────────────

_market: Optional[WorkflowMarket] = None


def get_workflow_market() -> WorkflowMarket:
    global _market
    if _market is None:
        _market = WorkflowMarket()
    return _market


def init_workflow_market(dag_engine: DAGEngine = None) -> WorkflowMarket:
    global _market
    _market = WorkflowMarket(dag_engine)
    return _market
