"""
NL Interpreter FastAPI Routes (v2.5.0)
自然语言任务解析引擎 — HTTP 接口层
将用户输入的自然语言转换为可执行的任务计划
"""

import asyncio
import logging
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from core.auth import AuthManager, KeyLevel, APIKey
from core.client import OpenClawClient
from core.nl_interpreter.interpreter import (
    NLInterpreter,
    get_interpreter,
    parse_natural_command,
    Intent,
    TaskPlan,
)
from core.nl_interpreter.llm_resolver import (
    LLMLightResolver,
    get_llm_resolver,
    init_llm_resolver,
    LLMParseResult,
    CONFIDENCE_THRESHOLD as LLM_THRESHOLD,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/nl", tags=["自然语言解析"])

# ─── 全局引用（由 main.py 注入）─────────────────────────────────
_task_mgr = None
_notify_mgr = None
_gateway_client = None
_auth_mgr: AuthManager = AuthManager()
_llm_resolver: LLMLightResolver = None

# ─── 注入方法 ──────────────────────────────────────────────────

def set_components(
    task_mgr=None,
    notify_mgr=None,
    gateway_client: OpenClawClient = None,
    auth_mgr: AuthManager = None,
    llm_api_key: str = None,
):
    global _task_mgr, _notify_mgr, _gateway_client, _auth_mgr, _llm_resolver
    if task_mgr is not None:
        _task_mgr = task_mgr
    if notify_mgr is not None:
        _notify_mgr = notify_mgr
    if gateway_client is not None:
        _gateway_client = gateway_client
    if auth_mgr is not None:
        _auth_mgr = auth_mgr
    if llm_api_key is not None:
        _llm_resolver = init_llm_resolver(llm_api_key)
    elif _llm_resolver is None:
        # 自动初始化（使用环境变量）
        _llm_resolver = init_llm_resolver()


def _get_client() -> OpenClawClient:
    global _gateway_client
    if _gateway_client is None:
        import os
        _gateway_client = OpenClawClient(
            base_url=os.getenv("OPENCLAW_URL", "http://localhost:18789"),
            api_key=os.getenv("OPENCLAW_TOKEN", ""),
        )
    return _gateway_client


def _require_level(required: KeyLevel):
    def checker(authorization: Optional[str] = None) -> APIKey:
        if not authorization:
            raise HTTPException(status_code=401, detail="缺少认证")
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="认证格式错误")
        key = authorization[7:].strip()
        key_obj = _auth_mgr.validate_key(key)
        if not key_obj or not key_obj.is_valid():
            raise HTTPException(status_code=401, detail="无效或已过期的 API Key")
        if not _auth_mgr.check_permission(key, required):
            raise HTTPException(status_code=403, detail=f"权限不足：需要 {required.value}")
        return key_obj
    return checker


# ═══════════════════════════════════════════════════════════════════
# Pydantic 模型
# ═══════════════════════════════════════════════════════════════════

class NLRequest(BaseModel):
    text: str = Field(..., description="自然语言指令")
    channel: str = Field(default="dingtalk", description="通知渠道")
    execute: bool = Field(default=True, description="是否立即执行（False=预览模式）")
    use_llm: bool = Field(default=True, description="置信度不足时是否启用GLM-4增强解析")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "帮我查一下今天有啥AI新闻",
                "channel": "dingtalk",
                "execute": True,
                "use_llm": True,
            }
        }


class NLBatchRequest(BaseModel):
    texts: List[str] = Field(..., description="批量自然语言指令")
    channel: str = Field(default="dingtalk", description="通知渠道")


class NLResponse(BaseModel):
    success: bool
    intent: str
    confidence: float
    agent: str
    plan: Dict[str, Any]
    task_id: Optional[str] = None
    message: str
    details: Optional[Dict[str, Any]] = None
    llm_enhanced: bool = Field(default=False, description="是否经过GLM-4增强解析")
    llm_reasoning: Optional[str] = Field(default=None, description="GLM-4推理说明")
    llm_latency_ms: Optional[float] = Field(default=None, description="GLM-4调用耗时")


