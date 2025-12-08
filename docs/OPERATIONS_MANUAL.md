# Earnetics (Fallat_CrewAI) Operations Manual

This manual covers day-to-day operation of the Earnetics command center, automation worker, revenue plays, and safety controls.

## 1) Prerequisites
- Python 3.11+, Git, SQLite (built-in), and Ollama running locally.
- `.env` configured (copied from `.env.example`) with:
  - `FALLAT_API_TOKEN` (required)
  - Stripe live keys: `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET`
  - SMTP creds for outbound email (optional but recommended)
  - LLM: `LLM_PROVIDER=ollama`, `OLLAMA_MODEL=llama3.1`, `OLLAMA_HOST=http://localhost:11434`
- Webhook: Stripe webhook must point to `/api/stripe/webhook` with the matching secret.

## 2) Start/Stop
```powershell
cd C:\AI_Projects\Fallat_CrewAI
$env:PYTHONPATH = "C:\AI_Projects\Fallat_CrewAI"
C:\Users\Joshua\AppData\Local\Programs\Python\Python311\python.exe -m uvicorn backend.main_server:app --host 0.0.0.0 --port 8000
```
- The autonomy worker auto-starts with the server.
- To stop: `Stop-Process -Name python*`

## 3) Command Center (UI)
- URL: `http://localhost:8000`
- Save your API token in the “API Token” box at the bottom (`FALLAT_API_TOKEN`).
- Key cards/actions:
  - Operations Control: **Run Revenue Cycle** (runs the autonomous loop, enqueues follow-up tasks), **Execute Core Play** (runs a seeded wealth play and queues its steps), **Create Product** (planned for product creation).
  - Autonomy Worker: shows running/pending; Start/Stop if needed (auto-starts).
  - System status, Plugins, Permissions, Scheduler panels for oversight.

## 4) Revenue Operations
- Wealth plays: click “Execute Core Play” or call `/wealth/plays/{id}/execute`. Steps are enqueued to the autonomy worker by channel → department mapping.
- Autonomous revenue cycle: click “Run Revenue Cycle” or call `/wealth/autonomous_cycle` (uses Ollama; no OpenAI key needed). Outputs are persisted and enqueue marketing/product/ops tasks.
- Worker departments polled: finance, payments, marketing, sales, operations, product, engineering, design, dropshipping, affiliate, innovation, analytics, system, customer_success, reinvestment.

## 5) Authentication & Headers
- Protected endpoints require both headers (until unified):
  - `X-Fallat-Token: <FALLAT_API_TOKEN>`
  - `X-Api-Token: <FALLAT_API_TOKEN>`
- In the UI, saving the token sets these for calls.

## 6) LLM & Providers
- Default: Ollama (`llama3.1`) via `LLM_PROVIDER=ollama`, `OLLAMA_HOST`, `OLLAMA_MODEL`.
- CrewAI uses an OpenAI-compatible shim to point at Ollama; no OpenAI key required. If you add `OPENAI_API_KEY`, CrewAI will use it.

## 7) Stripe & Payments
- Ensure `.env` Stripe keys are set and webhook points to `/api/stripe/webhook`.
- Live mode is active if live keys are present; healthcheck will show Stripe “configured (live)”.
- Payment-related tasks are handled by the worker (departments: finance/payments).

## 8) Monitoring & Health
- Health: `http://localhost:8000/health`
- Worker status: `http://localhost:8000/autonomy/worker/status` (UI card also shows running/pending).
- System status API: `/api/system/status` (polled by UI).
- Dashboard snapshot: `/api/dashboard/snapshot`.

## 9) Safety & Approvals (current)
- Token required for all sensitive actions.
- Worker approval gates for high-risk tasks can be added via permissions/scheduler; configure `approval_required_handlers` in the scheduler if needed.

## 10) Common Issues
- “Invalid API token”: ensure both headers are set or token saved in UI.
- Port in use (8000): stop lingering python/uvicorn processes, then restart.
- Stripe not found: start server from repo root without clearing env vars; confirm `.env` is loaded.
- CrewAI validation errors: ensure Ollama is running and `.env` LLM settings are present.

## 11) Backup & Data
- SQLite files in repo root (and `backend/`) hold business, audit, vector, credential vault, workflow scheduler, wealth runs.
- Back up the `*.db` files regularly; for Docker, mount `./data` and `./logs`.

## 12) Extending
- Buttons can be further wired to specific plays or product creation flows in `command_center.html`.
- Add approvals/rollback for high-spend actions via scheduler/approval queue as needed.

Owner: Earnetics Ops
Last updated: 2025-11-24
