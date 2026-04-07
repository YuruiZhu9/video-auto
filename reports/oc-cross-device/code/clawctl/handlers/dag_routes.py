#!/usr/bin/env python3
"""
DAG 任务编排 API 路由
挂载到 /api/v1/dag/*
"""

import logging
from flask import Blueprint, request, jsonify, g

logger = logging.getLogger(__name__)

dag_bp = Blueprint("dag", __name__, url_prefix="/api/v1/dag")

# 全局引用（由 server.py 启动时注入）
_task_manager = None
_client = None
_auth_mgr = None
_notify_mgr = None
_sse_manager = None
_dag_manager = None
_template_loader = None


def init_dag_routes(
    task_manager,
    client,
    auth_mgr,
    notify_mgr,
    sse_manager,
    dag_manager,
    template_loader,
):
    global _task_manager, _client, _auth_mgr
    global _notify_mgr, _sse_manager, _dag_manager, _template_loader
    _task_manager = task_manager
    _client = client
    _auth_mgr = auth_mgr
    _notify_mgr = notify_mgr
    _sse_manager = sse_manager
    _dag_manager = dag_manager
    _template_loader = template_loader


def _require_exec(f):
    """EXEC 权限装饰器"""
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        key_level = getattr(g, "key_level", None)
        if key_level not in ("exec", "admin"):
            return jsonify({"error": "需要 exec/admin 权限"}), 403
        return f(*args, **kwargs)
    return wrapper


@dag_bp.route("/", methods=["GET"])
def list_dags():
    """列出所有 DAG 实例"""
    dags = _dag_manager.list_dags()
    return jsonify({"dags": dags, "total": len(dags)})


@dag_bp.route("/", methods=["POST"])
@_require_exec
def create_dag():
    """
    创建新 DAG

    POST /api/v1/dag/
    Body: {
        "name": "晨间简报",
        "template": "morning-brief",   # 可选：预定义模板
        "nodes": [                     # 可选：自定义节点
            {"id": "fetch", "template": "info-fetcher", "deps": []},
            {"id": "analyze", "template": "tech-analyst", "deps": ["fetch"]},
        ]
    }
    """
    body = request.get_json() or {}
    name = body.get("name", "未命名DAG")
    template = body.get("template")
    nodes = body.get("nodes", [])

    dag = _dag_manager.create(name=name, template=template)

    # 添加自定义节点（覆盖模板）
    for node in nodes:
        dag.add_node(
            node_id=node["id"],
            task_template=node.get("template", node.get("task_template", "")),
            name=node.get("name"),
            params=node.get("params", {}),
            deps=node.get("deps", []),
            max_retries=node.get("max_retries", 2),
        )

    errors = dag.validate()
    if errors:
        return jsonify({"error": "DAG 校验失败", "details": errors}), 400

    return jsonify({
        "dag_id": dag.dag_id,
        "name": dag.name,
        "total_nodes": len(dag.nodes),
        "execution_order": dag.get_execution_order(),
        "message": f"DAG '{name}' 创建成功",
    }), 201


@dag_bp.route("/<dag_id>", methods=["GET"])
def get_dag(dag_id):
    """获取 DAG 详情"""
    dag = _dag_manager.get(dag_id)
    if not dag:
        return jsonify({"error": f"DAG {dag_id} 不存在"}), 404
    return jsonify(dag.to_dict())


@dag_bp.route("/<dag_id>", methods=["DELETE"])
@_require_exec
def delete_dag(dag_id):
    """删除 DAG 实例"""
    ok = _dag_manager.delete(dag_id)
    if not ok:
        return jsonify({"error": f"DAG {dag_id} 不存在"}), 404
    return jsonify({"message": f"DAG {dag_id} 已删除"})


