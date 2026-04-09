#!/usr/bin/env python3
"""
Shortcuts Integration — iOS/Android 快捷指令深度集成

提供：
1. 快捷指令模板库（可直接导入 iOS 快捷指令 App）
2. clawctl:// URL Scheme 完整实现
3. GET API 端点（适配 iOS 快捷指令"URL"动作）
4. Shortcut Import Link 生成器
"""

import re
import json
import logging
from urllib.parse import quote, urlencode
from typing import Optional, List
from dataclasses import dataclass, field

logger = logging.getLogger("clawctl.shortcuts")


# ── 快捷指令模板 ────────────────────────────────────────────────────────────

@dataclass
class ShortcutTemplate:
    """快捷指令模板"""
    id: str
    name: str
    description: str
    icon: str = "🔧"
    color: str = "#007AFF"
    trigger_url: str = ""
    nl_text: str = ""
    params: dict = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    def to_ios_shortcut(self, base_url: str, api_key: str) -> dict:
        """生成 iOS 快捷指令可导入的 URL Scheme"""
        params = {**self.params, "api_key": api_key}
        if self.nl_text:
            params["q"] = self.nl_text
        encoded_params = urlencode(params, safe="")
        url = f"{base_url}/api/v1/nl/cmd?{encoded_params}"
        return {
            "name": self.name,
            "url": url,
            "description": self.description,
            "icon": self.icon,
            "color": self.color,
            "tags": self.tags,
        }


# ── 预设快捷指令模板库 ───────────────────────────────────────────────────────

def get_default_templates() -> List[ShortcutTemplate]:
    """获取默认快捷指令模板"""
    return [
        # ── 日常任务 ──────────────────────────────────────────────────
        ShortcutTemplate(
            id="quick_report",
            name="📋 生成今日简报",
            description="触发信息抓取助手，生成当日 AI 热点简报",
            icon="📋",
            color="#FF9500",
            nl_text="生成今日技术简报",
            tags=["日常", "报告", "信息抓取"],
        ),
        ShortcutTemplate(
            id="ai_news",
            name="🌐 AI 热点新闻",
            description="实时抓取全球 AI 领域当日热门资讯",
            icon="🌐",
            color="#007AFF",
            nl_text="查一下今天有啥AI新闻",
            tags=["新闻", "AI", "信息抓取"],
        ),
        ShortcutTemplate(
            id="tech_scan",
            name="🔬 技术前沿扫描",
            description="深度扫描推荐系统和大模型技术前沿动态",
            icon="🔬",
            color="#5856D6",
            nl_text="做一次技术前沿扫描，重点关注大模型进展",
            tags=["技术", "扫描", "大模型"],
        ),
        ShortcutTemplate(
            id="market_pulse",
            name="📊 市场动态洞察",
            description="分析 AI 商业应用、创业公司、融资动态",
            icon="📊",
            color="#34C759",
            nl_text="分析一下最近AI创业公司有什么值得关注的",
            tags=["市场", "商业", "创业"],
        ),
        ShortcutTemplate(
            id="full_scan",
            name="🚀 全面信息扫描",
            description="全量执行信息抓取 + 技术分析 + 市场洞察",
            icon="🚀",
            color="#FF3B30",
            nl_text="做一次全面信息扫描",
            tags=["全面", "扫描", "综合"],
        ),

        # ── 快速操作 ──────────────────────────────────────────────────
        ShortcutTemplate(
            id="status_check",
            name="💡 查看系统状态",
            description="查询 OpenClaw Gateway 实时状态和活跃 Agent",
            icon="💡",
            color="#AF52DE",
            nl_text="查看系统状态",
            params={"intent_only": "true"},
            tags=["状态", "查询"],
        ),
        ShortcutTemplate(
            id="task_list",
            name="📜 最近任务记录",
            description="查询最近 10 条任务执行历史",
            icon="📜",
            color="#5AC8FA",
            nl_text="查看最近的任务执行情况",
            params={"intent_only": "true"},
            tags=["任务", "历史", "查询"],
        ),
        ShortcutTemplate(
            id="pending_tasks",
            name="⏳ 待处理任务",
            description="查看当前排队中的任务",
            icon="⏳",
            color="#FF2D55",
            nl_text="有没有任务失败了，查一下待处理任务",
            params={"intent_only": "true"},
            tags=["任务", "排队"],
        ),

        # ── 个性化分析 ────────────────────────────────────────────────
        ShortcutTemplate(
            id="recsys_deep",
            name="🎯 推荐系统深度分析",
            description="专注推荐系统算法、大厂实践、招聘市场",
            icon="🎯",
            color="#FF9500",
            nl_text="最近推荐系统有什么新的技术进展，帮我深入分析",
            tags=["推荐系统", "算法", "技术"],
        ),
        ShortcutTemplate(
            id="llm_news",
            name="🧠 大模型最新进展",
            description="追踪 GPT/Gemini/Claude/国产大模型最新发布",
            icon="🧠",
            color="#007AFF",
            nl_text="大模型最近有什么新的进展",
            tags=["大模型", "LLM", "技术"],
        ),
        ShortcutTemplate(
            id="job_market",
            name="💼 推荐算法就业市场",
            description="分析推荐算法岗位需求、薪资趋势、技能要求",
            icon="💼",
            color="#34C759",
            nl_text="帮我分析一下推荐算法工程师目前的就业市场情况",
            tags=["招聘", "就业", "薪资"],
        ),
        ShortcutTemplate(
            id="paper_review",
            name="📚 本周论文速递",
            description="从 LlamaFactory 每日论文中筛选最值得关注的内容",
            icon="📚",
            color="#5856D6",
            nl_text="帮我看看这周有什么值得读的AI论文",
            tags=["论文", "学术", "arXiv"],
        ),
    ]