class NLPreviewResponse(BaseModel):
    success: bool
    intent: str
    confidence: float
    agent: str
    plan: Dict[str, Any]
    message: str
    params_extracted: Dict[str, Any]


class NLIntentsResponse(BaseModel):
    success: bool
    total: int
    intents: List[Dict[str, Any]]


# ═══════════════════════════════════════════════════════════════════
# 工具函数
# ═══════════════════════════════════════════════════════════════════

def _build_success_message(plan: TaskPlan, task_id: Optional[str] = None) -> str:
    """构建 NL 解析成功消息"""
    emoji_map = {
        "trigger_report": "📋",
        "trigger_scan": "🔍",
        "trigger_analysis": "🔬",
        "trigger_fetch": "🌐",
        "trigger_search": "🔎",
        "send_message": "💬",
        "ask_question": "🤔",
        "query_status": "📊",
        "query_task": "📋",
        "query_history": "📜",
        "cancel_task": "🛑",
        "pause_schedule": "⏸",
        "resume_schedule": "▶️",
        "unknown": "❓",
    }
    emoji = emoji_map.get(plan.intent, "➡️")

    msg = f"{emoji} 收到！正在执行「{plan.intent}」"
    if task_id:
        msg += f"\n📋 任务ID: {task_id}"
    if plan.time_range and plan.time_range != "today":
        msg += f"\n🕐 时间范围: {plan.time_range}"
    if plan.topics:
        msg += f"\n🏷️ 关键词: {', '.join(plan.topics[:3])}"
    msg += "\n⏱ 完成后我会通知你~"
    return msg


def _build_confirm_message(plan: TaskPlan) -> str:
    """构建需要确认的消息"""
    return (
        f"🤔 意图不确定（置信度 {plan.confidence:.0%}），你的意思是：\n\n"
        f"• 意图：{plan.description}\n"
        f"• Agent：{plan.agent}\n"
        f"• 参数：{plan.params}\n\n"
        f"请用更明确的说法，例如：\n"
        f'"生成今日技术简报"\n'
        f'"查一下最新的AI新闻"'
    )


def _execute_plan(plan: TaskPlan, channel: str) -> tuple[bool, str, Optional[str]]:
    """
    执行解析后的任务计划
    返回: (success, message, task_id)
    """
    global _task_mgr, _notify_mgr, _gateway_client

    task_id = f"nl-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"

    try:
        client = _get_client()

        if plan.intent == "send_message":
            # 发送消息
            result = client.send_message(channel=channel, message=plan.params.get("text", ""))
            return True, f"✅ 消息已发送至 {channel}", task_id

        elif plan.intent == "ask_question":
            # 自由提问 → spawn agent 回答
            question = plan.params.get("text", "")
            result = client.spawn_agent(task=f"请回答以下问题（简洁有条理）：\n{question}")
            return True, f"🤔 问题已提交，正在思考中...", task_id

        elif plan.intent in ("trigger_report", "trigger_scan", "trigger_analysis",
                              "trigger_fetch", "trigger_search"):
            # 触发 agent
            agent = plan.agent
            params = plan.params.copy()
            params["_intent"] = plan.intent
            params["_nl_text"] = plan.params.get("text", "")

            result = client.spawn_agent(task=f"执行{plan.description}，参数：{params}")

            # 发送确认消息
            if _notify_mgr:
                try:
                    _notify_mgr.send(
                        channel,
                        _build_success_message(plan, task_id),
                    )
                except Exception as e:
                    logger.warning(f"NL 执行通知失败: {e}")

            return True, _build_success_message(plan, task_id), task_id

        elif plan.intent == "query_status":
            # 查询状态
            try:
                status = client.get_status()
                msg = f"📊 OpenClaw 状态\n"
                msg += f"• Gateway: {status.get('status', 'unknown')}\n"
                sessions = status.get("sessions", [])
                msg += f"• 活跃会话: {len(sessions)}"
                return True, msg, None
            except Exception as e:
                return False, f"❌ 状态查询失败: {e}", None

        elif plan.intent == "query_history":
            # 查询历史
            if _task_mgr and _task_mgr._db:
                tasks = _task_mgr._db.load_tasks(limit=5)
                if not tasks:
                    return True, "📜 暂无任务记录", None
                msg = "📜 最近任务记录：\n"
                for t in tasks[:5]:
                    status_emoji = {"completed": "✅", "failed": "❌", "running": "🔄"}.get(
                        t.get("status", ""), "⬜"
                    )
                    msg += f"{status_emoji} {t.get('name', 'unknown')} — {t.get('created_at', '')[:16]}\n"
                return True, msg, None
            return True, "📜 历史查询功能暂不可用", None

        elif plan.intent == "cancel_task":
            task_id_to_cancel = plan.params.get("task_id")
            if task_id_to_cancel and _task_mgr:
                ok = _task_mgr.cancel_task(task_id_to_cancel)
                return ok, f"{'✅' if ok else '❌'} 任务 {'已取消' if ok else '取消失败'}", task_id
            return True, "🛑 任务取消请求已收到", None

        elif plan.intent == "pause_schedule":
            return True, "⏸ 定时任务已暂停", None

        elif plan.intent == "resume_schedule":
            return True, "▶️ 定时任务已恢复", None

        else:
            return False, f"❓ 未知意图: {plan.intent}", None

    except Exception as e:
        logger.error(f"NL 执行失败: {e}")
        return False, f"❌ 执行失败: {e}", task_id


