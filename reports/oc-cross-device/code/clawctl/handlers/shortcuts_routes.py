#!/usr/bin/env python3
"""
Shortcuts Routes — iOS/Android 快捷指令 Flask 路由
支持 iOS 快捷指令"获取内容"动作和 Siri 语音触发

GET  /api/v1/shortcuts          快捷指令库
GET  /api/v1/shortcuts/library  完整快捷指令库 JSON
GET  /api/v1/shortcuts/{id}     单个快捷指令
POST /api/v1/shortcuts/parse    解析 clawctl:// URL
GET  /api/v1/shortcuts/cmd      iOS 快捷指令专用 GET 端点（核心集成点）
GET  /api/v1/shortcuts/mobile   移动端专用快捷指令列表（适配快捷指令 App）
"""

import os
import logging
from flask import Blueprint, request, jsonify, current_app

from .shortcuts import (
    get_default_templates,
    parse_clawctl_url,
    generate_ios_url_scheme,
    export_shortcut_library,
    export_ios_shortcuts_json,
    match_shortcut_for_intent,
)

logger = logging.getLogger("clawctl.routes.shortcuts")

shortcuts_bp = Blueprint("shortcuts", __name__, url_prefix="/api/v1/shortcuts")

_nl_executor = None


def init_shortcuts_routes(nl_executor):
    """注入 NL Executor 引用（供快捷指令执行使用）"""
    global _nl_executor
    _nl_executor = nl_executor


def _base_url():
    """推断 base_url"""
    forwarded = request.headers.get("X-Forwarded-Host")
    if forwarded:
        scheme = request.headers.get("X-Forwarded-Proto", "https")
        return f"{scheme}://{forwarded}"
    host = request.host_url.rstrip("/")
    return host


def _effective_key():
    """获取有效 API Key"""
    return request.args.get("api_key") or os.environ.get("CLAWCTL_DEFAULT_API_KEY", "")


# ── 端点实现 ───────────────────────────────────────────────────────────────

@shortcuts_bp.route("", methods=["GET"])
def list_shortcuts():
    """
    快捷指令库主端点

    iOS 快捷指令"获取内容"动作配置：
    - URL: https://your-server/api/v1/shortcuts
    - 方法: GET
    - 内容类型: JSON

    返回每个快捷指令的完整信息，包括可直接使用的 URL
    """
    base = _base_url()
    api_key = _effective_key()
    templates = get_default_templates()

    items = []
    for t in templates:
        items.append({
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "icon": t.icon,
            "color": t.color,
            "url": generate_ios_url_scheme(base, api_key, t),
            "nl_text": t.nl_text,
            "tags": t.tags,
        })

    categories = {}
    for t in templates:
        cat = "日常任务" if "日常" in t.tags else \
              "快速操作" if any(x in t.tags for x in ["查询"]) else \
              "个性化分析"
        categories.setdefault(cat, []).append(t.id)

    return jsonify({
        "version": "2.8.0",
        "total": len(items),
        "categories": categories,
        "templates": items,
    })


@shortcuts_bp.route("/library", methods=["GET"])
def get_library():
    """
    导出完整快捷指令库

    ?format=ios → iOS 快捷指令专用紧凑格式
    ?format=json → 标准 JSON（默认）
    """
    fmt = request.args.get("format", "json")
    base = _base_url()
    api_key = _effective_key()

    if fmt == "ios":
        # iOS 快捷指令专用格式（更紧凑）
        templates = get_default_templates()
        return jsonify({
            "version": "2.8.0",
            "shortcuts": [
                {
                    "name": t.name,
                    "icon": t.icon,
                    "color": t.color,
                    "url": generate_ios_url_scheme(base, api_key, t),
                    "description": t.description,
                }
                for t in templates
            ],
        })

    data = export_shortcut_library(base, api_key)
    return jsonify(data)


@shortcuts_bp.route("/mobile", methods=["GET"])
def mobile_shortcuts():
    """
    移动端专用快捷指令列表（适配 iOS 快捷指令 App）

    与 /shortcuts 的区别：
    - 返回更简洁的字段
    - URL 直接可用（URL编码）
    - 支持 intent_filter（iOS 快捷指令自动化用）
    """
    base = _base_url()
    api_key = _effective_key()
    templates = get_default_templates()

    shortcuts = []
    for t in templates:
        shortcuts.append({
            "intent_filter": f"nl:{t.nl_text[:20]}",
            "title": t.name,
            "icon": t.icon,
            "color": t.color,
            "url": generate_ios_url_scheme(base, api_key, t),
            "nl_text": t.nl_text,
            "group": "日常" if "日常" in t.tags else
                     "查询" if any(x in t.tags for x in ["查询"]) else
                     "分析",
        })

    return jsonify({
        "shortcuts": shortcuts,
        "tip": "在 iOS 快捷指令中使用「打开 URL」动作，将 URL 设为以上链接即可触发",
    })


