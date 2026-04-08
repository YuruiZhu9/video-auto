"""
LLM驱动的NL深度解析器 (v2.7.0)
当规则引擎置信度不足时，调用大模型进行深度语义理解和意图识别
"""

import os
import json
import logging
import time
from dataclasses import dataclass, field, asdict
from typing import Optional, Literal

import httpx

logger = logging.getLogger(__name__)

# ─── 常量 ──────────────────────────────────────────────────

# GLM-4-Flash API（免费额度：200万Tokens/天）
GLM_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
GLM_MODEL = "glm-4-flash"

# 置信度阈值：低于此值则触发LLM增强
CONFIDENCE_THRESHOLD = 0.55

# LLM解析超时（秒）
LLM_TIMEOUT = 15

# ─── Agent 映射 ────────────────────────────────────────────

AGENT_MAPPING = {
    "info-fetcher": "info-fetcher",
    "tech-analyst": "tech-analyst",
    "market-insight": "market-insight",
    "quick-report": "quick-report",
    "full-scan": "info-fetcher",
    "quick-fetch": "info-fetcher",
}

# ─── 系统提示词 ────────────────────────────────────────────

SYSTEM_PROMPT = """你是一个专业的AI助手任务解析引擎。你的任务是将用户的中文自然语言指令解析为结构化的任务计划。

## 支持的意图类型（必须严格返回以下之一）

| intent | 说明 | agent | 典型示例 |
|--------|------|-------|----------|
| trigger_fetch | 信息抓取 | info-fetcher | "帮我查AI新闻" "抓取最新资讯" |
| trigger_report | 生成报告 | tech-analyst/market-insight | "生成技术简报" "给我今日报告" |
| trigger_analysis | 技术分析 | tech-analyst | "分析RAG技术趋势" |
| trigger_scan | 全量扫描 | info-fetcher | "全量扫描AI动态" |
| trigger_search | 专项搜索 | info-fetcher | "搜索一下大模型最新进展" |
| send_message | 发送消息 | __direct__ | "发消息给技术群" |
| ask_question | 问答 | tech-analyst | "推荐系统怎么做召回" |
| query_status | 状态查询 | __direct__ | "现在状态如何" |
| query_task | 任务查询 | __direct__ | "最近任务有哪些" |
| cancel_task | 取消任务 | __direct__ | "取消刚才的任务" |
| pause_schedule | 暂停定时 | __direct__ | "暂停定时任务" |
| resume_schedule | 恢复定时 | __direct__ | "恢复定时任务" |
| help | 帮助 | __direct__ | "你能做什么" |
| unknown | 无法解析 | __direct__ | 其他一切 |

## 输出格式（严格JSON，禁止多余文字）

{
  "intent": "意图名",
  "confidence": 0.0-1.0,
  "agent": "agent名或__direct__",
  "params": {
    "topics": ["关键词1", "关键词2"],
    "scope": "brief/full/technical/all",
    "time_range": "today/yesterday/this_week/recent",
    "question": "如果ask_question，这是问题内容",
    "message": "如果send_message，这是消息内容"
  },
  "reasoning": "一句话说明为什么判断为这个意图（中文）",
  "suggestion": "如果confidence<0.6，给用户的友好建议（中文）"
}

## 解析规则

1. 意图识别优先：先判断用户想干什么（查/做/问/发）
2. 参数抽取其次：topics(话题)/scope(范围)/time_range(时间)
3. 话题关键词：大模型、推荐系统、AI Coding、AI视频、RAG、Agent、MoE、大模型安全、AI音乐
4. scope范围：brief(简报)/full(全量)/technical(技术深度)/all(全部)
5. 置信度：0.95=非常确定，0.7-0.9=比较确定，0.5-0.7=模糊，<0.5=不确定

## 注意事项

- 只返回JSON，不要有任何额外文字
- intent必须是小写+下划线格式
- topics最多返回5个，不要超过5个
- time_range只能是 today/yesterday/this_week/recent/this_month 之一
- 如果完全无法判断，intent="unknown"，confidence=0.1，reasoning说明原因"""

USER_PROMPT_TEMPLATE = """请解析以下自然语言指令：

"{user_input}"

要求：
1. 严格只返回JSON，格式如下：
{
  "intent": "...",
  "confidence": 0.0-1.0,
  "agent": "...",
  "params": {...},
  "reasoning": "...",
  "suggestion": "..."
}
2. 不要返回任何非JSON内容
3. topics最多5个"""


# ─── 数据结构 ──────────────────────────────────────────────

