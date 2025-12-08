from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.audit_log import log_event
from backend.notification_service import notification_service

ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
APPROVAL_DB_PATH = Path(os.getenv("APPROVAL_QUEUE_DB", "approval_queue.db"))


def _utcnow() -> str:
    return datetime.utcnow().strftime(ISO_FORMAT)


@dataclass
class ApprovalRequest:
    id: Optional[int]
    job_id: str
    handler: str
    payload: Dict[str, Any]
    status: str = "pending"
    created_at: str = _utcnow()
    decided_at: Optional[str] = None
    decision: Optional[str] = None
    message: Optional[str] = None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "ApprovalRequest":
        return cls(
            id=row["id"],
            job_id=row["job_id"],
            handler=row["handler"],
            payload=json.loads(row["payload"] or "{}"),
            status=row["status"],
            created_at=row["created_at"],
            decided_at=row["decided_at"],
            decision=row["decision"],
            message=row["message"],
        )

    def to_record(self) -> Dict[str, Any]:
        record = asdict(self)
        record["payload"] = json.dumps(self.payload)
        return record


class ApprovalQueue:
    def __init__(self, db_path: Path = APPROVAL_DB_PATH):
        self.db_path = db_path
        self._ensure_schema()
        self.on_approved: Optional[callable] = None
        self.on_rejected: Optional[callable] = None

    def _connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS approval_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT NOT NULL,
                    handler TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    decided_at TEXT,
                    decision TEXT,
                    message TEXT
                )
                """
            )
            conn.commit()

    def create_request(self, job_id: str, handler: str, payload: Dict[str, Any]) -> ApprovalRequest:
        request = ApprovalRequest(id=None, job_id=job_id, handler=handler, payload=payload)
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO approval_requests (job_id, handler, payload, status, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (request.job_id, request.handler, json.dumps(request.payload), request.status, request.created_at),
            )
            request.id = cur.lastrowid
            conn.commit()

        log_event("approvals.request_created", handler=handler, job_id=job_id)
        notification_service.send_notification(
            subject=f"Approval required: {handler}",
            message=f"Job {job_id} requires approval.",
        )
        return request

    def list_requests(self, status: Optional[str] = None, limit: int = 100) -> List[ApprovalRequest]:
        with self._connection() as conn:
            cur = conn.cursor()
            if status:
                cur.execute(
                    """
                    SELECT * FROM approval_requests
                    WHERE status = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                    """,
                    (status, limit),
                )
            else:
                cur.execute(
                    """
                    SELECT * FROM approval_requests
                    ORDER BY created_at DESC
                    LIMIT ?
                    """,
                    (limit,),
                )
            rows = cur.fetchall()
        return [ApprovalRequest.from_row(row) for row in rows]

    def get_request(self, request_id: int) -> Optional[ApprovalRequest]:
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM approval_requests WHERE id = ?", (request_id,))
            row = cur.fetchone()
        return ApprovalRequest.from_row(row) if row else None

    def approve(self, request_id: int, *, note: Optional[str] = None) -> ApprovalRequest:
        request = self.get_request(request_id)
        if not request:
            raise ValueError("Approval request not found")
        if request.status != "pending":
            raise ValueError("Approval request already processed")

        decided_at = _utcnow()
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE approval_requests
                SET status = 'approved', decided_at = ?, decision = ?, message = ?
                WHERE id = ?
                """,
                (decided_at, "approved", note, request_id),
            )
            conn.commit()

        updated = self.get_request(request_id)
        log_event("approvals.approved", handler=request.handler, job_id=request.job_id, note=note)
        notification_service.send_notification(
            subject=f"Approval granted: {request.handler}",
            message=f"Job {request.job_id} approved.",
        )
        if self.on_approved and updated:
            self.on_approved(updated)
        return updated  # type: ignore[arg-type]


    def reject(self, request_id: int, *, reason: Optional[str] = None) -> ApprovalRequest:
        request = self.get_request(request_id)
        if not request:
            raise ValueError("Approval request not found")
        if request.status != "pending":
            raise ValueError("Approval request already processed")

        decided_at = _utcnow()
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE approval_requests
                SET status = 'rejected', decided_at = ?, decision = ?, message = ?
                WHERE id = ?
                """,
                (decided_at, "rejected", reason, request_id),
            )
            conn.commit()

        updated = self.get_request(request_id)
        log_event("approvals.rejected", handler=request.handler, job_id=request.job_id, reason=reason)
        notification_service.send_notification(
            subject=f"Approval rejected: {request.handler}",
            message=f"Job {request.job_id} rejected.",
        )
        if self.on_rejected and updated:
            self.on_rejected(updated)
        return updated  # type: ignore[arg-type]



approval_queue = ApprovalQueue()


