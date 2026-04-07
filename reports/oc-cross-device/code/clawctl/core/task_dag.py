#!/usr/bin/env python3
"""
任务依赖编排系统（Task DAG）
支持任务节点依赖图、拓扑排序、并行执行、状态传播

设计原则：
- 节点：TaskNode（代表一个可执行的子任务）
- 边：依赖关系（A 依赖 B 完成才启动）
- 支持分支、汇聚、并行、串行等多种拓扑
- 状态自动传播：上游失败 → 下游取消
"""

import uuid
import time
import logging
import threading
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, FIRST_COMPLETED, Future
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Callable, Any
from collections import deque

logger = logging.getLogger(__name__)


class NodeStatus(Enum):
    PENDING = "pending"       # 等待中（依赖未满足）
    READY = "ready"           # 就绪（依赖已满足，可执行）
    RUNNING = "running"        # 执行中
    SUCCESS = "success"        # 成功
    FAILED = "failed"          # 失败
    SKIPPED = "skipped"        # 跳过（上游失败导致）
    CANCELLED = "cancelled"    # 手动取消


@dataclass
class TaskNode:
    """
    DAG 中的一个任务节点

    attrs:
        id: 唯一标识
        name: 显示名称
        task_template: 任务模板ID（如 "tech-analyst"）
        params: 任务参数字典
        deps: 依赖的节点ID列表（这些节点要先完成）
        status: 当前状态
        result: 执行结果
        error: 错误信息
        started_at / completed_at: 时间戳
        retry: 最大重试次数
    """
    id: str
    name: str
    task_template: str
    params: Dict[str, Any] = field(default_factory=dict)
    deps: List[str] = field(default_factory=list)
    status: NodeStatus = NodeStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    retry: int = 0
    max_retries: int = 2

    def duration_ms(self) -> Optional[int]:
        if self.started_at and self.completed_at:
            return int((self.completed_at - self.started_at) * 1000)
        return None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "task_template": self.task_template,
            "params": self.params,
            "deps": self.deps,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration_ms": self.duration_ms(),
            "retry": self.retry,
            "max_retries": self.max_retries,
        }


