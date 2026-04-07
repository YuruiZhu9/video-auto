#!/usr/bin/env python3
"""
SQLite Task History Database
任务历史持久化存储 — 支持审计、日志、统计
"""

import sqlite3
import json
import threading
import logging
import os
from datetime import datetime, timedelta
from typing import Optional, Any
from contextlib import contextmanager
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)

DB_PATH = os.environ.get("CLAWCTL_DB_PATH", "/workspace/reports/oc-cross-device/data/tasks.db")


# ── 数据模型 ────────────────────────────────────────────────────────────────

@dataclass
class TaskRecord:
    """持久化任务记录"""
    id: str
    name: str
    action: str
    params: str          # JSON string
    status: str
    priority: str
    notify: bool
    notify_channel: str
    result: Optional[str]   # JSON string
    error: Optional[str]
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    duration_ms: Optional[int]
    api_key_id: Optional[str] = None
    source_ip: Optional[str] = None
    tags: Optional[str] = None   # JSON list string

    def to_dict(self) -> dict:
        d = asdict(self)
        for k in ("params", "result", "tags"):
            if d[k] and isinstance(d[k], str):
                try:
                    d[k] = json.loads(d[k])
                except Exception:
                    pass
        return d


@dataclass
class AuditRecord:
    """审计日志记录"""
    id: int = 0
    timestamp: str = ""
    api_key_id: str = ""
    method: str = ""
    path: str = ""
    source_ip: Optional[str] = None
    status: str = "ok"
    detail: Optional[str] = None


@dataclass
class ScheduleRecord:
    """定时任务配置记录"""
    id: str
    name: str
    template: str
    cron_expr: str
    enabled: bool
    notify_on_complete: bool
    created_at: str
    last_run: Optional[str] = None
    next_run: Optional[str] = None
    run_count: int = 0


# ── 数据库管理器 ────────────────────────────────────────────────────────────

