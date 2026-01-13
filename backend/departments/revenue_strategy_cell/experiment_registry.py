"""Experiment Registry - tracks and manages experiments with WIP limits."""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.corporate_memory import BUSINESS_DB_PATH

MAX_ACTIVE_EXPERIMENTS = 2


class ExperimentRegistry:
    """Manages experiment lifecycle with WIP limits."""

    def __init__(self, db_path: Path = BUSINESS_DB_PATH):
        self.db_path = db_path
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        """Create experiment_registry table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS experiment_registry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    experiment_id TEXT UNIQUE NOT NULL,
                    play_id TEXT,
                    status TEXT NOT NULL DEFAULT 'pending',
                    attempts INTEGER NOT NULL DEFAULT 0,
                    started_at TEXT,
                    ended_at TEXT,
                    result_json TEXT,
                    decision TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def _connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_experiment(
        self,
        experiment_id: str,
        play_id: Optional[str] = None,
        status: str = "pending",
    ) -> Dict[str, Any]:
        """Create a new experiment."""
        now = datetime.now(timezone.utc).isoformat()
        
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO experiment_registry
                (experiment_id, play_id, status, attempts, created_at)
                VALUES (?, ?, ?, 0, ?)
            """, (experiment_id, play_id, status, now))
            conn.commit()
        
        return self.get_experiment(experiment_id)

    def get_experiment(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """Get an experiment by ID."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM experiment_registry WHERE experiment_id = ?",
                (experiment_id,),
            )
            row = cursor.fetchone()
        
        if not row:
            return None
        
        exp = dict(row)
        if exp.get("result_json"):
            exp["result_json"] = json.loads(exp["result_json"])
        return exp

    def list_active_experiments(self) -> List[Dict[str, Any]]:
        """List all active experiments."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM experiment_registry
                WHERE status IN ('pending', 'running')
                ORDER BY started_at DESC
            """)
            rows = cursor.fetchall()
        
        experiments = []
        for row in rows:
            exp = dict(row)
            if exp.get("result_json"):
                exp["result_json"] = json.loads(exp["result_json"])
            experiments.append(exp)
        
        return experiments

    def can_launch_experiment(self) -> bool:
        """Check if a new experiment can be launched (WIP limit)."""
        active = self.list_active_experiments()
        return len(active) < MAX_ACTIVE_EXPERIMENTS

    def update_experiment(
        self,
        experiment_id: str,
        status: Optional[str] = None,
        result: Optional[Dict[str, Any]] = None,
        decision: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update experiment status and results."""
        updates = []
        params = []
        
        if status:
            updates.append("status = ?")
            params.append(status)
            
            if status == "running" and not self.get_experiment(experiment_id).get("started_at"):
                updates.append("started_at = ?")
                params.append(datetime.now(timezone.utc).isoformat())
            
            if status in ["completed", "killed", "failed"]:
                updates.append("ended_at = ?")
                params.append(datetime.now(timezone.utc).isoformat())
        
        if result is not None:
            updates.append("result_json = ?")
            params.append(json.dumps(result))
        
        if decision:
            updates.append("decision = ?")
            params.append(decision)
        
        if status == "running":
            # Increment attempts
            updates.append("attempts = attempts + 1")
        
        if not updates:
            return self.get_experiment(experiment_id)
        
        params.append(experiment_id)
        
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE experiment_registry SET {', '.join(updates)} WHERE experiment_id = ?",
                params,
            )
            conn.commit()
        
        return self.get_experiment(experiment_id)

    def apply_decision_rules(self, experiment_id: str) -> Optional[str]:
        """Apply decision rules: PASS => SCALE, FAIL twice => KILL."""
        exp = self.get_experiment(experiment_id)
        if not exp:
            return None
        
        result = exp.get("result_json", {})
        attempts = exp.get("attempts", 0)
        
        # Check if passed
        if result.get("status") == "pass" or result.get("passed", False):
            self.update_experiment(experiment_id, decision="SCALE")
            return "SCALE"
        
        # Check if failed twice
        if attempts >= 2 and (result.get("status") == "fail" or result.get("passed", False) is False):
            self.update_experiment(experiment_id, decision="KILL", status="killed")
            return "KILL"
        
        return None

    def is_play_killed(self, play_id: str) -> bool:
        """Check if a play has been killed."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM experiment_registry
                WHERE play_id = ? AND decision = 'KILL'
            """, (play_id,))
            count = cursor.fetchone()[0]
        
        return count > 0

