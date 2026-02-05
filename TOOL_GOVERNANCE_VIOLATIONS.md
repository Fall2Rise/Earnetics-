# Tool Governance Violations — Known Issues

## ⚠️ Existing Violations (To Be Fixed)

These are **existing violations** that need to be migrated to ToolExecutor:

### 1. `autonomous/automation_worker.py`

**Lines 283, 314**: Direct Stripe API calls
```python
# ❌ VIOLATION
payments = await stripe.get_recent_payments(limit=limit)
product_result = await stripe.create_product(product_name, description, price)
```

**Fix Required:**
- Register tools: `stripe_get_recent_payments`, `stripe_create_product`
- Route through ToolExecutor in `_run_stripe_activity()`

### 2. `backend/real_ai_agents.py`

**Line 2752**: Direct scraping call
```python
# ❌ VIOLATION
scrape_result = lead_service.scrape_website(target["domain"], max_pages=15)
```

**Fix Required:**
- Register tool: `scrape_website`
- Route through ToolExecutor in agent action

---

## 🎯 Migration Plan

### Priority 1: High-Risk Tools
- Stripe operations (payments, products)
- Email sending
- Scraping operations
- System commands

### Priority 2: Medium-Risk Tools
- File writes
- Database writes
- Content publishing

### Priority 3: Low-Risk Tools
- Read-only operations (already safe)

---

## ✅ Going Forward

**ALL new code must follow the rule:**
- NO direct tool calls
- ALL tools through ToolExecutor
- ALL tools registered in bootstrap_registry.py

**Existing violations will be fixed incrementally.**
