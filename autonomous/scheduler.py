"""Background scheduler for autonomous telemetry and workflow orchestration."""

from __future__ import annotations

import asyncio
import logging
from typing import List, Optional
from autonomous.workflow_manager import OrchestrationResult

try:
    from autonomous.workflow_queue import WorkflowQueueRepository
except ModuleNotFoundError:  # pragma: no cover - fallback for legacy paths
    try:
        from workflow_queue import WorkflowQueueRepository  # type: ignore
    except ModuleNotFoundError:  # pragma: no cover
        WorkflowQueueRepository = None  # type: ignore

logger = logging.getLogger("AutonomyScheduler")


class AutonomyScheduler:
    """Run telemetry collection and workflow orchestration on intervals."""

    def __init__(
        self,
        telemetry_collector,
        workflow_orchestrator,
        corporate_memory=None,
        queue_repository: Optional["WorkflowQueueRepository"] = None,
        *,
        telemetry_interval_seconds: int = 3600,
        workflow_interval_seconds: int = 900,
        monitor_interval_seconds: int = 600,
        telemetry_lookback_days: int = 30,
        telemetry_immediate: bool = False,
        workflow_immediate: bool = False,
        alert_callback=None,
    ) -> None:
        self.telemetry_collector = telemetry_collector
        self.workflow_orchestrator = workflow_orchestrator
        self.corporate_memory = corporate_memory
        self.queue_repository = queue_repository
        self.telemetry_interval = max(0.1, float(telemetry_interval_seconds))
        self.workflow_interval = max(0.1, float(workflow_interval_seconds))
        self.monitor_interval = max(0.1, float(monitor_interval_seconds))
        self.telemetry_lookback_days = telemetry_lookback_days
        self.telemetry_immediate = telemetry_immediate
        self.workflow_immediate = workflow_immediate
        self.alert_callback = alert_callback
        self._running = False
        self._tasks: list[asyncio.Task] = []

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._tasks = [
            asyncio.create_task(self._telemetry_loop(), name="autonomy-telemetry"),
            asyncio.create_task(self._workflow_loop(), name="autonomy-workflow"),
        ]
        if self.corporate_memory:
            self._tasks.append(
                asyncio.create_task(self._monitor_loop(), name="autonomy-monitor")
            )
        logger.info(
            "Autonomy scheduler started (telemetry_interval=%ss, workflow_interval=%ss)",
            self.telemetry_interval,
            self.workflow_interval,
        )

    async def stop(self) -> None:
        if not self._running:
            return
        self._running = False
        while self._tasks:
            task = self._tasks.pop()
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        logger.info("Autonomy scheduler stopped")

    async def _telemetry_loop(self) -> None:
        first_iteration = True
        while self._running:
            try:
                if not self.telemetry_immediate or not first_iteration:
                    await asyncio.sleep(self.telemetry_interval)
                    if not self._running:
                        break
                first_iteration = False
                snapshot = self.telemetry_collector.collect_snapshot(
                    generated_by="autonomy-scheduler",
                    lookback_days=self.telemetry_lookback_days,
                    notes="Automated telemetry snapshot",
                )
                logger.debug(
                    "Telemetry snapshot captured (id=%s)", snapshot.get("id")
                )
            except asyncio.CancelledError:
                break
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.exception("Telemetry collection failed: %s", exc)

    async def _workflow_loop(self) -> None:
        first_iteration = True
        while self._running:
            try:
                if not self.workflow_immediate or not first_iteration:
                    await asyncio.sleep(self.workflow_interval)
                    if not self._running:
                        break
                first_iteration = False
                result: OrchestrationResult = self.workflow_orchestrator.run_once()
                logger.debug(
                    "Workflow orchestration run: %s",
                    result.to_dict(),
                )
                if self.queue_repository:
                    pending = self.queue_repository.count_pending()
                    logger.debug("Pending queue items: %s", pending)
            except asyncio.CancelledError:
                break
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.exception("Workflow orchestration failed: %s", exc)

    async def _monitor_loop(self) -> None:
        while self._running:
            try:
                await asyncio.sleep(self.monitor_interval)
                if not self._running:
                    break
                alerts: List[dict] = []
                overdue = self.corporate_memory.list_overdue_tasks()
                if overdue:
                    logger.warning(
                        "Detected %s overdue tasks", len(overdue)
                    )
                    alerts.extend(
                        {"alert_type": "workflow_overdue", **task} for task in overdue
                    )

                if self.queue_repository:
                    queue_risks = self.queue_repository.list_at_risk()
                    if queue_risks:
                        logger.warning("Queue risk detected (%s items)", len(queue_risks))
                        alerts.extend(
                            {"alert_type": "queue_risk", **item} for item in queue_risks
                        )

                if alerts and self.alert_callback:
                    try:
                        self.alert_callback(list(alerts))
                    except Exception as exc:  # pragma: no cover
                        logger.exception("Alert callback failed: %s", exc)
            except asyncio.CancelledError:
                break
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.exception("Overdue task monitoring failed: %s", exc)


__all__ = ["AutonomyScheduler"]
