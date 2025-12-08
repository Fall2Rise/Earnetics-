"""Tests for the autonomous automation worker."""

import asyncio
import importlib
import sqlite3

import pytest


class _StubStripe:
    enabled = False

    async def get_recent_payments(self, limit: int = 10):
        return []

    async def create_product(self, *args, **kwargs):
        return {"status": "skipped"}


class _StubEmail:
    enabled = False

    async def create_email_sequence(self, *_args, **_kwargs):
        return []

    async def send_promotional_email(self, *_args, **_kwargs):
        return {"sent": 0, "failed": 0, "errors": []}


class StubIntegrationManager:
    def __init__(self):
        self.stripe = _StubStripe()
        self.email = _StubEmail()


@pytest.fixture
def worker_environment(tmp_path, monkeypatch):
    db_path = tmp_path / "business.db"
    monkeypatch.setenv("BUSINESS_DB_PATH", str(db_path))

    corporate_memory = importlib.reload(importlib.import_module("backend.corporate_memory"))
    workflow_queue = importlib.reload(importlib.import_module("autonomous.workflow_queue"))
    automation_worker = importlib.reload(importlib.import_module("autonomous.automation_worker"))

    yield {
        "db_path": db_path,
        "corporate_memory": corporate_memory,
        "workflow_queue": workflow_queue,
        "automation_worker": automation_worker,
    }


def test_automation_worker_completes_task(worker_environment):
    async def scenario():
        corp_mod = worker_environment["corporate_memory"]
        queue_mod = worker_environment["workflow_queue"]
        worker_mod = worker_environment["automation_worker"]

        memory = corp_mod.CorporateMemory()
        queue = queue_mod.WorkflowQueueRepository()

        task_record = corp_mod.Task(title="Model revenue impact", department="finance", priority="high").to_record()
        created = memory.create_task(task_record)
        queue.enqueue_from_task(created)

        manager = StubIntegrationManager()
        worker = worker_mod.AutomationWorker(
            memory,
            queue,
            departments=["finance"],
            integration_manager=manager,
            email_agents={},
            poll_interval_seconds=0.1,
        )
        processed = await worker.process_once()

        stored_task = memory.get_task(created["id"])
        queue_entry = queue.get_item_by_task(created["id"])
        return processed, stored_task, queue_entry

    processed, stored_task, queue_entry = asyncio.run(scenario())
    assert processed is True
    assert stored_task["status"] == "completed"
    logs = stored_task["metadata"].get("automation_logs")
    assert logs and logs[-1]["status"] == "success"
    assert queue_entry["status"] == "completed"


def test_automation_worker_blocks_after_max_attempts(worker_environment):
    async def scenario():
        corp_mod = worker_environment["corporate_memory"]
        queue_mod = worker_environment["workflow_queue"]
        worker_mod = worker_environment["automation_worker"]

        memory = corp_mod.CorporateMemory()
        queue = queue_mod.WorkflowQueueRepository()

        task_record = corp_mod.Task(title="Sync affiliate payout", department="finance", priority="high").to_record()
        created = memory.create_task(task_record)
        queue.enqueue_from_task(created)

        with sqlite3.connect(worker_environment["db_path"]) as conn:
            conn.execute(
                "UPDATE autonomy_task_queue SET max_attempts = 1 WHERE task_id = ?",
                (created["id"],),
            )
            conn.commit()

        async def failing_handler(context):
            return worker_mod.TaskExecutionResult(
                success=False,
                message="integration offline",
                output={"detail": "integration offline"},
                retry_delay_minutes=0,
            )

        manager = StubIntegrationManager()
        worker = worker_mod.AutomationWorker(
            memory,
            queue,
            departments=["finance"],
            handlers={"finance": failing_handler},
            integration_manager=manager,
            email_agents={},
            poll_interval_seconds=0.1,
        )

        processed = await worker.process_once()
        stored_task = memory.get_task(created["id"])
        queue_entry = queue.get_item_by_task(created["id"])
        return processed, stored_task, queue_entry

    processed, stored_task, queue_entry = asyncio.run(scenario())
    assert processed is True
    assert stored_task["status"] == "blocked"
    logs = stored_task["metadata"].get("automation_logs")
    assert logs and any(entry.get("status") == "failed" for entry in logs)
    assert logs[-1].get("event") == "blocked"
    assert queue_entry["status"] == "failed"
    assert queue_entry["last_error"] == "integration offline"
