# Earnetics Asset Compounding Engine

The Asset Compounding Engine turns Earnetics away from random income chasing and toward durable wealth creation.

Core formula:

```text
Wealth = Ownership x Scale x Time
```

## What it does

The engine ranks opportunities by asset mechanics instead of personal preference.

It scores:

- Ownership
- Scalability
- Automation
- Recurring revenue
- Margin
- Speed to first cash
- Defensibility
- Reinvestment potential

The goal is to decide whether an opportunity is:

- A real asset play
- A fast validation test
- A watchlist item
- A weak labor trap that should be rejected or redesigned

## API routes

After wiring `backend.api.asset_compounding_router.router` into `REGISTERED_ROUTERS`, the backend exposes:

```http
GET /api/asset-compounding/playbook
POST /api/asset-compounding/score
POST /api/asset-compounding/rank
```

## Manual router wiring

In `backend/main_server.py`, add:

```python
from backend.api.asset_compounding_router import router as asset_compounding_router
```

Then add this inside `REGISTERED_ROUTERS`:

```python
asset_compounding_router,
```

Recommended placement is near the existing `wealth_router` and `revenue_loop_router` entries.

## Example scoring payload

```json
{
  "opportunity": {
    "name": "Lead Generation Asset Network",
    "description": "Owned niche lead sites selling verified calls and forms to service providers.",
    "asset_class": "lead_gen",
    "startup_cost": 750,
    "estimated_monthly_cashflow": 1500,
    "time_to_first_cash_days": 45,
    "owner_required_hours_per_week": 5,
    "ownership_score": 8,
    "scalability_score": 8.5,
    "automation_score": 8,
    "recurring_revenue_score": 7.5,
    "margin_score": 8.5,
    "defensibility_score": 5.5,
    "reinvestment_score": 8,
    "evidence": ["Owned digital property", "Repeatable across niches and cities"],
    "risks": ["SEO/ads volatility", "Requires reliable lead buyers"],
    "next_actions": ["Pick one urgent buyer niche", "Launch one landing page", "Sell first 10 leads manually"]
  }
}
```

## Execution principle

Earnetics should only push major energy into opportunities that can move through this ladder:

```text
Cashflow -> Systemize -> Ownership -> Compound
```

A high-paying task is not automatically good. A lower-income asset that scales, automates, and compounds can be better than a big labor-heavy job.

## How agents should use this

Any agent proposing a revenue idea should submit it to the engine before execution.

Recommended flow:

1. Signal collector finds opportunity.
2. Strategy agent turns it into a structured opportunity payload.
3. Asset Compounding Engine scores it.
4. If priority is `deploy_capital_and_agents` or `test_fast`, create execution tasks.
5. If priority is `watchlist`, monitor it.
6. If priority is `reject_or_rework`, redesign or discard it.

This keeps the system focused on wealth engines, not noise.
