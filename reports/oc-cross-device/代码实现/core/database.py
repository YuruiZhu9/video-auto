"""
任务历史数据库 — SQLite 持久化层

存储所有任务的执行记录，支持：
- 任务执行记录（成功/失败/进行中）
- 审计日志（操作记录）
- 统计查询（任务数量/耗时趋势）
"""

import sqlite3
import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from contextlib import contextmanager


@dataclass
class TaskRecord:
    """任务执行记录"""
    id: Optional[int] = None
    task_id: str = ""
    name: str = ""
    action: str = ""
    status: str = "pending"  # pending | running | completed | failed | cancelled
    result_summary: str = ""
    result_detail: str = ""
    error_message: str = ""
    duration_seconds: float = 0.0
    trigger_source: str = "api"  # api | cron | webhook | telegram | manual
    trigger_detail: str = ""
    created_at: str = ""
    started_at: str = ""
    completed_at: str = ""
    api_key_name: str = ""
    api_key_level: str = ""
    session_key: str = ""  # OpenClaw session key
    template_id: str = ""
    params_json: str = ""

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}

    @classmethod
    def from_row(cls, row: tuple) -> "TaskRecord":
        if row is None:
            return None
        keys = [
            "id", "task_id", "name", "action", "status",
            "result_summary", "result_detail", "error_message",
            "duration_seconds", "trigger_source", "trigger_detail",
            "created_at", "started_at", "completed_at",
            "api_key_name", "api_key_level", "session_key",
            "template_id", "params_json"
        ]
        return cls(**{k: v for k, v in zip(keys, row)})


@dataclass
class AuditRecord:
    """审计日志记录"""
    id: Optional[int] = None
    timestamp: str = ""
    api_key_name: str = ""
    api_key_level: str = ""
    action: str = ""
    method: str = ""
    path: str = ""
    ip_address: str = ""
    user_agent: str = ""
    request_body_hash: str = ""  # 请求体哈希（脱敏后）
    response_status: int = 0
    response_summary: str = ""
    duration_ms: float = 0.0