class TaskDatabase:
    """
    线程安全的 SQLite 数据库管理器
    所有操作自动事务化
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._local = threading.local()
        self._init_db()
        logger.info(f"数据库初始化完成: {db_path}")

    def _get_conn(self) -> sqlite3.Connection:
        """获取线程局部的数据库连接"""
        if not hasattr(self._local, "conn"):
            self._local.conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30,
            )
            self._local.conn.row_factory = sqlite3.Row
            # 启用 WAL 模式，提升并发读写性能
            self._local.conn.execute("PRAGMA journal_mode=WAL")
            self._local.conn.execute("PRAGMA foreign_keys=ON")
        return self._local.conn

    @contextmanager
    def _tx(self):
        """事务上下文管理器"""
        conn = self._get_conn()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    def _init_db(self):
        """初始化数据库表结构"""
        with self._tx() as conn:
            # 任务历史表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS task_history (
                    id              TEXT PRIMARY KEY,
                    name            TEXT NOT NULL,
                    action          TEXT NOT NULL,
                    params          TEXT DEFAULT '{}',
                    status          TEXT NOT NULL,
                    priority        TEXT DEFAULT 'NORMAL',
                    notify          INTEGER DEFAULT 1,
                    notify_channel  TEXT DEFAULT 'dingtalk',
                    result          TEXT,
                    error           TEXT,
                    created_at      TEXT NOT NULL,
                    started_at      TEXT,
                    completed_at    TEXT,
                    duration_ms     INTEGER,
                    api_key_id      TEXT,
                    source_ip       TEXT,
                    tags            TEXT DEFAULT '[]'
                )
            """)
            # 审计日志表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp   TEXT NOT NULL,
                    api_key_id  TEXT,
                    method      TEXT NOT NULL,
                    path        TEXT NOT NULL,
                    source_ip   TEXT,
                    status      TEXT DEFAULT 'ok',
                    detail      TEXT
                )
            """)
            # 定时任务表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS schedules (
                    id                   TEXT PRIMARY KEY,
                    name                 TEXT NOT NULL,
                    template             TEXT NOT NULL,
                    cron_expr            TEXT NOT NULL,
                    enabled              INTEGER DEFAULT 1,
                    notify_on_complete   INTEGER DEFAULT 1,
                    created_at           TEXT NOT NULL,
                    last_run             TEXT,
                    next_run             TEXT,
                    run_count            INTEGER DEFAULT 0
                )
            """)
            # 索引
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_created ON task_history(created_at DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON task_history(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_ts ON audit_log(timestamp DESC)")

    # ── 任务操作 ──────────────────────────────────────────────────────────

    def save_task(self, task_record: TaskRecord) -> bool:
        """保存/更新任务记录"""
        try:
            with self._tx() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO task_history
                    (id, name, action, params, status, priority, notify, notify_channel,
                     result, error, created_at, started_at, completed_at, duration_ms,
                     api_key_id, source_ip, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    task_record.id,
                    task_record.name,
                    task_record.action,
                    task_record.params,
                    task_record.status,
                    task_record.priority,
                    int(task_record.notify),
                    task_record.notify_channel,
                    task_record.result,
                    task_record.error,
                    task_record.created_at,
                    task_record.started_at,
                    task_record.completed_at,
                    task_record.duration_ms,
                    task_record.api_key_id,
                    task_record.source_ip,
                    task_record.tags,
                ))
            return True
        except Exception:
            logger.exception(f"保存任务失败: {task_record.id}")
            return False

    def get_task(self, task_id: str) -> Optional[TaskRecord]:
        """查询单个任务"""
        conn = self._get_conn()
        row = conn.execute(
            "SELECT * FROM task_history WHERE id = ?", (task_id,)
        ).fetchone()
        return TaskRecord(**dict(row)) if row else None

    def list_tasks(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        since: Optional[str] = None,
        until: Optional[str] = None,
    ) -> list[TaskRecord]:
        """查询任务列表（支持分页和日期过滤）"""
        conn = self._get_conn()
        sql = "SELECT * FROM task_history WHERE 1=1"
        params: list = []
        if status:
            sql += " AND status = ?"
            params.append(status)
        if since:
            sql += " AND created_at >= ?"
            params.append(since)
        if until:
            sql += " AND created_at <= ?"
            params.append(until)
        sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        rows = conn.execute(sql, params).fetchall()
        return [TaskRecord(**dict(r)) for r in rows]

    def count_tasks(self, status: Optional[str] = None, since: Optional[str] = None) -> int:
        """统计任务数量"""
        conn = self._get_conn()
        sql = "SELECT COUNT(*) FROM task_history WHERE 1=1"
        params: list = []
        if status:
            sql += " AND status = ?"
            params.append(status)
        if since:
            sql += " AND created_at >= ?"
            params.append(since)
        return conn.execute(sql, params).fetchone()[0]

    def delete_old_tasks(self, days: int = 30) -> int:
        """删除 N 天前的已完成任务"""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        with self._tx() as conn:
            cur = conn.execute(
                "DELETE FROM task_history WHERE completed_at < ? AND status IN ('success','failed','cancelled')",
                (cutoff,)
            )
        logger.info(f"清理过期任务: {cur.rowcount} 条")
        return cur.rowcount

    # ── 审计日志 ──────────────────────────────────────────────────────────

    def log_audit(
        self,
        api_key_id: str,
        method: str,
        path: str,
        source_ip: Optional[str] = None,
        status: str = "ok",
        detail: Optional[str] = None,
    ) -> bool:
        """写入审计日志"""
        try:
            with self._tx() as conn:
                conn.execute("""
                    INSERT INTO audit_log (timestamp, api_key_id, method, path, source_ip, status, detail)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (datetime.now().isoformat(), api_key_id, method, path, source_ip, status, detail))
            return True
        except Exception:
            logger.exception("写入审计日志失败")
            return False

    def list_audit(
        self,
        limit: int = 100,
        api_key_id: Optional[str] = None,
    ) -> list[AuditRecord]:
        """查询审计日志"""
        conn = self._get_conn()
        sql = "SELECT * FROM audit_log WHERE 1=1"
        params: list = []
        if api_key_id:
            sql += " AND api_key_id = ?"
            params.append(api_key_id)
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(sql, params).fetchall()
        return [AuditRecord(**dict(r)) for r in rows]

    # ── 定时任务管理 ───────────────────────────────────────────────────────

    def save_schedule(self, schedule: ScheduleRecord) -> bool:
        """保存定时任务配置"""
        try:
            with self._tx() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO schedules
                    (id, name, template, cron_expr, enabled, notify_on_complete,
                     created_at, last_run, next_run, run_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    schedule.id, schedule.name, schedule.template, schedule.cron_expr,
                    int(schedule.enabled), int(schedule.notify_on_complete),
                    schedule.created_at, schedule.last_run, schedule.next_run, schedule.run_count,
                ))
            return True
        except Exception:
            logger.exception(f"保存定时任务失败: {schedule.id}")
            return False

    def list_schedules(self, enabled_only: bool = False) -> list[ScheduleRecord]:
        """列出所有定时任务"""
        conn = self._get_conn()
        sql = "SELECT * FROM schedules"
        if enabled_only:
            sql += " WHERE enabled = 1"
        sql += " ORDER BY created_at"
        rows = conn.execute(sql).fetchall()
        return [ScheduleRecord(**dict(r)) for r in rows]

    def update_schedule_run(self, schedule_id: str, last_run: str, next_run: Optional[str] = None) -> bool:
        """更新定时任务运行记录"""
        with self._tx() as conn:
            conn.execute(
                "UPDATE schedules SET last_run = ?, next_run = ?, run_count = run_count + 1 WHERE id = ?",
                (last_run, next_run, schedule_id)
            )
        return True

    # ── 统计报表 ─────────────────────────────────────────────────────────

    def stats(self, days: int = 7) -> dict:
        """近 N 天任务统计"""
        since = (datetime.now() - timedelta(days=days)).isoformat()
        conn = self._get_conn()

        total = conn.execute(
            "SELECT COUNT(*) FROM task_history WHERE created_at >= ?", (since,)
        ).fetchone()[0]

        by_status = {}
        for row in conn.execute(
            "SELECT status, COUNT(*) FROM task_history WHERE created_at >= ? GROUP BY status",
            (since,)
        ).fetchall():
            by_status[row[0]] = row[1]

        # 近7天每日趋势
        daily = []
        for i in range(days):
            day = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            count = conn.execute(
                "SELECT COUNT(*) FROM task_history WHERE date(created_at) = ?", (day,)
            ).fetchone()[0]
            daily.append({"date": day, "count": count})

        # 平均耗时
        avg_row = conn.execute(
            "SELECT AVG(duration_ms) FROM task_history WHERE duration_ms IS NOT NULL AND created_at >= ?",
            (since,)
        ).fetchone()[0]
        avg_duration_ms = int(avg_row) if avg_row else 0

        # 成功率
        success = by_status.get("success", 0)
        failed = by_status.get("failed", 0)
        rate = round(success / (success + failed) * 100, 1) if (success + failed) > 0 else 0

        return {
            "period_days": days,
            "since": since,
            "total": total,
            "by_status": by_status,
            "daily": list(reversed(daily)),
            "avg_duration_ms": avg_duration_ms,
            "success_rate": rate,
        }
