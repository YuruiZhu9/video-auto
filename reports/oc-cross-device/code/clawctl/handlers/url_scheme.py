#!/usr/bin/env python3
"""
URL Scheme Handler — clawctl:// 协议处理器

支持 iOS 快捷指令 / Android Intent / macOS URL Handler
clawctl://run?template=xxx&api_key=xxx
clawctl://message?text=xxx&channel=dingtalk&api_key=xxx
clawctl://status?api_key=xxx
"""

import re
import json
import logging
from urllib.parse import parse_qs, unquote

logger = logging.getLogger("clawctl.url_scheme")


# ── 协议常量 ────────────────────────────────────────────────────────────────

PROTOCOL = "clawctl"
SUPPORTED_ACTIONS = {"run", "message", "status", "schedule"}

# ── 响应构建 ────────────────────────────────────────────────────────────────

def build_response(success: bool, message: str = "", data: dict = None) -> dict:
    return {"success": success, "message": message, "data": data or {}}


def build_deep_link(action: str, params: dict) -> str:
    """构建回调到客户端的 Deep Link（客户端打开 App 时使用）"""
    q = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{PROTOCOL}://callback?{q}"


# ── 解析 URL ────────────────────────────────────────────────────────────────

def parse_url(url: str) -> dict:
    """
    解析 clawctl:// URL
    返回 {"action": str, "params": dict}
    """
    if not url.startswith(f"{PROTOCOL}://"):
        return None
    url = url[len(f"{PROTOCOL}://"):]

    # 支持两种格式：
    # clawctl://run?key=val&key2=val2
    # clawctl://run/key1-val/key2-val   (path 风格，兼容某些快捷指令限制)
    if "?" in url:
        path_part, query_part = url.split("?", 1)
        action = path_part.split("/")[0]
        params = parse_qs(query_part, keep_blank_values=True)
        # parse_qs 返回 list，取第一个值
        params = {k: v[0] if len(v) == 1 else v for k, v in params.items()}
    else:
        parts = url.split("/")
        action = parts[0]
        params = {}
        for part in parts[1:]:
            if "=" in part:
                k, v = part.split("=", 1)
                params[k] = unquote(v)

    action = unquote(action)
    return {"action": action, "params": params}


# ── 主要处理器 ─────────────────────────────────────────────────────────────

def handle_url(
    url: str,
    task_manager=None,
    client=None,
    auth_manager=None,
    notify_mgr=None,
) -> dict:
    """
    处理 clawctl:// URL 请求

    Args:
        url: 完整的 clawctl:// URL
        task_manager: TaskManager 实例
        client: OpenClawClient 实例
        auth_manager: AuthManager 实例
        notify_mgr: NotifyManager 实例

    Returns:
        JSON-serializable dict
    """
    parsed = parse_url(url)
    if not parsed:
        return build_response(False, "无效的 URL Scheme，只能处理 clawctl:// 协议")

    action = parsed["action"]
    params = parsed["params"]

    # ── 统一参数校验 ──────────────────────────────────────────
    api_key = params.get("api_key", "")
    if not api_key and action in ("run", "message"):
        return build_response(False, "缺少必需参数: api_key")

    # API Key 鉴权（仅需要级别验证，不验证 IP）
    if api_key and auth_manager:
        key_obj = auth_manager.authenticate(api_key, require_level=None)
        if not key_obj:
            return build_response(False, "API Key 无效或已过期")

    # ── action: run — 触发任务 ───────────────────────────────
    if action == "run":
        template = params.get("template", "")
        name = params.get("name", f"快捷指令-{template}")
        extra_params = {}

        # 支持 JSON 参数（URL 编码的 JSON）
        raw_params = params.get("params", "")
        if raw_params:
            try:
                extra_params = json.loads(unquote(raw_params))
            except json.JSONDecodeError:
                return build_response(False, f"params 参数不是合法 JSON: {raw_params}")

        if not template:
            return build_response(False, "缺少必需参数: template")

        if task_manager is None:
            return build_response(False, "任务管理器未初始化")

        from ..core.task import Task, TaskStatus
        task = Task(
            name=name,
            action="spawn",
            params={"task": template, **extra_params},
            notify=True,
            notify_channel=params.get("notify_channel", "dingtalk"),
        )
        task_manager.submit(task)
        task_manager.execute_async(task)

        logger.info(f"[clawctl://run] 任务已创建: {task.id} | 模板: {template}")
        return build_response(True, f"✅ 任务已创建: {name}", {
            "task_id": task.id,
            "template": template,
            "status": task.status.value,
            "deep_link": build_deep_link("task", {"task_id": task.id}),
        })

    # ── action: message — 发送消息 ──────────────────────────
    elif action == "message":
        text = params.get("text", "")
        channel = params.get("channel", "dingtalk")

        if not text:
            return build_response(False, "缺少必需参数: text")

        if client is None:
            return build_response(False, "OpenClaw Client 未初始化")

        resp = client.send_message(channel=channel, message=text)
        if resp.success:
            logger.info(f"[clawctl://message] 消息已发送 | 渠道: {channel} | 长度: {len(text)}")
            return build_response(True, f"✅ 消息已发送 [{channel}]", {
                "channel": channel,
                "length": len(text),
            })
        else:
            return build_response(False, f"发送失败: {resp.error}")

    # ── action: status — 查询状态 ────────────────────────────
    elif action == "status":
        if client is None:
            return build_response(False, "OpenClaw Client 未初始化")

        resp = client.get_status()
        if resp.success:
            return build_response(True, "✅ 系统运行正常", {
                "status": resp.data,
                "tasks_total": 0,
            })
        else:
            return build_response(False, f"⚠️ 系统异常: {resp.error}", {
                "connected": False,
            })

    # ── action: schedule — 定时任务管理 ─────────────────────
    elif action == "schedule":
        if task_manager is None:
            return build_response(False, "任务管理器未初始化")

        sched_action = params.get("action", "list")  # list / enable / disable / trigger
        job_id = params.get("job", "")

        if sched_action == "list":
            jobs = task_manager.list_schedules() if hasattr(task_manager, "list_schedules") else []
            return build_response(True, f"共 {len(jobs)} 个定时任务", {"schedules": jobs})

        elif sched_action == "enable":
            ok = task_manager.enable_schedule(job_id) if hasattr(task_manager, "enable_schedule") else False
            return build_response(ok, f"定时任务 {job_id} {'已启用' if ok else '启用失败'}")

        elif sched_action == "disable":
            ok = task_manager.disable_schedule(job_id) if hasattr(task_manager, "disable_schedule") else False
            return build_response(ok, f"定时任务 {job_id} {'已暂停' if ok else '暂停失败'}")

        elif sched_action == "trigger":
            ok = task_manager.trigger_schedule_now(job_id) if hasattr(task_manager, "trigger_schedule_now") else False
            return build_response(ok, f"定时任务 {job_id} {'已触发' if ok else '触发失败'}")

        return build_response(False, f"未知 schedule 操作: {sched_action}")

    else:
        return build_response(False, f"不支持的操作: {action}，支持: {', '.join(SUPPORTED_ACTIONS)}")


