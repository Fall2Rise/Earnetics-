"""Integration tests for the corporate memory API endpoints."""

import importlib
import os
import sqlite3
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_ROOT = PROJECT_ROOT / "backend"


@pytest.fixture(autouse=True)
def ensure_import_paths():
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    if str(BACKEND_ROOT) not in sys.path:
        sys.path.insert(0, str(BACKEND_ROOT))
    yield


def _bootstrap_business_db(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # Minimal tables required by existing initialization plus new ones
    cur.execute(
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
    cur.execute(
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
    cur.execute(
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
    cur.execute(
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
    cur.execute(
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
    conn.commit()
    conn.close()


def test_corporate_memory_cycle(tmp_path, monkeypatch):
    db_path = tmp_path / "business.db"
    _bootstrap_business_db(db_path)
    monkeypatch.setenv("BUSINESS_DB_PATH", str(db_path))
    monkeypatch.setenv("AUTONOMY_SCHEDULER_ENABLED", "0")

    import backend.corporate_memory as corporate_memory
    importlib.reload(corporate_memory)

    import backend.executive_reasoning as executive_reasoning
    importlib.reload(executive_reasoning)

    import backend.main_server as main_server
    main_server = importlib.reload(main_server)

    client = TestClient(main_server.app)

    # Create objective
    objective_payload = {
        "title": "Increase MRR",
        "owner": "Atlas",
        "priority": "high",
        "status": "planned",
        "description": "Grow monthly recurring revenue via enterprise tier",
        "success_metrics": {"target_mrr": 60000},
        "start_date": "2024-09-01",
        "due_date": "2024-10-31",
        "source_directive_id": 1,
    }
    objective_resp = client.post("/corporate/objectives", json=objective_payload)
    assert objective_resp.status_code == 200
    objective = objective_resp.json()["objective"]
    assert objective["title"] == "Increase MRR"
    assert objective["success_metrics"]["target_mrr"] == 60000

    # Create task linked to objective
    task_payload = {
        "title": "Launch enterprise outreach sequence",
        "department": "sales",
        "objective_id": objective["id"],
        "assigned_agent": "Mercury",
        "priority": "high",
        "due_date": "2024-09-15",
        "metadata": {"channels": ["LinkedIn", "Email"]},
    }
    task_resp = client.post("/corporate/tasks", json=task_payload)
    assert task_resp.status_code == 200
    task = task_resp.json()["task"]
    assert task["department"] == "sales"
    assert task["objective_id"] == objective["id"]

    # Mark task complete
    complete_resp = client.post(f"/corporate/tasks/{task['id']}/complete")
    assert complete_resp.status_code == 200

    # Store knowledge article
    article_payload = {
        "title": "Enterprise outreach playbook",
        "content": "Detailed steps for contacting enterprise leads.",
        "tags": "sales,enterprise",
        "related_objective_id": objective["id"],
    }
    article_resp = client.post("/corporate/knowledge", json=article_payload)
    assert article_resp.status_code == 200

    # Verify listing endpoints
    objectives_list = client.get("/corporate/objectives", params={"status": "planned"})
    assert objectives_list.status_code == 200
    assert len(objectives_list.json()["objectives"]) >= 1

    tasks_list = client.get("/corporate/tasks", params={"department": "sales"})
    assert tasks_list.status_code == 200
    assert tasks_list.json()["tasks"][0]["status"] == "completed"

    articles_list = client.get("/corporate/knowledge", params={"tag": "sales"})
    assert articles_list.status_code == 200
    assert any("playbook" in article["title"].lower() for article in articles_list.json()["articles"])