@dag_bp.route("/<dag_id>/execute", methods=["POST"])
@_require_exec
def execute_dag(dag_id):
    """
    执行 DAG（异步）

    POST /api/v1/dag/{dag_id}/execute
    Body: {"max_parallel": 3, "timeout": 3600}
    """
    dag = _dag_manager.get(dag_id)
    if not dag:
        return jsonify({"error": f"DAG {dag_id} 不存在"}), 404
    if dag._running:
        return jsonify({"error": "DAG 已在执行中"}), 409

    body = request.get_json() or {}
    max_parallel = body.get("max_parallel", 3)
    timeout = body.get("timeout")  # 秒

    # 设置回调
    def on_node_start(node):
        if _sse_manager:
            _sse_manager.emit_task_update({
                "type": "dag_node_start",
                "dag_id": dag_id,
                "node_id": node.id,
                "node_name": node.name,
            })

    def on_node_done(node):
        if _sse_manager:
            _sse_manager.emit_task_update({
                "type": "dag_node_done",
                "dag_id": dag_id,
                "node_id": node.id,
                "status": node.status.value,
                "duration_ms": node.duration_ms(),
            })

    def on_dag_done(dag):
        if _sse_manager:
            _sse_manager.emit_task_update({
                "type": "dag_complete",
                "dag_id": dag_id,
                "summary": {
                    "success": len(dag.successful_nodes()),
                    "failed": len(dag.failed_nodes()),
                },
            })
        # 钉钉通知
        if _notify_mgr and dag.failed_nodes():
            _notify_mgr.send_alert(
                f"DAG {dag.name} 执行完成",
                f"成功 {len(dag.successful_nodes())}，失败 {len(dag.failed_nodes())}",
            )

    dag.set_callbacks(on_node_start, on_node_done, on_dag_done)

    # 构造执行器：使用 TaskManager 或 OpenClaw Client
    def executor(node):
        template_id = node.task_template
        # 查找模板
        tpl = None
        if _template_loader:
            for t in _template_loader.list().values():
                if t.get("id") == template_id or t.get("name") == template_id:
                    tpl = t
                    break
        # 透传给 OpenClaw（通过 Client）
        task_desc = node.params.get("task_desc", tpl.get("params", {}).get("task", f"执行 {node.name}") if tpl else f"执行 {node.name}")
        try:
            result = _client.spawn_agent(
                task=task_desc,
                runtime=node.params.get("runtime", "subagent"),
                timeout=node.params.get("timeout", 600),
            )
            return result
        except Exception as e:
            logger.error(f"DAG 节点 {node.id} 执行异常: {e}")
            raise

    # 异步执行（不阻塞请求）
    import threading
    t = threading.Thread(target=dag.execute, args=(executor, max_parallel, timeout), daemon=True)
    t.start()

    return jsonify({
        "dag_id": dag_id,
        "status": "started",
        "message": f"DAG '{dag.name}' 开始执行，共 {len(dag.nodes)} 个节点",
        "execution_order": dag.get_execution_order(),
    })


@dag_bp.route("/<dag_id>/cancel", methods=["POST"])
@_require_exec
def cancel_dag(dag_id):
    """取消 DAG 执行"""
    dag = _dag_manager.get(dag_id)
    if not dag:
        return jsonify({"error": f"DAG {dag_id} 不存在"}), 404
    dag.cancel()
    return jsonify({"message": f"DAG {dag_id} 已取消", "status": dag.is_complete()})


@dag_bp.route("/<dag_id>/nodes", methods=["GET"])
def get_dag_nodes(dag_id):
    """获取 DAG 所有节点"""
    dag = _dag_manager.get(dag_id)
    if not dag:
        return jsonify({"error": f"DAG {dag_id} 不存在"}), 404
    return jsonify({
        "nodes": [n.to_dict() for n in dag.nodes.values()],
        "execution_order": dag.get_execution_order(),
    })


@dag_bp.route("/templates", methods=["GET"])
def dag_templates():
    """获取预定义 DAG 模板列表"""
    templates = {
        "morning-brief": {
            "id": "morning-brief",
            "name": "晨间简报",
            "description": "抓取 → 分析 → 生成简报（三步串行）",
            "nodes": [
                {"id": "fetch", "template": "info-fetcher", "name": "信息抓取", "deps": []},
                {"id": "analyze", "template": "tech-analyst", "name": "技术分析", "deps": ["fetch"]},
                {"id": "report", "template": "quick-report", "name": "生成简报", "deps": ["analyze"]},
            ],
        },
        "deep-research": {
            "id": "deep-research",
            "name": "深度研究",
            "description": "并行抓取 → 综合分析 → 详细报告（五步）",
            "nodes": [
                {"id": "fetch_ai", "template": "info-fetcher", "name": "AI动态抓取", "deps": []},
                {"id": "fetch_rec", "template": "info-fetcher", "name": "推荐系统抓取", "deps": []},
                {"id": "fetch_market", "template": "market-insight", "name": "商业洞察", "deps": []},
                {"id": "synthesize", "template": "tech-analyst", "name": "综合分析", "deps": ["fetch_ai", "fetch_rec", "fetch_market"]},
                {"id": "report", "template": "quick-report", "name": "深度报告", "deps": ["synthesize"]},
            ],
        },
        "ai-news-daily": {
            "id": "ai-news-daily",
            "name": "每日AI新闻",
            "description": "快速抓取 → 生成日报（两步）",
            "nodes": [
                {"id": "quick_fetch", "template": "info-fetcher", "name": "快速抓取", "deps": []},
                {"id": "brief", "template": "quick-report", "name": "生成日报", "deps": ["quick_fetch"]},
            ],
        },
    }
    return jsonify({"templates": templates})
