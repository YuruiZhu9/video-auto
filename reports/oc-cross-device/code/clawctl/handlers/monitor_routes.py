#!/usr/bin/env python3
"""
监控与告警 API 路由
v2.4.0 新增
"""

import logging
from datetime import datetime
from typing import Optional

from flask import Blueprint, jsonify, request

logger = logging.getLogger(__name__)

monitor_bp = Blueprint("monitor", __name__, url_prefix="/api/v1/monitor")


def get_monitor():
    from . import get_monitoring_manager
    return get_monitoring_manager()


def get_multi_instance():
    from . import get_multi_instance_manager
    return get_multi_instance_manager()


# ── 指标查询 ─────────────────────────────────────────────────────

@monitor_bp.route("/snapshot", methods=["GET"])
def get_snapshot():
    """系统快照"""
    m = get_monitor()
    return jsonify({"success": True, "data": m.get_snapshot().to_dict()})


@monitor_bp.route("/series/<metric>", methods=["GET"])
def get_metric_series(metric: str):
    """指标时序数据"""
    m = get_monitor()
    minutes = request.args.get("minutes", 10, type=int)
    series = m.get_series(metric, minutes)
    return jsonify({"success": True, "metric": metric, "data": series})


@monitor_bp.route("/dashboard", methods=["GET"])
def get_dashboard():
    """Dashboard 汇总（一次拉取所有数据）"""
    m = get_monitor()
    return jsonify({"success": True, "data": m.get_dashboard_summary()})


@monitor_bp.route("/current/<metric>", methods=["GET"])
def get_current_metric(metric: str):
    """获取当前指标值"""
    m = get_monitor()
    value = m.get_current_value(metric)
    return jsonify({"success": True, "metric": metric, "value": value})


# ── 告警规则 ─────────────────────────────────────────────────────

@monitor_bp.route("/alerts/rules", methods=["GET"])
def list_alert_rules():
    """列出告警规则"""
    m = get_monitor()
    return jsonify({"success": True, "data": m.list_rules()})


@monitor_bp.route("/alerts/rules", methods=["POST"])
def add_alert_rule():
    """添加告警规则"""
    m = get_monitor()
    from ..core.monitor import AlertRule
    data = request.json
    try:
        rule = AlertRule(
            id=data["id"],
            name=data["name"],
            metric=data["metric"],
            condition=data["condition"],
            threshold=float(data["threshold"]),
            severity=data.get("severity", "warning"),
            cooldown=int(data.get("cooldown", 300)),
            channels=data.get("channels", []),
        )
        m.add_rule(rule)
        return jsonify({"success": True, "rule": rule})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@monitor_bp.route("/alerts/rules/<rule_id>", methods=["DELETE"])
def delete_alert_rule(rule_id: str):
    """删除告警规则"""
    m = get_monitor()
    ok = m.remove_rule(rule_id)
    return jsonify({"success": ok})


@monitor_bp.route("/alerts/active", methods=["GET"])
def get_active_alerts():
    """获取当前告警"""
    m = get_monitor()
    return jsonify({"success": True, "data": m.get_active_alerts()})


@monitor_bp.route("/alerts/history", methods=["GET"])
def get_alert_history():
    """获取告警历史"""
    m = get_monitor()
    limit = request.args.get("limit", 50, type=int)
    return jsonify({"success": True, "data": m.get_alert_history(limit)})


@monitor_bp.route("/alerts/<rule_id>/ack", methods=["POST"])
def ack_alert(rule_id: str):
    """确认告警"""
    m = get_monitor()
    ok = m.acknowledge_alert(rule_id)
    return jsonify({"success": ok})


# ── 多实例管理 ─────────────────────────────────────────────────────

@monitor_bp.route("/instances", methods=["GET"])
def list_instances():
    """列出所有 OpenClaw 实例"""
    mgr = get_multi_instance()
    group = request.args.get("group")
    return jsonify({"success": True, "data": mgr.list_instances(group=group)})


@monitor_bp.route("/instances", methods=["POST"])
def register_instance():
    """注册新实例"""
    mgr = get_multi_instance()
    from ..core.multi_instance import InstanceInfo
    data = request.json
    try:
        info = InstanceInfo(
            id=data["id"],
            name=data["name"],
            base_url=data["base_url"],
            api_key=data["api_key"],
            group=data.get("group", "default"),
            tags=data.get("tags", []),
            max_concurrent=data.get("max_concurrent", 5),
        )
        mgr.register_instance(info)
        return jsonify({"success": True, "instance": info.to_dict()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@monitor_bp.route("/instances/<instance_id>", methods=["GET"])
def get_instance(instance_id: str):
    """获取实例详情"""
    mgr = get_multi_instance()
    info = mgr.get_instance(instance_id)
    if not info:
        return jsonify({"success": False, "error": "Instance not found"}), 404
    return jsonify({"success": True, "data": info.to_dict()})


@monitor_bp.route("/instances/<instance_id>", methods=["PATCH"])
def update_instance(instance_id: str):
    """更新实例"""
    mgr = get_multi_instance()
    data = request.json
    # 过滤非配置字段
    config_keys = ["name", "base_url", "api_key", "group", "tags", "max_concurrent", "enabled"]
    updates = {k: v for k, v in data.items() if k in config_keys}
    ok = mgr.update_instance(instance_id, **updates)
    return jsonify({"success": ok})


@monitor_bp.route("/instances/<instance_id>", methods=["DELETE"])
def unregister_instance(instance_id: str):
    """注销实例"""
    mgr = get_multi_instance()
    ok = mgr.unregister_instance(instance_id)
    return jsonify({"success": ok})


@monitor_bp.route("/instances/health-check", methods=["POST"])
def trigger_health_check():
    """手动触发健康检查"""
    mgr = get_multi_instance()
    mgr._run_health_check()
    return jsonify({"success": True})


@monitor_bp.route("/instances/select", methods=["POST"])
def select_instance():
    """根据策略选择最优实例"""
    mgr = get_multi_instance()
    data = request.json
    from ..core.multi_instance import LoadBalanceStrategy

    strategy_str = data.get("strategy", "round_robin")
    try:
        strategy = LoadBalanceStrategy(strategy_str)
    except ValueError:
        strategy = LoadBalanceStrategy.ROUND_ROBIN

    info = mgr.get_best_instance(
        group=data.get("group", "default"),
        strategy=strategy,
        required_capability=data.get("capability"),
    )
    if not info:
        return jsonify({"success": False, "error": "No healthy instance found"})
    return jsonify({"success": True, "data": info.to_dict()})
