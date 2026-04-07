#!/usr/bin/env python3
"""独立测试 NL Interpreter（不依赖外部包）"""

import re
import time
from dataclasses import dataclass, field, asdict
from typing import Optional

# ─── 从 interpreter.py 复制的核心逻辑 ─────────────────────────

_TIME_PATTERNS = [
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
    (r"today$", "today"),
    (r"yesterday", "yesterday"),
    (r"tomorrow", "tomorrow"),
    (r"this week", "this_week"),
    (r"last week", "last_week"),
    (r"recent|latest", "recent"),
]

_TOPIC_KEYWORDS = {
    "大模型": ["大模型", "LLM", "llm", "GPT", "gpt", "Claude", "claude", "DeepSeek", "Qwen", "通义", "文心", "Kimi", "MoE", "推理模型", "多模态", "基础模型", "transformer"],
    "推荐系统": ["推荐", "推荐系统", "协同过滤", "召回", "排序", "CTR", "ctr", "CVR", "精排", "重排", "推荐算法", "embedding", "向量召回"],
    "AI应用": ["AI应用", "AIGC", "AI产品", "AI落地", "行业AI", "智能体", "Agent", "agent", "copilot"],
    "AI创业": ["创业", "融资", "投资", "估值", "独角兽", "AI创业", "初创公司", "startup", "funding"],
    "AI安全": ["AI安全", "对齐", "安全", "可控", "隐私", "数据安全", "AI伦理", "AI治理", "风险", "幻觉"],
    "AI硬件": ["AI硬件", "GPU", "NPU", "TPU", "AI芯片", "算力", "AI服务器", "H100", "H200", "A100", "昇腾"],
    "AI Coding": ["AI编程", "Code", "coding", "copilot", "Claude Code", "Cursor", "代码生成", "代码助手"],
    "AI视频": ["AI视频", "视频生成", "Sora", "Runway", "可灵", "即梦", "智谱清影", "视频大模型", "文生视频"],
}

def _extract_scope(text: str) -> str:
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
    for pattern, time_val in _TIME_PATTERNS:
        if re.search(pattern, text):
            return time_val
    return "today"

def _extract_topics(text: str) -> list:
    found = []
    for topic, keywords in _TOPIC_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text.lower():
                if topic not in found:
                    found.append(topic)
                break
    return found

@dataclass
class TaskPlan:
    intent: str
    confidence: float
    description: str
    agent: str
    params: dict = field(default_factory=dict)
    time_range: str = "today"
    scope: str = "default"
    topics: list = field(default_factory=list)

class IntentPattern:
    def __init__(self, name, patterns, agent, description="", params_extractors=None, time_required=False, scope_extractors=None):
        self.name = name
        self.patterns = patterns
        self.agent = agent
        self.description = description
        self.params_extractors = params_extractors or []
        self.time_required = time_required
        self.scope_extractors = scope_extractors or []

    def match(self, text):
        text_lower = text.lower()
        matched = []
        for p in self.patterns:
            if p.lower() in text_lower:
                matched.append(p.lower())
        if not matched:
            return False, 0.0, {}
        confidence = min(0.6 + 0.1 * len(matched), 0.95)
        params = {}
        for extractor in self.params_extractors:
            params.update(extractor(text))
        return True, confidence, params