@dataclass
class LLMParseResult:
    """LLM解析结果"""
    intent: str
    confidence: float
    agent: str
    params: dict
    reasoning: str
    suggestion: Optional[str] = None
    source: Literal["llm", "rule_fallback"] = "llm"
    latency_ms: float = 0.0

    def to_dict(self):
        return asdict(self)


# ─── LLM NL Resolver ───────────────────────────────────────

class LLMLightResolver:
    """
    LLM驱动的轻量NL解析器
    当规则引擎无法高置信度解析时，调用GLM-4进行深度语义理解
    """

    def __init__(self, api_key: Optional[str] = None, model: str = GLM_MODEL):
        self.api_key = api_key or os.getenv("GLM_API_KEY", "")
        self.model = model
        self._client: Optional[httpx.AsyncClient] = None
        self._enabled = bool(self.api_key)

    @property
    def enabled(self) -> bool:
        return self._enabled

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=LLM_TIMEOUT)
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def parse(self, text: str, rule_confidence: float = 0.0) -> Optional[LLMParseResult]:
        """
        解析自然语言指令

        Args:
            text: 用户输入
            rule_confidence: 规则引擎已有的置信度（用于判断是否需要调用LLM）

        Returns:
            LLMParseResult 或 None（LLM不可用或解析失败）
        """
        if not self._enabled:
            logger.debug("LLM解析器未启用（无API Key）")
            return None

        # 置信度充足，不需要LLM增强
        if rule_confidence >= CONFIDENCE_THRESHOLD:
            logger.debug(f"规则置信度 {rule_confidence:.2f} >= {CONFIDENCE_THRESHOLD}，跳过LLM")
            return None

        start = time.perf_counter()

        try:
            client = await self._get_client()

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": USER_PROMPT_TEMPLATE.format(user_input=text)},
                ],
                "temperature": 0.1,  # 低温度保证输出稳定
                "max_tokens": 600,
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            response = await client.post(GLM_API_URL, headers=headers, json=payload)
            response.raise_for_status()

            result_data = response.json()
            content = result_data["choices"][0]["message"]["content"].strip()

            # 提取JSON（处理可能的markdown代码块）
            json_str = self._extract_json(content)

            parsed = json.loads(json_str)

            # 验证并规范化
            result = self._normalize(parsed)
            result.source = "llm"
            result.latency_ms = (time.perf_counter() - start) * 1000

            logger.info(
                f"LLM解析成功: text='{text[:30]}...' → intent={result.intent} "
                f"conf={result.confidence:.2f} latency={result.latency_ms:.0f}ms"
            )

            return result

        except httpx.HTTPStatusError as e:
            logger.warning(f"LLM API HTTP错误: {e.response.status_code}")
            return None
        except json.JSONDecodeError as e:
            logger.warning(f"LLM返回JSON解析失败: {e}, content={content[:200]}")
            return None
        except Exception as e:
            logger.warning(f"LLM解析异常: {e}")
            return None

    def _extract_json(self, content: str) -> str:
        """从响应内容中提取JSON字符串"""
        content = content.strip()
        # 处理 ```json ... ``` 格式
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        # 去除可能的首尾空白
        content = content.strip()
        return content

    def _normalize(self, parsed: dict) -> LLMParseResult:
        """规范化LLM返回结果"""
        intent = parsed.get("intent", "unknown")
        confidence = float(parsed.get("confidence", 0.0))
        agent = parsed.get("agent", "__direct__")
        params = parsed.get("params", {})
        reasoning = parsed.get("reasoning", "")
        suggestion = parsed.get("suggestion")

        # 过滤空topics
        if "topics" in params and not params["topics"]:
            params.pop("topics")

        # 限制topics数量
        if "topics" in params and len(params["topics"]) > 5:
            params["topics"] = params["topics"][:5]

        # 规范化agent
        if agent in AGENT_MAPPING:
            agent = AGENT_MAPPING[agent]

        return LLMParseResult(
            intent=intent,
            confidence=min(max(confidence, 0.0), 1.0),
            agent=agent,
            params=params,
            reasoning=reasoning,
            suggestion=suggestion,
        )


# ─── 全局单例 ──────────────────────────────────────────────

_llm_resolver: Optional[LLMLightResolver] = None


def get_llm_resolver() -> LLMLightResolver:
    global _llm_resolver
    if _llm_resolver is None:
        _llm_resolver = LLMLightResolver()
    return _llm_resolver


def init_llm_resolver(api_key: Optional[str] = None) -> LLMLightResolver:
    global _llm_resolver
    _llm_resolver = LLMLightResolver(api_key=api_key)
    return _llm_resolver
