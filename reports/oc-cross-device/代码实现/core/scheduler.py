"""
Scheduler - APScheduler 定时任务调度器
将 CronTrigger 真正接入调度循环，支持秒级 cron 表达式
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger as APSCronTrigger
    from apscheduler.triggers.date import DateTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    APSCHEDULER_AVAILABLE = True
except ImportError:
    APSCHEDULER_AVAILABLE = False
    logger.warning("APScheduler not installed. Run: pip install APScheduler")


class ScheduledJob:
    """调度任务对象"""

    def __init__(
        self,
        job_id: str,
        name: str,
        template_id: Optional[str] = None,
        cron_expr: Optional[str] = None,
        interval_seconds: Optional[int] = None,
        enabled: bool = True,
    ):
        self.job_id = job_id
        self.name = name
        self.template_id = template_id
        self.cron_expr = cron_expr
        self.interval_seconds = interval_seconds
        self.enabled = enabled
        self._aps_job = None  # APScheduler job reference

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "name": self.name,
            "template_id": self.template_id,
            "cron_expr": self.cron_expr,
            "interval_seconds": self.interval_seconds,
            "enabled": self.enabled,
            "last_run": getattr(self, "last_run", None),
            "next_run": getattr(self, "next_run", None),
        }


class CronScheduler:
    """
    定时任务调度器

    基于 APScheduler，支持：
    - Cron 表达式（秒 分 时 日 月 周）
    - 间隔触发
    - 暂停 / 恢复 / 删除任务
    - 与 TaskManager 联动执行
    """

    def __init__(self, task_manager=None, client=None, db=None):
        self.task_manager = task_manager
        self.client = client
        self.db = db
        self._jobs: Dict[str, ScheduledJob] = {}
        self._scheduler: Optional[Any] = None
        self._tick_callbacks: List[Callable] = []

        if APSCHEDULER_AVAILABLE:
            self._scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
            self._scheduler.start()
            logger.info("CronScheduler started (APScheduler)")
        else:
            logger.warning("CronScheduler running in dummy mode (no APScheduler)")

    def register_tick_callback(self, cb: Callable):
        """注册每次触发后的回调（用于通知等）"""
        self._tick_callbacks.append(cb)

    def _execute_job(self, job: ScheduledJob):
        """执行一个调度任务"""
        logger.info(f"[Scheduler] Running job {job.name} ({job.job_id})")
        job.last_run = datetime.now().isoformat()
        if self.db:
            self.db.save_scheduled_job(job.to_dict())

        try:
            if job.template_id and self.task_manager:
                task = self.task_manager.create_task_from_template(job.template_id)
                if task and self.client:
                    task.start()
                    if job.template_id == "status_check":
                        result = self.client.get_status()
                    else:
                        result = self.client.spawn_agent(
                            task=self.task_manager.get_template(job.template_id).name,
                            **task.params,
                        )
                    task.complete(result)
                    if self.db:
                        self.db.save_task(task.to_dict())
        except Exception as e:
            logger.exception(f"Job {job.job_id} failed: {e}")

        # 触发回调
        for cb in self._tick_callbacks:
            try:
                cb(job)
            except Exception:
                logger.exception("Tick callback error")

    # ─── Public API ──────────────────────────────────────────────

    def add_job(
        self,
        name: str,
        template_id: Optional[str] = None,
        cron_expr: Optional[str] = None,
        interval_seconds: Optional[int] = None,
        enabled: bool = True,
    ) -> ScheduledJob:
        """
        添加定时任务

        Args:
            name: 任务名称
            template_id: 对应模板 ID
            cron_expr: cron 表达式（秒 分 时 日 月 周），如 "0 9 * * *" 表示每天9点
            interval_seconds: 间隔秒数（与 cron_expr 二选一）
            enabled: 是否立即启用
        """
        job_id = str(uuid.uuid4())[:8]
        job = ScheduledJob(
            job_id=job_id,
            name=name,
            template_id=template_id,
            cron_expr=cron_expr,
            interval_seconds=interval_seconds,
            enabled=enabled,
        )

        self._jobs[job_id] = job

        if APSCHEDULER_AVAILABLE and self._scheduler:
            trigger = self._build_trigger(job)
            if trigger:
                self._scheduler.add_job(
                    func=lambda j=job: self._execute_job(j),
                    trigger=trigger,
                    id=job_id,
                    replace_existing=True,
                    misfire_grace_time=60,
                )
                j = self._scheduler.get_job(job_id)
                if j:
                    job.next_run = j.next_run_time.isoformat() if j.next_run_time else None

        if self.db:
            self.db.save_scheduled_job(job.to_dict())

        logger.info(f"ScheduledJob added: {name} ({job_id}) cron={cron_expr} interval={interval_seconds}s")
        return job

    def remove_job(self, job_id: str) -> bool:
        """删除定时任务"""
        if job_id not in self._jobs:
            return False
        if APSCHEDULER_AVAILABLE and self._scheduler:
            self._scheduler.remove_job(job_id)
        del self._jobs[job_id]
        if self.db:
            self.db.delete_scheduled_job(job_id)
        logger.info(f"ScheduledJob removed: {job_id}")
        return True

    def pause_job(self, job_id: str) -> bool:
        """暂停定时任务"""
        job = self._jobs.get(job_id)
        if not job:
            return False
        job.enabled = False
        if APSCHEDULER_AVAILABLE and self._scheduler:
            self._scheduler.pause_job(job_id)
        if self.db:
            self.db.save_scheduled_job(job.to_dict())
        logger.info(f"ScheduledJob paused: {job_id}")
        return True

    def resume_job(self, job_id: str) -> bool:
        """恢复定时任务"""
        job = self._jobs.get(job_id)
        if not job:
            return False
        job.enabled = True
        if APSCHEDULER_AVAILABLE and self._scheduler:
            self._scheduler.resume_job(job_id)
        if self.db:
            self.db.save_scheduled_job(job.to_dict())
        logger.info(f"ScheduledJob resumed: {job_id}")
        return True

    def list_jobs(self) -> List[Dict[str, Any]]:
        """列出所有任务"""
        result = []
        for job in self._jobs.values():
            jdict = job.to_dict()
            # 实时更新 next_run
            if APSCHEDULER_AVAILABLE and self._scheduler:
                aps_job = self._scheduler.get_job(job.job_id)
                if aps_job and aps_job.next_run_time:
                    jdict["next_run"] = aps_job.next_run_time.isoformat()
            result.append(jdict)
        return result

    def get_job(self, job_id: str) -> Optional[ScheduledJob]:
        return self._jobs.get(job_id)

    def reload_from_db(self):
        """从数据库恢复调度任务（重启后）"""
        if not self.db:
            return
        for row in self.db.load_scheduled_jobs():
            job = ScheduledJob(
                job_id=row["job_id"],
                name=row["name"],
                template_id=row.get("template_id"),
                cron_expr=row.get("cron_expr"),
                interval_seconds=row.get("interval_seconds"),
                enabled=bool(row.get("enabled", 1)),
            )
            job.last_run = row.get("last_run")
            job.next_run = row.get("next_run")
            self._jobs[job.job_id] = job
            if APSCHEDULER_AVAILABLE and self._scheduler and job.enabled:
                trigger = self._build_trigger(job)
                if trigger:
                    self._scheduler.add_job(
                        func=lambda j=job: self._execute_job(j),
                        trigger=trigger,
                        id=job.job_id,
                        replace_existing=True,
                    )
        logger.info(f"Reloaded {len(self._jobs)} scheduled jobs from DB")

    def shutdown(self):
        """关闭调度器"""
        if APSCHEDULER_AVAILABLE and self._scheduler:
            self._scheduler.shutdown(wait=False)
            logger.info("CronScheduler shut down")

    # ─── Internal ────────────────────────────────────────────────

    @staticmethod
    def _build_trigger(job: ScheduledJob):
        """根据 job 配置构建 APScheduler trigger"""
        if not APSCHEDULER_AVAILABLE:
            return None

        if job.interval_seconds:
            return IntervalTrigger(seconds=job.interval_seconds)

        if job.cron_expr:
            parts = job.cron_expr.split()
            # cron 表达式：秒 分 时 日 月 周
            kw = {}
            mapping = ["second", "minute", "hour", "day", "month"]
            for i, val in enumerate(parts):
                if i < len(mapping):
                    kw[mapping[i]] = val
            # 周用 day_of_week
            if len(parts) >= 6:
                kw["day_of_week"] = parts[5]
            return APSCronTrigger(**kw)

        return DateTrigger(run_date=datetime.now() + timedelta(seconds=5))

    # ─── 快捷预设 ────────────────────────────────────────────────

    def add_preset_jobs(self, presets: Dict[str, Dict]):
        """
        添加预设定时任务

        presets = {
            "morning_report": {
                "name": "晨报",
                "template_id": "quick_report",
                "cron_expr": "0 8 * * *",   # 每天 8:00
            },
            ...
        }
        """
        for job_id, cfg in presets.items():
            self.add_job(
                name=cfg["name"],
                template_id=cfg.get("template_id"),
                cron_expr=cfg.get("cron_expr"),
                interval_seconds=cfg.get("interval_seconds"),
            )

    def get_presets(self) -> List[Dict[str, Any]]:
        """返回推荐预设模板"""
        return [
            {
                "preset_id": "morning_brief",
                "name": "晨报（每天 8:00）",
                "template_id": "quick_report",
                "cron_expr": "0 8 * * *",
                "description": "每天早上生成并推送当日简报",
            },
            {
                "preset_id": "hourly_status",
                "name": "每小时状态（每60分钟）",
                "template_id": "status_check",
                "interval_seconds": 3600,
                "description": "每小时检查一次 OpenClaw 系统状态",
            },
            {
                "preset_id": "evening_tech",
                "name": "技术日报（工作日 18:00）",
                "template_id": "tech_report",
                "cron_expr": "0 18 * * 1-5",
                "description": "工作日傍晚生成技术前沿报告",
            },
            {
                "preset_id": "morning_market",
                "name": "商业日报（工作日 9:30）",
                "template_id": "market_report",
                "cron_expr": "0 9 * * 1-5",
                "description": "工作日早间生成商业洞察报告",
            },
        ]
