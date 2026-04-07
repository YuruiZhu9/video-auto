#!/usr/bin/env python3
"""
clawctl - 定时任务调度器
基于 APScheduler 实现 Cron 定时触发
"""

import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Callable, Dict, Any

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)


@dataclass
class ScheduleJob:
    """定时任务定义"""
    id: str
    name: str
    template_id: str
    cron_expr: str  # e.g. "0 9 * * *" (min hour day mon dow)
    timezone: str = "Asia/Shanghai"
    enabled: bool = True
    notify_on_complete: bool = True
    notify_channel: str = "dingtalk"
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0
    params: Dict[str, Any] = field(default_factory=dict)
    _job_id: str = ""  # APScheduler internal ID

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "template_id": self.template_id,
            "cron": self.cron_expr,
            "timezone": self.timezone,
            "enabled": self.enabled,
            "notify_on_complete": self.notify_on_complete,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_run": self.next_run.isoformat() if self.next_run else None,
            "run_count": self.run_count,
            "params": self.params,
        }


class Scheduler:
    """
    定时任务调度器
    
    用法:
        scheduler = Scheduler(task_manager, notify_mgr)
        scheduler.add_job("daily_report", "0 9 * * *", "quick-report")
        scheduler.start()
    """

    def __init__(self, task_manager, notify_mgr=None, client=None):
        self._task_manager = task_manager
        self._notify_mgr = notify_mgr
        self._client = client
        self._sched: BackgroundScheduler = BackgroundScheduler(timezone="Asia/Shanghai")
        self._jobs: Dict[str, ScheduleJob] = {}
        self._lock = threading.RLock()
        self._started = False

    def _build_trigger(self, cron_expr: str, timezone: str) -> CronTrigger:
        """解析 Cron 表达式"""
        parts = cron_expr.split()
        if len(parts) == 5:
            minute, hour, day, month, dow = parts
        elif len(parts) == 6:
            # 扩展格式：秒 分 时 日 月 周
            sec, minute, hour, day, month, dow = parts
            parts = [minute, hour, day, month, dow]
        else:
            minute, hour, day, month, dow = "0", "9", "*", "*", "*"
        return CronTrigger(
            minute=parts[0], hour=parts[1], day=parts[2],
            month=parts[3], day_of_week=parts[4], timezone=timezone,
        )

    def _execute_job(self, job: ScheduleJob):
        """执行定时任务"""
        from ..core.task import Task
        logger.info(f"[Scheduler] 触发定时任务: {job.name} ({job.template_id})")
        try:
            # 从模板获取任务参数
            templates = self._task_manager.templates or {}
            template_cfg = templates.get(job.template_id, {})
            task_str = template_cfg.get("params", {}).get(
                "task",
                f"执行定时任务: {job.name}"
            )
            runtime = template_cfg.get("params", {}).get("runtime", "subagent")

            task = Task(
                name=f"scheduled:{job.name}",
                action="spawn",
                params={"task": task_str, "runtime": runtime},
                notify=job.notify_on_complete,
                notify_channel=job.notify_channel,
            )
            self._task_manager.submit(task)
            self._task_manager.execute_async(task)

            job.last_run = datetime.now()
            job.run_count += 1
            logger.info(f"[Scheduler] 任务已提交: {task.id}")
        except Exception as e:
            logger.exception(f"[Scheduler] 任务执行失败: {job.name}: {e}")

    def add_job(
        self,
        name: str,
        cron_expr: str,
        template_id: str,
        timezone: str = "Asia/Shanghai",
        enabled: bool = True,
        notify_on_complete: bool = True,
        notify_channel: str = "dingtalk",
        params: Optional[dict] = None,
        job_id: Optional[str] = None,
    ) -> ScheduleJob:
        """添加定时任务"""
        jid = job_id or name
        with self._lock:
            if jid in self._jobs:
                raise ValueError(f"定时任务已存在: {jid}")
            job = ScheduleJob(
                id=jid,
                name=name,
                template_id=template_id,
                cron_expr=cron_expr,
                timezone=timezone,
                enabled=enabled,
                notify_on_complete=notify_on_complete,
                notify_channel=notify_channel,
                params=params or {},
            )
            trigger = self._build_trigger(cron_expr, timezone)
            ap_job = self._sched.add_job(
                self._execute_job,
                trigger=trigger,
                args=[job],
                id=jid,
                replace_existing=True,
            )
            job._job_id = jid
            job.next_run = ap_job.next_run_time
            self._jobs[jid] = job
            logger.info(f"[Scheduler] 添加定时任务: {name} | cron={cron_expr} | next={job.next_run}")
            return job

    def remove_job(self, job_id: str) -> bool:
        """移除定时任务"""
        with self._lock:
            if job_id not in self._jobs:
                return False
            try:
                self._sched.remove_job(job_id)
                del self._jobs[job_id]
                logger.info(f"[Scheduler] 移除定时任务: {job_id}")
                return True
            except Exception as e:
                logger.error(f"[Scheduler] 移除失败: {job_id}: {e}")
                return False

    def pause_job(self, job_id: str) -> bool:
        """暂停定时任务"""
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return False
            try:
                self._sched.pause_job(job_id)
                job.enabled = False
                return True
            except Exception as e:
                logger.error(f"[Scheduler] 暂停失败: {e}")
                return False

    def resume_job(self, job_id: str) -> bool:
        """恢复定时任务"""
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return False
            try:
                self._sched.resume_job(job_id)
                job.enabled = True
                return True
            except Exception as e:
                logger.error(f"[Scheduler] 恢复失败: {e}")
                return False

    def list_jobs(self) -> list:
        """列出所有定时任务"""
        with self._lock:
            return [j.to_dict() for j in self._jobs.values()]

    def get_job(self, job_id: str) -> Optional[ScheduleJob]:
        return self._jobs.get(job_id)

    def trigger_now(self, job_id: str) -> Optional[str]:
        """手动立即触发定时任务"""
        with self._lock:
            job = self._jobs.get(job_id)
        if not job:
            return None
        self._execute_job(job)
        return job_id

    def start(self):
        """启动调度器"""
        if self._started:
            return
        self._sched.start()
        self._started = True
        logger.info("[Scheduler] 调度器已启动")

    def shutdown(self, wait: bool = True):
        """关闭调度器"""
        if not self._started:
            return
        self._sched.shutdown(wait=wait)
        self._started = False
        logger.info("[Scheduler] 调度器已关闭")

    def load_from_yaml(self, yaml_path: str):
        """从 YAML 文件加载定时任务"""
        import yaml
        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            schedules = data.get("schedules", [])
            for s in schedules:
                self.add_job(
                    name=s["name"],
                    cron_expr=s["cron"],
                    template_id=s["template_id"],
                    timezone=s.get("timezone", "Asia/Shanghai"),
                    enabled=s.get("enabled", True),
                    notify_on_complete=s.get("notify", {}).get("on_complete", True),
                    notify_channel=s.get("notify", {}).get("channel", "dingtalk"),
                    params=s.get("params", {}),
                    job_id=s.get("id"),
                )
            logger.info(f"[Scheduler] 从 {yaml_path} 加载了 {len(schedules)} 个定时任务")
        except Exception as e:
            logger.error(f"[Scheduler] YAML 加载失败: {e}")
