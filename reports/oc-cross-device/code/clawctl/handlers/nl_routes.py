#!/usr/bin/env python3
"""
自然语言任务路由
POST /api/v1/nl  — 一句话说清楚要什么，NL Interpreter 自动解析 + 执行
GET  /api/v1/nl/preview — 预览解析结果（不执行）
GET  /api/v1/nl/intents — 列出支持的意图列表
"""

import logging
from flask import Blueprint, request, jsonify

logger = logging.getLogger(__name__)

nl_bp = Blueprint("nl", __name__, url_prefix="/api/v1/nl")

# 全局引用（server.py 注入）
_nl_executor = None
_interpreter = None


def get_nl_blueprint():
    """返回已初始化的 blueprint（供 server.py 注册）"""
    return nl_bp


def init_nl_routes(nl_executor, interpreter):
    global _nl_executor, _interpreter
    _nl_executor = nl_executor
    _interpreter = interpreter


# ── 核心端点 ─────────────────────────────────────────────────────────────────

@nl_bp.route("", methods=["POST"])
def nl_execute():
    """
    自然语言 → 自动执行

    Body (JSON):
        text: str       自然语言输入
        channel: str    通知渠道 (dingtalk/telegram/feishu)

    Returns:
        JSON { success, intent, task_id, message }
    """
    data = request.get_json() or {}
    text = (data.get("text") or "").strip()
    channel = data.get("channel", "dingtalk")

    if not text:
        return jsonify({"success": False, "message": "text 为空"}), 400

    result = _nl_executor.execute(text, channel=channel)

    status = 200 if result.get("success") else (500 if result.get("error") else 400)
    return jsonify(result), status


@nl_bp.route("/preview", methods=["POST"])
def nl_preview():
    """
    预览解析结果（不执行）

    Body (JSON):
        text: str

    Returns:
        JSON ParsedIntent
    """
    data = request.get_json() or {}
    text = (data.get("text") or "").strip()

    if not text:
        return jsonify({"success": False, "message": "text 为空"}), 400

    parsed = _interpreter.parse(text)

    return jsonify({
        "success": True,
        "intent": {
            "value": parsed.intent.value,
            "confidence": parsed.confidence,
        },
        "agent": parsed.agent,
        "template": parsed.template,
        "params": parsed.params,
        "urgency": parsed.urgency.value,
        "notify": parsed.notify,
        "notify_channel": parsed.notify_channel,
        "reply_wanted": parsed.reply_wanted,
        "time_hint": parsed.time_hint.isoformat() if parsed.time_hint else None,
        "error": parsed.error,
    })


@nl_bp.route("/intents", methods=["GET"])
def nl_intents():
    """
    列出所有支持的意图及示例

    Returns:
        JSON { intents: [{ value, label, description, keywords }] }
    """
    from ..core.nl_interpreter import INTENT_PATTERNS, Intent

    INTENT_META = {
        Intent.TRIGGER_REPORT: ("📊 生成报告", "生成今日简报/周报，汇总信息"),
        Intent.TRIGGER_SCAN: ("🔍 全量扫描", "全面抓取所有信息源最新动态"),
        Intent.TRIGGER_ANALYSIS: ("🧠 技术/商业分析", "分析某个技术趋势或商业机会"),
        Intent.TRIGGER_FETCH: ("📰 资讯抓取", "获取今日AI新闻和大厂动态"),
        Intent.TRIGGER_SEARCH: ("🔎 搜索查询", "搜索某个主题的最新信息"),
        Intent.SEND_MESSAGE: ("📨 发送消息", "给OpenClaw发一条消息"),
        Intent.ASK_QUESTION: ("💬 提问", "问OpenClaw一个问题"),
        Intent.QUERY_STATUS: ("🏥 系统状态", "查看OpenClaw运行状态"),
        Intent.QUERY_TASK: ("📋 任务查询", "查看任务执行进度"),
        Intent.QUERY_HISTORY: ("📜 历史记录", "查看最近的任务记录"),
        Intent.CANCEL_TASK: ("❌ 取消任务", "取消一个正在运行的任务"),
        Intent.PAUSE_SCHEDULE: ("⏸ 暂停定时", "暂停某个定时任务"),
        Intent.RESUME_SCHEDULE: ("▶️ 恢复定时", "恢复某个定时任务"),
        Intent.UNKNOWN: ("❓ 未知", "未能识别的意图"),
    }

    intents_list = []
    for intent, (label, desc) in INTENT_META.items():
        intents_list.append({
            "value": intent.value,
            "label": label,
            "description": desc,
            "keywords": INTENT_PATTERNS.get(intent, [])[:5],
        })

    return jsonify({
        "success": True,
        "intents": intents_list,
        "tip": "直接 POST /api/v1/nl 发送自然语言即可自动解析并执行"
    })


@nl_bp.route("/batch", methods=["POST"])
def nl_batch():
    """
    批量自然语言解析

    Body (JSON):
        texts: list[str]

    Returns:
        JSON { results: [ParsedIntent, ...] }
    """
    data = request.get_json() or {}
    texts = data.get("texts", [])

    if not texts or not isinstance(texts, list):
        return jsonify({"success": False, "message": "需要提供 texts 数组"}), 400

    results = _interpreter.parse_batch(texts)

    return jsonify({
        "success": True,
        "results": [
            {
                "raw": r.raw,
                "intent": r.intent.value,
                "confidence": r.confidence,
                "agent": r.agent,
                "template": r.template,
                "params": r.params,
            }
            for r in results
        ]
    })