class TaskDAG:
    """
    有向无环图（DAG）任务编排器

    使用拓扑排序自动解析依赖顺序，
    支持并行就绪节点批量执行，
    上游失败自动触发下游跳过。

    示例：
        dag = TaskDAG(name="AI晨间简报")
        dag.add_node("抓取", "info-fetcher", params={"scope": "today"})
        dag.add_node("分析", "tech-analyst", deps=["抓取"])
        dag.add_node("推送", "notify", deps=["分析"])
        dag.execute(executor)
    """

    def __init__(self, name: str = "DAG", dag_id: Optional[str] = None):
        self.dag_id = dag_id or uuid.uuid4().hex[:12]
        self.name = name
        self.nodes: Dict[str, TaskNode] = {}
        self.edges: Dict[str, Set[str]] = {}  # from -> {to, ...}
        self.reversed_edges: Dict[str, Set[str]] = {}  # to -> {from, ...}
        self._lock = threading.RLock()

        # 执行回调
        self._on_node_start: Optional[Callable[[TaskNode], None]] = None
        self._on_node_done: Optional[Callable[[TaskNode], None]] = None
        self._on_dag_done: Optional[Callable[["TaskDAG"], None]] = None

        # 执行状态
        self._running = False
        self._cancelled = False

    # ── 图构建 API ────────────────────────────────────────────────────────────

    def add_node(
        self,
        node_id: str,
        task_template: str,
        name: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        deps: Optional[List[str]] = None,
        max_retries: int = 2,
    ) -> "TaskDAG":
        """
        添加一个任务节点

        dag.add_node("节点ID", "tech-analyst",
                      name="技术分析",
                      params={"scope": "brief"},
                      deps=["前置节点ID"])
        """
        with self._lock:
            if node_id in self.nodes:
                raise ValueError(f"节点 {node_id} 已存在")
            node = TaskNode(
                id=node_id,
                name=name or node_id,
                task_template=task_template,
                params=params or {},
                deps=deps or [],
                max_retries=max_retries,
            )
            self.nodes[node_id] = node
            self.edges[node_id] = set()
            self.reversed_edges.setdefault(node_id, set())
            for dep in node.deps:
                self.reversed_edges.setdefault(dep, set())
                self.edges.setdefault(dep, set()).add(node_id)
        return self

    def add_edge(self, from_node: str, to_node: str) -> "TaskDAG":
        """添加依赖边：B 依赖 A 完成"""
        with self._lock:
            if from_node not in self.nodes or to_node not in self.nodes:
                raise KeyError(f"节点不存在: {from_node} → {to_node}")
            self.edges.setdefault(from_node, set()).add(to_node)
            self.reversed_edges.setdefault(to_node, set()).add(from_node)
            if from_node not in self.nodes[to_node].deps:
                self.nodes[to_node].deps.append(from_node)
        return self

    def validate(self) -> List[str]:
        """检测环并返回错误列表，空=有效 DAG"""
        errors = []
        # 检查缺失节点
        for nid, node in self.nodes.items():
            for dep in node.deps:
                if dep not in self.nodes:
                    errors.append(f"节点 '{nid}' 依赖 '{dep}'，但该节点不存在")
        # 检查环（DFS）
        visited = set()
        rec_stack = set()
        path = []

        def dfs(nid: str) -> bool:
            visited.add(nid)
            rec_stack.add(nid)
            path.append(nid)
            for nxt in self.edges.get(nid, []):
                if nxt not in visited:
                    if dfs(nxt):
                        return True
                elif nxt in rec_stack:
                    errors.append(f"检测到环: {' → '.join(path)} → {nxt}")
                    return True
            path.pop()
            rec_stack.remove(nid)
            return False

        for nid in self.nodes:
            if nid not in visited:
                dfs(nid)
        return errors

    # ── 拓扑分析 ──────────────────────────────────────────────────────────────

    def get_ready_nodes(self) -> List[TaskNode]:
        """返回所有就绪节点（依赖已满足 + 未执行）"""
        with self._lock:
            ready = []
            for node in self.nodes.values():
                if node.status not in (NodeStatus.PENDING, NodeStatus.READY):
                    continue
                # 检查依赖是否全部成功
                all_deps_done = all(
                    self.nodes[d].status in (NodeStatus.SUCCESS, NodeStatus.SKIPPED)
                    for d in node.deps
                )
                # 检查依赖是否有失败（不能继续）
                any_dep_failed = any(
                    self.nodes[d].status == NodeStatus.FAILED
                    for d in node.deps
                )
                if all_deps_done and not any_dep_failed:
                    if node.status == NodeStatus.PENDING:
                        node.status = NodeStatus.READY
                    ready.append(node)
            return ready

    def is_complete(self) -> bool:
        """所有节点是否处理完毕"""
        return all(
            n.status in (NodeStatus.SUCCESS, NodeStatus.FAILED,
                         NodeStatus.SKIPPED, NodeStatus.CANCELLED)
            for n in self.nodes.values()
        )

    def failed_nodes(self) -> List[TaskNode]:
        return [n for n in self.nodes.values() if n.status == NodeStatus.FAILED]

    def successful_nodes(self) -> List[TaskNode]:
        return [n for n in self.nodes.values() if n.status == NodeStatus.SUCCESS]

    # ── 执行引擎 ──────────────────────────────────────────────────────────────

    def set_callbacks(
        self,
        on_node_start: Optional[Callable[[TaskNode], None]] = None,
        on_node_done: Optional[Callable[[TaskNode], None]] = None,
        on_dag_done: Optional[Callable[["TaskDAG"], None]] = None,
    ):
        self._on_node_start = on_node_start
        self._on_node_done = on_node_done
        self._on_dag_done = on_dag_done

    def execute(
        self,
        executor: Callable[[TaskNode], Any],
        max_parallel: int = 3,
        timeout: Optional[int] = None,
    ) -> "TaskDAG":
        """
        执行 DAG

        executor: 同步或异步函数，签名为 executor(node: TaskNode) -> Any
                  同步函数在调用线程执行；
                  异步函数（async def）会在新线程中启动事件循环。
        max_parallel: 最大并发节点数
        timeout: DAG 总超时（秒），None=不限

        返回 self（链式调用）
        """
        errors = self.validate()
        if errors:
            raise ValueError(f"DAG 校验失败: {'; '.join(errors)}")

        self._running = True
        self._cancelled = False
        start_time = time.time()
        completed_count = 0
        total_nodes = len(self.nodes)

        logger.info(f"[DAG {self.dag_id}] 开始执行，共 {total_nodes} 个节点，最大并发 {max_parallel}")

        with ThreadPoolExecutor(max_workers=max_parallel) as pool:
            pending_futures: Dict[Future, TaskNode] = {}

            while not self.is_complete() and not self._cancelled:
                # 超时检查
                if timeout and (time.time() - start_time) > timeout:
                    logger.warning(f"[DAG {self.dag_id}] 超时，取消执行")
                    self.cancel()
                    break

                # 收集就绪节点
                ready = self.get_ready_nodes()
                for node in ready:
                    if self._cancelled:
                        break
                    logger.info(f"[DAG {self.dag_id}] 节点 {node.id} 就绪，提交执行")
                    node.status = NodeStatus.RUNNING
                    node.started_at = time.time()
                    if self._on_node_start:
                        try:
                            self._on_node_start(node)
                        except Exception as e:
                            logger.error(f"on_node_start 回调异常: {e}")

                    fut = pool.submit(self._run_node_sync, executor, node)
                    pending_futures[fut] = node

                # 等待任意一个完成
                if not pending_futures:
                    if not self.is_complete():
                        logger.warning(f"[DAG {self.dag_id}] 无就绪节点且未完成，疑似死锁")
                    break

                done_futs, _ = concurrent.futures.wait(
                    pending_futures.keys(),
                    timeout=5.0,
                    return_when=FIRST_COMPLETED,
                )

                for fut in done_futures:
                    node = pending_futures.pop(fut)
                    self._finish_node(node, fut)

                # 传播失败：标记下游为 SKIPPED
                self._propagate_failures()

        self._running = False
        logger.info(
            f"[DAG {self.dag_id}] 执行完毕 "
            f"成功={len(self.successful_nodes())} "
            f"失败={len(self.failed_nodes())} "
            f"跳过={sum(1 for n in self.nodes.values() if n.status == NodeStatus.SKIPPED)}"
        )
        if self._on_dag_done:
            try:
                self._on_dag_done(self)
            except Exception as e:
                logger.error(f"on_dag_done 回调异常: {e}")
        return self

    def _run_node_sync(self, executor: Callable, node: TaskNode) -> Any:
        """在线程池线程中执行节点，支持 async executor"""
        try:
            import asyncio
            result = executor(node)
            # 如果返回协程，在新事件循环中运行
            if asyncio.iscoroutine(result):
                loop = asyncio.new_event_loop()
                try:
                    return loop.run_until_complete(result)
                finally:
                    loop.close()
            return result
        except Exception as e:
            logger.error(f"节点 {node.id} 执行异常: {e}")
            raise

    def _finish_node(self, node: TaskNode, fut: Future):
        node.completed_at = time.time()
        try:
            result = fut.result()
            node.result = result
            if node.status == NodeStatus.RUNNING:
                node.status = NodeStatus.SUCCESS
            logger.info(f"[DAG {self.dag_id}] 节点 {node.id} 完成，耗时 {node.duration_ms()}ms")
        except Exception as e:
            node.error = str(e)
            if node.retry < node.max_retries:
                node.retry += 1
                node.status = NodeStatus.READY
                node.started_at = None
                node.completed_at = None
                logger.warning(f"[DAG {self.dag_id}] 节点 {node.id} 失败，将重试（第{node.retry}/{node.max_retries}次）")
            else:
                node.status = NodeStatus.FAILED
                logger.error(f"[DAG {self.dag_id}] 节点 {node.id} 最终失败: {e}")
        if self._on_node_done:
            try:
                self._on_node_done(node)
            except Exception as e:
                logger.error(f"on_node_done 回调异常: {e}")

    def _propagate_failures(self):
        """将因上游失败导致无法执行的节点标记为 SKIPPED（迭代传播）"""
        changed = True
        while changed:
            changed = False
            for node in self.nodes.values():
                if node.status in (NodeStatus.PENDING, NodeStatus.READY):
                    all_deps_done = all(
                        self.nodes[d].status not in (NodeStatus.PENDING, NodeStatus.READY, NodeStatus.RUNNING)
                        for d in node.deps
                    )
                    any_unavailable = any(
                        self.nodes[d].status in (NodeStatus.FAILED, NodeStatus.SKIPPED, NodeStatus.CANCELLED)
                        for d in node.deps
                    )
                    if all_deps_done and any_unavailable:
                        node.status = NodeStatus.SKIPPED
                        node.error = f"上游依赖 {'/'.join(node.deps)} 不可用"
                        node.completed_at = time.time()
                        logger.info(f"[DAG {self.dag_id}] 节点 {node.id} 因上游失败被跳过")
                        changed = True

    def cancel(self):
        """取消 DAG 执行"""
        self._cancelled = True
        for node in self.nodes.values():
            if node.status in (NodeStatus.PENDING, NodeStatus.READY, NodeStatus.RUNNING):
                node.status = NodeStatus.CANCELLED
                node.completed_at = time.time()

    def get_execution_order(self) -> List[str]:
        """返回拓扑排序后的节点ID列表"""
        in_degree = {nid: len(self.reversed_edges.get(nid, [])) for nid in self.nodes}
        queue = deque([nid for nid, d in in_degree.items() if d == 0])
        order = []
        while queue:
            nid = queue.popleft()
            order.append(nid)
            for nxt in self.edges.get(nid, []):
                in_degree[nxt] -= 1
                if in_degree[nxt] == 0:
                    queue.append(nxt)
        return order

    def to_dict(self) -> dict:
        return {
            "dag_id": self.dag_id,
            "name": self.name,
            "total_nodes": len(self.nodes),
            "running": self._running,
            "complete": self.is_complete(),
            "nodes": {nid: n.to_dict() for nid, n in self.nodes.items()},
            "execution_order": self.get_execution_order(),
            "summary": {
                "success": len(self.successful_nodes()),
                "failed": len(self.failed_nodes()),
                "skipped": sum(1 for n in self.nodes.values() if n.status == NodeStatus.SKIPPED),
            },
        }


