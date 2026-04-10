#!/usr/bin/env python3
"""
Plugin Manager — clawctl 插件系统 v2.9.0
支持动态注册自定义意图、处理函数、API schema
"""

from __future__ import annotations
import os
import json
import logging
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional, Callable, Any

logger = logging.getLogger("clawctl.plugin")

# ── 数据模型 ──────────────────────────────────────────────────────────────────

@dataclass
class IntentConfig:
    intent: str
    keywords: list[str]
    handler: str = ""          # handler 函数名（plugin内部）
    description: str = ""
    params_schema: dict = field(default_factory=dict)
    examples: list[str] = field(default_factory=list)


@dataclass
class Plugin:
    id: str
    name: str
    description: str
    version: str = "1.0.0"
    author: str = ""
    intents: list[dict] = field(default_factory=list)
    handlers: dict = field(default_factory=dict)  # intent → callable
    enabled: bool = True
    config: dict = field(default_factory=dict)
    _path: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "intents": self.intents,
            "enabled": self.enabled,
        }


# ── Plugin Manager ─────────────────────────────────────────────────────────────

class PluginManager:
    """
    插件管理器：
    - 扫描并加载 plugins/ 目录下的插件
    - 维护意图注册表，供 NL Interpreter 使用
    - 生命周期管理（enable/disable/卸载）
    """

    def __init__(self, plugin_dir: Optional[str] = None):
        if plugin_dir is None:
            plugin_dir = str(Path(__file__).parent.parent / "plugins")
        self.plugin_dir = Path(plugin_dir)
        self.plugin_dir.mkdir(parents=True, exist_ok=True)

        self.plugins: dict[str, Plugin] = {}
        self._intent_map: dict[str, Plugin] = {}  # intent_name → plugin
        self._keyword_map: dict[str, str] = {}      # keyword → intent
        self._handlers: dict[str, Callable] = {}   # "plugin_id:intent" → handler

        self._builtin_plugins()
        self._scan_and_load()

    # ── 内置插件 ─────────────────────────────────────────────────────────────

    def _builtin_plugins(self):
        """内置插件：无需安装，直接注册"""
        builtins = [
            Plugin(
                id="builtin_commands",
                name="快捷命令",
                description="常用快捷命令：status/list/help/ping",
                intents=[
                    {"intent": "system_status", "keywords": ["状态", "系统状态", "运行状态", "还好吗"], "handler": "handle_status"},
                    {"intent": "task_list", "keywords": ["任务列表", "最近任务", "任务记录"], "handler": "handle_list"},
                    {"intent": "help_me", "keywords": ["帮助", "help", "怎么用", "使用说明"], "handler": "handle_help"},
                    {"intent": "ping_pong", "keywords": ["ping", "在吗", "活着"], "handler": "handle_ping"},
                ],
                handlers={
                    "builtin_commands:system_status": self._h_status,
                    "builtin_commands:task_list": self._h_list,
                    "builtin_commands:help_me": self._h_help,
                    "builtin_commands:ping_pong": self._h_ping,
                },
            ),
        ]
        for p in builtins:
            self._register_plugin(p)

    # ── 内置 handler 实现 ─────────────────────────────────────────────────────

    def _h_status(self, text: str, params: dict, ctx: dict) -> dict:
        from .client import OpenClawClient
        client = ctx.get("client")
        if client:
            try:
                status = client.get_status()
                return {"success": True, "message": f"✅ OpenClaw 运行正常\n会话数: {status.get('session_count', '?')}"}
            except Exception as e:
                return {"success": False, "message": f"⚠️ 连接异常: {e}"}
        return {"success": True, "message": "✅ clawctl 运行正常"}

    def _h_list(self, text: str, params: dict, ctx: dict) -> dict:
        db = ctx.get("db")
        if db:
            records = db.get_recent(limit=5)
            lines = ["📋 最近任务："]
            for r in records:
                lines.append(f"  [{r.get('status','?')}] {r.get('name','?')} — {r.get('created', '?')}")
            return {"success": True, "message": "\n".join(lines) or "暂无任务记录"}
        return {"success": True, "message": "📋 暂无任务记录"}

    def _h_help(self, text: str, params: dict, ctx: dict) -> dict:
        msg = """🤖 **clawctl 可用指令**

**快捷命令**
• 状态/系统状态 — 查看 OpenClaw 运行状态
• 任务列表 — 查看最近任务记录
• 帮助 — 显示本说明

**自然语言**
• "帮我查AI新闻" → 执行资讯抓取
• "生成今日简报" → 执行快速报告
• "分析RAG技术趋势" → 执行技术分析

**快捷触发**
• /api/v1/trigger/quick-report
• /api/v1/trigger/tech-analyst

**Siri/快捷指令**
• 对 Siri 说「AI简报」触发 OpenClaw
"""
        return {"success": True, "message": msg}

    def _h_ping(self, text: str, params: dict, ctx: dict) -> dict:
        return {"success": True, "message": "🏓 pong! clawctl 在线~"}

    # ── 注册/注销 ─────────────────────────────────────────────────────────────

    def register(self, plugin: Plugin):
        """注册插件"""
        self._register_plugin(plugin)
        logger.info(f"✅ 插件注册: {plugin.name} ({plugin.id}), 意图数: {len(plugin.intents)}")

    def _register_plugin(self, plugin: Plugin):
        self.plugins[plugin.id] = plugin
        for intent_cfg in plugin.intents:
            intent_name = intent_cfg["intent"]
            self._intent_map[intent_name] = plugin
            for kw in intent_cfg.get("keywords", []):
                self._keyword_map[kw] = intent_name
            handler_key = f"{plugin.id}:{intent_name}"
            if handler_key in plugin.handlers:
                self._handlers[handler_key] = plugin.handlers[handler_key]

    def unregister(self, plugin_id: str) -> bool:
        """卸载插件"""
        plugin = self.plugins.pop(plugin_id, None)
        if not plugin:
            return False
        # 清理意图映射
        for intent_cfg in plugin.intents:
            self._intent_map.pop(intent_cfg["intent"], None)
        # 清理 handler
        for intent_cfg in plugin.intents:
            self._handlers.pop(f"{plugin_id}:{intent_cfg['intent']}", None)
        logger.info(f"🗑 插件卸载: {plugin.name} ({plugin_id})")
        return True

    def enable(self, plugin_id: str):
        if plugin_id in self.plugins:
            self.plugins[plugin_id].enabled = True
            logger.info(f"✅ 插件启用: {plugin_id}")

    def disable(self, plugin_id: str):
        if plugin_id in self.plugins:
            self.plugins[plugin_id].enabled = False
            logger.info(f"⏸ 插件禁用: {plugin_id}")

    # ── 意图查询 ─────────────────────────────────────────────────────────────

    def resolve_intent(self, intent_name: str) -> Optional[Plugin]:
        """通过意图名查找插件"""
        plugin = self._intent_map.get(intent_name)
        if plugin and plugin.enabled:
            return plugin
        return None

    def resolve_keyword(self, keyword: str) -> Optional[str]:
        """通过关键词查找意图"""
        return self._keyword_map.get(keyword)

    def get_handler(self, plugin_id: str, intent: str) -> Optional[Callable]:
        """获取插件处理函数"""
        return self._handlers.get(f"{plugin_id}:{intent}")

    def get_all_intents(self) -> list[dict]:
        """获取所有已注册意图"""
        result = []
        for plugin in self.plugins.values():
            if not plugin.enabled:
                continue
            for intent_cfg in plugin.intents:
                result.append({
                    "plugin_id": plugin.id,
                    "plugin_name": plugin.name,
                    **intent_cfg,
                })
        return result

    # ── 动态加载 ─────────────────────────────────────────────────────────────

    def _scan_and_load(self):
        """扫描 plugins/ 目录，加载 .json/.py 插件"""
        if not self.plugin_dir.exists():
            return

        for entry in self.plugin_dir.iterdir():
            if entry.is_dir():
                manifest = entry / "manifest.json"
                if manifest.exists():
                    self._load_json_plugin(entry, manifest)
            elif entry.suffix == ".json" and entry.stem not in ["__init__", "builtin"]:
                self._load_standalone_json(entry)

    def _load_json_plugin(self, plugin_dir: Path, manifest_path: Path):
        try:
            manifest = json.loads(manifest_path.read_text())
            plugin = Plugin(
                id=manifest.get("id", plugin_dir.name),
                name=manifest.get("name", plugin_dir.name),
                description=manifest.get("description", ""),
                version=manifest.get("version", "1.0.0"),
                author=manifest.get("author", ""),
                intents=manifest.get("intents", []),
                config=manifest.get("config", {}),
                _path=str(plugin_dir),
            )
            self.register(plugin)
        except Exception as e:
            logger.warning(f"⚠️ 插件加载失败 {manifest_path}: {e}")

    def _load_standalone_json(self, path: Path):
        try:
            data = json.loads(path.read_text())
            plugin = Plugin(
                id=data.get("id", path.stem),
                name=data.get("name", path.stem),
                description=data.get("description", ""),
                intents=data.get("intents", []),
                enabled=data.get("enabled", True),
            )
            self.register(plugin)
        except Exception as e:
            logger.warning(f"⚠️ 插件加载失败 {path}: {e}")

    # ── 插件市场（静态） ──────────────────────────────────────────────────────

    @staticmethod
    def get_marketplace() -> list[dict]:
        """返回可用插件市场列表（无需联网）"""
        return [
            {
                "id": "job-hunter",
                "name": "求职助手",
                "description": "自动抓取 Boss 直聘/猎聘岗位，一键生成简历匹配报告",
                "author": "clawctl community",
                "intents": [
                    {"intent": "job_search", "keywords": ["找工作", "职位", "薪资", "岗位"], "description": "搜索职位"},
                    {"intent": "resume_match", "keywords": ["匹配简历", "简历分析"], "description": "简历匹配"},
                ],
            },
            {
                "id": "stock-watcher",
                "name": "股票盯盘",
                "description": "监控自选股异动，微信/钉钉推送告警",
                "author": "clawctl community",
                "intents": [
                    {"intent": "stock_alert", "keywords": ["股票", "涨跌", "盯盘", "持仓"], "description": "设置股票告警"},
                ],
            },
            {
                "id": "meeting-notes",
                "name": "会议纪要",
                "description": "接入飞书/钉钉会议，AI 自动生成结构化会议纪要",
                "author": "clawctl community",
                "intents": [
                    {"intent": "meeting_summary", "keywords": ["会议纪要", "会议总结"], "description": "生成会议纪要"},
                ],
            },
            {
                "id": "dev-ops",
                "name": "运维助手",
                "description": "服务器健康检查、日志分析、异常告警自动化",
                "author": "clawctl community",
                "intents": [
                    {"intent": "health_check", "keywords": ["健康检查", "服务器状态"], "description": "执行健康检查"},
                    {"intent": "log_analyze", "keywords": ["分析日志", "错误日志"], "description": "分析日志"},
                ],
            },
        ]


# ── 全局单例 ──────────────────────────────────────────────────────────────────

_manager: Optional[PluginManager] = None

def get_plugin_manager() -> PluginManager:
    global _manager
    if _manager is None:
        _manager = PluginManager()
    return _manager
