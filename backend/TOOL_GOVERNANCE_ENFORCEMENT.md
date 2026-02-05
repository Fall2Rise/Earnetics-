# Tool Governance Enforcement — Developer Guide

## 🚨 Hard Rule: ToolExecutor is the ONLY Way

**After Phase 3, this is non-negotiable:**

```
❌ NO: Direct tool handler calls
✅ YES: ToolExecutor.execute() only
```

---

## Quick Reference

### ✅ DO THIS

```python
# Get executor
executor = app.state.tool_executor

# Execute tool
result = executor.execute(
    tool_name="my_tool",
    args={"param": "value"},
    actor="AgentName",
    autonomous=True,  # True for agents/loops, False for manual
    meta={"department": "marketing"}  # Optional
)
```

### ❌ DON'T DO THIS

```python
# ❌ NEVER import and call directly
from backend.tools.my_tools import my_tool_handler
result = my_tool_handler(args)  # ❌ FORBIDDEN

# ❌ NEVER call external APIs directly from loops/agents
import stripe
stripe.Product.create(...)  # ❌ FORBIDDEN

# ❌ NEVER bypass ToolExecutor
result = send_email(...)  # ❌ FORBIDDEN
```

---

## Where to Use ToolExecutor

### 1. Autonomy Loops
**File**: `autonomous/automation_worker.py`  
**Method**: `_execute_queue_item()`

```python
# Queue item format:
{
    "tool": "tool_name",
    "args": {...},
    "meta": {...}
}

# Execution:
executor.execute(tool_name, args, actor="AutomationWorker", autonomous=True)
```

### 2. Real AI Agents
**File**: `backend/real_ai_agents.py`  
**Method**: `_execute_actions()`

```python
# Action format:
{
    "type": "tool",
    "tool": "tool_name",
    "args": {...},
    "meta": {...}
}

# Execution:
executor.execute(tool_name, args, actor=agent.name, autonomous=True)
```

### 3. Revenue Loop
**File**: `backend/ewc/revenue_loop.py`  
**Method**: `run()`, `_run_step()`

```python
# For any external effect (payments, scraping, outreach):
executor.execute(tool_name, args, actor="RevenueLoop", autonomous=True)
```

### 4. Manual Commands
**File**: Anywhere user triggers action  
**Method**: Direct call with `autonomous=False`

```python
# Manual commands bypass approval:
executor.execute(tool_name, args, actor="joshua", autonomous=False)
```

---

## Tool Registration

**ALL tools must be registered in:**
`backend/tools/bootstrap_registry.py`

```python
from backend.tools.tool_registry import ToolSpec

def bootstrap_tools(registry: ToolRegistry):
    registry.register(
        ToolSpec(
            name="my_tool",
            category="READ_ONLY",  # or PAYMENTS, PUBLISH, etc.
            handler=my_tool_handler,
            description="What this tool does"
        )
    )
```

---

## Governance Flow

```
1. ToolRegistry.get(tool_name) → ToolSpec
2. ToolExecutor.execute() → Check mode + policy
3. If blocked → Return {"status": "blocked"}
4. If approval required → Create approval request
5. If allowed → Call handler → Return result
```

---

## Testing

### Verify Tool is Registered

```powershell
Invoke-RestMethod http://127.0.0.1:8000/ops/tools
```

### Test Tool Execution

```powershell
$body = @{
    tool_name = "healthcheck"
    args = @{}
    actor = "admin"
    autonomous = $false
} | ConvertTo-Json

Invoke-RestMethod -Method Post `
  -Headers @{"X-Ops-Token"=$env:OPS_ADMIN_TOKEN; "Content-Type"="application/json"} `
  -Body $body `
  http://127.0.0.1:8000/ops/execute
```

---

## Common Mistakes

### ❌ Mistake 1: Importing Tool Handler

```python
# ❌ WRONG
from backend.tools.stripe_tools import create_product
result = create_product(...)
```

**Fix:**
```python
# ✅ CORRECT
executor = app.state.tool_executor
result = executor.execute("stripe_create_product", {...}, actor="...", autonomous=True)
```

### ❌ Mistake 2: Direct API Calls

```python
# ❌ WRONG
import stripe
stripe.Product.create(...)
```

**Fix:**
```python
# ✅ CORRECT
executor.execute("stripe_create_product", {...}, actor="...", autonomous=True)
```

### ❌ Mistake 3: Forgetting to Register

```python
# ❌ WRONG - Tool not registered
executor.execute("my_new_tool", {...})  # Will fail: "Unknown tool"
```

**Fix:**
```python
# ✅ CORRECT - Register first
# In bootstrap_registry.py:
registry.register(ToolSpec(name="my_new_tool", category="...", handler=...))
```

---

## Enforcement Checklist

Before submitting code:

- [ ] All tool calls use `ToolExecutor.execute()`
- [ ] No direct imports of tool handlers
- [ ] No direct API calls (Stripe, Email, etc.)
- [ ] All tools registered in `bootstrap_registry.py`
- [ ] Tool categories match governance policies
- [ ] `autonomous=True` for agent/loop executions
- [ ] `autonomous=False` for manual commands

---

## Questions?

**Q: Can I call internal helper functions directly?**  
A: Yes, if they're pure computation (no external effects). Tools that interact with external systems (APIs, files, databases) must go through ToolExecutor.

**Q: What if ToolExecutor is not available?**  
A: Raise `RuntimeError("ToolExecutor not wired")`. The system should fail fast rather than silently bypass governance.

**Q: Can I create a wrapper function?**  
A: No. Wrappers that call tools directly still bypass governance. Use ToolExecutor.execute() directly.

**Q: What about legacy code?**  
A: Legacy handlers still work (backward compatible), but new code and tool-based queue items must use ToolExecutor.

---

## Remember

**The path is:**
```
ToolRegistry → ToolExecutor → Governance → Approvals → Handler
```

**No shortcuts. No exceptions. This is how you keep modes real.**
