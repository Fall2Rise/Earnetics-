from __future__ import annotations

import importlib
import json
import sqlite3
from datetime import datetime
from pathlib import Path

import pytest


@pytest.fixture()
def seeded_dashboard_db(tmp_path, monkeypatch):
    db_path = tmp_path / "dashboard.db"
    monkeypatch.setenv("BUSINESS_DB_PATH", str(db_path))

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            source TEXT,
            category TEXT,
            status TEXT,
            created_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            status TEXT,
            revenue_generated REAL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            status TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE customer_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT,
            metric_value REAL,
            metric_date TEXT,
            source TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE department_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            department TEXT,
            status TEXT,
            updated_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE autonomy_task_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE executive_directives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            directive_type TEXT,
            payload TEXT,
            due_date TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE department_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT,
            metric_value REAL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE data_collections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_type TEXT,
            data_source TEXT,
            collected_at TEXT
        )
        """
    )

    now = datetime.utcnow().isoformat()
    cur.execute(
        "INSERT INTO transactions (amount, source, category, status, created_at) VALUES (?, ?, ?, ?, ?)",
        (497.0, "AI Course", "digital", "completed", now),
    )

    cur.execute(
        "INSERT INTO products (name, status, revenue_generated) VALUES (?, ?, ?)",
        ("Automation Suite", "active", 15230.0),
    )
    cur.execute("INSERT INTO campaigns (name, status) VALUES (?, ?)", ("Launch Campaign", "running"))
    cur.execute(
        "INSERT INTO customer_analytics (metric_name, metric_value, metric_date, source) VALUES (?, ?, ?, ?)",
        ("Monthly Leads", 125, now[:10], "analytics-engine"),
    )
    cur.execute(
        "INSERT INTO department_tasks (title, department, status, updated_at) VALUES (?, ?, ?, ?)",
        ("Deploy marketing automation", "marketing", "completed", now),
    )
    cur.execute("INSERT INTO autonomy_task_queue (status) VALUES (?)", ("pending",))
    cur.execute(
        "INSERT INTO executive_directives (title, directive_type, payload, due_date, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
        (
            "Scale content pipeline",
            "growth",
            json.dumps({"projected_monthly_revenue": 15000}),
            now[:10],
            now,
            now,
        ),
    )
    cur.execute(
        "INSERT INTO department_performance (metric_name, metric_value) VALUES (?, ?)",
        ("pipeline_value", 42000),
    )
    cur.execute(
        "INSERT INTO data_collections (data_type, data_source, collected_at) VALUES (?, ?, ?)",
        ("keyword_scan", "market-intel", now),
    )

    conn.commit()
    conn.close()

    import backend.corporate_memory as corporate_memory

    importlib.reload(corporate_memory)
    import backend.api.dashboard_router as dashboard_router

    importlib.reload(dashboard_router)
    return dashboard_router


def test_dashboard_snapshot_returns_live_data(seeded_dashboard_db):
    snapshot = seeded_dashboard_db.get_dashboard_snapshot()

    assert snapshot["revenue"]["total"] >= 497.0
    assert snapshot["operations"]["active_streams"] == 1
    assert snapshot["analytics"]["headline"] == "Monthly Leads"
    assert snapshot["tasks"]["queued"] == 1
    assert snapshot["market"]["projected_monthly"] >= 15000
    assert len(snapshot["departments"]) >= 1
    assert snapshot["activity"], "Expected recent activity entries"
