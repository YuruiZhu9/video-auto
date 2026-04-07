#!/usr/bin/env python3
"""
NLInterpreter — 自然语言任务解析器
将日常语言转化为可执行的任务计划

支持中文/英文双语解析
Intent Classification + Parameter Extraction → Task Plan
"""

from __future__ import annotations

import re
import time
import logging
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional
from datetime import datetime, timedelta

logger = logging.getLogger("nl_interpreter")


# ─────────────────────────────────────────────────────────────
# Intent 枚举
# ─────────────────────────────────────────────────────────────

class Intent(Enum):
    TECH_BRIEF = "tech_brief"        # 技术简报
    MARKET_INSIGHT = "market_insight"  # 商业洞察
    FULL_SCAN = "full_scan"          # 全量扫描
    QUICK_FETCH = "quick_fetch"      # 快速抓取
    CUSTOM_TASK = "custom_task"       # 自定义任务
    STATUS_QUERY = "status_query"    # 状态查询
    CANCEL_TASK = "cancel_task"      # 取消任务
    HELP = "help"                    # 帮助
    UNKNOWN = "unknown"              # 未知


# ─────────────────────────────────────────────────────────────
# 时间解析
# ─────────────────────────────────────────────────────────────

_TIME_PATTERNS = [
    # 中文
    (r"今天早上的|今日早间|早上", "morning"),
    (r"今天中午|今日午间|中午", "noon"),
    (r"今天下午|今日下午|下午", "afternoon"),
    (r"今天晚上|今日晚间|晚上|今晚", "evening"),
    (r"今[天日]|今日", "today"),
    (r"昨天", "yesterday"),
    (r"明天", "tomorrow"),
    (r"这周|本周|这星期", "this_week"),
    (r"上周", "last_week"),
    (r"下周", "next_week"),
    (r"这个月|本月", "this_month"),
    # 英文
    (r"today", "today"),
    (r"yesterday", "yesterday"),
    (r"tomorrow", "tomorrow"),
    (r"this week", "this_week"),
    (r"last week", "last_week"),
    (r"this month", "this_month"),
]

_SCOPE_PATTERNS = [
    (r"简略|简短|概要|速览|一句话|一句话总结", "brief"),
    (r"详细|完整|全面|深度|深入", "full"),
    (r"最新|最近|今日|当天|当天热点", "latest"),
    (r"全量|全部|所有", "all"),
]


def _parse_time(text: str) -> dict:
    """从文本中解析时间范围"""
    now = datetime.now()
    result = {"label": "default", "since": None, "until": None}

    for pattern, label in _TIME_PATTERNS:
        if re.search(pattern, text):
            result["label"] = label
            if label == "today":
                result["since"] = now.replace(hour=0, minute=0, second=0).isoformat()
            elif label == "yesterday":
                d = now - timedelta(days=1)
                result["since"] = d.replace(hour=0, minute=0, second=0).isoformat()
                result["until"] = d.replace(hour=23, minute=59, second=59).isoformat()
            elif label == "tomorrow":
                d = now + timedelta(days=1)
                result["since"] = d.replace(hour=0, minute=0, second=0).isoformat()
            elif label == "this_week":
                wd = now.weekday()
                result["since"] = (now - timedelta(days=wd)).replace(hour=0, minute=0, second=0).isoformat()
            elif label == "last_week":
                wd = now.weekday()
                result["since"] = (now - timedelta(days=wd + 7)).replace(hour=0, minute=0, second=0).isoformat()
                result["until"] = (now - timedelta(days=wd + 1)).replace(hour=23, minute=59, second=59).isoformat()
            elif label == "this_month":
                result["since"] = now.replace(day=1, hour=0, minute=0, second=0).isoformat()
            elif label == "morning":
                result["since"] = now.replace(hour=6, minute=0, second=0).isoformat()
                result["until"] = now.replace(hour=12, minute=0, second=0).isoformat()
            elif label == "afternoon":
                result["since"] = now.replace(hour=12, minute=0, second=0).isoformat()
                result["until"] = now.replace(hour=18, minute=0, second=0).isoformat()
            elif label == "evening":
                result["since"] = now.replace(hour=18, minute=0, second=0).isoformat()
                result["until"] = now.replace(hour=23, minute=59, second=59).isoformat()
            break

    return result


