"""Storage layer for Revenue Strategy Cell."""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.corporate_memory import BUSINESS_DB_PATH


class StrategyStore:
    """Store and retrieve strategy runs, plays, experiments, and dispatch packets."""

    def __init__(self, db_path: Path = BUSINESS_DB_PATH):
        self.db_path = db_path
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        """Create tables if they don't exist."""
        schema_file = Path(__file__).parent / "tables.sql"
        with sqlite3.connect(self.db_path) as conn:
            with open(schema_file, "r", encoding="utf-8") as f:
                conn.executescript(f.read())
            conn.commit()

    def _connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_run(
        self,
        run_id: str,
        output_json: Dict[str, Any],
        cash_collected_to_date: float = 0.0,
        goal_cash_target: float = 150000.0,
        goal_deadline: str = "2026-01-31",
        duration_ms: Optional[int] = None,
        status: str = "completed",
        error_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new strategy run."""
        now = datetime.now(timezone.utc).isoformat()
        
        top_plays = output_json.get("top_plays", [])
        dispatch_packets = output_json.get("dispatch_packets", {})
        experiments = output_json.get("experiments", [])
        
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO strategy_runs
                (run_id, created_at, goal_cash_target, goal_deadline, cash_collected_to_date,
                 output_json, duration_ms, number_of_plays_generated, number_of_experiments_launched,
                 number_of_dispatch_packets, status, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    now,
                    goal_cash_target,
                    goal_deadline,
                    cash_collected_to_date,
                    json.dumps(output_json),
                    duration_ms,
                    len(top_plays),
                    len(experiments),
                    sum(len(tasks) for tasks in dispatch_packets.values()),
                    status,
                    error_message,
                ),
            )
            conn.commit()
        
        # Store play cards
        for play in top_plays:
            self.create_play_card(run_id, play)
        
        # Store experiments
        for exp in experiments:
            self.create_experiment(run_id, exp)
        
        # Store dispatch packets
        for dept_name, tasks in dispatch_packets.items():
            if tasks:
                self.create_dispatch_packet(run_id, dept_name, tasks)
        
        return self.get_run(run_id)

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get a strategy run by run_id."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM strategy_runs WHERE run_id = ?", (run_id,))
            row = cursor.fetchone()
        
        if not row:
            return None
        
        return dict(row)

    def list_runs(self, limit: int = 20) -> List[Dict[str, Any]]:
        """List recent strategy runs."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM strategy_runs ORDER BY created_at DESC LIMIT ?",
                (limit,),
            )
            rows = cursor.fetchall()
        
        return [dict(row) for row in rows]

    def get_latest_run(self) -> Optional[Dict[str, Any]]:
        """Get the most recent strategy run."""
        runs = self.list_runs(limit=1)
        return runs[0] if runs else None

    def create_play_card(self, run_id: str, play: Dict[str, Any]) -> None:
        """Store a play card."""
        now = datetime.now(timezone.utc).isoformat()
        
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO strategy_play_cards
                (run_id, play_id, title, target_buyer, price_points_json, ev_json, play_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    play.get("play_id"),
                    play.get("title"),
                    play.get("target_buyer"),
                    json.dumps(play.get("price_points", [])),
                    json.dumps(play.get("ev_model", {})),
                    json.dumps(play),
                    now,
                ),
            )
            conn.commit()

    def get_plays(self, run_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get play cards, optionally filtered by run_id."""
        with self._connection() as conn:
            cursor = conn.cursor()
            if run_id:
                cursor.execute(
                    "SELECT * FROM strategy_play_cards WHERE run_id = ? ORDER BY created_at DESC",
                    (run_id,),
                )
            else:
                cursor.execute(
                    "SELECT * FROM strategy_play_cards ORDER BY created_at DESC LIMIT 50"
                )
            rows = cursor.fetchall()
        
        plays = []
        for row in rows:
            play = dict(row)
            play["play_json"] = json.loads(play["play_json"])
            play["price_points_json"] = json.loads(play["price_points_json"])
            play["ev_json"] = json.loads(play["ev_json"])
            plays.append(play)
        
        return plays

    def create_experiment(self, run_id: str, experiment: Dict[str, Any]) -> None:
        """Store an experiment."""
        now = datetime.now(timezone.utc).isoformat()
        
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO strategy_experiments
                (run_id, experiment_id, linked_play_id, hypothesis, steps_json,
                 pass_metrics_json, fail_metrics_json, duration_hours, owner_department,
                 created_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    experiment.get("experiment_id"),
                    experiment.get("linked_play_id"),
                    experiment.get("hypothesis"),
                    json.dumps(experiment.get("steps", [])),
                    json.dumps(experiment.get("pass_metrics", {})),
                    json.dumps(experiment.get("fail_metrics", {})),
                    experiment.get("duration_hours", 48),
                    experiment.get("owner_department"),
                    now,
                    experiment.get("status", "pending"),
                ),
            )
            conn.commit()

    def get_experiments(self, run_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get experiments, optionally filtered by run_id."""
        with self._connection() as conn:
            cursor = conn.cursor()
            if run_id:
                cursor.execute(
                    "SELECT * FROM strategy_experiments WHERE run_id = ? ORDER BY created_at DESC",
                    (run_id,),
                )
            else:
                cursor.execute(
                    "SELECT * FROM strategy_experiments ORDER BY created_at DESC LIMIT 50"
                )
            rows = cursor.fetchall()
        
        experiments = []
        for row in rows:
            exp = dict(row)
            exp["steps_json"] = json.loads(exp["steps_json"])
            exp["pass_metrics_json"] = json.loads(exp["pass_metrics_json"])
            exp["fail_metrics_json"] = json.loads(exp["fail_metrics_json"])
            experiments.append(exp)
        
        return experiments

    def create_dispatch_packet(
        self, run_id: str, department_name: str, tasks: List[Dict[str, Any]]
    ) -> None:
        """Store a dispatch packet."""
        now = datetime.now(timezone.utc).isoformat()
        
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO dispatch_packets
                (run_id, department_name, packet_json, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (run_id, department_name, json.dumps(tasks), now),
            )
            conn.commit()

    def get_dispatch_packets(
        self, run_id: Optional[str] = None, department: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get dispatch packets, optionally filtered."""
        with self._connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM dispatch_packets WHERE 1=1"
            params = []
            
            if run_id:
                query += " AND run_id = ?"
                params.append(run_id)
            
            if department:
                query += " AND department_name = ?"
                params.append(department)
            
            query += " ORDER BY created_at DESC LIMIT 50"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
        
        packets = []
        for row in rows:
            packet = dict(row)
            packet["packet_json"] = json.loads(packet["packet_json"])
            packets.append(packet)
        
        return packets

    def update_dispatch_job_id(
        self, packet_id: int, job_id: str
    ) -> None:
        """Update dispatch packet with job ID after job creation."""
        now = datetime.now(timezone.utc).isoformat()
        
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE dispatch_packets
                SET dispatched_job_id = ?, dispatched_at = ?
                WHERE id = ?
                """,
                (job_id, now, packet_id),
            )
            conn.commit()

