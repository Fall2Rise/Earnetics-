"""Unit tests for the background autonomy scheduler."""

import asyncio

import pytest

from autonomous.scheduler import AutonomyScheduler
from autonomous.workflow_manager import OrchestrationResult


class StubTelemetryCollector:
    def __init__(self):
        self.count = 0

    def collect_snapshot(self, *, generated_by: str, lookback_days: int, notes: str):
        self.count += 1
        return {"id": self.count, "generated_by": generated_by}

class StubCorporateMemory:
    def __init__(self):
        self.called = 0

    def list_overdue_tasks(self):
        self.called += 1
        return []


class StubQueueRepository:
    def __init__(self):
        self.pending_calls = 0
        self.risk_calls = 0

    def count_pending(self):
        self.pending_calls += 1
        return 1

    def list_at_risk(self):
        self.risk_calls += 1
        if self.risk_calls == 1:
            return [
                {
                    "id": 1,
                    "task_id": 99,
                    "department": "sales",
                    "priority": "high",
                    "status": "in_progress",
                    "sla_minutes": 1,
                }
            ]
        return []




class StubWorkflowOrchestrator:
    def __init__(self):
        self.count = 0

    def run_once(self) -> OrchestrationResult:
        self.count += 1
        return OrchestrationResult(
            processed_directives=0,
            objectives_created=0,
            tasks_created=0,
            skipped=0,
        )


@pytest.mark.asyncio
async def test_scheduler_runs_periodic_loops():
    telemetry = StubTelemetryCollector()
    workflow = StubWorkflowOrchestrator()
    memory = StubCorporateMemory()
    queue = StubQueueRepository()
    alerts: list[dict] = []
    scheduler = AutonomyScheduler(
        telemetry,
        workflow,
        corporate_memory=memory,
        queue_repository=queue,
        telemetry_interval_seconds=0,
        workflow_interval_seconds=0,
        monitor_interval_seconds=0,
        telemetry_immediate=True,
        workflow_immediate=True,
        alert_callback=alerts.extend,
    )

    await scheduler.start()
    await asyncio.sleep(0.2)
    await scheduler.stop()

    assert telemetry.count >= 1
    assert workflow.count >= 1
    assert memory.called >= 1
    assert queue.pending_calls >= 1
    assert queue.risk_calls >= 1
    assert alerts
    assert alerts[0]["alert_type"] == "queue_risk"