# ═══════════════════════════════════════════════════════════════════
# API 端点
# ═══════════════════════════════════════════════════════════════════

@router.post("", response_model=NLResponse, summary="自然语言 → 自动执行")
async def nl_execute(
    req: NLRequest,
    authorization: Optional[str] = None,
):
    """
    **核心端点**：将自然语言指令自动解析并执行

    - 自动识别 13 种意图（触发报告/抓取/分析/状态查询/消息发送等）
    - 提取 Agent/时间/关键词/通知渠道参数
    - 立即执行或预览模式

    **示例**：
    ```bash
    curl -X POST http://localhost:8081/api/v1/nl \\
      -H "Content-Type: application/json" \\
      -d '{"text": "帮我查一下今天有啥AI新闻", "channel": "dingtalk"}'
    ```
    """
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="text 不能为空")

    text = req.text.strip()
    interpreter = get_interpreter()
    plan = interpreter.parse(text)

    # ─── LLM增强：置信度不足时调用GLM-4 ───────────────────────
    llm_result: Optional[LLMParseResult] = None
    if req.use_llm and plan.confidence < LLM_THRESHOLD and plan.intent != "unknown":
        try:
            llm_resolver = _llm_resolver or get_llm_resolver()
            if llm_resolver.enabled:
                llm_result = await llm_resolver.parse(text, rule_confidence=plan.confidence)
                if llm_result and llm_result.confidence > plan.confidence:
                    # LLM结果更可靠，使用LLM解析结果
                    plan.intent = llm_result.intent
                    plan.confidence = llm_result.confidence
                    plan.agent = llm_result.agent
                    plan.params.update(llm_result.params)
                    plan.description = llm_result.reasoning
                    logger.info(
                        f"[NL+LLM] text='{text[:50]}...' → intent={plan.intent} "
                        f"conf={plan.confidence:.2f} (LLM增强，推理:{llm_result.reasoning})"
                    )
        except Exception as e:
            logger.warning(f"LLM增强解析失败（降级到规则引擎）: {e}")

    logger.info(f"[NL] text='{text[:50]}...' → intent={plan.intent} conf={plan.confidence:.2f}")

    # 审计日志
    try:
        key_obj = _require_level(KeyLevel.EXECUTE)(authorization)
        _auth_mgr.log_action(
            "nl_parse",
            key_id=key_obj.key_id,
            detail=f"NL → {plan.intent} ({plan.confidence:.2f}): {text[:50]}",
        )
    except Exception:
        pass

    # 置信度太低 → 友好提示
    if plan.intent == "unknown" or plan.confidence < 0.4:
        return NLResponse(
            success=False,
            intent=plan.intent,
            confidence=plan.confidence,
            agent=plan.agent,
            plan=plan.to_dict(),
            message=_build_confirm_message(plan),
        )

    # 预览模式（不执行）
    if not req.execute:
        return NLResponse(
            success=True,
            intent=plan.intent,
            confidence=plan.confidence,
            agent=plan.agent,
            plan=plan.to_dict(),
            message="🔍 预览模式：\n" + _build_success_message(plan),
            details={"params_extracted": plan.to_dict()},
        )

    # 执行
    ok, message, task_id = _execute_plan(plan, req.channel)

    return NLResponse(
        success=ok,
        intent=plan.intent,
        confidence=plan.confidence,
        agent=plan.agent,
        plan=plan.to_dict(),
        task_id=task_id,
        message=message,
    )


