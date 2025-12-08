"""Wealth execution run storage and management."""

from __future__ import annotations

import json
import logging
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class WealthRunStore:
    """SQLite-backed storage for wealth play execution runs."""

    def __init__(self, db_path: str = "wealth_runs.db") -> None:
        self.db_path = db_path
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS wealth_runs (
                    run_id TEXT PRIMARY KEY,
                    play_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    step_state TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_wealth_runs_play_id 
                ON wealth_runs(play_id)
                """
            )
            conn.commit()
            logger.debug("WealthRunStore schema initialized at %s", self.db_path)

    def create_run(self, play: Dict[str, Any]) -> Dict[str, Any]:
        run_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()
        status = "planned"
        
        steps = []
        execution_plan = play.get("execution_plan", {})
        for step in execution_plan.get("steps", []):
            steps.append({
                "key": step.get("key", ""),
                "agent": step.get("agent", ""),
                "desc": step.get("desc", ""),
                "status": "planned",
            })
        
        step_state_json = json.dumps(steps)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO wealth_runs (run_id, play_id, created_at, status, step_state)
                VALUES (?, ?, ?, ?, ?)
                """,
                (run_id, play.get("id", ""), created_at, status, step_state_json),
            )
            conn.commit()
        
        logger.info("Created run %s for play %s", run_id, play.get("id"))
        
        return {
            "run_id": run_id,
            "play_id": play.get("id", ""),
            "created_at": created_at,
            "status": status,
            "steps": steps,
        }

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT run_id, play_id, created_at, status, step_state
                FROM wealth_runs
                WHERE run_id = ?
                """,
                (run_id,),
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return {
                "run_id": row["run_id"],
                "play_id": row["play_id"],
                "created_at": row["created_at"],
                "status": row["status"],
                "steps": json.loads(row["step_state"]),
            }

    def list_runs_for_play(self, play_id: str) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT run_id, play_id, created_at, status, step_state
                FROM wealth_runs
                WHERE play_id = ?
                ORDER BY created_at DESC
                """,
                (play_id,),
            )
            rows = cursor.fetchall()
            
            runs = []
            for row in rows:
                runs.append({
                    "run_id": row["run_id"],
                    "play_id": row["play_id"],
                    "created_at": row["created_at"],
                    "status": row["status"],
                    "steps": json.loads(row["step_state"]),
                })
            
            return runs
