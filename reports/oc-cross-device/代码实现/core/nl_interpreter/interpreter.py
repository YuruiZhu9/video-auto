"""
自然语言任务解析引擎 (NL Interpreter)
将用户输入的自然语言转换为可执行的任务计划
"""

import re
import time
import logging
from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


# ─── Intent 定义 ────────────────────────────────────────────

@dataclass
class Intent:
    name: str
    confidence: float
    description: str
    params: dict = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


@dataclass
class TaskPlan:
    intent: str
    confidence: float
    description: str
    agent: str
    params: dict
    time_range: str = "today"
    scope: str = "default"
    topics: list = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


# ─── 时间解析 ───────────────────────────────────────────────

_TIME_PATTERNS = [
    # 中文
    (r"今天早间|今日早间|上午", "morning"),
    (r"今天下午|今日下午|下午", "afternoon"),
    (r"今天晚间|今日晚间|今晚|夜间", "evening"),
    (r"今天$|今日$", "today"),
    (r"昨天$", "yesterday"),
    (r"明天$", "tomorrow"),
    (r"本周$|这周$|本周内", "this_week"),
    (r"上周$", "last_week"),
    (r"最近|近期|最近几天", "recent"),
    (r"本月|这个月", "this_month"),
    # 英文
    (r"today$", "today"),
    (r"yesterday", "yesterday"),
    (r"tomorrow", "tomorrow"),
    (r"this week", "this_week"),
    (r"last week", "last_week"),
    (r"recent|latest", "recent"),
]

# ─── 话题关键词 ─────────────────────────────────────────────

_TOPIC_KEYWORDS = {
    "大模型": ["大模型", "LLM", "llm", "GPT", "gpt", "Claude", "claude", "Gemini", "DeepSeek", "Qwen", "通义", "文心", "Kimi", "MoE", "RAG", "推理模型", "多模态", "基础模型", "大语言模型", "语言模型", "transformer", "Transformer"],
    "推荐系统": ["推荐", "推荐系统", "协同过滤", "召回", "排序", "CTR", "ctr", "CVR", "精排", "重排", "推荐算法", "embedding", "向量召回", "特征工程", "RS", "recommendation"],
    "AI应用": ["AI应用", "AIGC", "AI产品", "AI落地", "行业AI", "AI产业化", "应用场景", "智能体", "Agent", "agent", "RAG", "copilot", "Copilot"],
    "AI创业": ["创业", "融资", "投资", "估值", "独角兽", "AI创业", "初创公司", "startup", "funding", "Series A", "Series B", "VC", "vc", "估值"],
    "AI安全": ["AI安全", "对齐", "安全", "可控", "隐私", "数据安全", "AI伦理", "AI治理", "风险", "幻觉", "越狱", "红队", "对抗", "safety", "alignment", "security", "privacy"],
    "AI硬件": ["AI硬件", "GPU", "NPU", "TPU", "AI芯片", "算力", "AI服务器", "H100", "H200", "A100", "昇腾", "寒武纪", "硅基流动", "算力租赁", "算力平台", "芯片"],
    "AI Coding": ["AI编程", "Code", "coding", "copilot", "Claude Code", "Cursor", "代码生成", "代码助手", "IDE插件", "AI写代码", "code agent"],
    "AI视频": ["AI视频", "视频生成", "Sora", "Runway", "可灵", "即梦", "智谱清影", "视频大模型", "文生视频", "AI短视频"],
    "AI音乐": ["AI音乐", "音乐生成", "Suno", "UDIO", "音频生成", "AUDIO", "AI作曲", "AI唱歌"],
}

# ─── 意图模式 ────────────────────────────────────────────────

class IntentPattern:
    def __init__(self, name: str, patterns: list[str], agent: str,
                 description: str = "", params_extractors: list = None,
                 time_required: bool = False, scope_extractors: list = None):
        self.name = name
        self.patterns = patterns
        self.agent = agent
        self.description = description
        self.params_extractors = params_extractors or []
        self.time_required = time_required
        self.scope_extractors = scope_extractors or []

    def match(self, text: str) -> tuple[bool, float, dict]:
        """
        尝试匹配文本，返回 (是否匹配, 置信度, 提取的参数)
        """
        text_lower = text.lower()
        matched = []
        for p in self.patterns:
            # 精确匹配关键词
            if p.lower() in text_lower:
                matched.append(p.lower())
        
        if not matched:
            return False, 0.0, {}
        
        # 置信度：匹配越多越确定
        confidence = min(0.6 + 0.1 * len(matched), 0.95)
        
        params = {}
        for extractor in self.params_extractors:
            params.update(extractor(text))
        
        return True, confidence, params