@router.post("/preview", response_model=NLPreviewResponse, summary="预览解析结果")
async def nl_preview(
    req: NLRequest,
    authorization: Optional[str] = None,
):
    """
    **预览模式**：解析自然语言但不执行，用于调试和用户体验优化

    返回完整的解析结果（意图/Agent/参数），不触发实际操作

    **示例**：
    ```bash
    curl -X POST http://localhost:8081/api/v1/nl/preview \\
      -H "Content-Type: application/json" \\
      -d '{"text": "生成今日商业简报"}'
    ```
    """
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="text 不能为空")

    text = req.text.strip()
    interpreter = get_interpreter()
    plan = interpreter.parse(text)

    logger.info(f"[NL/preview] '{text[:50]}...' → {plan.intent} ({plan.confidence:.2f})")

    return NLPreviewResponse(
        success=True,
        intent=plan.intent,
        confidence=plan.confidence,
        agent=plan.agent,
        plan=plan.to_dict(),
        message=f"✅ 解析成功\n意图：{plan.description}\nAgent：{plan.agent}",
        params_extracted={
            "intent": plan.intent,
            "confidence": plan.confidence,
            "agent": plan.agent,
            "time_range": plan.time_range,
            "scope": plan.scope,
            "topics": plan.topics,
            "params": plan.params,
        },
    )


@router.get("/intents", response_model=NLIntentsResponse, summary="支持的意图列表")
async def nl_intents(
    authorization: Optional[str] = None,
):
    """
    返回 NL Interpreter 支持的 13 种意图及其描述和示例

    用于前端构建命令提示、快捷指令参数说明等
    """
    from core.nl_interpreter.interpreter import INTENT_PATTERNS, AGENT_KEYWORDS

    intents = []
    for name, patterns in INTENT_PATTERNS.items():
        examples = [p["pattern"] for p in patterns.get("zh", [])][:3]
        agents = []
        for kw, agent in AGENT_KEYWORDS.items():
            if any(kw in " ".join(examples) for ex in examples):
                agents.append(agent)
        intents.append({
            "name": name,
            "description": patterns.get("desc", name),
            "examples": examples,
            "agents": list(set(agents)) if agents else ["generic"],
        })

    return NLIntentsResponse(
        success=True,
        total=len(intents),
        intents=intents,
    )



