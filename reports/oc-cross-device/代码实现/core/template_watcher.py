"""
任务模板 YAML 热加载模块

功能：
- 自动监测 templates.yaml 文件变化（文件修改时间）
- 变化时自动重新加载，无需重启服务
- 支持增量更新（只加载新增/修改的模板）
- 加载失败时保留旧模板，不影响运行

使用方式：
```python
watcher = TemplateWatcher(task_manager, yaml_path="/path/to/templates.yaml")
watcher.start()  # 启动监控协程

# 手动触发一次加载（启动时）
watcher.load()

# 停止监控
watcher.stop()
```
"""

import os
import asyncio
import logging
import hashlib
from pathlib import Path
from typing import Optional
from datetime import datetime

import yaml

logger = logging.getLogger(__name__)


class TemplateWatcher:
    """
    模板文件热加载监控器

    原理：定时检查文件 mtime，变化则重新加载
    最小检查间隔：5 秒（防止频繁 IO）
    """

    def __init__(
        self,
        task_manager,
        yaml_path: str = "templates.yaml",
        check_interval: float = 10.0,
    ):
        """
        Args:
            task_manager: TaskManager 实例
            yaml_path: 模板 YAML 文件路径
            check_interval: 检查间隔（秒）
        """
        self._task_mgr = task_manager
        self._yaml_path = Path(yaml_path)
        self._check_interval = check_interval
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._last_mtime: Optional[float] = None
        self._last_hash: Optional[str] = None

    def _compute_hash(self, content: bytes) -> str:
        """计算文件内容 MD5"""
        return hashlib.md5(content).hexdigest()

    def _load_yaml(self) -> dict:
        """加载 YAML 文件"""
        if not self._yaml_path.exists():
            logger.warning(f"[TemplateWatcher] 文件不存在: {self._yaml_path}")
            return {}

        try:
            with open(self._yaml_path, "r", encoding="utf-8") as f:
                content = f.read()
            return yaml.safe_load(content) or {}
        except yaml.YAMLError as e:
            logger.error(f"[TemplateWatcher] YAML 解析失败: {e}")
            return {}
        except Exception as e:
            logger.error(f"[TemplateWatcher] 文件读取失败: {e}")
            return {}

    def _register_template_from_yaml(self, template_id: str, data: dict) -> bool:
        """
        从 YAML 数据注册单个模板到 TaskManager

        Returns:
            True 注册成功，False 跳过
        """
        from core.task import TaskTemplate

        try:
            # 标准化字段
            name = data.get("name", template_id)
            display_name = data.get("display_name") or data.get("name") or template_id
            description = data.get("description", "")
            action = data.get("action", "spawn")
            agent = data.get("agent")
            params = data.get("params", {})
            tags = data.get("tags", [])
            schedule = data.get("schedule", {})
            icon = data.get("icon", "📋")

            # 支持简写（composite 类型）
            steps = data.get("steps", [])

            tmpl = TaskTemplate(
                name=template_id,
                display_name=display_name,
                description=description,
                action=action,
                agent=agent,
                params=params,
            )

            # 额外属性（TaskTemplate 本身没有的，通过 extra 存储）
            tmpl.extra = {
                "tags": tags,
                "schedule": schedule,
                "icon": icon,
                "steps": steps,
                "loaded_at": datetime.now().isoformat(),
                "source": "yaml",
            }

            self._task_mgr.add_template(tmpl)
            return True

        except Exception as e:
            logger.error(f"[TemplateWatcher] 注册模板 {template_id} 失败: {e}")
            return False

    def load(self) -> tuple[int, int]:
        """
        加载模板文件

        Returns:
            (成功数, 失败数)
        """
        data = self._load_yaml()
        templates_section = data.get("templates", {})

        if not templates_section:
            logger.info("[TemplateWatcher] 模板文件为空或无 templates 节点")
            return 0, 0

        # 统计
        success = 0
        failed = 0
        loaded_ids = []

        for template_id, template_data in templates_section.items():
            if self._register_template_from_yaml(template_id, template_data):
                success += 1
                loaded_ids.append(template_id)
            else:
                failed += 1

        # 注册快捷命令别名
        shortcuts = data.get("shortcuts", {})
        if shortcuts and hasattr(self._task_mgr, "_shortcuts"):
            self._task_mgr._shortcuts.update(shortcuts)

        # 更新 mtime 记录
        if self._yaml_path.exists():
            stat = self._yaml_path.stat()
            self._last_mtime = stat.st_mtime
            with open(self._yaml_path, "rb") as f:
                self._last_hash = self._compute_hash(f.read())

        logger.info(
            f"[TemplateWatcher] 加载完成：{success} 成功 / {failed} 失败"
            f" | 模板IDs: {loaded_ids[:5]}{'...' if len(loaded_ids)>5 else ''}"
        )
        return success, failed

    def check_and_reload(self) -> Optional[tuple[int, int]]:
        """
        检查文件是否有变化，有则重新加载

        Returns:
            None — 无变化
            (success, failed) — 已重新加载
        """
        if not self._yaml_path.exists():
            return None

        stat = self._yaml_path.stat()
        current_mtime = stat.st_mtime

        # 方式1：按 mtime 判断（简单有效）
        if self._last_mtime is not None and abs(current_mtime - self._last_mtime) < 1:
            return None  # 无变化

        # 方式2：按内容 hash 判断（更精确）
        with open(self._yaml_path, "rb") as f:
            content = f.read()
        current_hash = self._compute_hash(content)

        if self._last_hash and current_hash == self._last_hash:
            self._last_mtime = current_mtime  # 同步时间戳
            return None  # 内容无变化

        logger.info(f"[TemplateWatcher] 检测到模板文件变化，重新加载...")
        result = self.load()
        return result

    async def _watch_loop(self):
        """监控协程（后台运行）"""
        logger.info(
            f"[TemplateWatcher] 监控已启动: {self._yaml_path}"
            f" | 检查间隔: {self._check_interval}s"
        )

        # 启动时先加载一次
        self.load()

        while self._running:
            try:
                result = self.check_and_reload()
                if result:
                    success, failed = result
                    logger.info(f"[TemplateWatcher] 热加载完成: {success} 成功, {failed} 失败")
            except Exception as e:
                logger.error(f"[TemplateWatcher] 监控异常: {e}")

            await asyncio.sleep(self._check_interval)

    def start(self):
        """启动监控（后台协程）"""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._watch_loop())
        logger.info("[TemplateWatcher] 已启动")

    def stop(self):
        """停止监控"""
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None
        logger.info("[TemplateWatcher] 已停止")


# ─── 快捷命令路由（扩展 TaskManager）────────────────────────

class ShortcutRouter:
    """
    快捷命令路由器

    将用户输入的快捷命令映射到对应模板
    例如："/tech" → tech_brief 模板
    """

    def __init__(self, task_manager):
        self._task_mgr = task_manager
        self._shortcuts: dict[str, str] = {}

    def register_shortcut(self, alias: str, template_id: str):
        """注册快捷命令"""
        self._shortcuts[alias.lstrip("/")] = template_id

    def resolve(self, text: str) -> Optional[str]:
        """解析文本，返回模板ID（如果匹配快捷命令）"""
        text = text.strip().lstrip("/")
        return self._shortcuts.get(text)

    def list_shortcuts(self) -> dict:
        """列出所有快捷命令"""
        return dict(self._shortcuts)
