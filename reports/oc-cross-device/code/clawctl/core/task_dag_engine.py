#!/usr/bin/env python3
"""
task_dag_engine.py — DAG 可视化执行引擎
DAG 定义 → 执行驱动 → 结果聚合 → Mermaid 可视化

支持：
  - 顺序执行 / 并行执行 / 条件分支 / 循环
  - 与 TaskManager / Notifier 无缝集成
  - Mermaid 图生成（可直接粘贴到 mermaid.live）
  - YAML / JSON 双向序列化
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger("clawctl.dag_engine")


# ─────────────────────────────────────────────────────────────────────────────
# 数据结构
# ─────────────────────────────────────────────────────────────────────────────

class NodeType(str, Enum):
    AGENT = "agent"          # OpenClaw Agent
    NOTIFICATION = "notification"  # 消息通知
    HTTP = "http"            # HTTP 请求
    CONDITION = "condition"  # 条件分支
    LOOP = "loop"            # 循环节点
    PARALLEL = "parallel"    # 并行网关


class NodeStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class DAGNode:
    id: str
    type: NodeType
    name: str = ""
    params: dict = field(default_factory=dict)
    depends_on: list[str] = field(default_factory=list)
    retry: int = 1                    # 重试次数
    timeout: int = 300                # 超时秒数
    status: NodeStatus = NodeStatus.PENDING
    result: Any = None
    error: str = ""
    start_time: float = 0
    end_time: float = 0

    @property
    def duration_ms(self) -> float:
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time) * 1000
        return 0


@dataclass
class DAGEdge:
    from_node: str
    to_node: str
    condition: str = ""   # Mermaid 条件描述


@dataclass
class DAG:
    name: str
    description: str = ""
    nodes: list[DAGNode] = field(default_factory=list)
    edges: list[DAGEdge] = field(default_factory=list)
    variables: dict[str, Any] = field(default_factory=dict)  # 跨节点共享变量
    max_parallel: int = 5

    def get_node(self, node_id: str) -> Optional[DAGNode]:
        for n in self.nodes:
            if n.id == node_id:
                return n
        return None

    def topological_sort(self) -> list[list[DAGNode]]:
        """
        返回拓扑分层：每层内节点可并行执行
        [
          [node_a, node_b],   ← 第 0 层：可并行
          [node_c],           ← 第 1 层
          [node_d],           ← 第 2 层
        ]
        """
        in_degree = {n.id: 0 for n in self.nodes}
        adj = {n.id: [] for n in self.nodes}

        for edge in self.edges:
            adj[edge.from_node].append(edge.to_node)
            in_degree[edge.to_node] += 1

        layers = []
        current = [n for n in self.nodes if in_degree[n.id] == 0]
        current_ids = set(n.id for n in current)

        while current:
            layers.append(list(current))
            next_layer = []
            for node in current:
                for target_id in adj[node.id]:
                    in_degree[target_id] -= 1
                    if in_degree[target_id] == 0 and target_id not in current_ids:
                        node_obj = self.get_node(target_id)
                        if node_obj:
                            next_layer.append(node_obj)
                            current_ids.add(target_id)
            current = next_layer

        return layers


@dataclass
class DAGExecution:
    dag: DAG
    execution_id: str = field(default_factory=lambda: f"dag-{uuid.uuid4().hex[:8]}")
    status: NodeStatus = NodeStatus.PENDING
    node_results: dict[str, Any] = field(default_factory=dict)
    start_time: float = 0
    end_time: float = 0
    total_nodes: int = 0
    success_nodes: int = 0
    failed_nodes: int = 0

    @property
    def duration_ms(self) -> float:
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time) * 1000
        return 0


# ─────────────────────────────────────────────────────────────────────────────
# 执行器基类
# ─────────────────────────────────────────────────────────────────────────────

class NodeExecutor(ABC):
    """节点执行器基类"""

    @abstractmethod
    async def execute(self, node: DAGNode, context: dict[str, Any]) -> Any:
        raise NotImplementedError


class AgentNodeExecutor(NodeExecutor):
    """Agent 节点执行器"""

    def __init__(self, task_manager: Any):
        self.task_manager = task_manager

    async def execute(self, node: DAGNode, context: dict[str, Any]) -> Any:
        params = {**node.params}
        # 注入前置节点结果
        for key, val in params.items():
            if isinstance(val, str) and val.startswith("$"):
                ref_id = val[1:]
                if ref_id in context:
                    params[key] = context[ref_id]
                elif "." in ref_id:
                    parts = ref_id.split(".", 1)
                    if parts[0] in context:
                        params[key] = context[parts[0]].get(parts[1], val)

        task_name = params.pop("task", node.name)
        task = self.task_manager.create_task(task_name, params=params)

        logger.info(f"[DAGEngine] 执行 Agent 节点: {node.id} → {task_name}")
        result = await self.task_manager.execute_task_async(task)
        return result


class NotificationNodeExecutor(NodeExecutor):
    """通知节点执行器"""

    def __init__(self, notifier: Any):
        self.notifier = notifier

    async def execute(self, node: DAGNode, context: dict[str, Any]) -> Any:
        from handlers.notify import Notification
        notif = Notification(
            title=node.params.get("title", f"DAG 节点: {node.name}"),
            content=node.params.get("content", str(context)),
            channel=node.params.get("channel", "dingtalk"),
        )
        success = self.notifier.send(notif)
        logger.info(f"[DAGEngine] 通知节点 {node.id} → {success}")
        return {"sent": success, "channel": notif.channel}


class ConditionNodeExecutor(NodeExecutor):
    """条件分支执行器"""

    async def execute(self, node: DAGNode, context: dict[str, Any]) -> bool:
        condition = node.params.get("condition", "")
        # 支持简单表达式: "analyze.confidence > 0.8"
        try:
            local_vars = {"context": context, **context}
            result = eval(condition, {"__builtins__": {}}, local_vars)
            logger.info(f"[DAGEngine] 条件节点 {node.id}: {condition} → {result}")
            return bool(result)
        except Exception as e:
            logger.warning(f"[DAGEngine] 条件求值失败 {node.id}: {e}，默认 False")
            return False


# ─────────────────────────────────────────────────────────────────────────────
# DAG 执行引擎
# ─────────────────────────────────────────────────────────────────────────────

class DAGEngine:
    """
    DAG 可视化执行引擎

    用法：
        engine = DAGEngine(task_manager, notifier)
        exec_result = await engine.execute(dag)
        mermaid = DAGVisualizer.to_mermaid(dag)
    """

    def __init__(
        self,
        task_manager: Any = None,
        notifier: Any = None,
    ):
        self.task_manager = task_manager
        self.notifier = notifier
        self._executors: dict[NodeType, NodeExecutor] = {
            NodeType.AGENT: AgentNodeExecutor(task_manager) if task_manager else None,
            NodeType.NOTIFICATION: NotificationNodeExecutor(notifier) if notifier else None,
            NodeType.CONDITION: ConditionNodeExecutor(),
        }

    def add_executor(self, node_type: NodeType, executor: NodeExecutor):
        self._executors[node_type] = executor

    async def execute(self, dag: DAG) -> DAGExecution:
        """执行完整 DAG，返回执行记录"""
        execution = DAGExecution(dag=dag)
        execution.start_time = time.time()
        execution.total_nodes = len(dag.nodes)

        context: dict[str, Any] = {**dag.variables}
        completed_ids: set[str] = set()

        layers = dag.topological_sort()
        logger.info(f"[DAGEngine] DAG '{dag.name}' 共 {len(layers)} 层，{len(dag.nodes)} 节点")

        for layer_idx, layer in enumerate(layers):
            logger.info(f"[DAGEngine] 执行第 {layer_idx} 层，共 {len(layer)} 节点")

            # 过滤已完成的 skip 节点
            tasks = []
            for node in layer:
                if node.id in completed_ids:
                    continue
                tasks.append(self._execute_node(node, context))

            if not tasks:
                continue

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for node, result in zip(layer, results):
                if isinstance(result, Exception):
                    node.status = NodeStatus.FAILED
                    node.error = str(result)
                    node.end_time = time.time()
                    execution.failed_nodes += 1
                    logger.error(f"[DAGEngine] 节点 {node.id} 失败: {result}")
                    # DAG 失败策略：立即中止
                    execution.status = NodeStatus.FAILED
                    execution.end_time = time.time()
                    return execution
                else:
                    node.status = NodeStatus.SUCCESS
                    node.result = result
                    node.end_time = time.time()
                    execution.node_results[node.id] = result
                    context[node.id] = result
                    completed_ids.add(node.id)
                    execution.success_nodes += 1

        execution.status = NodeStatus.SUCCESS
        execution.end_time = time.time()
        return execution

    async def _execute_node(self, node: DAGNode, context: dict[str, Any]) -> Any:
        """执行单个节点（带重试）"""
        executor = self._executors.get(node.type)
        if not executor:
            raise RuntimeError(f"未注册 {node.type} 类型的执行器")

        node.status = NodeStatus.RUNNING
        node.start_time = time.time()
        last_error = None

        for attempt in range(node.retry):
            try:
                result = await asyncio.wait_for(
                    executor.execute(node, context),
                    timeout=node.timeout,
                )
                return result
            except asyncio.TimeoutError:
                last_error = f"超时（{node.timeout}s）"
            except Exception as e:
                last_error = str(e)

            if attempt < node.retry - 1:
                wait = 2 ** attempt
                logger.warning(f"[DAGEngine] 节点 {node.id} 第 {attempt+1} 次失败，{wait}s 后重试")
                await asyncio.sleep(wait)

        raise RuntimeError(f"重试 {node.retry} 次后仍失败: {last_error}")


# ─────────────────────────────────────────────────────────────────────────────
# 可视化
# ─────────────────────────────────────────────────────────────────────────────

class DAGVisualizer:
    """生成 Mermaid / ASCII / JSON 格式的 DAG 描述"""

    @staticmethod
    def to_mermaid(dag: DAG) -> str:
        """生成 Mermaid 流程图"""
        lines = ["flowchart TD"]
        style_map: dict[str, str] = {}

        # 节点定义
        icon_map = {
            NodeType.AGENT: "🤖",
            NodeType.NOTIFICATION: "📨",
            NodeType.HTTP: "🌐",
            NodeType.CONDITION: "🔀",
            NodeType.LOOP: "🔄",
            NodeType.PARALLEL: "⚡",
        }

        for node in dag.nodes:
            icon = icon_map.get(node.type, "📦")
            label = f'{icon} {node.name or node.id}'
            safe_id = node.id.replace("-", "_")
            lines.append(f'    {safe_id}["{label}"]')
            style_map[node.type.value] = node.type.value

        lines.append("")

        # 边定义
        for edge in dag.edges:
            from_id = edge.from_node.replace("-", "_")
            to_id = edge.to_node.replace("-", "_")
            if edge.condition:
                lines.append(f'    {from_id} -->|"{edge.condition}"| {to_id}')
            else:
                lines.append(f'    {from_id} --> {to_id}')

        lines.append("")
        # 样式
        lines.append("    classDef agent fill:#e1f5fe,stroke:#01579b,color:#01579b")
        lines.append("    classDef notification fill:#f3e5f5,stroke:#4a148c,color:#4a148c")
        lines.append("    classDef http fill:#e8f5e9,stroke:#1b5e20,color:#1b5e20")
        lines.append("    classDef condition fill:#fff8e1,stroke:#f57f17,color:#f57f17")
        lines.append("    classDef loop fill:#fce4ec,stroke:#b71c1c,color:#b71c1c")
        lines.append("    classDef parallel fill:#f1f8e9,stroke:#33691e,color:#33691e")

        for node in dag.nodes:
            safe_id = node.id.replace("-", "_")
            lines.append(f'    class {safe_id} {node.type.value}')

        return "\n".join(lines)

    @staticmethod
    def to_ascii(dag: DAG) -> str:
        """生成 ASCII 树形图"""
        lines = [f"📋 {dag.name}", f"   {dag.description}", ""]
        layers = dag.topological_sort()
        for i, layer in enumerate(layers):
            prefix = "├── " if i < len(layers) - 1 else "└── "
            for j, node in enumerate(layer):
                p = prefix if i == len(layers) - 1 else "│   " if j < len(layer) - 1 else "    "
                status_icon = {
                    NodeStatus.SUCCESS: "✅",
                    NodeStatus.FAILED: "❌",
                    NodeStatus.RUNNING: "⏳",
                    NodeStatus.PENDING: "⭕",
                    NodeStatus.SKIPPED: "⏭",
                }.get(node.status, "⭕")
                lines.append(f"{prefix if j == 0 else p}{status_icon} [{node.type.value}] {node.name or node.id}")
                prefix = "│   "
        return "\n".join(lines)

    @staticmethod
    def to_json(dag: DAG) -> dict:
        """生成 JSON 格式 DAG 描述（供前端渲染）"""
        return {
            "name": dag.name,
            "description": dag.description,
            "nodes": [
                {
                    "id": n.id,
                    "type": n.type.value,
                    "name": n.name or n.id,
                    "params": n.params,
                    "depends_on": n.depends_on,
                }
                for n in dag.nodes
            ],
            "edges": [
                {"from": e.from_node, "to": e.to_node, "condition": e.condition}
                for e in dag.edges
            ],
            "mermaid": DAGVisualizer.to_mermaid(dag),
            "layers": len(dag.topological_sort()),
        }


# ─────────────────────────────────────────────────────────────────────────────
# 序列化器
# ─────────────────────────────────────────────────────────────────────────────

class DAGSerializer:
    """YAML / JSON ↔ DAG 对象"""

    @staticmethod
    def from_dict(data: dict) -> DAG:
        nodes = []
        for nd in data.get("nodes", []):
            node = DAGNode(
                id=nd["id"],
                type=NodeType(nd.get("type", "agent")),
                name=nd.get("name", nd["id"]),
                params=nd.get("params", {}),
                depends_on=nd.get("depends_on", []),
                retry=nd.get("retry", 1),
                timeout=nd.get("timeout", 300),
            )
            nodes.append(node)

        edges = []
        for node in nodes:
            for dep in node.depends_on:
                edges.append(DAGEdge(from_node=dep, to_node=node.id))

        return DAG(
            name=data.get("name", "Untitled"),
            description=data.get("description", ""),
            nodes=nodes,
            edges=edges,
            variables=data.get("variables", {}),
            max_parallel=data.get("max_parallel", 5),
        )

    @staticmethod
    def from_yaml(data: dict) -> DAG:
        return DAGSerializer.from_dict(data)

    def to_dict(self, dag: DAG) -> dict:
        return {
            "name": dag.name,
            "description": dag.description,
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
            "max_parallel": dag.max_parallel,
        }

    def to_yaml(self, dag: DAG) -> str:
        import yaml
        return yaml.dump(self.to_dict(dag), allow_unicode=True, default_flow_style=False)


# ─────────────────────────────────────────────────────────────────────────────
# 工具函数
# ─────────────────────────────────────────────────────────────────────────────

def build_dag_from_yaml(yml_path: str) -> DAG:
    """从 YAML 文件加载 DAG"""
    import yaml
    with open(yml_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return DAGSerializer.from_yaml(data)


def quick_dag(name: str, *node_specs: tuple) -> DAG:
    """
    快速构建 DAG（代码式）

    用法：
        dag = quick_dag(
            "AI日报",
            ("fetch",  NodeType.AGENT,        "info-fetcher",  []),
            ("analyze", NodeType.AGENT,       "tech-analyst",  ["fetch"]),
            ("report",  NodeType.AGENT,        "quick-report",  ["analyze"]),
            ("notify",  NodeType.NOTIFICATION, "dingtalk",      ["report"]),
        )
    """
    nodes = []
    for spec in node_specs:
        node_id, node_type, task_name, depends = spec
        nodes.append(DAGNode(
            id=node_id,
            type=NodeType(node_type),
            name=task_name,
            params={"task": task_name} if node_type in (NodeType.AGENT,) else {},
            depends_on=list(depends),
        ))

    edges = []
    for node in nodes:
        for dep in node.depends_on:
            edges.append(DAGEdge(from_node=dep, to_node=node.id))

    return DAG(name=name, nodes=nodes, edges=edges)


# ─────────────────────────────────────────────────────────────────────────────
# 测试
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    dag = quick_dag(
        "AI 日报流水线",
        ("fetch",    "agent",         "info-fetcher",  []),
        ("analyze",  "agent",         "tech-analyst",   ["fetch"]),
        ("report",   "agent",         "quick-report",   ["analyze"]),
        ("notify",   "notification",  "钉钉通知",       ["report"]),
    )

    print("=== Mermaid 图 ===")
    print(DAGVisualizer.to_mermaid(dag))
    print()
    print("=== ASCII 树形图 ===")
    print(DAGVisualizer.to_ascii(dag))
    print()
    print("=== JSON 描述 ===")
    import json
    print(json.dumps(DAGVisualizer.to_json(dag), indent=2, ensure_ascii=False))
