# 🚨 EARNETICS TOOL GOVERNANCE — HARD RULE

## ⚠️ ABSOLUTE REQUIREMENT

**After Phase 3, this is a HARD RULE with zero exceptions:**

## ❌ FORBIDDEN

### NO Direct Tool Calls from Loops
```python
# ❌ FORBIDDEN - DO NOT DO THIS
result = stripe_create_product(name, price)  # Direct call
result = send_email(to, subject, body)      # Direct call
result = publish_blog_post(title, content)   # Direct call
```

### NO Direct Tool Calls from Agents
```python
# ❌ FORBIDDEN - DO NOT DO THIS
class MyAgent(RealAIAgent):
    async def _execute_actions(self, decision):
        # ❌ FORBIDDEN
        result = stripe_create_product(...)  # Direct call
        result = send_email(...)              # Direct call
```

### NO Direct Tool Calls from Autonomy Workers
```python
# ❌ FORBIDDEN - DO NOT DO THIS
async def _execute_queue_item(self, queue_item):
    # ❌ FORBIDDEN
    result = scrape_leads(...)  # Direct call
    result = run_command(...)   # Direct call
```

---

## ✅ REQUIRED PATH

**ALL tool execution MUST follow this exact path:**

```
ToolRegistry → ToolExecutor → Governance → Approvals → Handler
```

### Step-by-Step Flow

1. **ToolRegistry**: Tool must be registered with name, category, handler
2. **ToolExecutor**: All execution goes through `executor.execute()`
3. **Governance**: Mode + policy check (allowed? approval required?)
4. **Approvals**: If required, creates approval request
5. **Handler**: Only executes if governance allows

---

## ✅ CORRECT IMPLEMENTATION

### From Autonomy Loops

```python
# ✅ CORRECT
async def _execute_queue_item(self, queue_item):
    tool_name = queue_item.get("tool")
    if tool_name:
        executor = getattr(app.state, "tool_executor", None)
        if executor is None:
            raise RuntimeError("ToolExecutor not wired")
        
        result = executor.execute(
            tool_name=tool_name,
            args=queue_item.get("args", {}),
            actor="AutomationWorker",
            autonomous=True,
            meta={"department": queue_item.get("department")}
        )
```

### From Agents

```python
# ✅ CORRECT
async def _execute_actions(self, decision):
    actions = decision.get("actions", [])
    executor = getattr(app.state, "tool_executor", None)
    
    for action in actions:
        if action.get("type") == "tool":
            result = executor.execute(
                tool_name=action.get("tool"),
                args=action.get("args", {}),
                actor=self.name,
                autonomous=True,
                meta={"agent": self.name}
            )
```

### From Manual Commands (Atom Direct Line)

```python
# ✅ CORRECT (manual = autonomous=False)
executor = app.state.tool_executor
result = executor.execute(
    tool_name="publish_blog_post",
    args={"title": "My Post"},
    actor="joshua",
    autonomous=False  # Manual commands bypass approval
)
```

---

## 🔒 ENFORCEMENT

### Code Review Checklist

Before merging any code that executes tools:

- [ ] ✅ Uses `ToolExecutor.execute()` (not direct handler calls)
- [ ] ✅ Tool is registered in `backend/tools/bootstrap_registry.py`
- [ ] ✅ Tool has correct category matching governance policies
- [ ] ✅ `autonomous=True` for agent/loop executions
- [ ] ✅ `autonomous=False` for manual commands
- [ ] ✅ No direct imports of tool handler functions
- [ ] ✅ No direct calls to Stripe/Email/Scraping/etc. APIs from loops/agents

### Automated Checks (Future)

Consider adding:
- Linter rule: detect direct tool handler calls
- Pre-commit hook: scan for forbidden patterns
- Runtime guard: log warnings if tools called outside ToolExecutor

---

## 📋 TOOL REGISTRATION REQUIREMENT

**Before any tool can be executed, it MUST be registered:**

