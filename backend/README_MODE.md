# Runtime Mode Governance System

## Overview

The Earnetics Command Center supports three runtime modes that control autonomous agent behavior:

1. **SAFE_AUTONOMY** (default): Autonomous loops run; risky tool categories require human approval
2. **COMMANDER**: Autonomous loops cannot execute tools; only manual commands can execute
3. **FULL_AUTONOMY**: Autonomous loops can execute all allowed tools within budgets/rate limits

## Quick Start

### Set Admin Token

```powershell
$env:OPS_ADMIN_TOKEN="set-a-strong-token-here"
```

### Set Default Mode (Optional)

```powershell
$env:EARNETICS_MODE="SAFE_AUTONOMY"  # or COMMANDER, FULL_AUTONOMY
```

### Get Current Mode

```powershell
Invoke-RestMethod http://127.0.0.1:8000/ops/mode
```

### Switch Mode

```powershell
Invoke-RestMethod -Method Post `
  -Headers @{ "X-Ops-Token" = $env:OPS_ADMIN_TOKEN } `
  -ContentType "application/json" `
  -Body '{"mode":"COMMANDER","reason":"mobile control session"}' `
  http://127.0.0.1:8000/ops/mode
```

### List Pending Approvals

```powershell
Invoke-RestMethod http://127.0.0.1:8000/ops/approvals
```

### Approve Request

```powershell
Invoke-RestMethod -Method Post `
  -Headers @{ "X-Ops-Token" = $env:OPS_ADMIN_TOKEN } `
  http://127.0.0.1:8000/ops/approvals/<REQUEST_ID>/approve
```

### Reject Request

```powershell
Invoke-RestMethod -Method Post `
  -Headers @{ "X-Ops-Token" = $env:OPS_ADMIN_TOKEN } `
  http://127.0.0.1:8000/ops/approvals/<REQUEST_ID>/reject
```

## API Endpoints

### GET `/ops/mode`
Get current runtime mode and metadata.

**Response:**
```json
{
  "mode": "SAFE_AUTONOMY",
  "changed_by": "system",
  "reason": ""
}
```

### POST `/ops/mode`
Set runtime mode (requires `X-Ops-Token` header).

**Request:**
```json
{
  "mode": "COMMANDER",
  "reason": "Manual control session"
}
```

**Headers:**
- `X-Ops-Token`: Admin token (from `OPS_ADMIN_TOKEN` env var)

### GET `/ops/policy`
Get current governance policy for the active mode.

**Response:**
```json
{
  "mode": "SAFE_AUTONOMY",
  "policy": {
    "allowed": ["READ_ONLY", "WRITE_LOCAL", "PUBLISH", ...],
    "approval_required": ["PUBLISH", "OUTREACH", "PAYMENTS", ...]
  }
}
```

### GET `/ops/approvals`
List approval requests.

**Query Parameters:**
- `status`: Filter by status (`pending`, `approved`, `rejected`, `executed`, `failed`)
- `limit`: Maximum number of results (default: 50)

**Response:**
```json
{
  "count": 2,
  "items": [
    {
      "id": "uuid-here",
      "created_at": 1234567890.0,
      "status": "pending",
      "requested_by": "agent_name",
      "tool_name": "publish_blog_post",
      "tool_category": "PUBLISH",
      "payload_json": "{...}",
      "reason": "Approval required in SAFE_AUTONOMY"
    }
  ]
}
```

### POST `/ops/approvals/{request_id}/approve`
Approve and execute a pending request (requires `X-Ops-Token` header).

**Response:**
```json
{
  "status": "executed",
  "request_id": "uuid-here",
  "tool": "publish_blog_post",
  "result": {...}
}
```

### POST `/ops/approvals/{request_id}/reject`
Reject a pending request (requires `X-Ops-Token` header).

**Response:**
```json
{
  "status": "rejected",
  "request_id": "uuid-here"
}
```

## Tool Categories

Tools are categorized for governance:

- **READ_ONLY**: Safe read operations (metrics, status checks)
- **WRITE_LOCAL**: File/database writes on local system
- **PUBLISH**: Posting content, publishing pages
- **OUTREACH**: Email/DM outreach
- **PAYMENTS**: Stripe operations (price changes, payouts, refunds)
- **SCRAPE**: Scraping/lead collection
- **EXEC_SYSTEM**: Running shell commands / OS automation

## Mode Policies

### SAFE_AUTONOMY (Default)
- **Allowed**: All categories
- **Approval Required**: `PUBLISH`, `OUTREACH`, `PAYMENTS`, `EXEC_SYSTEM`, `SCRAPE`
- **Behavior**: Agents run autonomously, but risky operations require approval

### COMMANDER
- **Allowed**: All categories
- **Approval Required**: All categories (for autonomous execution)
- **Behavior**: Blocks all autonomous tool execution. Only manual commands (with `autonomous=False`) can execute tools.

### FULL_AUTONOMY
- **Allowed**: All categories
- **Approval Required**: None
- **Behavior**: Agents can execute all tools without approval (still subject to budgets/rate limits)

## Integration

### Using ToolExecutor in Agent Loops

```python
from backend.core.tool_executor import ToolExecutor

# Get executor from app state
executor = app.state.tool_executor

# Execute tool (autonomous call)
result = executor.execute(
    tool_name="publish_blog_post",
    payload={"title": "My Post", "content": "..."},
    actor="content_agent",
    autonomous=True
)

# Check result
if result["status"] == "needs_approval":
    request_id = result["request_id"]
    # Wait for approval...
elif result["status"] == "executed":
    # Tool executed successfully
    pass
elif result["status"] == "blocked":
    # Tool blocked by current mode
    pass
```

### Registering Tools

```python
from backend.core.tool_executor import ToolRegistry

# Get registry from app state
registry = app.state.tool_registry

def my_tool_handler(payload: dict) -> dict:
    # Implement tool logic
    return {"result": "success"}

# Register tool
registry.register(
    name="my_tool",
    category="WRITE_LOCAL",  # or appropriate category
    handler=my_tool_handler
)
```

## Persistence

- **Mode State**: Stored in `backend/data/runtime_mode.json`
- **Approvals**: Stored in `backend/data/approvals.db` (SQLite)

## Audit Logging

All mode changes, tool executions, approvals, and rejections are logged via the audit callback. Wire this to your existing audit system:

```python
def audit_cb(event: str, data: dict):
    # Log to your audit system
    log_event(f"governance.{event}", **data)
```

## Security

- Mode changes require `OPS_ADMIN_TOKEN` environment variable
- Approval actions require `OPS_ADMIN_TOKEN` header
- All operations are audited
- Thread-safe mode management

## Troubleshooting

### "OPS_ADMIN_TOKEN not set"
Set the environment variable:
```powershell
$env:OPS_ADMIN_TOKEN="your-secure-token"
```

### "Unauthorized" when setting mode
Ensure `X-Ops-Token` header matches `OPS_ADMIN_TOKEN` environment variable.

### Tools always blocked
Check current mode:
```powershell
Invoke-RestMethod http://127.0.0.1:8000/ops/mode
```

If in `COMMANDER` mode, autonomous execution is blocked. Use manual commands or switch mode.

### Approval requests not appearing
Check approval store:
```powershell
Invoke-RestMethod "http://127.0.0.1:8000/ops/approvals?status=pending"
```

Ensure tools are registered with correct categories and mode requires approval for that category.
