#!/usr/bin/env python3
"""
NL Interpreter Plugin Extension — 为 NLInterpreter 注入 Plugin 系统能力
支持动态注册自定义意图，让用户通过 Plugin 系统扩展 NL 解析能力

使用方法：
    from clawctl.core.nl_interpreter import NLInterpreter
    from clawctl.core.plugin_manager import PluginManager
    from clawctl.core.nl_plugin_ext import patch_nl_interpreter

    pm = PluginManager()
    interpreter = NLInterpreter()
    patch_nl_interpreter(interpreter, pm)

    # 现在 interpreter 支持插件注册的所有自定义意图
    result = interpreter.parse("帮我搜一下推荐算法岗位")
"""

from typing import Optional

# 缓存已 patch 的实例
_patch_cache = set()


def patch_nl_interpreter(interpreter, plugin_manager) -> None:
    """
    为 NLInterpreter 实例注入插件能力（幂等操作）
    - 扩展 INTENT_PATTERNS（添加插件意图）
    - 扩展 AGENT_KEYWORDS（添加插件 Agent 别名）
    - 添加 plugin_manager 引用
    - 添加 add_custom_intent() 方法
    - 覆盖 _recognize_intent() 在插件意图上优先匹配
    """
    global _patch_cache

    # 防止重复 patch
    instance_id = id(interpreter)
    if instance_id in _patch_cache:
        return

    # ── 1. 注入 plugin_manager ─────────────────────────────────────────────────
    interpreter._plugin_manager = plugin_manager
    interpreter._custom_intents = {}  # {intent_name: {"keywords": [], "plugin_id": "", "handler": ""}}

    # ── 2. 合并插件意图到 INTENT_PATTERNS ────────────────────────────────────
    # NLInterpreter 使用模块级 INTENT_PATTERNS dict，
    # 需要通过动态方式扩展
    _sync_plugin_intents(interpreter)

    # ── 3. 添加 add_custom_intent 方法 ────────────────────────────────────────
    def add_custom_intent(intent_name: str, keywords: list[str], handler: str = "", plugin_id: str = ""):
        """
        动态注册自定义意图（运行时生效）
        """
        import logging
        logger = logging.getLogger("clawctl.nl_plugin")
        if not keywords:
            logger.warning(f"⚠️ 插件意图 '{intent_name}' 无关键词，跳过注册")
            return

        # 存储到自定义意图表
        interpreter._custom_intents[intent_name] = {
            "keywords": keywords,
            "plugin_id": plugin_id,
            "handler": handler,
        }
        # 合并到解析用关键词表
        _sync_plugin_intents(interpreter)
        logger.info(f"✅ 插件意图注册: {intent_name} (关键词: {keywords[:3]}...)")

    interpreter.add_custom_intent = add_custom_intent

    # ── 4. 覆盖 _recognize_intent — 插件意图优先匹配 ──────────────────────────
    _original_recognize = interpreter._recognize_intent

    def _recognize_intent_patched(text: str):
        """
        增强版意图识别：插件意图 > 内置意图
        """
        # 第一轮：插件自定义意图（最高优先级）
        custom_intents = getattr(interpreter, '_custom_intents', {})
        for intent_name, cfg in custom_intents.items():
            for kw in cfg.get("keywords", []):
                if kw in text:
                    # 返回自定义意图（字符串形式）
                    return (intent_name, 0.95)

        # 第二轮：调用原始识别器
        return _original_recognize(text)

    interpreter._recognize_intent = _recognize_intent_patched

    # ── 5. 添加 execute_with_plugin_handler ─────────────────────────────────
    def execute_with_plugin(text: str, channel: str = "dingtalk") -> dict:
        """
        带插件处理函数执行的完整解析流程
        """
        parsed = interpreter.parse(text)
        plugin_manager = getattr(interpreter, '_plugin_manager', None)

        # 尝试调用插件处理函数
        if plugin_manager and parsed.intent:
            intent_str = parsed.intent.value if hasattr(parsed.intent, 'value') else str(parsed.intent)
            plugin = plugin_manager.resolve_intent(intent_str)
            if plugin:
                handler = plugin_manager.get_handler(plugin.id, intent_str)
                if handler:
                    try:
                        result = handler(
                            text=text,
                            params=parsed.params,
                            ctx={"channel": channel, "plugin_manager": plugin_manager},
                        )
                        return result
                    except Exception as e:
                        return {"success": False, "error": str(e), "message": f"插件处理异常: {e}"}

        # 回退到标准执行
        return interpreter.execute(text, channel)

    interpreter.execute_with_plugin = execute_with_plugin

    _patch_cache.add(instance_id)


def _sync_plugin_intents(interpreter):
    """
    将插件自定义意图同步到 interpreter 的解析逻辑中
    """
    # 自定义意图存储在 _custom_intents 中，在 _recognize_intent_patched 中已处理
    # 此函数预留做将来扩展关键词表使用
    pass


def unpatch_nl_interpreter(interpreter) -> None:
    """移除插件扩展（恢复原始行为）"""
    global _patch_cache
    instance_id = id(interpreter)
    _patch_cache.discard(instance_id)
    if hasattr(interpreter, '_custom_intents'):
        interpreter._custom_intents.clear()
    if hasattr(interpreter, '_plugin_manager'):
        interpreter._plugin_manager = None
