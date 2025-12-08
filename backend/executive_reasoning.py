"""Executive reasoning support utilities for autonomous agents.

This module provides telemetry snapshot collection from the business
SQLite database and a directive registry for top-level AI agents. The
collector produces structured metrics that higher-level agents can feed
into reasoning prompts, while the registry persists strategic
initiatives for downstream workflow orchestration.
"""

from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

BUSINESS_DB_PATH = Path(os.getenv("BUSINESS_DB_PATH", "business_database.db"))
ISO_FORMAT = "%Y-%m-%dT%H:%M:%S"


def _utcnow() -> datetime:
    return datetime.utcnow()


class DatabaseError(RuntimeError):
    """Raised when telemetry or directive persistence fails."""


class ExecutiveDatabase:
    """Low-level database helper for executive reasoning tables."""

    def __init__(self, db_path: Path = BUSINESS_DB_PATH):
        self.db_path = db_path
        self._ensure_tables()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_tables(self) -> None:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS strategic_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    generated_by TEXT NOT NULL,
                    metrics JSON NOT NULL,
                    period_start TEXT,
                    period_end TEXT,
                    notes TEXT
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS executive_directives (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    directive_type TEXT NOT NULL,
                    owner TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    description TEXT,
                    payload JSON NOT NULL,
                    confidence REAL,
                    due_date TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    source_snapshot_id INTEGER,
                    FOREIGN KEY (source_snapshot_id) REFERENCES strategic_snapshots (id)
                )
                """
            )
            conn.commit()

    # Snapshot operations -------------------------------------------------

    def insert_snapshot(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO strategic_snapshots (
                    created_at,
                    generated_by,
                    metrics,
                    period_start,
                    period_end,
                    notes
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot["created_at"],
                    snapshot["generated_by"],
                    json.dumps(snapshot["metrics"], ensure_ascii=False),
                    snapshot.get("period_start"),
                    snapshot.get("period_end"),
                    snapshot.get("notes"),
                ),
            )
            snapshot_id = cursor.lastrowid
            conn.commit()
        snapshot["id"] = snapshot_id
        return snapshot

    def fetch_latest_snapshot(self) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, created_at, generated_by, metrics, period_start, period_end, notes
                FROM strategic_snapshots
                ORDER BY created_at DESC
                LIMIT 1
                """
            )
            row = cursor.fetchone()
            if not row:
                return None
            payload = dict(row)
            payload["metrics"] = json.loads(payload["metrics"])
            return payload

    # Directive operations ------------------------------------------------

    def insert_directive(self, directive: Dict[str, Any]) -> Dict[str, Any]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO executive_directives (
                    title,
                    directive_type,
                    owner,
                    priority,
                    status,
                    description,
                    payload,
                    confidence,
                    due_date,
                    created_at,
                    updated_at,
                    source_snapshot_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    directive["title"],
                    directive["directive_type"],
                    directive["owner"],
                    directive["priority"],
                    directive.get("status", "pending"),
                    directive.get("description"),
                    json.dumps(directive.get("payload", {}), ensure_ascii=False),
                    directive.get("confidence"),
                    directive.get("due_date"),
                    directive["created_at"],
                    directive["updated_at"],
                    directive.get("source_snapshot_id"),
                ),
            )
            directive_id = cursor.lastrowid
            conn.commit()
        directive["id"] = directive_id
        return directive

    def list_directives(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        query = "SELECT * FROM executive_directives"
        params: List[Any] = []
        if status:
            query += " WHERE status = ?"
            params.append(status)
        query += " ORDER BY created_at DESC"
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
        results: List[Dict[str, Any]] = []
        for row in rows:
            record = dict(row)
            record["payload"] = json.loads(record["payload"])
            results.append(record)
        return results

    def update_directive_status(
        self,
        directive_id: int,
        status: str,
        notes: Optional[str] = None,
    ) -> None:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE executive_directives
                SET status = ?, updated_at = ?, description = COALESCE(description, ?)
                WHERE id = ?
                """,
                (status, _utcnow().strftime(ISO_FORMAT), notes, directive_id),
            )
            conn.commit()


@dataclass
class TelemetryMetrics:
    total_transactions: int
    total_revenue: float
    revenue_last_30_days: float
    average_deal_size: float
    active_campaigns: int
    marketing_spend: float
    lead_volume: int
    qualified_leads: int
    pipeline_conversion_rate: float
    customer_metrics: Dict[str, float]
    data_sources: List[str]


class StrategicTelemetryCollector:
    """Aggregate business metrics into strategic snapshots."""

    def __init__(self, db: Optional[ExecutiveDatabase] = None):
        self.db = db or ExecutiveDatabase()

    def collect_snapshot(
        self,
        generated_by: str = "system",
        lookback_days: int = 30,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        period_end = _utcnow()
        period_start = period_end - timedelta(days=lookback_days)
        metrics = self._aggregate_metrics(period_start, period_end)
        snapshot = {
            "created_at": period_end.strftime(ISO_FORMAT),
            "generated_by": generated_by,
            "metrics": asdict(metrics),
            "period_start": period_start.strftime(ISO_FORMAT),
            "period_end": period_end.strftime(ISO_FORMAT),
            "notes": notes,
        }
        return self.db.insert_snapshot(snapshot)

    def get_latest_snapshot(self) -> Optional[Dict[str, Any]]:
        return self.db.fetch_latest_snapshot()

    # Internal helpers ----------------------------------------------------

    def _aggregate_metrics(
        self, period_start: datetime, period_end: datetime
    ) -> TelemetryMetrics:
        if not BUSINESS_DB_PATH.exists():
            raise DatabaseError(f"Business database not found at {BUSINESS_DB_PATH}")

        with sqlite3.connect(BUSINESS_DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            total_transactions = self._fetch_scalar(
                cursor, "SELECT COUNT(*) FROM transactions"
            )
            total_revenue = self._fetch_scalar(
                cursor, "SELECT IFNULL(SUM(amount), 0) FROM transactions"
            )
            last_30_revenue = self._fetch_scalar(
                cursor,
                """
                SELECT IFNULL(SUM(amount), 0)
                FROM transactions
                WHERE datetime(created_at) >= datetime(?)
                """,
                (period_start.strftime(ISO_FORMAT),),
            )
            average_deal_size = (
                total_revenue / total_transactions if total_transactions else 0.0
            )

            active_campaigns = self._fetch_scalar(
                cursor,
                "SELECT COUNT(*) FROM campaigns WHERE status IN ('active', 'running')",
            )
            marketing_spend = self._fetch_scalar(
                cursor,
                "SELECT IFNULL(SUM(spent), 0) FROM campaigns WHERE status IN ('active', 'running')",
            )

            lead_volume = self._fetch_scalar(cursor, "SELECT COUNT(*) FROM leads")
            qualified_leads = self._fetch_scalar(
                cursor,
                "SELECT COUNT(*) FROM leads WHERE status IN ('qualified', 'won')",
            )
            pipeline_conversion_rate = 0.0
            cursor.execute(
                "SELECT SUM(conversion_count) as conversions, SUM(visitor_count) as visitors FROM sales_funnel_stages"
            )
            funnel_row = cursor.fetchone()
            if funnel_row and funnel_row["visitors"]:
                pipeline_conversion_rate = (
                    funnel_row["conversions"] / funnel_row["visitors"]
                )

            customer_metrics = self._load_customer_metrics(cursor)

        data_sources = [
            "transactions",
            "campaigns",
            "leads",
            "sales_funnel_stages",
            "customer_analytics",
        ]
        return TelemetryMetrics(
            total_transactions=total_transactions,
            total_revenue=round(total_revenue, 2),
            revenue_last_30_days=round(last_30_revenue, 2),
            average_deal_size=round(average_deal_size, 2),
            active_campaigns=active_campaigns,
            marketing_spend=round(marketing_spend, 2),
            lead_volume=lead_volume,
            qualified_leads=qualified_leads,
            pipeline_conversion_rate=round(pipeline_conversion_rate, 4),
            customer_metrics=customer_metrics,
            data_sources=data_sources,
        )

    @staticmethod
    def _fetch_scalar(
        cursor: sqlite3.Cursor, query: str, params: Iterable[Any] = ()
    ) -> float:
        cursor.execute(query, params)
        row = cursor.fetchone()
        if row is None:
            return 0.0
        value = row[0]
        return float(value) if value is not None else 0.0

    @staticmethod
    def _load_customer_metrics(cursor: sqlite3.Cursor) -> Dict[str, float]:
        cursor.execute(
            """
            SELECT metric_name, metric_value
            FROM customer_analytics
            ORDER BY metric_date DESC
            LIMIT 25
            """
        )
        metrics: Dict[str, float] = {}
        for metric_name, metric_value in cursor.fetchall():
            if metric_value is None:
                continue
            metrics[metric_name] = float(metric_value)
        return metrics


@dataclass
class ExecutiveDirective:
    title: str
    directive_type: str
    owner: str
    priority: str
    payload: Dict[str, Any]
    description: Optional[str] = None
    confidence: Optional[float] = None
    due_date: Optional[str] = None
    status: str = "pending"
    source_snapshot_id: Optional[int] = None

    def to_record(self) -> Dict[str, Any]:
        now = _utcnow().strftime(ISO_FORMAT)
        record = asdict(self)
        record.update({"created_at": now, "updated_at": now})
        return record


class DirectiveRegistry:
    """Store and retrieve executive directives."""

    def __init__(self, db: Optional[ExecutiveDatabase] = None):
        self.db = db or ExecutiveDatabase()

    def register_directive(self, directive: ExecutiveDirective) -> Dict[str, Any]:
        record = directive.to_record()
        stored = self.db.insert_directive(record)
        stored["payload"] = directive.payload
        return stored

    def list_directives(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        return self.db.list_directives(status=status)

    def update_status(
        self, directive_id: int, status: str, notes: Optional[str] = None
    ) -> None:
        self.db.update_directive_status(directive_id, status, notes)


__all__ = [
    "StrategicTelemetryCollector",
    "DirectiveRegistry",
    "ExecutiveDirective",
    "DatabaseError",
]
