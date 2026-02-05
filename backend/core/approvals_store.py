from __future__ import annotations

import json
import sqlite3
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ApprovalRequest:
    id: str
    created_at: float
    status: str  # pending|approved|rejected|executed|failed
    requested_by: str
    tool_name: str
    tool_category: str
    payload_json: str
    reason: str = ""
    decided_by: str = ""
    decided_at: float = 0.0
    result_json: str = ""


class ApprovalsStore:
    def __init__(self, db_path: str = "backend/data/approvals.db"):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._init()

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def _init(self):
        with self._conn() as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS approvals (
                  id TEXT PRIMARY KEY,
                  created_at REAL,
                  status TEXT,
                  requested_by TEXT,
                  tool_name TEXT,
                  tool_category TEXT,
                  payload_json TEXT,
                  reason TEXT,
                  decided_by TEXT,
                  decided_at REAL,
                  result_json TEXT
                )
                """
            )

    def create(self, requested_by: str, tool_name: str, tool_category: str, payload: Dict[str, Any], reason: str="") -> ApprovalRequest:
        rid = str(uuid.uuid4())
        req = ApprovalRequest(
            id=rid,
            created_at=time.time(),
            status="pending",
            requested_by=requested_by,
            tool_name=tool_name,
            tool_category=tool_category,
            payload_json=json.dumps(payload, ensure_ascii=False),
            reason=reason,
        )
        with self._conn() as con:
            con.execute(
                "INSERT INTO approvals VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (req.id, req.created_at, req.status, req.requested_by, req.tool_name, req.tool_category,
                 req.payload_json, req.reason, req.decided_by, req.decided_at, req.result_json),
            )
        return req

    def list(self, status: Optional[str] = None, limit: int = 50) -> List[ApprovalRequest]:
        q = "SELECT * FROM approvals"
        params: List[Any] = []
        if status:
            q += " WHERE status=?"
            params.append(status)
        q += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        with self._conn() as con:
            rows = con.execute(q, params).fetchall()

        return [ApprovalRequest(*row) for row in rows]

    def get(self, rid: str) -> Optional[ApprovalRequest]:
        with self._conn() as con:
            row = con.execute("SELECT * FROM approvals WHERE id=?", (rid,)).fetchone()
        return ApprovalRequest(*row) if row else None

    def update_status(self, rid: str, status: str, decided_by: str = "", result: Dict[str, Any] | None = None):
        decided_at = time.time() if decided_by else 0.0
        result_json = json.dumps(result or {}, ensure_ascii=False)
        with self._conn() as con:
            con.execute(
                "UPDATE approvals SET status=?, decided_by=?, decided_at=?, result_json=? WHERE id=?",
                (status, decided_by, decided_at, result_json, rid),
            )
