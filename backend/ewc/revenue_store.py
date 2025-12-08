from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

DEFAULT_DB_PATH = Path("corporate_operations.db")
ISO_FORMAT = "%Y-%m-%dT%H:%M:%S"


def _utcnow() -> str:
    return datetime.utcnow().strftime(ISO_FORMAT)


class RevenueCycleStore:
    """Persistence layer for autonomous revenue loop outputs."""

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
                CREATE TABLE IF NOT EXISTS revenue_cycles (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    market_context TEXT,
                    product_roadmap TEXT,
                    validated_opportunity TEXT,
                    automation_module_spec TEXT,
                    approved_module TEXT,
                    revenue_play_report TEXT
                )
                """
            )
            conn.commit()

    def record_cycle(self, market_context: Dict[str, Any], cycle: Dict[str, Any]) -> Dict[str, Any]:
        cycle_id = str(uuid.uuid4())
        payload = {
            "id": cycle_id,
            "created_at": _utcnow(),
            "market_context": json.dumps(market_context, ensure_ascii=False),
            "product_roadmap": json.dumps(cycle.get("product_roadmap", {}), ensure_ascii=False),
            "validated_opportunity": json.dumps(
                cycle.get("validated_opportunity", {}), ensure_ascii=False
            ),
            "automation_module_spec": json.dumps(
                cycle.get("automation_module_spec", {}), ensure_ascii=False
            ),
            "approved_module": json.dumps(cycle.get("approved_module", {}), ensure_ascii=False),
            "revenue_play_report": json.dumps(
                cycle.get("revenue_play_report", {}), ensure_ascii=False
            ),
        }

        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO revenue_cycles (
                    id, created_at, market_context,
                    product_roadmap, validated_opportunity,
                    automation_module_spec, approved_module,
                    revenue_play_report
                ) VALUES (:id, :created_at, :market_context,
                          :product_roadmap, :validated_opportunity,
                          :automation_module_spec, :approved_module,
                          :revenue_play_report)
                """,
                payload,
            )
            conn.commit()

        return {"cycle_id": cycle_id, **cycle}

    def list_cycles(self, limit: int = 25) -> List[Dict[str, Any]]:
        query = "SELECT * FROM revenue_cycles ORDER BY created_at DESC LIMIT ?"
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(query, (limit,))
            rows = cur.fetchall()
        results: List[Dict[str, Any]] = []
        for row in rows:
            results.append({
                "id": row["id"],
                "created_at": row["created_at"],
                "market_context": json.loads(row["market_context"] or "{}"),
                "product_roadmap": json.loads(row["product_roadmap"] or "{}"),
                "validated_opportunity": json.loads(row["validated_opportunity"] or "{}"),
                "automation_module_spec": json.loads(row["automation_module_spec"] or "{}"),
                "approved_module": json.loads(row["approved_module"] or "{}"),
                "revenue_play_report": json.loads(row["revenue_play_report"] or "{}"),
            })
        return results