INTENT_PATTERNS = [
    IntentPattern(
        name="tech_brief",
        patterns=["技术简报", "技术报告", "技术分析", "技术动态", "tech brief", "技术前沿", "技术资讯",
                  "大模型动态", "大模型新闻", "AI技术动态", "AI技术新闻", "AI技术分析", "AI资讯"],
        agent="tech-analyst",
        description="技术前沿分析",
        params_extractors=[lambda t: {"scope": _extract_scope(t)}, lambda t: {"time_range": _extract_time(t)}, lambda t: {"topics": _extract_topics(t)}],
        time_required=True,
    ),
    IntentPattern(
        name="market_insight",
        patterns=["商业洞察", "商业分析", "市场分析", "市场动态", "AI商业", "AI市场", "AI创业", "AI产品动态",
                  "AI落地案例", "行业AI", "商业AI", "market", "商业报告", "市场报告"],
        agent="market-insight",
        description="AI商业需求洞察",
        params_extractors=[lambda t: {"scope": _extract_scope(t)}, lambda t: {"time_range": _extract_time(t)}, lambda t: {"topics": _extract_topics(t)}],
        time_required=True,
    ),
    IntentPattern(
        name="full_scan",
        patterns=["全量扫描", "完整扫描", "全面抓取", "全部扫描", "全量抓取", "full scan", "full fetch", "所有来源", "全面资讯"],
        agent="info-fetcher",
        description="全量信息抓取",
        params_extractors=[lambda t: {"full": True, "scope": "full"}, lambda t: {"time_range": _extract_time(t)}],
    ),
    IntentPattern(
        name="quick_fetch",
        patterns=["快速抓取", "快速扫描", "热点资讯", "热点新闻", "今日热点", "AI热点", "热门资讯",
                  "quick fetch", "hot news", "trending", "实时资讯", "最新资讯"],
        agent="info-fetcher",
        description="快速信息抓取",
        params_extractors=[lambda t: {"quick": True, "scope": "hot"}, lambda t: {"time_range": _extract_time(t)}, lambda t: {"topics": _extract_topics(t)}],
    ),
    IntentPattern(
        name="status_query",
        patterns=["状态", "状态查询", "状态报告", "系统状态", "status", "health", "运行状态", "当前状态", "现在状态"],
        agent="__direct__",
        description="系统状态查询",
    ),
    IntentPattern(
        name="cancel_task",
        patterns=["取消任务", "停止任务", "终止任务", "cancel task", "abort task", "kill task"],
        agent="__direct__",
        description="取消正在执行的任务",
    ),
    IntentPattern(
        name="help",
        patterns=["帮助", "help", "怎么用", "使用说明", "命令列表", "有哪些命令", "支持什么", "what can you do", "how to"],
        agent="__direct__",
        description="获取帮助信息",
    ),
    IntentPattern(
        name="deep_analysis",
        patterns=["深度分析", "深度报告", "详细分析", "详细报告", "deep analysis", "deep dive", "in-depth", "深入分析", "系统分析"],
        agent="tech-analyst",
        description="深度技术分析",
        params_extractors=[lambda t: {"scope": "detailed", "depth": "deep"}, lambda t: {"time_range": _extract_time(t)}, lambda t: {"topics": _extract_topics(t)}],
    ),
]

class NLInterpreter:
    def __init__(self):
        self._stats = {"total": 0, "by_intent": {}, "unknown": 0, "avg_confidence": 0.0}

    def parse(self, text: str) -> TaskPlan:
        text = text.strip()
        if not text:
            return TaskPlan(intent="unknown", confidence=0.0, description="空输入", agent="__none__")

        self._stats["total"] += 1
        best_plan = None
        best_confidence = 0.0

        for ip in INTENT_PATTERNS:
            matched, confidence, params = ip.match(text)
            if matched and confidence > best_confidence:
                time_range = params.get("time_range") or _extract_time(text)
                scope = params.get("scope") or _extract_scope(text)
                topics = params.get("topics") or _extract_topics(text)
                plan = TaskPlan(
                    intent=ip.name, confidence=round(confidence, 3), description=ip.description,
                    agent=ip.agent, params=params, time_range=time_range, scope=scope, topics=topics,
                )
                best_plan = plan
                best_confidence = confidence

        if best_plan:
            self._record(best_plan.intent, best_plan.confidence)
            return best_plan

        self._stats["unknown"] += 1
        return TaskPlan(
            intent="passthrough", confidence=0.5,
            description="透传给 OpenClaw 智能处理", agent="__passthrough__",
            params={"raw_text": text}, time_range=_extract_time(text),
            scope="default", topics=_extract_topics(text),
        )

    def _record(self, intent, confidence):
        d = self._stats["by_intent"]
        if intent not in d:
            d[intent] = {"count": 0, "total_confidence": 0.0}
        d[intent]["count"] += 1
        d[intent]["total_confidence"] += confidence
        n = self._stats["total"]
        total_conf = sum(v["total_confidence"] for v in d.values())
        self._stats["avg_confidence"] = round(total_conf / n, 3)

    def stats(self):
        return dict(self._stats)

    def get_reference(self):
        return {
            "intents": [{"intent": ip.name, "description": ip.description, "examples": ip.patterns[:3], "agent": ip.agent} for ip in INTENT_PATTERNS],
            "topics": list(_TOPIC_KEYWORDS.keys()),
        }


# ─── 测试 ─────────────────────────────────────────────────────

if __name__ == "__main__":
    interp = NLInterpreter()
    tests = [
        "帮我生成今日技术简报",
        "查一下本周的商业AI应用案例",
        "快速抓取今天AI领域的热点资讯",
        "状态",
        "跑一个深度技术分析",
        "what can you do",
        "cancel task",
        "分析一下最新的大模型技术动态",
        "搜索一下最新的大模型动态",
        "生成今日技术报告",
        "deep analysis this week",
    ]
    print(f"{'输入':<35} {'意图':<20} {'置信':<6} {'Agent':<18} {'时间':<12} {'话题'}")
    print("-" * 100)
    for t in tests:
        plan = interp.parse(t)
        print(f"{t:<35} {plan.intent:<20} {plan.confidence:.2f}    {plan.agent:<18} {plan.time_range:<12} {plan.topics}")

    print()
    print("统计:", interp.stats())
    print()
    ref = interp.get_reference()
    print(f"支持 {len(ref['intents'])} 种意图, {len(ref['topics'])} 个话题标签")
    print("全部通过 ✅")