# ── 注册到 Flask ────────────────────────────────────────────────────────────

def register_url_scheme_routes(app, task_manager, client, auth_manager, notify_mgr):
    """将 URL Scheme 处理器注册到 Flask App"""

    @app.route(f"/{PROTOCOL}/<path:url>", methods=["GET", "POST"])
    @app.route(f"/url-scheme", methods=["GET", "POST"])
    def clawctl_url_scheme(url=None):
        from flask import request
        if url is None:
            url = request.values.get("url", "")
        if not url:
            return {"error": "缺少 url 参数"}, 400

        result = handle_url(
            url=url,
            task_manager=task_manager,
            client=client,
            auth_manager=auth_manager,
            notify_mgr=notify_mgr,
        )
        return result

    @app.route(f"/api/v1/shortcuts", methods=["GET"])
    def list_shortcuts():
        """列出所有支持的快捷指令"""
        shortcuts = [
            {
                "name": "AI 早报",
                "scheme": f"clawctl://run?template=quick_fetch&api_key={{YOUR_KEY}}&name=AI早报",
                "description": "触发快速信息抓取，生成当日 AI 资讯简报",
                "action": "run",
                "params": {"template": "quick_fetch", "name": "AI早报"},
                "requires_key": True,
            },
            {
                "name": "发送消息",
                "scheme": f"clawctl://message?text={{TEXT}}&channel=dingtalk&api_key={{YOUR_KEY}}",
                "description": "发送文本消息到指定渠道",
                "action": "message",
                "params": {"text": "", "channel": "dingtalk"},
                "requires_key": True,
            },
            {
                "name": "状态检查",
                "scheme": f"clawctl://status?api_key={{YOUR_KEY}}",
                "description": "查询 OpenClaw 系统运行状态",
                "action": "status",
                "params": {},
                "requires_key": True,
            },
            {
                "name": "商业洞察",
                "scheme": f"clawctl://run?template=biz_brief&api_key={{YOUR_KEY}}&name=商业速报",
                "description": "分析 AI 商业应用动态，发现新机会",
                "action": "run",
                "params": {"template": "biz_brief", "name": "商业速报"},
                "requires_key": True,
            },
            {
                "name": "技术简报",
                "scheme": f"clawctl://run?template=tech_brief&api_key={{YOUR_KEY}}&name=技术早读",
                "description": "追踪推荐系统+大模型技术前沿",
                "action": "run",
                "params": {"template": "tech_brief", "name": "技术早读"},
                "requires_key": True,
            },
            {
                "name": "定时任务管理",
                "scheme": f"clawctl://schedule?action=list&api_key={{YOUR_KEY}}",
                "description": "列出/启用/暂停/触发定时任务",
                "action": "schedule",
                "params": {"action": "list"},
                "requires_key": True,
            },
        ]
        return {"shortcuts": shortcuts}

    logger.info(f"[clawctl] URL Scheme 路由已注册 (支持 {PROTOCOL}://)")
