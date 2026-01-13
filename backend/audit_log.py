"""Audit logging utilities for governance and compliance.

This module emits structured events via the main logging pipeline and also
persists them to a lightweight SQLite database for later review.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

_AUDIT_LOGGER_NAME = "audit"
_audit_logger = logging.getLogger(_AUDIT_LOGGER_NAME)

ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
def _normalize_env_path(env_value: Optional[str], default: str) -> Path:
    """Normalize path from environment variable, converting backslashes to forward slashes."""
    if not env_value:
        return Path(default)
    return Path(env_value.replace("\\", "/"))

DEFAULT_DB_PATH = _normalize_env_path(os.getenv("AUDIT_LOG_DB"), "audit_log.db")


def _utcnow() -> str:
    return datetime.utcnow().strftime(ISO_FORMAT)


@dataclass
class AuditRecord:
    timestamp: str
    action: str
    status: str
    agent: Optional[str] = None
    user: Optional[str] = None
    message: Optional[str] = None
    details: Dict[str, Any] = None


class AuditLogStore:
    def __init__(self, db_path: Path = DEFAULT_DB_PATH) -> None:
        self.db_path = db_path
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
                CREATE TABLE IF NOT EXISTS audit_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    action TEXT NOT NULL,
                    status TEXT NOT NULL,
                    agent TEXT,
                    user TEXT,
                    message TEXT,
                    details TEXT
                )
                """
            )
            # Backfill missing columns for existing installs
            cur.execute("PRAGMA table_info(audit_events)")
            cols = {row[1] for row in cur.fetchall()}
            if "status" not in cols:
                cur.execute("ALTER TABLE audit_events ADD COLUMN status TEXT")
            if "agent" not in cols:
                cur.execute("ALTER TABLE audit_events ADD COLUMN agent TEXT")
            if "user" not in cols:
                cur.execute("ALTER TABLE audit_events ADD COLUMN user TEXT")
            if "message" not in cols:
                cur.execute("ALTER TABLE audit_events ADD COLUMN message TEXT")
            if "details" not in cols:
                cur.execute("ALTER TABLE audit_events ADD COLUMN details TEXT")
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_events(action)"
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_events(timestamp DESC)"
            )
            conn.commit()

    def record(self, record: AuditRecord) -> None:
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO audit_events (timestamp, action, status, agent, user, message, details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.timestamp,
                    record.action,
                    record.status,
                    record.agent,
                    record.user,
                    record.message,
                    json.dumps(record.details or {}),
                ),
            )
            conn.commit()

    def query(
        self,
        *,
        limit: int = 100,
        status: Optional[str] = None,
        action: Optional[str] = None,
        agent: Optional[str] = None,
        user: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        clauses: List[str] = []
        params: List[Any] = []
        if status:
            clauses.append("status = ?")
            params.append(status)
        if action:
            clauses.append("action = ?")
            params.append(action)
        if agent:
            clauses.append("agent = ?")
            params.append(agent)
        if user:
            clauses.append("user = ?")
            params.append(user)
        where = ""
        if clauses:
            where = "WHERE " + " AND ".join(clauses)
        query = f"""
            SELECT id, timestamp, action, status, agent, user, message, details
            FROM audit_events
            {where}
            ORDER BY timestamp DESC
            LIMIT ?
        """
        params.append(limit)
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            rows = cur.fetchall()
        results: List[Dict[str, Any]] = []
        for row in rows:
            entry = dict(row)
            details_raw = entry.get("details")
            entry["details"] = json.loads(details_raw) if details_raw else {}
            results.append(entry)
        return results



_store = AuditLogStore()
_broadcast_callback = None


def set_broadcast_callback(callback):
    global _broadcast_callback
    _broadcast_callback = callback



def log_event(
    action: str,
    *,
    agent: Optional[str] = None,
    user: Optional[str] = None,
    status: str = "success",
    message: Optional[str] = None,
    **extra: Any,
) -> None:
    # Learn from this action via Evolution Engine (non-blocking)
    # Moved to background to prevent blocking the audit log
    try:
        import threading
        from backend.atom_evolution_engine import AtomEvolutionEngine
        
        def _learn_async():
            """Background learning to avoid blocking audit log"""
            try:
                evolution_engine = getattr(log_event, "_evolution_engine", None)
                if evolution_engine is None:
                    evolution_engine = AtomEvolutionEngine()
                    log_event._evolution_engine = evolution_engine
                
                if agent:  # Only learn from agent actions
                    feedback = evolution_engine.learn_from_action(
                        agent=agent,
                        action=action,
                        context=message or "",
                        status=status,
                        details=extra
                    )
                    if feedback and _broadcast_callback:
                        # Broadcast evolution feedback
                        try:
                            _broadcast_callback({
                                "type": "evolution_feedback",
                                "payload": feedback
                            })
                        except Exception:
                            pass  # Don't fail if broadcast fails
            except Exception as e:
                # Don't fail if evolution learning fails
                import logging
                logging.getLogger(__name__).debug(f"Evolution learning failed: {e}")
        
        # Run learning in background thread to avoid blocking
        if agent:  # Only spawn thread for agent actions
            thread = threading.Thread(target=_learn_async, daemon=True)
            thread.start()
    except Exception as e:
        # Don't fail if evolution learning setup fails
        import logging
        logging.getLogger(__name__).debug(f"Evolution learning setup failed: {e}")
    payload: Dict[str, Any] = {
        "action": action,
        "status": status,
    }
    if agent:
        payload["agent"] = agent
    if user:
        payload["user"] = user
    if message:
        payload["log_message"] = message
    if extra:
        payload["details"] = extra

    # Avoid passing arbitrary kwargs to logger; use extra for payload
    _audit_logger.info("audit_event", extra=payload)

    record = AuditRecord(
        timestamp=_utcnow(),
        action=action,
        status=status,
        agent=agent,
        user=user,
        message=message,
        details=extra or {},
    )
    try:
        _store.record(record)
        if _broadcast_callback:
            try:
                _broadcast_callback({
                    "type": "AUDIT_LOG",
                    "payload": asdict(record)
                })
            except Exception:
                pass
    except Exception as exc:  # pragma: no cover - defensive
        _audit_logger.error("audit_store_error", extra={"error": str(exc), "action": action})


def list_events(
    *,
    limit: int = 100,
    status: Optional[str] = None,
    action: Optional[str] = None,
    agent: Optional[str] = None,
    user: Optional[str] = None,
) -> List[Dict[str, Any]]:
    return _store.query(
        limit=limit,
        status=status,
        action=action,
        agent=agent,
        user=user,
    )


def get_event(event_id: int) -> Optional[Dict[str, Any]]:
    with _store._connection() as conn:  # type: ignore[attr-defined]  # internal access
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, timestamp, action, status, agent, user, message, details
            FROM audit_events
            WHERE id = ?
            """,
            (event_id,),
        )
        row = cur.fetchone()
    if not row:
        return None
    entry = dict(row)
    details_raw = entry.get("details")
    entry["details"] = json.loads(details_raw) if details_raw else {}
    return entry


__all__ = ["log_event", "list_events", "get_event", "AuditLogStore", "AuditRecord"]