```python
# backend/tools/bootstrap_registry.py
from backend.tools.tool_registry import ToolSpec

def bootstrap_tools(registry: ToolRegistry):
    # ✅ Register ALL tools here
    registry.register(
        ToolSpec(
            name="stripe_create_product",
            category="PAYMENTS",  # Must match governance categories
            handler=stripe_create_product_handler,
            description="Create a Stripe product"
        )
    )
```

**Categories must match:**
- `READ_ONLY`
- `WRITE_LOCAL`
- `PUBLISH`
- `OUTREACH`
- `PAYMENTS`
- `SCRAPE`
- `EXEC_SYSTEM`

---

## 🎯 WHY THIS MATTERS

### Without ToolExecutor:
- ❌ No governance enforcement
- ❌ No approval system
- ❌ No mode-based blocking
- ❌ No audit trail
- ❌ Rogue behavior possible

### With ToolExecutor:
- ✅ All tools go through governance
- ✅ Approval system works
- ✅ Mode-based blocking enforced
- ✅ Complete audit trail
- ✅ Rogue behavior prevented

---

## 🚨 VIOLATION CONSEQUENCES

**If code violates this rule:**

1. **Code Review**: Reject PR
2. **Production**: Tools won't work (ToolExecutor not called)
3. **Security**: Bypass governance = security risk
4. **Compliance**: No audit trail = compliance violation

---

## 📝 EXAMPLES OF VIOLATIONS

### ❌ Violation 1: Direct Import and Call

```python
# ❌ VIOLATION
from backend.tools.stripe_tools import stripe_create_product

async def my_loop():
    result = stripe_create_product(...)  # ❌ Direct call
```

**Fix:**
```python
# ✅ CORRECT
executor = app.state.tool_executor
result = executor.execute(
    tool_name="stripe_create_product",
    args={...},
    actor="MyLoop",
    autonomous=True
)
```

### ❌ Violation 2: Agent Direct Call

```python
# ❌ VIOLATION
class MyAgent(RealAIAgent):
    async def _execute_actions(self, decision):
        from backend.tools.email_tools import send_email
        send_email(...)  # ❌ Direct call
```

**Fix:**
```python
# ✅ CORRECT
class MyAgent(RealAIAgent):
    async def _execute_actions(self, decision):
        actions = [{"type": "tool", "tool": "send_email", "args": {...}}]
        # Let base class route through ToolExecutor
        return await super()._execute_actions({"actions": actions})
```

### ❌ Violation 3: Loop Direct Call

```python
# ❌ VIOLATION
async def revenue_loop():
    import stripe
    stripe.Product.create(...)  # ❌ Direct API call
```

**Fix:**
```python
# ✅ CORRECT
async def revenue_loop():
    executor = app.state.tool_executor
    result = executor.execute(
        tool_name="stripe_create_product",
        args={...},
        actor="RevenueLoop",
        autonomous=True
    )
```

---

## ✅ VERIFICATION

### Check if ToolExecutor is Being Used

```python
# Search codebase for direct tool calls
grep -r "stripe_create_product\|send_email\|publish_blog" --exclude-dir=venv
# Should only find:
# - Tool handler definitions
# - Tool registration in bootstrap_registry.py
# - ToolExecutor.execute() calls
```

### Runtime Verification

All tool executions should log:
- `tool_executing` event
- `tool_executed` event (or `tool_blocked`, `approval_requested`)

Check audit logs to verify all tools go through ToolExecutor.

---

## 🎯 SUMMARY

**THE RULE:**
```
NO loop calls tools directly
NO agent calls tools directly
Everything goes through:
ToolRegistry → ToolExecutor → Governance → Approvals → Handler
```

**THE PATH:**
1. Register tool in `bootstrap_registry.py`
2. Call `executor.execute(tool_name, args, actor, autonomous)`
3. Governance checks mode + policy
4. Approval created if required
5. Handler executes if allowed

**THE ENFORCEMENT:**
- Code review required
- No exceptions
- Violations = security risk

**This is how you stop rogue behavior and keep modes real.**