# ─── Intent Pattern 库 ──────────────────────────────────────

INTENT_PATTERNS: list[IntentPattern] = [

    # ── 技术简报 ────────────────────────────────────────────
    IntentPattern(
        name="tech_brief",
        patterns=[
            "技术简报", "技术报告", "技术分析", "技术动态",
            "tech brief", "技术前沿", "技术资讯",
            "大模型动态", "大模型新闻", "AI技术动态",
            "AI技术新闻", "AI技术分析", "AI资讯",
        ],
        agent="tech-analyst",
        description="技术前沿分析",
        params_extractors=[
            lambda t: {"scope": _extract_scope(t)},
            lambda t: {"time_range": _extract_time(t)},
            lambda t: {"topics": _extract_topics(t)},
        ],
        time_required=True,
        scope_extractors=[_extract_scope],
    ),

    # ── 商业洞察 ────────────────────────────────────────────
    IntentPattern(
        name="market_insight",
        patterns=[
            "商业洞察", "商业分析", "市场分析", "市场动态",
            "AI商业", "AI市场", "AI创业", "AI产品动态",
            "AI落地案例", "行业AI", "商业AI",
            "market", "商业报告", "市场报告",
        ],
        agent="market-insight",
        description="AI商业需求洞察",
        params_extractors=[
            lambda t: {"scope": _extract_scope(t)},
            lambda t: {"time_range": _extract_time(t)},
            lambda t: {"topics": _extract_topics(t)},
        ],
        time_required=True,
    ),

    # ── 全量扫描 ────────────────────────────────────────────
    IntentPattern(
        name="full_scan",
        patterns=[
            "全量扫描", "完整扫描", "全面抓取", "全部扫描",
            "全量抓取", "full scan", "full fetch",
            "所有来源", "全面资讯",
        ],
        agent="info-fetcher",
        description="全量信息抓取",
        params_extractors=[
            lambda t: {"full": True, "scope": "full"},
            lambda t: {"time_range": _extract_time(t)},
        ],
    ),

    # ── 快速抓取 ────────────────────────────────────────────
    IntentPattern(
        name="quick_fetch",
        patterns=[
            "快速抓取", "快速扫描", "热点资讯", "热点新闻",
            "今日热点", "AI热点", "热门资讯",
            "quick fetch", "hot news", "trending",
            "实时资讯", "最新资讯",
        ],
        agent="info-fetcher",
        description="快速信息抓取",
        params_extractors=[
            lambda t: {"quick": True, "scope": "hot"},
            lambda t: {"time_range": _extract_time(t)},
            lambda t: {"topics": _extract_topics(t)},
        ],
    ),

    # ── 状态查询 ────────────────────────────────────────────
    IntentPattern(
        name="status_query",
        patterns=[
            "状态", "状态查询", "状态报告", "系统状态",
            "status", "health", "运行状态",
            "当前状态", "现在状态",
        ],
        agent="__direct__",
        description="系统状态查询",
    ),

    # ── 取消任务 ────────────────────────────────────────────
    IntentPattern(
        name="cancel_task",
        patterns=[
            "取消任务", "停止任务", "终止任务",
            "cancel task", "abort task", "kill task",
        ],
        agent="__direct__",
        description="取消正在执行的任务",
    ),

    # ── 帮助 ───────────────────────────────────────────────
    IntentPattern(
        name="help",
        patterns=[
            "帮助", "help", "怎么用", "使用说明",
            "命令列表", "有哪些命令", "支持什么",
            "what can you do", "how to",
        ],
        agent="__direct__",
        description="获取帮助信息",
    ),

    # ── 深度分析 ────────────────────────────────────────────
    IntentPattern(
        name="deep_analysis",
        patterns=[
            "深度分析", "深度报告", "详细分析", "详细报告",
            "deep analysis", "deep dive", "in-depth",
            "深入分析", "系统分析",
        ],
        agent="tech-analyst",
        description="深度技术分析",
        params_extractors=[
            lambda t: {"scope": "detailed", "depth": "deep"},
            lambda t: {"time_range": _extract_time(t)},
            lambda t: {"topics": _extract_topics(t)},
        ],
    ),
]


# ─── 辅助提取函数 ────────────────────────────────────────────