@router.post("/llm-parse", summary="纯LLM深度解析")
async def nl_llm_parse(
    req: NLRequest,
    authorization: Optional[str] = None,
):
    """
    **专用LLM解析端点**：强制使用GLM-4进行深度语义解析
    适用于复杂指令、模糊表达、跨语言等规则引擎难以处理的场景

    **示例**：
    ```bash
    curl -X POST http://localhost:8081/api/v1/nl/llm-parse \
      -H "Content-Type: application/json" \
      -d '{"text": "最近有没有什么比较火的AI创业公司？给我分析一下"}'
    ```
    """
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="text 不能为空")

    text = req.text.strip()

    try:
        llm_resolver = _llm_resolver or get_llm_resolver()
        if not llm_resolver.enabled:
            raise HTTPException(
                status_code=503,
                detail="LLM解析器未启用（请配置 GLM_API_KEY 环境变量）"
            )

        llm_result = await llm_resolver.parse(text, rule_confidence=0.0)

        if not llm_result:
            return {
                "success": False,
                "message": "❌ LLM解析失败，请稍后重试",
                "llm_enhanced": False,
            }

        # 如果需要执行
        if req.execute and llm_result.intent != "unknown":
            # 构造 TaskPlan
            plan = TaskPlan(
                intent=llm_result.intent,
                confidence=llm_result.confidence,
                description=llm_result.reasoning,
                agent=llm_result.agent,
                params=llm_result.params,
            )
            ok, msg, task_id = _execute_plan(plan, req.channel)
            return {
                "success": True,
                "intent": llm_result.intent,
                "confidence": llm_result.confidence,
                "agent": llm_result.agent,
                "params": llm_result.params,
                "reasoning": llm_result.reasoning,
                "llm_enhanced": True,
                "llm_latency_ms": llm_result.latency_ms,
                "execute_result": msg,
                "task_id": task_id,
                "message": f"🤖 LLM深度解析 + 执行完成\n{msg}",
            }

        return {
            "success": True,
            "intent": llm_result.intent,
            "confidence": llm_result.confidence,
            "agent": llm_result.agent,
            "params": llm_result.params,
            "reasoning": llm_result.reasoning,
            "suggestion": llm_result.suggestion,
            "llm_enhanced": True,
            "llm_latency_ms": llm_result.latency_ms,
            "message": f"🤖 LLM解析完成（置信度 {llm_result.confidence:.0%}）",
        }

    except HTTPException:
        raise
    except Exception as e:
        return {
            "success": False,
            "message": f"❌ LLM解析异常: {e}",
            "llm_enhanced": False,
        }


@router.post("/batch", summary="批量自然语言解析")
async def nl_batch(
    req: NLBatchRequest,
    authorization: Optional[str] = None,
):
    """
    **批量解析**：一次处理多条自然语言指令

    用于快捷指令批量触发、分析日志等场景
    """
    if len(req.texts) > 20:
        raise HTTPException(status_code=400, detail="最多支持 20 条批量解析")

    interpreter = get_interpreter()
    results = []

    for text in req.texts:
        plan = interpreter.parse(text.strip())
        results.append({
            "text": text,
            "intent": plan.intent,
            "confidence": plan.confidence,
            "agent": plan.agent,
            "plan": plan.to_dict(),
        })

    # 如果需要执行 → 并发执行
    if len(req.texts) == 1 and results[0]["confidence"] >= 0.4:
        plan = interpreter.parse(req.texts[0])
        task_plan = TaskPlan(
            intent=plan.intent,
            confidence=plan.confidence,
            description=plan.description,
            agent=plan.agent,
            params=plan.params,
        )
        ok, message, task_id = _execute_plan(task_plan, req.channel)
        results[0]["executed"] = True
        results[0]["task_id"] = task_id
        results[0]["message"] = message

    return {
        "success": True,
        "total": len(results),
        "results": results,
    }


# ═══════════════════════════════════════════════════════════════════
# URL Scheme / 快捷指令兼容端点（轻量版）
# ═══════════════════════════════════════════════════════════════════

@router.get("/cmd", summary="快捷指令兼容入口（GET）")
async def nl_cmd(
    q: str = Query(..., description="自然语言指令"),
    channel: str = Query(default="dingtalk"),
    api_key: Optional[str] = Query(default=None),
):
    """
    **快捷指令专用端点（GET）**

    URL Scheme 格式：
    ```
    http://localhost:8081/api/v1/nl/cmd?q=生成今日技术简报&channel=dingtalk&api_key=sk-xxx
    ```

    支持直接在浏览器或快捷指令中调用
    """
    # 简单 API Key 验证（如果配置了）
    import os
    allowed_key = os.getenv("NL_CMD_KEY", "")
    if allowed_key and api_key and api_key != allowed_key:
        raise HTTPException(status_code=403, detail="API Key 无效")

    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="q 参数不能为空")

    interpreter = get_interpreter()
    plan = interpreter.parse(q.strip())

    if plan.intent == "unknown" or plan.confidence < 0.4:
        return {
            "success": False,
            "message": _build_confirm_message(plan),
            "plan": plan.to_dict(),
        }

    ok, message, task_id = _execute_plan(plan, channel)

    return {
        "success": ok,
        "intent": plan.intent,
        "task_id": task_id,
        "message": message,
    }
