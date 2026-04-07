#!/usr/bin/env python3
"""
clawctl - 任务模板加载器
支持 YAML 文件模板 + 内置默认模板，支持热加载
"""

import os
import logging
import threading
import hashlib
import time
from typing import Dict, Optional, Any

import yaml

logger = logging.getLogger(__name__)

# ── 内置默认模板 ──────────────────────────────────────────────────────────────

DEFAULT_TEMPLATES: Dict[str, dict] = {
    "quick-report": {
        "name": "快速报告",
        "description": "生成今日 AI 资讯简报",
        "action": "spawn",
        "params": {
            "task": "生成今日 AI 资讯简报，重点关注大模型和推荐系统进展，输出结构化 Markdown 报告",
            "runtime": "subagent",
            "timeout": 300,
        },
        "notify": {"on_start": True, "on_complete": True, "on_failed": True},
    },
    "tech-analyst": {
        "name": "技术前沿分析",
        "description": "追踪推荐系统+大模型技术前沿",
        "action": "spawn",
        "params": {
            "task": "执行技术前沿分析：\n1. 抓取 arXiv cs.IR/cs.LG 最新论文摘要\n2. 分析推荐系统和大模型最新进展\n3. 评估对转行算法工程师的学习价值\n4. 输出分析报告",
            "runtime": "subagent",
            "timeout": 600,
        },
        "notify": {"on_start": True, "on_complete": True, "on_failed": True},
    },
    "market-insight": {
        "name": "商业洞察",
        "description": "分析 AI 商业应用机会",
        "action": "spawn",
        "params": {
            "task": "分析 AI 商业应用动态：\n1. 扫描 Product Hunt / 36氪 / 虎嗅 最新 AI 产品\n2. 分析企业 AI 落地案例\n3. 发现新的商业机会\n4. 输出商业机会报告",
            "runtime": "subagent",
            "timeout": 600,
        },
        "notify": {"on_start": True, "on_complete": True, "on_failed": True},
    },
    "full-scan": {
        "name": "全量扫描",
        "description": "执行全量信息抓取",
        "action": "spawn",
        "params": {
            "task": "执行全量信息抓取，汇总：\n1. 全球 AI 领域最新动态\n2. 国内外头部大模型厂商动态\n3. 推荐系统和大模型技术进展\n4. 生成综合分析报告",
            "runtime": "subagent",
            "timeout": 900,
        },
        "notify": {"on_start": True, "on_complete": True, "on_failed": True},
    },
}


class TemplateLoader:
    """
    任务模板管理器
    
    功能：
    - 从 YAML 文件加载模板（支持热加载）
    - 合并内置默认模板
    - 模板搜索与过滤
    - 模板参数覆盖
    """

    def __init__(
        self,
        yaml_path: Optional[str] = None,
        hot_reload: bool = True,
        reload_interval: int = 15,
    ):
        self._yaml_path = yaml_path
        self._hot_reload = hot_reload
        self._reload_interval = reload_interval
        self._templates: Dict[str, dict] = {}
        self._file_hash: str = ""
        self._lock = threading.RLock()
        self._watcher_thread: Optional[threading.Thread] = None
        self._watching = False
        self._load()

    def _load(self):
        """加载所有模板"""
        with self._lock:
            # 从 YAML 加载
            if self._yaml_path and os.path.exists(self._yaml_path):
                try:
                    with open(self._yaml_path, "r", encoding="utf-8") as f:
                        raw = yaml.safe_load(f) or {}
                    yaml_templates = raw.get("templates", {})
                    self._templates.update(yaml_templates)
                    self._file_hash = self._get_file_hash()
                    logger.info(f"[Templates] 从 {self._yaml_path} 加载了 {len(yaml_templates)} 个模板")
                except Exception as e:
                    logger.error(f"[Templates] YAML 加载失败: {e}")

            # 合并内置模板（不覆盖用户定义）
            for k, v in DEFAULT_TEMPLATES.items():
                if k not in self._templates:
                    self._templates[k] = v

    def _get_file_hash(self) -> str:
        if not self._yaml_path or not os.path.exists(self._yaml_path):
            return ""
        with open(self._yaml_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    def _check_reload(self) -> bool:
        """检查文件是否变化"""
        if not self._yaml_path or not os.path.exists(self._yaml_path):
            return False
        current_hash = self._get_file_hash()
        if current_hash != self._file_hash:
            self._file_hash = current_hash
            return True
        return False

    def _watch_loop(self):
        """文件监控循环"""
        while self._watching:
            time.sleep(self._reload_interval)
            if self._check_reload():
                logger.info("[Templates] 检测到模板文件变化，开始热加载...")
                # 清除并重新加载
                with self._lock:
                    self._templates.clear()
                    self._templates.update(DEFAULT_TEMPLATES)
                    if self._yaml_path and os.path.exists(self._yaml_path):
                        with open(self._yaml_path, "r", encoding="utf-8") as f:
                            raw = yaml.safe_load(f) or {}
                        self._templates.update(raw.get("templates", {}))
                logger.info(f"[Templates] 热加载完成，当前共 {len(self._templates)} 个模板")

    def start_watcher(self):
        """启动热加载监控线程"""
        if not self._hot_reload or not self._yaml_path:
            return
        self._watching = True
        self._watcher_thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._watcher_thread.start()
        logger.info(f"[Templates] 热加载监控已启动 (间隔 {self._reload_interval}s)")

    def stop_watcher(self):
        """停止热加载监控"""
        self._watching = False

    def reload(self):
        """手动重新加载"""
        with self._lock:
            self._templates.clear()
            self._load()
        logger.info("[Templates] 手动重载完成")

    def list(self, pattern: Optional[str] = None) -> Dict[str, dict]:
        """列出模板"""
        if not pattern:
            return dict(self._templates)
        return {k: v for k, v in self._templates.items() if pattern in k or pattern in v.get("name", "")}

    def get(self, name: str) -> Optional[dict]:
        return self._templates.get(name)

    def add(self, name: str, template: dict):
        """动态添加模板"""
        with self._lock:
            self._templates[name] = template

    def remove(self, name: str) -> bool:
        """移除模板"""
        with self._lock:
            if name in self._templates:
                del self._templates[name]
                return True
            return False

    def render_task(self, name: str, params: Optional[dict] = None) -> Optional[dict]:
        """渲染模板为任务参数"""
        tpl = self._templates.get(name)
        if not tpl:
            return None
        params = params or {}
        result = dict(tpl)
        # 深度合并 params
        if "params" in tpl:
            result["params"] = {**tpl["params"], **params}
        return result