# ── DAG Manager ───────────────────────────────────────────────────────────────

class DAGManager:
    """
    DAG 全局管理器：注册、管理、追踪所有 DAG 实例
    """

    def __init__(self):
        self._dags: Dict[str, TaskDAG] = {}
        self._lock = threading.RLock()

    def create(
        self,
        name: str,
        dag_id: Optional[str] = None,
        template: Optional[str] = None,
    ) -> TaskDAG:
        """
        创建新 DAG，支持模板快捷创建
        template: 预定义模板 ID
        """
        dag = TaskDAG(name=name, dag_id=dag_id)
        # 预定义模板
        if template == "morning-brief":
            # 晨间简报：抓取 → 分析 → 推送
            dag.add_node("fetch", "info-fetcher",
                          name="信息抓取",
                          params={"scope": "today", "sources": ["bocha", "aibase", "techcrunch"]})
            dag.add_node("analyze", "tech-analyst",
                          name="技术分析",
                          deps=["fetch"],
                          params={"scope": "brief"})
            dag.add_node("report", "quick-report",
                          name="生成简报",
                          deps=["analyze"],
                          params={"format": "markdown"})
        elif template == "deep-research":
            # 深度研究：并行抓取多个来源 → 综合分析 → 报告
            dag.add_node("fetch_ai", "info-fetcher",
                          name="AI动态抓取",
                          params={"topics": ["大模型", "AI应用"]})
            dag.add_node("fetch_rec", "info-fetcher",
                          name="推荐系统抓取",
                          params={"topics": ["推荐系统", "算法"]})
            dag.add_node("fetch_market", "market-insight",
                          name="商业洞察",
                          deps=[])
            dag.add_node("synthesize", "tech-analyst",
                          name="综合分析",
                          deps=["fetch_ai", "fetch_rec", "fetch_market"],
                          params={"depth": "deep"})
            dag.add_node("report", "quick-report",
                          name="深度报告",
                          deps=["synthesize"],
                          params={"format": "detailed"})
        elif template == "ai-news-daily":
            # 每日AI新闻：快速抓取 → 简报
            dag.add_node("quick_fetch", "info-fetcher",
                          name="快速抓取",
                          params={"scope": "today", "fast": True})
            dag.add_node("brief", "quick-report",
                          name="生成日报",
                          deps=["quick_fetch"],
                          params={"format": "daily"})
        elif template is not None:
            logger.warning(f"未知 DAG 模板: {template}")

        with self._lock:
            self._dags[dag.dag_id] = dag
        logger.info(f"[DAGManager] 创建 DAG: {dag.dag_id} ({name})，模板: {template}")
        return dag

    def get(self, dag_id: str) -> Optional[TaskDAG]:
        with self._lock:
            return self._dags.get(dag_id)

    def list_dags(self) -> List[dict]:
        with self._lock:
            return [
                {
                    "dag_id": d.dag_id,
                    "name": d.name,
                    "total_nodes": len(d.nodes),
                    "running": d._running,
                    "complete": d.is_complete(),
                    "summary": {
                        "success": len(d.successful_nodes()),
                        "failed": len(d.failed_nodes()),
                    },
                }
                for d in self._dags.values()
            ]

    def delete(self, dag_id: str) -> bool:
        with self._lock:
            if dag_id in self._dags:
                del self._dags[dag_id]
                return True
            return False


# 全局单例
_dag_manager: Optional[DAGManager] = None
_dag_lock = threading.Lock()


def get_dag_manager() -> DAGManager:
    global _dag_manager
    if _dag_manager is None:
        with _dag_lock:
            if _dag_manager is None:
                _dag_manager = DAGManager()
    return _dag_manager