def _parse_scope(text: str) -> str:
    """从文本中解析信息范围"""
    for pattern, label in _SCOPE_PATTERNS:
        if re.search(pattern, text):
            return label
    return "default"


# ─────────────────────────────────────────────────────────────
# Intent 分类规则
# ─────────────────────────────────────────────────────────────

_INTENT_RULES: list[tuple[re.Pattern, Intent, list[str]]] = []

def _compile_rules():
    patterns = [
        # 技术简报
        (r"技术|简报|tech", Intent.TECH_BRIEF, ["技术简报", "tech brief"]),
        (r"技术.*分析|tech.*analyst", Intent.TECH_BRIEF, ["技术分析"]),
        (r"今日技术|技术动态|技术新闻|AI.*动态", Intent.TECH_BRIEF, ["AI技术动态"]),
        (r"大模型|llm|gpt|gemini|deepseek|qwen", Intent.TECH_BRIEF, ["大模型动态"]),

        # 商业洞察
        (r"商业|市场|market|business|商机", Intent.MARKET_INSIGHT, ["商业洞察"]),
        (r"商业.*需求|需求.*分析|应用.*场景", Intent.MARKET_INSIGHT, ["商业需求分析"]),
        (r"行业.*动态|垂直.*AI|医疗.*AI|教育.*AI|法律.*AI", Intent.MARKET_INSIGHT, ["行业动态"]),

        # 快速抓取
        (r"快速|quick|fetch|抓取|资讯|新闻|热点", Intent.QUICK_FETCH, ["快速抓取"]),
        (r"信息.*获取|搜一下|查一下|帮我找|搜索", Intent.QUICK_FETCH, ["信息获取"]),

        # 全量扫描
        (r"全量|全部|所有|full.*scan|全面", Intent.FULL_SCAN, ["全量扫描"]),
        (r"深度.*扫描|深度.*抓取|深度.*分析", Intent.FULL_SCAN, ["深度扫描"]),

        # 状态查询
        (r"状态|status|情况如何|怎么样了", Intent.STATUS_QUERY, ["状态查询"]),
        (r"有什么|最近.*什么|更新", Intent.STATUS_QUERY, ["状态查询"]),

        # 取消任务
        (r"取消|停掉|kill|cancel", Intent.CANCEL_TASK, ["取消任务"]),

        # 帮助
        (r"帮助|help|怎么用|使用说明|命令列表", Intent.HELP, ["帮助"]),
        (r"支持.*什么|有哪些|功能列表", Intent.HELP, ["功能列表"]),
    ]

    for pattern, intent, keywords in patterns:
        _INTENT_RULES.append((re.compile(pattern, re.I), intent, keywords))

_compile_rules()


# ─────────────────────────────────────────────────────────────
# Task Plan 数据类
# ─────────────────────────────────────────────────────────────

@dataclass
class TaskPlan:
    """自然语言 → 可执行任务计划"""
    original_text: str
    intent: Intent
    confidence: float           # 0.0–1.0 置信度
    template_id: Optional[str] = None
    agent: Optional[str] = None   # OpenClaw agent name
    params: dict = field(default_factory=dict)
    message: Optional[str] = None  # 直接透传给 OpenClaw 的消息
    description: str = ""
    estimated_time: str = "1-3分钟"
    suggestions: list[str] = field(default_factory=list)

    def to_execute_params(self) -> dict:
        """转换为 TaskManager.execute() 参数"""
        if self.message:
            return {"message": self.message, **self.params}
        return {
            "template_id": self.template_id,
            "agent": self.agent,
            **self.params,
        }

    def to_dict(self) -> dict:
        return asdict(self)


