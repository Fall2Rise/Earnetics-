import asyncio
import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from backend.audit_log import log_event

FACTORY_DB = os.getenv("BUSINESS_DB_PATH", "business_database.db")


STAGES = [
    "IDEATION",
    "VALIDATION",
    "SETUP",
    "ASSETS_CREATED",
    "TESTING",
    "LIVE",
    "SCALING",
    "MAINTENANCE",
]

# Minimal stage → department mapping for task hints
STAGE_OWNERS = {
    "IDEATION": ["executive", "rnd"],
    "VALIDATION": ["rnd", "revenue_ops", "executive"],
    "SETUP": ["product", "marketing"],
    "ASSETS_CREATED": ["product", "marketing"],
    "TESTING": ["marketing", "revenue_ops"],
    "LIVE": ["marketing", "finance", "executive"],
    "SCALING": ["revenue_ops", "marketing", "finance"],
    "MAINTENANCE": ["revenue_ops", "training"],
}


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class FactoryEngine:
    """Lightweight factory loop that advances revenue streams through stages."""

    def __init__(self, interval_seconds: int = 30) -> None:
        self.interval = interval_seconds
        self._task: Optional[asyncio.Task] = None
        self._running = False
        self._ensure_schema()

    # Database helpers --------------------------------------------------
    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(FACTORY_DB)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS revenue_streams (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    progress REAL NOT NULL DEFAULT 0,
                    department_owner TEXT,
                    kpi TEXT,
                    metrics TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS factory_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stream_id INTEGER NOT NULL,
                    stage TEXT NOT NULL,
                    department TEXT NOT NULL,
                    title TEXT,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at TEXT,
                    updated_at TEXT,
                    FOREIGN KEY(stream_id) REFERENCES revenue_streams(id)
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS revenue_stream_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stream_id INTEGER NOT NULL,
                    stage TEXT NOT NULL,
                    note TEXT,
                    created_at TEXT,
                    FOREIGN KEY(stream_id) REFERENCES revenue_streams(id)
                )
                """
            )
            conn.commit()

    # Public API --------------------------------------------------------
    def list_streams(self) -> List[Dict[str, Any]]:
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, name, stage, progress, department_owner, kpi, metrics, created_at, updated_at FROM revenue_streams ORDER BY updated_at DESC, id DESC"
            )
            rows = cur.fetchall()
        streams = []
        for row in rows:
            metrics = {}
            try:
                metrics = json.loads(row["metrics"] or "{}")
            except Exception:
                metrics = {}
            streams.append(
                {
                    "id": row["id"],
                    "name": row["name"],
                    "stage": row["stage"],
                    "progress": row["progress"],
                    "department_owner": row["department_owner"],
                    "kpi": row["kpi"],
                    "metrics": metrics,
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                }
            )
        return streams

    def get_stream(self, stream_id: int) -> Optional[Dict[str, Any]]:
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, name, stage, progress, department_owner, kpi, metrics, created_at, updated_at FROM revenue_streams WHERE id=?",
                (stream_id,),
            )
            row = cur.fetchone()
            if not row:
                return None
            cur.execute(
                "SELECT stage, note, created_at FROM revenue_stream_history WHERE stream_id=? ORDER BY id DESC",
                (stream_id,),
            )
            hist = [dict(r) for r in cur.fetchall()]
        metrics = {}
        try:
            metrics = json.loads(row["metrics"] or "{}")
        except Exception:
            metrics = {}
        return {
            "id": row["id"],
            "name": row["name"],
            "stage": row["stage"],
            "progress": row["progress"],
            "department_owner": row["department_owner"],
            "kpi": row["kpi"],
            "metrics": metrics,
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "history": hist,
        }

    def create_stream(self, name: str, note: str = "") -> Dict[str, Any]:
        now = utcnow()
        stage = "IDEATION"
        dept = ",".join(STAGE_OWNERS.get(stage, []))
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO revenue_streams (name, stage, progress, department_owner, kpi, metrics, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (name, stage, 0.0, dept, "not_set", "{}", now, now),
            )
            stream_id = cur.lastrowid
            cur.execute(
                "INSERT INTO revenue_stream_history (stream_id, stage, note, created_at) VALUES (?, ?, ?, ?)",
                (stream_id, stage, note or "created", now),
            )
            conn.commit()
        log_event("factory.stream.created", status="success", log_message=name, details={"stream_id": stream_id})
        return self.get_stream(stream_id)  # type: ignore

    # Loop / heartbeat --------------------------------------------------
    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        # Ensure at least one seed stream exists so the factory has work
        if not self.list_streams():
            try:
                self.create_stream("Auto Stream 1", "seeded on start")
            except Exception:
                pass
        self._task = asyncio.create_task(self._run_loop())
        log_event("factory.loop.started", status="success")

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None
        log_event("factory.loop.stopped", status="success")

    async def _run_loop(self) -> None:
        try:
            while self._running:
                await self._tick()
                await asyncio.sleep(self.interval)
        except asyncio.CancelledError:
            pass

    async def _tick(self) -> None:
        streams = self.list_streams()
        now = utcnow()
        # No auto-advance; heartbeat only
        for stream in streams:
            self._ensure_stage_tasks(stream["id"], stream["stage"], now)
            if self._all_tasks_done(stream["id"], stream["stage"]):
                try:
                    self.advance_stage(stream["id"], "tasks completed; auto-advance")
                except Exception:
                    pass
        log_event("factory.heartbeat", status="success", details={"streams": len(streams), "timestamp": now})

    def advance_stage(self, stream_id: int, note: str = "") -> Dict[str, Any]:
        """Manually advance a stream to the next stage."""
        stream = self.get_stream(stream_id)
        if not stream:
            raise ValueError("Stream not found")
        stage = stream["stage"]
        try:
            idx = STAGES.index(stage)
            next_stage = STAGES[min(idx + 1, len(STAGES) - 1)]
        except ValueError:
            next_stage = "IDEATION"
        if next_stage == stage:
            return stream
        now = utcnow()
        self._update_stream(stream_id, next_stage, 10.0, now, note or f"advance to {next_stage}")
        return self.get_stream(stream_id)

    def _update_stream(self, stream_id: int, stage: str, progress: float, now: str, note: str = "") -> None:
        dept = ",".join(STAGE_OWNERS.get(stage, []))
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE revenue_streams
                SET stage=?, progress=?, department_owner=?, updated_at=?
                WHERE id=?
                """,
                (stage, progress, dept, now, stream_id),
            )
            cur.execute(
                "INSERT INTO revenue_stream_history (stream_id, stage, note, created_at) VALUES (?, ?, ?, ?)",
                (stream_id, stage, note or f"advance to {stage}", now),
            )
            conn.commit()
        # When we enter a new stage, create tasks for that stage
        self._ensure_stage_tasks(stream_id, stage, now)

    # Task helpers ------------------------------------------------------
    def _ensure_stage_tasks(self, stream_id: int, stage: str, now: str) -> None:
        """Create stage-specific tasks if none exist. Auto-complete them to keep the loop flowing until real worker wiring."""
        departments = STAGE_OWNERS.get(stage, [])
        if not departments:
            return
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT COUNT(*) FROM factory_tasks WHERE stream_id=? AND stage=?",
                (stream_id, stage),
            )
            count = cur.fetchone()[0]
            if count:
                return
            for dept in departments:
                cur.execute(
                    """
                    INSERT INTO factory_tasks (stream_id, stage, department, title, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (stream_id, stage, dept, f"{stage} task for {dept}", "completed", now, now),
                )
            conn.commit()
            log_event(
                "factory.tasks.created",
                status="success",
                details={"stream_id": stream_id, "stage": stage, "departments": departments},
            )

    def _all_tasks_done(self, stream_id: int, stage: str) -> bool:
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT COUNT(*) FROM factory_tasks WHERE stream_id=? AND stage=? AND status!='completed'",
                (stream_id, stage),
            )
            remaining = cur.fetchone()[0]
        return remaining == 0

    def status(self) -> Dict[str, Any]:
        streams = self.list_streams()
        return {
            "running": self._running,
            "interval_seconds": self.interval,
            "streams": len(streams),
            "timestamp": utcnow(),
        }


# Singleton factory engine
FACTORY_ENGINE = FactoryEngine()
