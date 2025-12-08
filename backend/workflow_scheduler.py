from __future__ import annotations

import asyncio
import json
import os
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional, Set

from backend.audit_log import log_event
from backend.notification_service import notification_service

ISO_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
SCHEDULER_DB = Path(os.getenv("WORKFLOW_SCHEDULER_DB", "workflow_scheduler.db"))

Handler = Callable[[Dict[str, Any]], Awaitable[Any]] | Callable[[Dict[str, Any]], Any]
_HANDLERS: Dict[str, Handler] = {}


def register_handler(name: str, handler: Handler) -> None:
    _HANDLERS[name] = handler


def _utcnow() -> datetime:
    return datetime.utcnow()


def _to_iso(ts: datetime) -> str:
    return ts.strftime(ISO_FORMAT)


@dataclass
class ScheduledJob:
    id: str
    handler: str
    payload: Dict[str, Any]
    schedule_type: str
    schedule_value: str
    next_run: datetime
    last_run: Optional[datetime] = None
    status: str = "scheduled"
    created_at: datetime = _utcnow()

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "ScheduledJob":
        return cls(
            id=row["id"],
            handler=row["handler"],
            payload=json.loads(row["payload"]),
            schedule_type=row["schedule_type"],
            schedule_value=row["schedule_value"],
            next_run=datetime.fromisoformat(row["next_run"]),
            last_run=datetime.fromisoformat(row["last_run"]) if row["last_run"] else None,
            status=row["status"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def to_record(self) -> Dict[str, Any]:
        record = asdict(self)
        record["payload"] = json.dumps(self.payload)
        record["next_run"] = _to_iso(self.next_run)
        record["last_run"] = _to_iso(self.last_run) if self.last_run else None
        record["created_at"] = _to_iso(self.created_at)
        return record


class OrchestrationScheduler:
    def __init__(self, db_path: Path = SCHEDULER_DB, *, approval_queue: Optional["ApprovalQueue"] = None):
        self.db_path = db_path
        self.approval_queue = approval_queue
        self.approval_required_handlers: Set[str] = set()
        self._ensure_schema()

    def _connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS scheduled_jobs (
                    id TEXT PRIMARY KEY,
                    handler TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    schedule_type TEXT NOT NULL,
                    schedule_value TEXT NOT NULL,
                    next_run TEXT NOT NULL,
                    last_run TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS job_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT NOT NULL,
                    handler TEXT NOT NULL,
                    run_started TEXT NOT NULL,
                    run_finished TEXT,
                    status TEXT NOT NULL,
                    message TEXT,
                    payload TEXT,
                    FOREIGN KEY(job_id) REFERENCES scheduled_jobs(id)
                )
                """
            )
            conn.commit()

    def _set_status(self, job_id: str, status: str) -> None:
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE scheduled_jobs SET status = ? WHERE id = ?", (status, job_id))
            conn.commit()

    def require_approval(self, handler: str) -> None:
        self.approval_required_handlers.add(handler)

    def register_approval_queue(self, approval_queue: "ApprovalQueue") -> None:
        self.approval_queue = approval_queue

    def add_job(
        self,
        job_id: str,
        handler: str,
        payload: Dict[str, Any],
        schedule_type: str,
        schedule_value: str,
        *,
        start_at: Optional[datetime] = None,
    ) -> ScheduledJob:
        next_run = start_at or self._calculate_next_run(schedule_type, schedule_value)
        job = ScheduledJob(
            id=job_id,
            handler=handler,
            payload=payload,
            schedule_type=schedule_type,
            schedule_value=schedule_value,
            next_run=next_run,
        )
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT OR REPLACE INTO scheduled_jobs
                (id, handler, payload, schedule_type, schedule_value, next_run, last_run, status, created_at)
                VALUES (:id, :handler, :payload, :schedule_type, :schedule_value, :next_run, :last_run, :status, :created_at)
                """,
                job.to_record(),
            )
            conn.commit()
        log_event("scheduler.add_job", handler=handler, job_id=job_id, schedule=schedule_value)
        return job

    def remove_job(self, job_id: str) -> bool:
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM scheduled_jobs WHERE id = ?", (job_id,))
            deleted = cur.rowcount
            conn.commit()
        if deleted:
            log_event("scheduler.remove_job", job_id=job_id)
        return bool(deleted)

    def list_jobs(self) -> List[ScheduledJob]:
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM scheduled_jobs ORDER BY next_run ASC")
            rows = cur.fetchall()
        return [ScheduledJob.from_row(row) for row in rows]

    def due_jobs(self, *, now: Optional[datetime] = None) -> List[ScheduledJob]:
        now = now or _utcnow()
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM scheduled_jobs WHERE status = 'scheduled' AND next_run <= ? ORDER BY next_run ASC",
                (_to_iso(now),),
            )
            rows = cur.fetchall()
        return [ScheduledJob.from_row(row) for row in rows]

    async def run_due_jobs(self) -> List[Dict[str, Any]]:
        results = []
        for job in self.due_jobs():
            results.append(await self.execute_job(job.id))
        return results

    async def execute_job(self, job_id: str, *, bypass_approval: bool = False) -> Dict[str, Any]:
        job = self.get_job(job_id)
        if not job:
            return {"job_id": job_id, "status": "error", "message": "Job not found"}

        handler = _HANDLERS.get(job.handler)
        if handler is None:
            self._record_run(job, success=False, message="handler_not_registered")
            return {"job_id": job.id, "status": "error", "message": "Handler not registered"}

        if not bypass_approval and job.handler in self.approval_required_handlers:
            if self.approval_queue is None:
                return {"job_id": job.id, "status": "error", "message": "Approval queue not configured"}
            self._set_status(job.id, "awaiting_approval")
            self.approval_queue.create_request(job.id, job.handler, job.payload)
            log_event("scheduler.awaiting_approval", job_id=job.id, handler=job.handler)
            return {"job_id": job.id, "status": "awaiting_approval"}

        self._set_status(job.id, "running")
        try:
            result = handler(job.payload)
            if asyncio.iscoroutine(result):
                result = await result
            self._record_run(job, success=True)
            notification_service.send_notification(
                subject=f"Job executed: {job.handler}",
                message=f"Job {job.id} completed successfully.",
            )
            return {"job_id": job.id, "status": "success", "result": result}
        except Exception as exc:  # pragma: no cover - defensive
            self._record_run(job, success=False, message=str(exc))
            notification_service.send_notification(
                subject=f"Job failed: {job.handler}",
                message=f"Job {job.id} failed with error: {exc}",
            )
            return {"job_id": job.id, "status": "error", "message": str(exc)}

    def get_job(self, job_id: str) -> Optional[ScheduledJob]:
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM scheduled_jobs WHERE id = ?", (job_id,))
            row = cur.fetchone()
        return ScheduledJob.from_row(row) if row else None

    def _record_run(self, job: ScheduledJob, *, success: bool, message: Optional[str] = None) -> None:
        now = _utcnow()
        next_run: Optional[datetime] = None
        status = "scheduled"
        if job.schedule_type == "once":
            next_run = job.next_run
            status = "completed"
        else:
            next_run = self._calculate_next_run(job.schedule_type, job.schedule_value, reference=now)

        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE scheduled_jobs
                SET last_run = ?, next_run = ?, status = ?
                WHERE id = ?
                """,
                (
                    _to_iso(now),
                    _to_iso(next_run),
                    status,
                    job.id,
                ),
            )
            cur.execute(
                """
                INSERT INTO job_history (job_id, handler, run_started, run_finished, status, message, payload)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job.id,
                    job.handler,
                    _to_iso(job.next_run),
                    _to_iso(now),
                    "success" if success else "error",
                    message,
                    json.dumps(job.payload),
                ),
            )
            conn.commit()

        log_event(
            "scheduler.run_job",
            job_id=job.id,
            handler=job.handler,
            status="success" if success else "error",
            message=message,
        )

    def reschedule_after_rejection(self, job_id: str) -> None:
        job = self.get_job(job_id)
        if not job:
            return
        now = _utcnow()
        next_run = self._calculate_next_run(job.schedule_type, job.schedule_value, reference=now)
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE scheduled_jobs
                SET status = 'scheduled', next_run = ?, last_run = ?
                WHERE id = ?
                """,
                (_to_iso(next_run), job.last_run and _to_iso(job.last_run) or None, job.id),
            )
            conn.commit()

    def _calculate_next_run(
        self,
        schedule_type: str,
        schedule_value: str,
        *,
        reference: Optional[datetime] = None,
    ) -> datetime:
        reference = reference or _utcnow()
        if schedule_type == "interval":
            seconds = float(schedule_value)
            return reference + timedelta(seconds=seconds)
        if schedule_type == "once":
            return datetime.fromisoformat(schedule_value)
        if schedule_type == "cron":
            minute, hour, *_ = schedule_value.strip().split()
            next_time = reference.replace(second=0, microsecond=0)
            next_time += timedelta(minutes=1)
            while True:
                if (minute == "*" or int(minute) == next_time.minute) and (hour == "*" or int(hour) == next_time.hour):
                    return next_time
                next_time += timedelta(minutes=1)
        raise ValueError(f"Unsupported schedule type: {schedule_type}")


# Register a default handler that simply logs the payload for smoke tests.
def _log_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    log_event("scheduler.default_handler", payload=payload)
    return {"ack": True}


register_handler("log_payload", _log_payload)