# ─────────────────────────────────────────────────────────────
# 自然语言解析引擎
# ─────────────────────────────────────────────────────────────

class NLInterpreter:
    """
    自然语言任务解析器

    用法:
        interpreter = NLInterpreter()
        plan = interpreter.parse("帮我生成今日技术简报")
        if plan:
            result = task_manager.execute_task(plan.to_execute_params())
    """

    # 内置任务模板映射（可扩展）
    TEMPLATE_MAP = {
        Intent.TECH_BRIEF: {
            "template_id": "tech-brief",
            "agent": "tech-analyst",
            "description": "技术前沿分析",
            "estimated_time": "2-3分钟",
        },
        Intent.MARKET_INSIGHT: {
            "template_id": "market-insight",
            "agent": "market-insight",
            "description": "商业需求洞察",
            "estimated_time": "3-5分钟",
        },
        Intent.FULL_SCAN: {
            "template_id": "full-scan",
            "agent": "info-fetcher",
            "description": "全量信息扫描",
            "estimated_time": "5-10分钟",
        },
        Intent.QUICK_FETCH: {
            "template_id": "quick-fetch",
            "agent": "info-fetcher",
            "description": "快速资讯抓取",
            "estimated_time": "1-2分钟",
        },
    }

    # OpenClaw 可用 Agent 列表
    AVAILABLE_AGENTS = {
        "info-fetcher": "信息抓取助手",
        "tech-analyst": "技术前沿分析师",
        "market-insight": "商业需求洞察分析师",
    }

    # 快捷触发模板（无需配置直接使用）
    QUICK_TEMPLATES = {
        "tech-brief": "技术简报",
        "market-insight": "商业洞察",
        "full-scan": "全量扫描",
        "quick-fetch": "快速资讯",
    }

    def __init__(self, custom_intents: dict | None = None):
        """
        Args:
            custom_intents: 自定义 Intent 映射，如 {"生成报表": Intent.CUSTOM_TASK}
        """
        self.custom_intents = custom_intents or {}
        self._rule_stats = {i: 0 for i in Intent}

    def parse(self, text: str) -> TaskPlan:
        """
        解析自然语言命令，返回任务计划

        Args:
            text: 用户输入的自然语言

        Returns:
            TaskPlan 对象，包含 intent / confidence / params
        """
        text = text.strip()
        if not text:
            return TaskPlan(
                original_text=text,
                intent=Intent.UNKNOWN,
                confidence=0.0,
                description="输入为空",
                suggestions=["请输入想执行的任务，如'今日技术简报'"],
            )

        # ── Step 1: Intent 分类 ──────────────────────────────
        intent, confidence = self._classify_intent(text)

        # ── Step 2: 参数提取 ─────────────────────────────────
        time_info = _parse_time(text)
        scope = _parse_scope(text)
        topics = self._extract_topics(text)

        # ── Step 3: 构建任务计划 ─────────────────────────────
        plan = self._build_plan(text, intent, confidence, time_info, scope, topics)

        logger.info(
            f"[NL] 解析结果: intent={intent.value} conf={confidence:.2f} "
            f"scope={scope} time={time_info['label']} topics={topics}"
        )
        return plan

    def _classify_intent(self, text: str) -> tuple[Intent, float]:
        """基于规则 + 权重的 Intent 分类"""

        # 优先级处理（短命令精确匹配）
        quick_map = {
            r"^简报$": Intent.TECH_BRIEF,
            r"^技术$": Intent.TECH_BRIEF,
            r"^商业$": Intent.MARKET_INSIGHT,
            r"^市场$": Intent.MARKET_INSIGHT,
            r"^扫描$": Intent.FULL_SCAN,
            r"^抓取$": Intent.QUICK_FETCH,
            r"^状态$": Intent.STATUS_QUERY,
            r"^status$": Intent.STATUS_QUERY,
            r"^帮助$": Intent.HELP,
            r"^help$": Intent.HELP,
            r"^取消$": Intent.CANCEL_TASK,
        }
        for pattern, intent in quick_map.items():
            if re.fullmatch(pattern, text, re.I):
                self._rule_stats[intent] += 1
                return intent, 0.99

        # 规则匹配打分
        scores: dict[Intent, float] = {}
        for pattern, intent, keywords in _INTENT_RULES:
            if pattern.search(text):
                # 自定义规则权重更高
                weight = 1.2 if intent in self.custom_intents.values() else 1.0
                keyword_bonus = sum(0.1 for kw in keywords if kw in text) * weight
                scores[intent] = scores.get(intent, 0.5) + 0.3 + keyword_bonus

        if not scores:
            return Intent.UNKNOWN, 0.0

        best_intent = max(scores, key=scores.get)
        max_score = scores[best_intent]
        # 归一化：最高1.0
        confidence = min(1.0, max_score)
        self._rule_stats[best_intent] += 1
        return best_intent, confidence

    def _extract_topics(self, text: str) -> list[str]:
        """提取用户关注的话题关键词"""
        topics = []

        topic_map = {
            "大模型": ["大模型", "LLM", "GPT", "Gemini", "DeepSeek", "Qwen", "Llama", "Claude"],
            "推荐系统": ["推荐", "RecSys", "推荐系统", "协同过滤", "embedding"],
            "AI应用": ["AI应用", "AIGC", "AI Agent", "RAG", "知识库"],
            "AI创业": ["创业", "startup", "融资", "投资", "独角兽"],
            "AI安全": ["AI安全", "对齐", "可控性", "监管", "合规"],
            "AI硬件": ["AI芯片", "GPU", "H100", "算力", "NPU"],
        }

        for topic, keywords in topic_map.items():
            if any(kw.lower() in text.lower() for kw in keywords):
                topics.append(topic)

        return topics

    def _build_plan(
        self,
        text: str,
        intent: Intent,
        confidence: float,
        time_info: dict,
        scope: str,
        topics: list[str],
    ) -> TaskPlan:
        """根据解析结果构建任务计划"""

        suggestions = []

        # ── 帮助 ──────────────────────────────────────────────
        if intent == Intent.HELP:
            return TaskPlan(
                original_text=text,
                intent=Intent.HELP,
                confidence=1.0,
                description="显示帮助信息",
                suggestions=list(self.QUICK_TEMPLATES.values()),
                params={},
            )

        # ── 状态查询 ──────────────────────────────────────────
        if intent == Intent.STATUS_QUERY:
            return TaskPlan(
                original_text=text,
                intent=Intent.STATUS_QUERY,
                confidence=confidence,
                description="查询 OpenClaw 系统状态",
                message=f"请帮我查询当前 OpenClaw 的运行状态，包括活跃任务、CPU/内存使用情况。",
                estimated_time="10秒",
                params={},
            )

        # ── 取消任务 ──────────────────────────────────────────
        if intent == Intent.CANCEL_TASK:
            return TaskPlan(
                original_text=text,
                intent=Intent.CANCEL_TASK,
                confidence=confidence,
                description="取消指定任务",
                message="列出当前运行中的任务，并询问用户要取消哪个。",
                estimated_time="5秒",
                params={},
            )

        # ── 已知 Intent → 模板映射 ───────────────────────────
        if intent in self.TEMPLATE_MAP:
            template = self.TEMPLATE_MAP[intent]
            params = {
                "scope": scope if scope != "default" else "default",
                "time_range": time_info["label"],
            }
            if time_info.get("since"):
                params["since"] = time_info["since"]
            if topics:
                params["topics"] = topics

            suggestions = self._get_suggestions(intent, time_info, scope, topics)

            return TaskPlan(
                original_text=text,
                intent=intent,
                confidence=confidence,
                template_id=template["template_id"],
                agent=template["agent"],
                description=template["description"],
                estimated_time=template["estimated_time"],
                params=params,
                suggestions=suggestions,
            )

        # ── 未知 Intent → 透传给 OpenClaw 智能理解 ───────────
        # 这是最有价值的降级策略：让 OpenClaw 本身来理解用户意图
        return TaskPlan(
            original_text=text,
            intent=Intent.CUSTOM_TASK,
            confidence=confidence,
            description="自定义任务（由 OpenClaw 智能解析）",
            message=(
                f"用户说：{text}\n\n"
                f"请理解用户的意图，从以下能力中选择最合适的来执行：\n"
                f"1. 信息抓取助手 — 实时抓取AI领域最新资讯\n"
                f"2. 技术前沿分析师 — 追踪推荐系统+大模型技术前沿\n"
                f"3. 商业需求洞察分析师 — 发现跨行业AI应用商机\n"
                f"如果都不合适，请直接回答用户问题或执行合理的任务。\n"
                f"执行后将结果简要总结返回。"
            ),
            estimated_time="1-5分钟",
            params={"topics": topics} if topics else {},
            suggestions=[
                "正在交给 OpenClaw 智能处理...",
                "您也可以直接说：'技术简报'、'商业洞察'、'快速抓取'",
            ],
        )

    def _get_suggestions(
        self,
        intent: Intent,
        time_info: dict,
        scope: str,
        topics: list[str],
    ) -> list[str]:
        """生成下一步操作建议"""
        suggestions = []

        if intent == Intent.TECH_BRIEF:
            suggestions = [
                "📊 详细技术分析（深度）",
                "🔍 带大模型专项分析",
                "📅 本周技术趋势汇总",
            ]
        elif intent == Intent.MARKET_INSIGHT:
            suggestions = [
                "💼 垂直行业AI应用分析",
                "🚀 AI创业公司动态",
                "🏢 企业级AI需求调研",
            ]
        elif intent == Intent.QUICK_FETCH:
            suggestions = [
                "🔥 今日热点资讯",
                "🏭 大厂动态追踪",
                "📰 AI论文速递",
            ]
        elif intent == Intent.FULL_SCAN:
            suggestions = [
                "🕷️ 全网AI信息扫描",
                "📈 行业深度报告",
            ]

        return suggestions

    def get_command_reference(self) -> dict:
        """获取可用命令参考（用于帮助信息）"""
        return {
            "简短命令": {
                "简报": "生成今日技术简报",
                "商业": "生成商业洞察报告",
                "扫描": "执行全量信息扫描",
                "抓取": "快速抓取最新资讯",
                "状态": "查看系统状态",
                "帮助": "显示帮助信息",
            },
            "自然语言命令": [
                "帮我生成今日技术简报",
                "搜索一下最新的大模型动态",
                "查一下本周的商业AI应用案例",
                "快速抓取今天AI领域的热点资讯",
                "跑一个深度技术分析",
                "行业动态怎么样",
            ],
            "示例场景": [
                ("出差路上", "在手机上用 Siri 触发：'Siri，帮我跑一个技术简报'"),
                ("早晨通勤", "'帮我查一下昨晚有什么AI大新闻'"),
                ("会议前", "'快速扫描一下今日资讯，5分钟出结果'"),
                ("周末复盘", "'生成本周技术趋势报告，详细版'"),
            ],
        }

    def stats(self) -> dict:
        """返回解析统计（调试用）"""
        return dict(self._rule_stats)


# ─────────────────────────────────────────────────────────────
# 快捷函数
# ─────────────────────────────────────────────────────────────

def parse_natural_command(text: str, **kwargs) -> TaskPlan:
    """一行 API：解析自然语言命令"""
    return NLInterpreter(**kwargs).parse(text)
