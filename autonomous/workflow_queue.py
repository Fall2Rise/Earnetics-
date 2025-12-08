"""Persistent workflow queue for autonomous task orchestration."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from backend.corporate_memory import BUSINESS_DB_PATH as DEFAULT_DB_PATH
except ModuleNotFoundError:  # pragma: no cover - legacy path fallback
    from corporate_memory import BUSINESS_DB_PATH as DEFAULT_DB_PATH


ISO_FORMAT = "%Y-%m-%dT%H:%M:%S"


def _utcnow() -> datetime:
    return datetime.utcnow()


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        try:
            return datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            return None


@dataclass
class QueueItem:
    """Representation of a queued task awaiting autonomous execution."""

    task_id: int
    department: str
    priority: str
    status: str = "pending"
    available_at: str = _utcnow().strftime(ISO_FORMAT)
    objective_id: Optional[int] = None
    directive_id: Optional[int] = None
    due_date: Optional[str] = None
    sla_minutes: int = 0
    attempts: int = 0
    max_attempts: int = 3
    claimed_by: Optional[str] = None
    claimed_at: Optional[str] = None
    last_error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_record(self) -> Dict[str, Any]:
        now = _utcnow().strftime(ISO_FORMAT)
        payload = asdict(self)
        payload.setdefault("created_at", now)
        payload.setdefault("updated_at", now)
        return payload


class WorkflowQueueRepository:
    """SQLite-backed repository for workflow queue operations."""

    def __init__(self, db_path: Path | str = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path)
        self._ensure_table()

    def _connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_table(self) -> None:
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS autonomy_task_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    objective_id INTEGER,
                    directive_id INTEGER,
                    department TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    status TEXT NOT NULL,
                    available_at TEXT NOT NULL,
                    due_date TEXT,
                    sla_minutes INTEGER DEFAULT 0,
                    attempts INTEGER DEFAULT 0,
                    max_attempts INTEGER DEFAULT 3,
                    claimed_by TEXT,
                    claimed_at TEXT,
                    last_error TEXT,
                    metadata JSON,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (task_id) REFERENCES department_tasks (id),
                    FOREIGN KEY (objective_id) REFERENCES corporate_objectives (id),
                    UNIQUE (task_id)
                )
                """
            )
            conn.commit()

    # ------------------------------------------------------------------
    # Enqueue operations

    def enqueue(self, item: QueueItem) -> Dict[str, Any]:
        record = item.to_record()
        metadata = record.get("metadata") or {}
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO autonomy_task_queue (
                    task_id, objective_id, directive_id, department, priority,
                    status, available_at, due_date, sla_minutes, attempts,
                    max_attempts, claimed_by, claimed_at, last_error, metadata,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record["task_id"],
                    record.get("objective_id"),
                    record.get("directive_id"),
                    record["department"],
                    record["priority"],
                    record.get("status", "pending"),
                    record["available_at"],
                    record.get("due_date"),
                    record.get("sla_minutes", 0),
                    record.get("attempts", 0),
                    record.get("max_attempts", 3),
                    record.get("claimed_by"),
                    record.get("claimed_at"),
                    record.get("last_error"),
                    json.dumps(metadata, ensure_ascii=False),
                    record["created_at"],
                    record["updated_at"],
                ),
            )
            record_id = cur.lastrowid
            conn.commit()
        record["id"] = record_id
        record["metadata"] = metadata
        return record

    def enqueue_from_task(
        self,
        task_record: Dict[str, Any],
        *,
        directive_id: Optional[int] = None,
        available_at: Optional[str] = None,
        priority: Optional[str] = None,
    ) -> Dict[str, Any]:
        item = QueueItem(
            task_id=task_record["id"],
            department=task_record["department"],
            priority=priority or task_record.get("priority", "medium"),
            objective_id=task_record.get("objective_id"),
            directive_id=directive_id,
            due_date=task_record.get("due_date"),
            sla_minutes=int(task_record.get("sla_minutes") or 0),
            metadata={"task_snapshot": task_record},
        )
        if available_at:
            item.available_at = available_at
        return self.enqueue(item)

    def get_item_by_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM autonomy_task_queue WHERE task_id = ?", (task_id,))
            row = cur.fetchone()
        if not row:
            return None
        record = dict(row)
        record["metadata"] = json.loads(record.get("metadata") or "{}")
        return record

    def mark_claimed_by_task(self, task_id: int, worker: str) -> Optional[Dict[str, Any]]:
        now = _utcnow().strftime(ISO_FORMAT)
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE autonomy_task_queue
                SET status = 'in_progress',
                    attempts = attempts + 1,
                    claimed_by = ?,
                    claimed_at = ?,
                    updated_at = ?
                WHERE task_id = ?
            """, (worker, now, now, task_id))
            conn.commit()
            if cur.rowcount == 0:
                return None
        return self.get_item_by_task(task_id)

    def release_task_by_id(self, task_id: int, *, reason: Optional[str] = None, delay_minutes: int = 0) -> Optional[Dict[str, Any]]:
        resume_at = (_utcnow() + timedelta(minutes=delay_minutes)).strftime(ISO_FORMAT)
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE autonomy_task_queue
                SET status = 'pending',
                    claimed_by = NULL,
                    claimed_at = NULL,
                    available_at = ?,
                    last_error = ?,
                    updated_at = ?
                WHERE task_id = ?
            """, (resume_at, reason, _utcnow().strftime(ISO_FORMAT), task_id))
            conn.commit()
            if cur.rowcount == 0:
                return None
        return self.get_item_by_task(task_id)

    def mark_completed_by_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE autonomy_task_queue
                SET status = 'completed',
                    claimed_by = NULL,
                    claimed_at = NULL,
                    last_error = NULL,
                    updated_at = ?
                WHERE task_id = ?
            """, (_utcnow().strftime(ISO_FORMAT), task_id))
            conn.commit()
            if cur.rowcount == 0:
                return None
        return self.get_item_by_task(task_id)

    # ------------------------------------------------------------------
    # Claim and lifecycle management

    def claim_next(self, department: str, worker: str) -> Optional[Dict[str, Any]]:
        now = _utcnow().strftime(ISO_FORMAT)
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT * FROM autonomy_task_queue
                WHERE department = ?
                  AND status = 'pending'
                  AND available_at <= ?
                ORDER BY
                    CASE priority
                        WHEN 'urgent' THEN 0
                        WHEN 'high' THEN 1
                        WHEN 'medium' THEN 2
                        WHEN 'low' THEN 3
                        ELSE 4
                    END,
                    COALESCE(due_date, '9999-12-31'),
                    created_at
                LIMIT 1
                """,
                (department, now),
            )
            row = cur.fetchone()
            if not row:
                return None
            record = dict(row)
            attempts = record.get("attempts", 0) + 1
            metadata = json.loads(record.get("metadata") or "{}")
            cur.execute(
                """
                UPDATE autonomy_task_queue
                SET status = 'in_progress', attempts = ?, claimed_by = ?,
                    claimed_at = ?, updated_at = ?
                WHERE id = ?
                """,
                (attempts, worker, now, now, record["id"]),
            )
            conn.commit()
        record.update(
            {
                "status": "in_progress",
                "attempts": attempts,
                "claimed_by": worker,
                "claimed_at": now,
                "metadata": metadata,
            }
        )
        return record

    def mark_completed(self, queue_id: int) -> None:
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE autonomy_task_queue
                SET status = 'completed', updated_at = ?, claimed_by = NULL,
                    claimed_at = NULL, last_error = NULL
                WHERE id = ?
                """,
                (_utcnow().strftime(ISO_FORMAT), queue_id),
            )
            conn.commit()

    def release(self, queue_id: int, *, reason: Optional[str] = None, delay_minutes: int = 5) -> None:
        resume_at = (_utcnow() + timedelta(minutes=delay_minutes)).strftime(ISO_FORMAT)
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE autonomy_task_queue
                SET status = 'pending', claimed_by = NULL, claimed_at = NULL,
                    available_at = ?, last_error = ?, updated_at = ?
                WHERE id = ?
                """,
                (resume_at, reason, _utcnow().strftime(ISO_FORMAT), queue_id),
            )
            conn.commit()

    def recover_in_progress_items(self, *, claimed_by: Optional[str] = None) -> int:
        """Return in-progress queue items to pending so a new worker run can resume."""

        now = _utcnow().strftime(ISO_FORMAT)
        query = """
                UPDATE autonomy_task_queue
                SET status = 'pending',
                    claimed_by = NULL,
                    claimed_at = NULL,
                    available_at = ?,
                    updated_at = ?
                WHERE status = 'in_progress'
            """
        params: list[Any] = [now, now]
        if claimed_by is not None:
            query += " AND (claimed_by = ? OR claimed_by IS NULL)"
            params.append(claimed_by)
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()
            return cur.rowcount

    def mark_failed(self, queue_id: int, *, error: str) -> None:
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE autonomy_task_queue
                SET status = 'failed', last_error = ?, updated_at = ?
                WHERE id = ?
                """,
                (error, _utcnow().strftime(ISO_FORMAT), queue_id),
            )
            conn.commit()

    # ------------------------------------------------------------------
    # Inspection helpers

    def list_at_risk(self) -> List[dict]:
        now = _utcnow()
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM autonomy_task_queue
                WHERE status IN ('pending', 'in_progress')
            """)
            rows = cur.fetchall()

        results: List[dict] = []
        for row in rows:
            record = dict(row)
            record['metadata'] = json.loads(record.get('metadata') or '{}')
            status = (record.get('status') or '').lower()
            attempts = int(record.get('attempts') or 0)
            max_attempts = int(record.get('max_attempts') or 0) or 3
            sla_minutes = int(record.get('sla_minutes') or 0)
            reason = None

            if attempts >= max_attempts and max_attempts > 0:
                reason = 'max_attempts_reached'

            if not reason and status == 'in_progress' and sla_minutes > 0:
                claimed_at = record.get('claimed_at')
                claimed_dt = _parse_datetime(claimed_at)
                if claimed_dt and (now - claimed_dt).total_seconds() > sla_minutes * 60:
                    reason = 'sla_breach'

            if not reason and record.get('due_date'):
                due_dt = _parse_datetime(record['due_date'])
                if due_dt and due_dt < now:
                    reason = 'past_due'

            if reason:
                record['alert_reason'] = reason
                results.append(record)

        return results


    def list_items(self, *, status: Optional[str] = None, limit: int = 50) -> List[dict]:
        query = "SELECT * FROM autonomy_task_queue"
        params: List[Any] = []
        if status:
            query += " WHERE status = ?"
            params.append(status)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            rows = cur.fetchall()
        results: List[dict] = []
        for row in rows:
            record = dict(row)
            record["metadata"] = json.loads(record.get("metadata") or "{}")
            results.append(record)
        return results

    def count_pending(self, department: Optional[str] = None) -> int:
        query = "SELECT COUNT(*) FROM autonomy_task_queue WHERE status = 'pending'"
        params: List[Any] = []
        if department:
            query += " AND department = ?"
            params.append(department)
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            (count,) = cur.fetchone()
        return int(count)

    def purge_completed(self, max_age_days: int = 30) -> int:
        cutoff = (_utcnow() - timedelta(days=max_age_days)).strftime(ISO_FORMAT)
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                DELETE FROM autonomy_task_queue
                WHERE status IN ('completed', 'failed')
                  AND updated_at < ?
                """,
                (cutoff,),
            )
            deleted = cur.rowcount
            conn.commit()
        return deleted


__all__ = ["QueueItem", "WorkflowQueueRepository"]





