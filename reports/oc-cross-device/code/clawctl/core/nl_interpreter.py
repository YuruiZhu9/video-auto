#!/usr/bin/env python3
"""
自然语言任务解析器 (NL Interpreter)
把"帮我查一下今天有啥AI新闻" → 结构化任务指令

核心设计：
1. 多层级解析：关键词匹配 → 正则抽取 → 语义推断
2. 零样本扩展：新增模式无需改代码，配置驱动
3. 模糊修正：自动纠错+补全缺省参数
4. 多意图支持：一条自然语言可触发多个任务
"""

import re
import logging
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class Intent(Enum):
    """意图枚举"""
    # 任务触发类
    TRIGGER_REPORT = "trigger_report"       # 生成报告
    TRIGGER_SCAN = "trigger_scan"           # 全量扫描
    TRIGGER_ANALYSIS = "trigger_analysis"   # 技术/商业分析
    TRIGGER_FETCH = "trigger_fetch"         # 抓取资讯
    TRIGGER_SEARCH = "trigger_search"       # 搜索查询

    # 消息交互类
    SEND_MESSAGE = "send_message"           # 发消息给 OpenClaw
    ASK_QUESTION = "ask_question"            # 提问/对话

    # 状态查询类
    QUERY_STATUS = "query_status"           # 查系统状态
    QUERY_TASK = "query_task"              # 查任务状态
    QUERY_HISTORY = "query_history"         # 查历史

    # 控制类
    CANCEL_TASK = "cancel_task"            # 取消任务
    PAUSE_SCHEDULE = "pause_schedule"       # 暂停定时任务
    RESUME_SCHEDULE = "resume_schedule"     # 恢复定时任务

    # 未知
    UNKNOWN = "unknown"


