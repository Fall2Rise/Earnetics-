# Department Agent Workflow

## Overview
Autonomous department agents now consume tasks through a priority-based queue that respects dependencies and SLAs. Tasks remain `pending` until their dependencies are completed; once ready, they can be claimed programmatically.

## Key Endpoints
- `GET /corporate/tasks/ready` - returns dependency-satisfied pending tasks sorted by priority and due date.
- `POST /corporate/tasks/claim` - atomically assigns the highest-priority ready task to a department agent.
- `POST /corporate/tasks/{task_id}/release` - returns an in-progress task to the queue.
- `POST /corporate/tasks/{task_id}/complete` - marks task finished and records completion timestamp.

## Priority & Dependencies
- Priorities follow `critical`, `high`, `medium`, `low` ordering.
- Dependencies are tracked as task IDs; all dependent tasks must be completed before a task becomes claimable.
- Optional `sla_minutes` allows downstream monitoring to highlight at-risk tasks.

## Usage Pattern
1. Agent checks `GET /corporate/tasks/ready?department=sales` to view actionable work.
2. Agent claims the top task via `POST /corporate/tasks/claim` with department and agent identifier.
3. If the agent cannot continue, it calls the release endpoint; otherwise, the task is completed when work finishes.

## Testing
- `tests/test_autonomous_workflow.py::test_task_dependency_claim_flow` covers dependency gating, claim, and release semantics.
- Existing corporate memory tests validate task creation and completion flows with the updated schema.