@shortcuts_bp.route("/<shortcut_id>", methods=["GET"])
def get_shortcut(shortcut_id: str):
    """获取单个快捷指令详情"""
    base = _base_url()
    api_key = _effective_key()

    for t in get_default_templates():
        if t.id == shortcut_id:
            return jsonify({
                "id": t.id,
                "name": t.name,
                "description": t.description,
                "icon": t.icon,
                "color": t.color,
                "url": generate_ios_url_scheme(base, api_key, t),
                "nl_text": t.nl_text,
                "tags": t.tags,
            })

    return jsonify({"error": f"快捷指令 '{shortcut_id}' 不存在"}), 404


@shortcuts_bp.route("/parse", methods=["POST"])
def parse_clawctl_url():
    """
    解析 clawctl:// URL

    支持格式：
    clawctl://run?q=生成今日简报&api_key=xxx
    clawctl://message?text=帮我查新闻&channel=dingtalk
    clawctl://status
    """
    url = request.get_json().get("url") or request.args.get("url", "")

    result = parse_clawctl_url(url)
    if not result:
        return jsonify({
            "success": False,
            "error": "无效的 clawctl:// URL 格式",
            "hint": "正确格式: clawctl://action?key1=val1&key2=val2",
        }), 400

    return jsonify({"success": True, **result})


@shortcuts_bp.route("/cmd", methods=["GET"])
def shortcut_cmd():
    """
    🚀 iOS 快捷指令专用 GET 端点（最核心的集成点）

    使用方式（iOS 快捷指令）：
    1. 添加「URL」动作 → 设置为: {BASE_URL}/api/v1/shortcuts/cmd
    2. 添加「文本」动作 → 输入触发指令，如"生成今日简报"
    3. 添加「查找URL」动作 → 拼接参数

    直接访问示例：
    /api/v1/shortcuts/cmd?q=生成今日技术简报&channel=dingtalk

    ?intent_only=true → 只解析，不执行
    ?template=xxx → 按模板ID触发
    """
    q = request.args.get("q", "").strip()
    channel = request.args.get("channel", "dingtalk")
    template_id = request.args.get("template")
    intent_only = request.args.get("intent_only", "false").lower() == "true"
    api_key = _effective_key()

    if not q:
        return jsonify({
            "success": False,
            "error": "q 参数为空",
            "hint": "在 iOS 快捷指令的 URL 中添加 ?q=你的指令",
        }), 400

    # 按模板 ID 查找自然语言文本
    nl_text = q
    if template_id:
        for t in get_default_templates():
            if t.id == template_id:
                nl_text = t.nl_text
                break

    # 调用 NL Executor 执行
    if _nl_executor is None:
        base = _base_url()
        return jsonify({
            "success": True,
            "message": f"✅ 收到指令：{nl_text}",
            "template_id": template_id,
            "note": "NL Routes 未启动，指令已记录",
            "docs": f"{base}/api/v1/nl/intents",
        })

    try:
        if intent_only:
            from ..core.nl_interpreter import NLInterpreter
            interpreter = NLInterpreter()
            parsed = interpreter.parse(nl_text)
            return jsonify({
                "success": True,
                "intent": parsed.intent.value if parsed else "unknown",
                "confidence": parsed.confidence if parsed else 0,
                "params": parsed.params if parsed else {},
                "note": "intent_only=true，仅返回解析结果，未执行",
            })

        result = _nl_executor.execute(nl_text, channel=channel)
        return jsonify(result)

    except Exception as e:
        logger.error(f"快捷指令执行失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "fallback_url": f"{_base_url()}/api/v1/shortcuts",
        }), 500


# ── Shortcut 分享链接生成（供 Web UI 使用）──────────────────────────────────

@shortcuts_bp.route("/share/<shortcut_id>", methods=["GET"])
def share_shortcut(shortcut_id: str):
    """
    生成分享链接（分享到微信/钉钉/邮件时使用）

    返回一个可直接打开的 URL，用户点击后：
    - 已安装 App → 唤起 App 并执行
    - 未安装 → 打开 Web 页面引导安装
    """
    base = _base_url()
    api_key = _effective_key()

    for t in get_default_templates():
        if t.id == shortcut_id:
            share_url = generate_ios_url_scheme(base, api_key, t)

            # 如果是 Web（未安装 App），返回引导页 URL
            web_fallback = f"{base}/?cmd={t.id}#share"

            return jsonify({
                "shortcut_id": t.id,
                "name": t.name,
                "icon": t.icon,
                "direct_url": share_url,
                "web_fallback": web_fallback,
                "share_text": (
                    f"{t.icon} {t.name}\n\n"
                    f"{t.description}\n\n"
                    f"👉 点击链接触发：{share_url}\n\n"
                    f"（需先安装 OpenClaw App 或在快捷指令中配置）"
                ),
            })

    return jsonify({"error": f"快捷指令 '{shortcut_id}' 不存在"}), 404
