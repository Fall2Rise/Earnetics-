"""Tests for executive telemetry collection and directive registry endpoints."""

import importlib
import os
import sqlite3
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_ROOT = PROJECT_ROOT / "backend"


def _init_business_database(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            source TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            customer_id TEXT,
            customer_email TEXT,
            payment_method TEXT,
            status TEXT,
            created_at TEXT,
            processed_at TEXT,
            stripe_transaction_id TEXT,
            department_allocated TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE campaigns (
            id TEXT PRIMARY KEY,
            name TEXT,
            campaign_type TEXT,
            target_audience TEXT,
            budget REAL,
            spent REAL,
            status TEXT,
            impressions INTEGER,
            clicks INTEGER,
            conversions INTEGER,
            created_at TEXT,
            updated_at TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE leads (
            id TEXT PRIMARY KEY,
            name TEXT,
            email TEXT,
            phone TEXT,
            source TEXT,
            status TEXT,
            score INTEGER,
            notes TEXT,
            last_contact_date TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE sales_funnel_stages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stage_name TEXT,
            visitor_count INTEGER,
            conversion_count INTEGER,
            date_recorded TEXT,
            notes TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE customer_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT,
            metric_value REAL,
            metric_date TEXT,
            source TEXT,
            notes TEXT
        )
        """
    )

    # Seed data covering the last 60 days
    base_time = "2024-07-01T12:00:00"
    cursor.executemany(
        """
        INSERT INTO transactions (
            amount, source, category, description, customer_id,
            customer_email, payment_method, status, created_at,
            processed_at, stripe_transaction_id, department_allocated
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                497.00,
                "stripe",
                "product",
                "AI Automation Suite",
                "cust-001",
                "ceo@example.com",
                "card",
                "completed",
                base_time,
                base_time,
                "pi_123",
                "marketing",
            ),
            (
                197.00,
                "stripe",
                "product",
                "Blueprint",
                "cust-002",
                "founder@example.com",
                "card",
                "completed",
                "2024-08-01T09:15:00",
                "2024-08-01T09:16:00",
                "pi_456",
                "sales",
            ),
            (
                97.00,
                "stripe",
                "product",
                "Toolkit",
                "cust-003",
                "ops@example.com",
                "card",
                "completed",
                "2024-08-20T10:30:00",
                "2024-08-20T10:31:00",
                "pi_789",
                "sales",
            ),
        ],
    )

    cursor.executemany(
        """
        INSERT INTO campaigns (
            id, name, campaign_type, target_audience, budget, spent, status,
            impressions, clicks, conversions, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                "cmp-active",
                "LinkedIn Automation",
                "social",
                "Founders",
                1200.0,
                850.0,
                "active",
                12000,
                600,
                45,
                "2024-08-01T00:00:00",
                "2024-08-20T00:00:00",
            ),
            (
                "cmp-paused",
                "Google Ads",
                "search",
                "SMB Owners",
                2000.0,
                2000.0,
                "paused",
                18000,
                720,
                60,
                "2024-07-15T00:00:00",
                "2024-08-10T00:00:00",
            ),
        ],
    )

    cursor.executemany(
        """
        INSERT INTO leads (
            id, name, email, phone, source, status, score, notes,
            last_contact_date, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                "lead-001",
                "Jordan CEO",
                "jordan@example.com",
                "+1555000001",
                "webinar",
                "qualified",
                85,
                "Ready for proposal",
                "2024-08-15",
                "2024-08-10T14:00:00",
                "2024-08-20T09:00:00",
            ),
            (
                "lead-002",
                "Taylor Ops",
                "taylor@example.com",
                "+1555000002",
                "organic",
                "new",
                55,
                "Needs case studies",
                "2024-08-19",
                "2024-08-12T09:30:00",
                "2024-08-19T16:45:00",
            ),
        ],
    )

    cursor.executemany(
        """
        INSERT INTO sales_funnel_stages (
            stage_name, visitor_count, conversion_count, date_recorded, notes
        ) VALUES (?, ?, ?, ?, ?)
        """,
        [
            ("awareness", 5000, 500, "2024-08-01", "Top of funnel"),
            ("consideration", 1200, 180, "2024-08-01", "Middle of funnel"),
        ],
    )

    cursor.executemany(
        """
        INSERT INTO customer_analytics (
            metric_name, metric_value, metric_date, source, notes
        ) VALUES (?, ?, ?, ?, ?)
        """,
        [
            ("nps", 42.0, "2024-08-20", "survey", "Monthly survey results"),
            (
                "customer_lifetime_value",
                1297.5,
                "2024-08-20",
                "finance",
                "Rolling 90-day average",
            ),
        ],
    )

    conn.commit()
    conn.close()


@pytest.fixture(autouse=True)
def add_project_root_to_path():
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    if str(BACKEND_ROOT) not in sys.path:
        sys.path.insert(0, str(BACKEND_ROOT))
    yield
    # Cleanup not strictly necessary for test suite execution


def test_executive_endpoints(tmp_path, monkeypatch):
    db_path = tmp_path / "business.db"
    _init_business_database(db_path)
    monkeypatch.setenv("BUSINESS_DB_PATH", str(db_path))
    monkeypatch.setenv("AUTONOMY_SCHEDULER_ENABLED", "0")

    # Reload modules so they pick up the temporary database path
    er_module = importlib.import_module("backend.executive_reasoning")
    er_module = importlib.reload(er_module)
    main_server = importlib.import_module("backend.main_server")
    main_server = importlib.reload(main_server)

    client = TestClient(main_server.app)

    # Collect telemetry snapshot
    response = client.post(
        "/executive/telemetry/collect",
        json={"generated_by": "pytest", "lookback_days": 45},
    )
    assert response.status_code == 200
    snapshot_payload = response.json()["snapshot"]
    assert snapshot_payload["metrics"]["total_transactions"] == 3
    assert snapshot_payload["metrics"]["active_campaigns"] == 1

    # Retrieve latest snapshot
    latest_response = client.get("/executive/telemetry/latest")
    assert latest_response.status_code == 200
    assert latest_response.json()["id"] == snapshot_payload["id"]

    # Create directive tied to snapshot
    directive_request = {
        "title": "Expand premium funnel",
        "directive_type": "growth",
        "owner": "Akasha",
        "priority": "high",
        "payload": {
            "target_mrr": 45000,
            "experiments": ["webinar series", "partner outreach"],
        },
        "description": "Leverage recent conversion trends to expand pipeline",
        "confidence": 0.78,
        "due_date": "2024-09-30",
        "source_snapshot_id": snapshot_payload["id"],
    }
    directive_response = client.post(
        "/executive/directives",
        json=directive_request,
    )
    assert directive_response.status_code == 200
    directive_payload = directive_response.json()["directive"]
    assert directive_payload["title"] == "Expand premium funnel"
    assert directive_payload["source_snapshot_id"] == snapshot_payload["id"]

    listing_response = client.get("/executive/directives/pending")
    assert listing_response.status_code == 200
    directives = listing_response.json()["directives"]
    assert any(d["id"] == directive_payload["id"] for d in directives)