class TaskDatabase:
    """
    SQLite 任务历史数据库

    表结构：
    - tasks: 任务执行记录
    - audit_log: 操作审计日志
    - templates_stats: 模板使用统计（聚合表）
    """

    SCHEMA = """
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id TEXT NOT NULL,
        name TEXT NOT NULL DEFAULT '',
        action TEXT NOT NULL DEFAULT '',
        status TEXT NOT NULL DEFAULT 'pending',
        result_summary TEXT DEFAULT '',
        result_detail TEXT DEFAULT '',
        error_message TEXT DEFAULT '',
        duration_seconds REAL DEFAULT 0.0,
        trigger_source TEXT DEFAULT 'api',
        trigger_detail TEXT DEFAULT '',
        created_at TEXT NOT NULL,
        started_at TEXT DEFAULT '',
        completed_at TEXT DEFAULT '',
        api_key_name TEXT DEFAULT '',
        api_key_level TEXT DEFAULT '',
        session_key TEXT DEFAULT '',
        template_id TEXT DEFAULT '',
        params_json TEXT DEFAULT '{}'
    );

    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        api_key_name TEXT DEFAULT '',
        api_key_level TEXT DEFAULT '',
        action TEXT NOT NULL,
        method TEXT DEFAULT '',
        path TEXT DEFAULT '',
        ip_address TEXT DEFAULT '',
        user_agent TEXT DEFAULT '',
        request_body_hash TEXT DEFAULT '',
        response_status INTEGER DEFAULT 0,
        response_summary TEXT DEFAULT '',
        duration_ms REAL DEFAULT 0.0
    );

    CREATE TABLE IF NOT EXISTS templates_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        template_id TEXT UNIQUE NOT NULL,
        template_name TEXT DEFAULT '',
        total_runs INTEGER DEFAULT 0,
        success_count INTEGER DEFAULT 0,
        failed_count INTEGER DEFAULT 0,
        avg_duration_seconds REAL DEFAULT 0.0,
        last_run_at TEXT DEFAULT ''
    );

    CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
    CREATE INDEX IF NOT EXISTS idx_tasks_created ON tasks(created_at);
    CREATE INDEX IF NOT EXISTS idx_tasks_template ON tasks(template_id);
    CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp);
    """

    def __init__(self, db_path: str = "data/tasks.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._init_db()

    def _init_db(self):
        with self._get_conn() as conn:
            conn.executescript(self.SCHEMA)
            conn.commit()

    @contextmanager
    def _get_conn(self):
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    # ─── 任务记录 CRUD ─────────────────────────────────────────────

    def create_task(self, record: TaskRecord) -> int:
        """创建新任务记录，返回自增 ID"""
        with self._lock:
            with self._get_conn() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO tasks (
                        task_id, name, action, status, trigger_source,
                        trigger_detail, created_at, api_key_name, api_key_level,
                        session_key, template_id, params_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.task_id, record.name, record.action,
                        record.status, record.trigger_source, record.trigger_detail,
                        record.created_at or self._now_iso(),
                        record.api_key_name, record.api_key_level,
                        record.session_key, record.template_id,
                        record.params_json or "{}"
                    )
                )
                conn.commit()
                return cursor.lastrowid

    def update_task_started(self, db_id: int, session_key: str = "") -> None:
        with self._lock:
            with self._get_conn() as conn:
                conn.execute(
                    "UPDATE tasks SET status='running', started_at=?, session_key=? WHERE id=?",
                    (self._now_iso(), session_key, db_id)
                )
                conn.commit()

    def update_task_completed(
        self,
        db_id: int,
        status: str,
        result_summary: str = "",
        result_detail: str = "",
        error_message: str = "",
        session_key: str = ""
    ) -> None:
        with self._lock:
            with self._get_conn() as conn:
                completed_at = self._now_iso()
                # 计算耗时
                row = conn.execute(
                    "SELECT started_at FROM tasks WHERE id=?", (db_id,)
                ).fetchone()
                duration = 0.0
                if row and row[0]:
                    try:
                        start = datetime.fromisoformat(row[0])
                        end = datetime.fromisoformat(completed_at)
                        duration = (end - start).total_seconds()
                    except Exception:
                        pass
                conn.execute(
                    """
                    UPDATE tasks SET
                        status=?, result_summary=?, result_detail=?,
                        error_message=?, completed_at=?, duration_seconds=?,
                        session_key=COALESCE(NULLIF(?,''), session_key)
                    WHERE id=?
                    """,
                    (status, result_summary, result_detail,
                     error_message, completed_at, duration,
                     session_key, db_id)
                )
                conn.commit()

    def get_task(self, db_id: int) -> Optional[TaskRecord]:
        with self._lock:
            with self._get_conn() as conn:
                row = conn.execute("SELECT * FROM tasks WHERE id=?", (db_id,)).fetchone()
                return TaskRecord.from_row(row) if row else None

    def get_task_by_task_id(self, task_id: str) -> Optional[TaskRecord]:
        with self._lock:
            with self._get_conn() as conn:
                row = conn.execute(
                    "SELECT * FROM tasks WHERE task_id=? ORDER BY id DESC LIMIT 1",
                    (task_id,)
                ).fetchone()
                return TaskRecord.from_row(row) if row else None

    def list_tasks(
        self,
        status: Optional[str] = None,
        template_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[TaskRecord]:
        with self._lock:
            with self._get_conn() as conn:
                sql = "SELECT * FROM tasks WHERE 1=1"
                params: List[Any] = []
                if status:
                    sql += " AND status=?"
                    params.append(status)
                if template_id:
                    sql += " AND template_id=?"
                    params.append(template_id)
                sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                rows = conn.execute(sql, params).fetchall()
                return [TaskRecord.from_row(r) for r in rows]

    def count_tasks(self, status: Optional[str] = None) -> Dict[str, int]:
        with self._lock:
            with self._get_conn() as conn:
                total = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
                counts = dict(conn.execute(
                    "SELECT status, COUNT(*) FROM tasks GROUP BY status"
                ).fetchall())
                return {
                    "total": total,
                    "completed": counts.get("completed", 0),
                    "failed": counts.get("failed", 0),
                    "running": counts.get("running", 0),
                    "pending": counts.get("pending", 0),
                    "cancelled": counts.get("cancelled", 0),
                }

    def get_recent_tasks(self, limit: int = 20) -> List[TaskRecord]:
        return self.list_tasks(limit=limit)

    def get_task_stats_7d(self) -> Dict[str, Any]:
        """近7天任务统计"""
        with self._lock:
            with self._get_conn() as conn:
                today = datetime.now(timezone.utc).date().isoformat()
                week_ago = (
                    datetime.now(timezone.utc) - __import__("datetime").timedelta(days=7)
                ).date().isoformat()

                daily = conn.execute(
                    """
                    SELECT DATE(created_at) as day,
                           COUNT(*) as total,
                           SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) as ok,
                           SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) as fail,
                           AVG(CASE WHEN status IN ('completed','failed')
                                    THEN duration_seconds ELSE NULL END) as avg_dur
                    FROM tasks
                    WHERE DATE(created_at) >= ?
                    GROUP BY DATE(created_at)
                    ORDER BY day ASC
                    """,
                    (week_ago,)
                ).fetchall()

                status_dist = conn.execute(
                    """
                    SELECT status, COUNT(*) as cnt FROM tasks
                    WHERE DATE(created_at) >= ?
                    GROUP BY status
                    """,
                    (week_ago,)
                ).fetchall()

                return {
                    "daily": [
                        {
                            "day": r[0],
                            "total": r[1],
                            "ok": r[2],
                            "fail": r[3],
                            "avg_dur": round(r[4] or 0, 1),
                        }
                        for r in daily
                    ],
                    "status_distribution": {r[0]: r[1] for r in status_dist},
                }

    # ─── 审计日志 ──────────────────────────────────────────────────

    def log_audit(
        self,
        action: str,
        method: str = "",
        path: str = "",
        ip_address: str = "",
        user_agent: str = "",
        api_key_name: str = "",
        api_key_level: str = "",
        response_status: int = 200,
        response_summary: str = "",
        duration_ms: float = 0.0,
    ) -> None:
        with self._lock:
            with self._get_conn() as conn:
                conn.execute(
                    """
                    INSERT INTO audit_log (
                        timestamp, api_key_name, api_key_level, action,
                        method, path, ip_address, user_agent,
                        response_status, response_summary, duration_ms
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        self._now_iso(), api_key_name, api_key_level, action,
                        method, path, ip_address, user_agent,
                        response_status, response_summary, duration_ms
                    )
                )
                conn.commit()

    def list_audit(
        self,
        limit: int = 100,
        offset: int = 0,
        action: Optional[str] = None,
    ) -> List[AuditRecord]:
        with self._lock:
            with self._get_conn() as conn:
                sql = "SELECT * FROM audit_log WHERE 1=1"
                params: List[Any] = []
                if action:
                    sql += " AND action=?"
                    params.append(action)
                sql += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                rows = conn.execute(sql, params).fetchall()
                return [AuditRecord(**dict(r)) for r in rows]

    # ─── 模板统计 ──────────────────────────────────────────────────

    def update_template_stats(self, template_id: str, template_name: str = "") -> None:
        with self._lock:
            with self._get_conn() as conn:
                stats = conn.execute(
                    """
                    SELECT
                        COUNT(*) as total,
                        SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) as ok,
                        SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) as fail,
                        AVG(CASE WHEN status IN ('completed','failed')
                                 THEN duration_seconds ELSE NULL END) as avg_dur,
                        MAX(completed_at) as last_run
                    FROM tasks WHERE template_id=?
                    """,
                    (template_id,)
                ).fetchone()
                if stats:
                    conn.execute(
                        """
                        INSERT INTO templates_stats
                            (template_id, template_name, total_runs, success_count,
                             failed_count, avg_duration_seconds, last_run_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(template_id) DO UPDATE SET
                            template_name=excluded.template_name,
                            total_runs=excluded.total_runs,
                            success_count=excluded.success_count,
                            failed_count=excluded.failed_count,
                            avg_duration_seconds=excluded.avg_duration_seconds,
                            last_run_at=excluded.last_run_at
                        """,
                        (
                            template_id, template_name,
                            stats[0] or 0, stats[1] or 0, stats[2] or 0,
                            round(stats[3] or 0, 2), stats[4] or ""
                        )
                    )
                    conn.commit()

    def get_template_stats(self) -> List[Dict]:
        with self._lock:
            with self._get_conn() as conn:
                rows = conn.execute(
                    "SELECT * FROM templates_stats ORDER BY total_runs DESC"
                ).fetchall()
                return [dict(r) for r in rows]