# ── URL Scheme 解析 ─────────────────────────────────────────────────────────

CLAWCTL_RE = re.compile(
    r"^clawctl://(?P<action>\w+)(?:\?(?P<query>.+))?$",
    re.IGNORECASE,
)


def parse_clawctl_url(url: str) -> Optional[dict]:
    """解析 clawctl:// URL，返回结构化参数"""
    m = CLAWCTL_RE.match(url.strip())
    if not m:
        return None

    from urllib.parse import parse_qs
    action = m.group("action")
    query = m.group("query") or ""
    params = {}
    for k, vals in parse_qs(query).items():
        params[k] = vals[0] if len(vals) == 1 else vals

    return {"action": action, "params": params}


def build_clawctl_url(action: str, **params) -> str:
    """构建 clawctl:// URL"""
    q = urlencode(params)
    return f"clawctl://{action}?{q}"


# ── iOS 快捷指令导入链接生成器 ───────────────────────────────────────────────

def generate_shortcut_import_link(template: ShortcutTemplate, base_url: str) -> str:
    """
    生成可直接打开"快捷指令"App 并添加指令的 URL
    iOS Shortcuts 支持 clawremote:// 或直接 URL 作为"打开 URL"动作
    """
    q = urlencode({"q": template.nl_text, "template": template.id}, safe="")
    return f"clawctl://run?{q}"


def generate_ios_url_scheme(base_url: str, api_key: str, template: ShortcutTemplate) -> str:
    """生成可直接在 iOS 快捷指令中使用的 URL（"URL"动作）"""
    params = urlencode({
        "q": template.nl_text,
        "api_key": api_key,
        "template": template.id,
    }, safe="")
    return f"{base_url}/api/v1/nl/cmd?{params}"


# ── Shortcut Intent Filter ───────────────────────────────────────────────────

INTENT_SHORTCUT_MAP = {
    "trigger_report": "quick_report",
    "trigger_fetch": "ai_news",
    "trigger_scan": "full_scan",
    "trigger_analysis": "tech_scan",
    "query_status": "status_check",
    "query_history": "task_list",
}


def match_shortcut_for_intent(intent: str) -> Optional[ShortcutTemplate]:
    """根据意图匹配最佳快捷指令模板"""
    tid = INTENT_SHORTCUT_MAP.get(intent)
    if not tid:
        return None
    for t in get_default_templates():
        if t.id == tid:
            return t
    return None


# ── 快捷指令库导出 ──────────────────────────────────────────────────────────

def export_shortcut_library(base_url: str, api_key: str) -> dict:
    """导出完整快捷指令库（供前端/App 使用）"""
    templates = get_default_templates()
    return {
        "version": "2.8.0",
        "updated_at": "2026-04-09",
        "total": len(templates),
        "templates": [t.to_ios_shortcut(base_url, api_key) for t in templates],
        "categories": {
            "日常任务": [t.id for t in templates if "日常" in t.tags],
            "快速操作": [t.id for t in templates if "快速" in t.tags or "查询" in t.tags],
            "个性化分析": [t.id for t in templates if any(x in t.tags for x in ["推荐系统", "大模型", "招聘", "论文"])],
        },
    }


def export_ios_shortcuts_json(base_url: str, api_key: str) -> str:
    """导出 iOS 快捷指令兼容的 JSON（可用于分享/导入）"""
    data = export_shortcut_library(base_url, api_key)
    return json.dumps(data, ensure_ascii=False, indent=2)


# ── CLI 支持 ────────────────────────────────────────────────────────────────

def print_shortcuts_help(base_url: str = "http://localhost:8081"):
    """打印快捷指令使用帮助"""
    print("\n📱 OpenClaw 快捷指令库 (v2.8.0)")
    print("=" * 60)
    print(f"\n🌐 API 地址: {base_url}\n")

    categories = {
        "📋 日常任务": [],
        "⚡ 快速操作": [],
        "🎯 个性化分析": [],
    }

    for t in get_default_templates():
        cat = "📋 日常任务" if "日常" in t.tags else \
              "⚡ 快速操作" if "快速" in t.tags or "查询" in t.tags else \
              "🎯 个性化分析"
        categories[cat].append(t)

    for cat, templates in categories.items():
        print(f"\n{cat}")
        print("-" * 50)
        for t in templates:
            url = generate_ios_url_scheme(base_url, "YOUR_API_KEY", t)
            print(f"\n  {t.icon} {t.name}")
            print(f"     {t.description}")
            print(f"     URL: {url[:80]}...")


if __name__ == "__main__":
    import sys
    base = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8081"
    print_shortcuts_help(base)
    print("\n\n📦 导出 JSON:")
    print(export_ios_shortcuts_json(base, "YOUR_API_KEY")[:500] + "...")