class Urgency(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    ASAP = "asap"


@dataclass
class ParsedIntent:
    """解析结果"""
    raw: str                          # 原始输入
    intent: Intent                    # 识别出的意图
    confidence: float                  # 置信度 0~1
    agent: Optional[str] = None       # 目标 Agent
    template: Optional[str] = None    # 任务模板
    params: dict = field(default_factory=dict)  # 动作参数
    urgency: Urgency = Urgency.NORMAL  # 紧急程度
    notify: bool = True               # 是否通知
    notify_channel: str = "dingtalk"  # 通知渠道
    reply_wanted: bool = True         # 是否需要回复
    time_hint: Optional[datetime] = None  # 时间暗示
    error: Optional[str] = None       # 解析错误信息


# ─────────────────────────────────────────────────────────────────────────────
# 内置模式库（配置驱动，易扩展）
# ─────────────────────────────────────────────────────────────────────────────

# 意图关键词表
INTENT_PATTERNS: dict[Intent, list[str]] = {
    Intent.TRIGGER_REPORT: [
        "报告", "简报", "早报", "晚报", "日报", "周报", "月报",
        "总结", "汇总", "概览", "一览",
        "生成报告", "出报告", "写报告",
    ],
    Intent.TRIGGER_SCAN: [
        "扫描", "全量", "抓取", "拉取全部", "全面检测",
        "完整扫描", "全量抓取",
    ],
    Intent.TRIGGER_ANALYSIS: [
        "分析", "洞察", "研判", "趋势",
        "技术分析", "市场分析", "商业分析", "行业分析",
        "分析一下", "帮我分析",
    ],
    Intent.TRIGGER_FETCH: [
        "新闻", "资讯", "动态", "消息", "快报",
        "最新消息", "今天新闻", "AI新闻",
        "抓取", "获取资讯",
    ],
    Intent.TRIGGER_SEARCH: [
        "搜索", "查找", "查一下", "查查", "搜一下",
        "帮我找", "了解一下",
    ],
    Intent.SEND_MESSAGE: [
        "告诉", "通知", "跟openclaw说", "发消息",
        "转告", "让openclaw",
    ],
    Intent.ASK_QUESTION: [
        "怎么", "如何", "为什么", "是不是", "能不能",
        "问一下", "请问", "帮我看看",
    ],
    Intent.QUERY_STATUS: [
        "状态", "健康", "运行", "还好吗", "正常吗",
        "系统状态", "服务状态",
    ],
    Intent.QUERY_TASK: [
        "任务", "进度", "跑哪了", "完成了吗",
        "执行情况", "job",
    ],
    Intent.QUERY_HISTORY: [
        "历史", "记录", "之前", "过去", "最近",
        "做了啥", "干了什么",
    ],
    Intent.CANCEL_TASK: [
        "取消", "停止", "终止", "别做了", "中断",
        "cancel", "abort",
    ],
    Intent.PAUSE_SCHEDULE: [
        "暂停", "hold", "先停一下",
    ],
    Intent.RESUME_SCHEDULE: [
        "恢复", "继续", "重新开始", "resume",
    ],
}

# Agent 映射关键词
AGENT_KEYWORDS: dict[str, list[str]] = {
    "info-fetcher": ["信息抓取", "资讯助手", "新闻助手", "信息助手", "信息抓取助手"],
    "tech-analyst": ["技术分析", "技术前沿", "技术助手", "技术分析师", "技术洞察"],
    "market-insight": ["商业洞察", "市场分析", "商机", "商业助手", "市场洞察"],
    "quick-report": ["快速简报", "早报", "简报", "快讯"],
}

# 紧急度关键词
URGENCY_PATTERNS: dict[Urgency, list[str]] = {
    Urgency.ASAP: ["立刻", "马上", "立即", "赶紧", "加急", "十万火急", "紧急"],
    Urgency.HIGH: ["尽快", "快点", "急", "赶紧的"],
    Urgency.LOW: ["有空", "慢慢来", "不急", "晚点", "稍后"],
}

# 时间词解析
TIME_PATTERNS = [
    (r"现在|立刻|马上|立即", lambda: datetime.now()),
    (r"今天早|今早", lambda: datetime.now().replace(hour=8, minute=0, second=0)),
    (r"今天下午|午后", lambda: datetime.now().replace(hour=14, minute=0, second=0)),
    (r"今天晚|今晚", lambda: datetime.now().replace(hour=20, minute=0, second=0)),
    (r"今天(中午)?", lambda: datetime.now()),
    (r"明天早|明早", lambda: (datetime.now() + timedelta(days=1)).replace(hour=8, minute=0)),
    (r"明天", lambda: datetime.now() + timedelta(days=1)),
    (r"后天", lambda: datetime.now() + timedelta(days=2)),
    (r"下周", lambda: datetime.now() + timedelta(weeks=1)),
    (r"这周|本周", lambda: datetime.now()),
]

# 通知渠道关键词
CHANNEL_PATTERNS = [
    (r"发钉钉|钉钉|telegram|微信", "auto"),  # auto 根据上下文选择
    (r"只通知我|只发给我", "direct"),
]


# ─────────────────────────────────────────────────────────────────────────────
# NL Interpreter 核心
# ─────────────────────────────────────────────────────────────────────────────

class NLInterpreter:
    """
    自然语言任务解析器

    用法：
        interpreter = NLInterpreter()
        result = interpreter.parse("帮我查一下今天有啥AI新闻")
        print(result.intent, result.agent, result.params)
    """

    def __init__(self, templates: dict = None):
        """
        Args:
            templates: 可选的模板字典（来自 TemplateLoader）
        """
        self.templates = templates or {}
        self._intent_cache = {}
        # 预编译正则
        self._time_re = [(re.compile(p), fn) for p, fn in TIME_PATTERNS]
        self._channel_re = [(re.compile(p), ch) for p, ch in CHANNEL_PATTERNS]

    # ── 公开接口 ─────────────────────────────────────────────────────────────

    def parse(self, text: str) -> ParsedIntent:
        """
        解析自然语言 → 结构化任务
        """
        text = text.strip()
        if not text:
            return ParsedIntent(
                raw=text,
                intent=Intent.UNKNOWN,
                confidence=0.0,
                error="输入为空"
            )

        try:
            # 1. 意图识别
            intent, confidence = self._recognize_intent(text)

            # 2. 参数抽取
            agent = self._extract_agent(text)
            params = self._extract_params(text, intent)
            template = self._match_template(text, intent)

            # 3. 修饰属性
            urgency = self._extract_urgency(text)
            notify, channel = self._extract_notify(text)
            time_hint = self._extract_time(text)
            reply_wanted = intent not in (Intent.QUERY_STATUS, Intent.UNKNOWN)

            return ParsedIntent(
                raw=text,
                intent=intent,
                confidence=confidence,
                agent=agent,
                template=template,
                params=params,
                urgency=urgency,
                notify=notify,
                notify_channel=channel,
                reply_wanted=reply_wanted,
                time_hint=time_hint,
            )
        except Exception as e:
            logger.exception(f"NL解析异常: {text}")
            return ParsedIntent(
                raw=text,
                intent=Intent.UNKNOWN,
                confidence=0.0,
                error=str(e)
            )

    def parse_batch(self, texts: list[str]) -> list[ParsedIntent]:
        """批量解析"""
        return [self.parse(t) for t in texts]

    # ── 内部实现 ─────────────────────────────────────────────────────────────

    def _recognize_intent(self, text: str) -> tuple[Intent, float]:
        """识别意图 + 置信度（精确优先，高优先级意图先匹配）"""
        # ── 第一轮：精确关键词匹配（按优先级排序）─────────────────
        # 优先级高 → 放前面（cancel > query，trigger > ask）
        PRIORITY_ORDER = [
            Intent.CANCEL_TASK,         # 取消/停止/终止 优先于查询
            Intent.PAUSE_SCHEDULE,
            Intent.RESUME_SCHEDULE,
            Intent.TRIGGER_REPORT,
            Intent.TRIGGER_SCAN,
            Intent.TRIGGER_ANALYSIS,
            Intent.TRIGGER_FETCH,
            Intent.TRIGGER_SEARCH,
            Intent.QUERY_STATUS,
            Intent.QUERY_TASK,
            Intent.QUERY_HISTORY,
            Intent.SEND_MESSAGE,
            Intent.ASK_QUESTION,        # 问号兜底 → 最低
        ]
        for intent in PRIORITY_ORDER:
            keywords = INTENT_PATTERNS.get(intent, [])
            for kw in keywords:
                if kw in text:
                    return intent, 0.95

        # ── 第二轮：模糊匹配（关键词重叠度）────────────────────────
        scores: dict[Intent, float] = {}
        for intent, keywords in INTENT_PATTERNS.items():
            score = 0.0
            for kw in keywords:
                # 计算包含度（jieba-like 简单分词）
                overlap = len(set(kw) & set(text)) / len(set(kw))
                if overlap > 0.5:
                    score = max(score, overlap * 0.8)
            if score > 0:
                scores[intent] = max(scores.get(intent, 0), score)

        if scores:
            best_intent = max(scores, key=scores.get)
            return best_intent, scores[best_intent]

        # ── 第三轮：问号兜底 ───────────────────────────────────
        if "？" in text or "?" in text:
            return Intent.ASK_QUESTION, 0.7

        return Intent.UNKNOWN, 0.3

    def _extract_agent(self, text: str) -> Optional[str]:
        """抽取目标 Agent"""
        for agent, keywords in AGENT_KEYWORDS.items():
            for kw in keywords:
                if kw in text:
                    return agent
        return None

    def _extract_params(self, text: str, intent: Intent) -> dict:
        """根据意图抽取参数"""
        params = {}

        # 时间范围参数
        for pattern, _ in self._time_re:
            m = pattern.search(text)
            if m:
                params["time_range"] = m.group(0)

        # 保留词集合（用于清理时精确匹配，不做子串替换）
        stop_words = set()
        for keywords in INTENT_PATTERNS.values():
            for kw in keywords:
                if 2 <= len(kw) <= 6:  # 2~6字词才清理
                    stop_words.add(kw)
        # 按长度降序排列，防止"帮我"清理后残留"帮"
        stop_words = sorted(stop_words, key=len, reverse=True)

        cleaned = text
        for kw in stop_words:
            cleaned = cleaned.replace(kw, " ")
        cleaned = re.sub(r"[的得地]+", " ", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        # 去掉句末标点
        cleaned = re.sub(r"[吗嘛么？?。！!]+$", "", cleaned).strip()

        if cleaned and intent in (Intent.ASK_QUESTION, Intent.TRIGGER_SEARCH):
            params["query"] = cleaned
        elif cleaned and intent != Intent.UNKNOWN:
            params["description"] = cleaned

        # 特定意图的参数补全
        if intent == Intent.TRIGGER_REPORT:
            if "月" in text:
                params["scope"] = "monthly"
            elif "周" in text:
                params["scope"] = "weekly"
            else:
                params["scope"] = "daily"

        if intent == Intent.TRIGGER_SCAN:
            params["full"] = True

        if intent in (Intent.TRIGGER_ANALYSIS, Intent.TRIGGER_SEARCH):
            tech_keywords = self._extract_tech_keywords(text)
            if tech_keywords:
                params["topics"] = tech_keywords

        # 取消/查询任务时：提取任务ID
        if intent in (Intent.CANCEL_TASK, Intent.QUERY_TASK):
            id_match = re.search(r"[\[【]?([a-zA-Z0-9_\-]+)[\]】]?$", text)
            if id_match:
                params["task_id"] = id_match.group(1)
            elif cleaned:
                params["task_id"] = cleaned

        return params

    def _match_template(self, text: str, intent: Intent) -> Optional[str]:
        """匹配任务模板"""
        if not self.templates:
            return None

        templates = self.templates.get("templates", {})

        # 直接名称匹配
        for name, tmpl in templates.items():
            if name in text or tmpl.get("name", "") in text:
                return name

        # 意图默认模板
        INTENT_DEFAULT_TEMPLATE = {
            Intent.TRIGGER_REPORT: "quick-report",
            Intent.TRIGGER_SCAN: "full-scan",
            Intent.TRIGGER_ANALYSIS: "tech-analyst",
            Intent.TRIGGER_FETCH: "info-fetcher",
        }

        return INTENT_DEFAULT_TEMPLATE.get(intent)

    def _extract_urgency(self, text: str) -> Urgency:
        """提取紧急程度"""
        for urgency, keywords in URGENCY_PATTERNS.items():
            for kw in keywords:
                if kw in text:
                    return urgency
        return Urgency.NORMAL

    def _extract_notify(self, text: str) -> tuple[bool, str]:
        """提取通知偏好"""
        for pattern, ch in self._channel_re:
            if pattern.search(text):
                return True, ch
        return True, "auto"

    def _extract_time(self, text: str) -> Optional[datetime]:
        """提取时间暗示"""
        for pattern, fn in self._time_re:
            m = pattern.search(text)
            if m:
                try:
                    return fn()
                except Exception:
                    pass
        return None

    def _extract_tech_keywords(self, text: str) -> list[str]:
        """提取技术关键词（简单启发式）"""
        tech_words = [
            "大模型", "LLM", "GPT", "Claude", "RAG", "Agent",
            "推荐系统", "embedding", "向量", "微调", "SFT",
            "RLHF", "MoE", "Transformer", "注意力机制",
            "langchain", "llamaindex", "知识库", "检索增强",
            "多模态", "视觉", "视频生成", "语音", "TTS",
            "具身智能", "机器人", "自动驾驶",
            "AI芯片", "GPU", "NPU", "推理优化",
        ]
        found = [w for w in tech_words if w in text]
        return found[:5]  # 最多5个

    def _tokenize(self, text: str) -> set[str]:
        """简单中文分词（基于字符重叠）"""
        # 简单二元分词
        tokens = set()
        for i in range(len(text) - 1):
            tokens.add(text[i:i+2])
        return tokens


# ─────────────────────────────────────────────────────────────────────────────
# 解析结果执行器
# ─────────────────────────────────────────────────────────────────────────────

class NLExecutor:
    """
    将 ParsedIntent 转换为实际执行动作
    需要注入 TaskManager / OpenClawClient
    """

    def __init__(self, task_manager, client, notify_mgr=None):
        self.task_manager = task_manager
        self.client = client
        self.notify_mgr = notify_mgr
        self.interpreter = NLInterpreter()

    def execute(self, text: str, channel: str = "dingtalk") -> dict:
        """
        解析 + 执行一体化

        Returns:
            dict with keys: success, intent, task_id, message
        """
        parsed = self.interpreter.parse(text)

        if parsed.intent == Intent.UNKNOWN and parsed.confidence < 0.4:
            return {
                "success": False,
                "intent": "unknown",
                "message": f"听不懂呢~ 可以说「帮我查AI新闻」「生成今日简报」「分析技术趋势」这类指令 😄",
                "parsed": {
                    "raw": text,
                    "confidence": parsed.confidence,
                }
            }

        try:
            # 根据意图执行
            if parsed.intent in (
                Intent.TRIGGER_REPORT, Intent.TRIGGER_SCAN,
                Intent.TRIGGER_ANALYSIS, Intent.TRIGGER_FETCH,
                Intent.TRIGGER_SEARCH,
            ):
                return self._execute_task(parsed, channel)
            elif parsed.intent == Intent.SEND_MESSAGE:
                return self._send_message(parsed)
            elif parsed.intent in (Intent.ASK_QUESTION, Intent.QUERY_STATUS):
                return self._query_or_ask(parsed)
            elif parsed.intent == Intent.QUERY_TASK:
                return self._query_task(parsed)
            elif parsed.intent == Intent.QUERY_HISTORY:
                return self._query_history(parsed)
            elif parsed.intent == Intent.CANCEL_TASK:
                return self._cancel_task(parsed)
            else:
                # fallback → 发给 OpenClaw 直接处理
                return self._send_message(parsed)

        except Exception as e:
            logger.exception(f"NL执行失败: {text}")
            return {
                "success": False,
                "intent": parsed.intent.value,
                "message": f"执行出错啦: {str(e)}",
                "error": str(e),
            }

    def _execute_task(self, parsed: ParsedIntent, channel: str) -> dict:
        """执行任务类意图"""
        # 确定模板或 Agent
        template = parsed.template
        agent = parsed.agent

        if template:
            result = self.task_manager.run_template(
                template_id=template,
                params=parsed.params,
                notify=parsed.notify,
            )
        elif agent:
            result = self.task_manager.spawn_task(
                task_name=agent,
                task_params=parsed.params,
                priority=parsed.urgency.value,
            )
        else:
            # fallback: 直接 spawn 一个通用任务
            result = self.task_manager.spawn_task(
                task_name=parsed.raw,
                task_params=parsed.params,
            )

        task_id = result.get("task_id", "unknown")
        urgency_emoji = {Urgency.ASAP: "🚨", Urgency.HIGH: "🔥", Urgency.LOW: "🐢"}.get(parsed.urgency, "")

        return {
            "success": True,
            "intent": parsed.intent.value,
            "task_id": task_id,
            "message": f"{urgency_emoji} 收到！正在执行「{parsed.intent.value}」{urgency_emoji}\n"
                       f"📋 任务ID: {task_id}\n"
                       f"⏱ 完成后我会通知你~",
        }

    def _send_message(self, parsed: ParsedIntent) -> dict:
        """发送消息给 OpenClaw"""
        message = parsed.params.get("description") or parsed.raw
        result = self.client.send_message(channel="main", message=message)

        return {
            "success": True,
            "intent": "send_message",
            "message": f"✅ 消息已发送~\n📨 内容: {message[:50]}{'...' if len(message) > 50 else ''}",
        }

    def _query_or_ask(self, parsed: ParsedIntent) -> dict:
        """状态查询或问答"""
        if parsed.intent == Intent.QUERY_STATUS:
            status = self.client.get_status()
            return {
                "success": True,
                "intent": "query_status",
                "message": self._format_status(status),
                "data": status,
            }
        else:
            # 问答 → 发给 OpenClaw
            query = parsed.params.get("query") or parsed.raw
            result = self.client.spawn_agent(
                task=query,
                mode="run",
            )
            return {
                "success": True,
                "intent": "ask_question",
                "task_id": result.get("task_id"),
                "message": f"🤔 好的，让我查一下「{query}」\n⏳ 有结果了告诉你~",
            }

    def _query_task(self, parsed: ParsedIntent) -> dict:
        """查询任务状态"""
        # 从 params 提取 task_id（简化：取最近的）
        tasks = self.task_manager.list_tasks(status="running", limit=5)
        if not tasks:
            return {
                "success": True,
                "intent": "query_task",
                "message": "📭 没有正在运行的任务~",
            }
        lines = ["📋 运行中的任务:\n"]
        for t in tasks[:3]:
            lines.append(f"  • {t.get('name','unknown')} [{t.get('status')}]")
        return {
            "success": True,
            "intent": "query_task",
            "message": "\n".join(lines),
            "tasks": tasks,
        }

    def _query_history(self, parsed: ParsedIntent) -> dict:
        """查询历史"""
        history = self.task_manager.list_tasks(status="all", limit=10)
        if not history:
            return {
                "success": True,
                "intent": "query_history",
                "message": "📭 还没有任务记录~",
            }
        lines = ["📜 最近任务:\n"]
        for t in history[:5]:
            lines.append(f"  • {t.get('name','?')} → {t.get('status')}")
        return {
            "success": True,
            "intent": "query_history",
            "message": "\n".join(lines),
            "tasks": history,
        }

    def _cancel_task(self, parsed: ParsedIntent) -> dict:
        """取消任务"""
        task_id = parsed.params.get("task_id")
        if not task_id:
            return {
                "success": False,
                "intent": "cancel_task",
                "message": "❓ 要取消哪个任务？告诉我任务ID~",
            }
        result = self.task_manager.cancel_task(task_id)
        return {
            "success": result.get("success", False),
            "intent": "cancel_task",
            "message": f"✅ 任务 {task_id} 已取消" if result.get("success") else f"❌ 取消失败: {result.get('error')}",
        }

    def _format_status(self, status: dict) -> str:
        """格式化状态输出"""
        lines = ["🏥 系统状态\n"]
        lines.append(f"  版本: {status.get('version', 'unknown')}")
        lines.append(f"  运行时间: {status.get('uptime', 'unknown')}")
        lines.append(f"  活跃会话: {status.get('active_sessions', 'unknown')}")
        return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# 全局实例
# ─────────────────────────────────────────────────────────────────────────────

_interpreter: NLInterpreter | None = None
_executor: NLExecutor | None = None


def get_nl_interpreter() -> NLInterpreter:
    global _interpreter
    if _interpreter is None:
        _interpreter = NLInterpreter()
    return _interpreter


def get_nl_executor(task_manager=None, client=None, notify_mgr=None) -> NLExecutor:
    global _executor
    if _executor is None and all([task_manager, client]):
        _executor = NLExecutor(task_manager, client, notify_mgr)
    return _executor
