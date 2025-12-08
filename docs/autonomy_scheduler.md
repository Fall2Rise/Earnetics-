# Autonomy Scheduler Overview

The background scheduler keeps executive telemetry and workflow orchestration running without manual intervention.

## Components
- Telemetry loop - calls StrategicTelemetryCollector.collect_snapshot on a configurable cadence.
- Workflow loop - invokes AutonomousWorkflowOrchestrator.run_once to convert pending directives into objectives/tasks.
- Resilience - each loop logs failures and continues; cancellation is handled cleanly on shutdown.

## Configuration
Set environment variables before starting backend/main_server.py or Docker services:

| Variable | Default | Description |
| --- | --- | --- |
| AUTONOMY_SCHEDULER_ENABLED | true | Toggle background scheduler on/off. |
| AUTONOMY_TELEMETRY_INTERVAL | 3600 | Seconds between telemetry snapshots. Accepts float values. |
| AUTONOMY_WORKFLOW_INTERVAL | 900 | Seconds between workflow orchestration passes. |
| AUTONOMY_MONITOR_INTERVAL | 600 | Seconds between SLA/overdue monitoring runs. |
| AUTONOMY_TELEMETRY_LOOKBACK | 30 | Days of history included in scheduled snapshots. |
| AUTONOMY_TELEMETRY_IMMEDIATE | false | Run telemetry loop immediately on startup when true. |
| AUTONOMY_WORKFLOW_IMMEDIATE | false | Run workflow loop immediately on startup when true. |

## Operations
- Scheduler starts/stops automatically via FastAPI startup/shutdown events when enabled.
- Manual orchestration remains available via POST /autonomy/workflows/run for ad-hoc executions.
- Logs appear under the AutonomyScheduler logger; capture INFO or DEBUG level for visibility.

## Testing
- Unit coverage in tests/test_autonomy_scheduler.py verifies loop execution semantics.
- Integration tests disable the scheduler via AUTONOMY_SCHEDULER_ENABLED=0 to maintain deterministic behaviour.
- `/autonomy/alerts` endpoint surfaces current overdue tasks even if the scheduler is paused.