def _extract_scope(text: str) -> str:
    """提取分析范围"""
    scope_map = {
        r"详细|深度|完整|全面|全量": "detailed",
        r"简略|简单|概要|快速": "brief",
        r"最新|最近|今日|当天": "latest",
    }
    for pattern, scope in scope_map.items():
        if re.search(pattern, text):
            return scope
    return "default"


def _extract_time(text: str) -> str:
    """提取时间范围"""
    for pattern, time_val in _TIME_PATTERNS:
        if re.search(pattern, text):
            return time_val
    return "today"  # 默认今天


def _extract_topics(text: str) -> list:
    """提取话题标签"""
    found = []
    for topic, keywords in _TOPIC_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text.lower():
                if topic not in found:
                    found.append(topic)
                break
    return found


# ─── NL Interpreter ─────────────────────────────────────────

class NLInterpreter:
    """
    自然语言任务解析器

    使用规则引擎进行意图识别和参数提取，
    未知命令降级透传给 OpenClaw 自身处理。
    """

    def __init__(self):
        self._stats = {
            "total": 0,
            "by_intent": {},
            "unknown": 0,
            "avg_confidence": 0.0,
        }

    def parse(self, text: str) -> TaskPlan:
        """
        解析自然语言命令，返回任务计划
        """
        text = text.strip()
        if not text:
            return self._unknown_plan("空输入")

        self._stats["total"] += 1
        best_plan: Optional[TaskPlan] = None
        best_confidence = 0.0

        for ip in INTENT_PATTERNS:
            matched, confidence, params = ip.match(text)
            if matched and confidence > best_confidence:
                time_range = params.get("time_range") or _extract_time(text)
                scope = params.get("scope") or _extract_scope(text)
                topics = params.get("topics") or _extract_topics(text)

                plan = TaskPlan(
                    intent=ip.name,
                    confidence=round(confidence, 3),
                    description=ip.description,
                    agent=ip.agent,
                    params=params,
                    time_range=time_range,
                    scope=scope,
                    topics=topics,
                )
                best_plan = plan
                best_confidence = confidence

        if best_plan:
            self._record(best_plan.intent, best_plan.confidence)
            return best_plan

        # 降级：透传给 OpenClaw 自身
        self._stats["unknown"] += 1
        logger.info(f"[NLInterpreter] 未知命令，降级透传: {text!r}")
        return TaskPlan(
            intent="passthrough",
            confidence=0.5,
            description="透传给 OpenClaw 智能处理",
            agent="__passthrough__",
            params={"raw_text": text},
            time_range=_extract_time(text),
            scope="default",
            topics=_extract_topics(text),
        )

    def _record(self, intent: str, confidence: float):
        """记录解析统计"""
        d = self._stats["by_intent"]
        if intent not in d:
            d[intent] = {"count": 0, "total_confidence": 0.0}
        d[intent]["count"] += 1
        d[intent]["total_confidence"] += confidence

        n = self._stats["total"]
        total_conf = sum(v["total_confidence"] for v in d.values())
        self._stats["avg_confidence"] = round(total_conf / n, 3)

    def stats(self) -> dict:
        """返回解析统计"""
        return dict(self._stats)

    def reset_stats(self):
        """重置统计"""
        self._stats = {
            "total": 0,
            "by_intent": {},
            "unknown": 0,
            "avg_confidence": 0.0,
        }

    def _unknown_plan(self, reason: str) -> TaskPlan:
        return TaskPlan(
            intent="unknown",
            confidence=0.0,
            description=reason,
            agent="__none__",
            params={},
        )

    def get_reference(self) -> dict:
        """获取命令参考（帮助信息）"""
        return {
            "description": "自然语言任务解析器 — 输入中文或英文命令，自动识别意图并执行",
            "intents": [
                {
                    "intent": ip.name,
                    "description": ip.description,
                    "examples": ip.patterns[:4],
                    "agent": ip.agent,
                }
                for ip in INTENT_PATTERNS
            ],
            "time_keywords": {t: v for pattern, v in _TIME_PATTERNS for t in [pattern.pattern if hasattr(pattern, 'pattern') else str(pattern)]},
            "topics": list(_TOPIC_KEYWORDS.keys()),
        }


# ─── 全局单例 ────────────────────────────────────────────────

_interpreter: Optional[NLInterpreter] = None


def get_interpreter() -> NLInterpreter:
    global _interpreter
    if _interpreter is None:
        _interpreter = NLInterpreter()
    return _interpreter


def parse_natural_command(text: str) -> TaskPlan:
    """快捷函数：一行 API 解析自然语言命令"""
    return get_interpreter().parse(text)
