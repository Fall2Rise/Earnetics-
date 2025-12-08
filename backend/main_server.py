#!/usr/bin/env python3
"""Fallat CrewAI command center server.

A refactored FastAPI application that stitches together the modular revenue
routers, secures access with optional API tokens, and serves the local command
center UI. The implementation favours clarity and maintainability over the
previous monolithic script while keeping all new marketplace and permission
modules online.
"""

from __future__ import annotations

import asyncio
import logging
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from collections import deque

from fastapi import Depends, FastAPI, File, Header, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv


class RateLimiter:
    """Lightweight token bucket limiter to protect critical endpoints."""

    def __init__(self, limit: int = 60, window_seconds: int = 60) -> None:
        self.limit = max(1, limit)
        self.window = max(1, window_seconds)
        self._events: Dict[str, deque[float]] = {}

    def allow(self, key: str) -> bool:
        now = datetime.now(timezone.utc).timestamp()
        bucket = self._events.setdefault(key, deque())
        # purge expired entries
        cutoff = now - self.window
        while bucket and bucket[0] < cutoff:
            bucket.popleft()
        if len(bucket) >= self.limit:
            return False
        bucket.append(now)
        return True


from backend import auth
from backend.logging_config import configure_logging
from backend.vector_memory import VectorMemoryError, VectorMemoryStore
from backend.api.vector_memory_router import (
    configure_memory_store,
    router as vector_memory_router,
)
from backend.api.embedding_router import router as embedding_router
from backend.credential_vault import CredentialVault, CredentialVaultError
from backend.api.credentials_router import (
    configure_credential_vault,
    router as credentials_router,
)
from backend.api.integration_registry_router import router as integration_registry_router
from backend.api.audit_router import router as audit_router
from backend.api.workflow_scheduler_router import router as workflow_scheduler_router
from backend.api.approval_router import router as approval_router
from backend.api.notification_router import router as notification_router
from backend.api.agents_router import router as agents_router
from backend.api.model_router import router as model_router
from backend.api.real_estate_router import router as real_estate_router
from backend.api.trading_router import router as trading_router
from backend.api.support_router import router as support_router
from backend.api.plugin_router import router as plugin_router
from backend.api.permission_router import router as permission_router
from backend.api.dashboard_router import router as dashboard_router
from backend.api.corporate_router import router as corporate_router
from backend.api.wealth_router import router as wealth_router
from backend.api.revenue_loop_router import router as revenue_loop_router
from backend.api.autonomy_worker_router import router as autonomy_worker_router
from backend.api.library_router import router as library_router
from backend.api.factory_router import router as factory_router
from backend.api.campaign_router import router as campaign_router
from backend.api.stripe_router import router as stripe_router
from backend.api.content_engine_router import router as content_engine_router
from backend.api.guardian_router import router as guardian_router
from backend.api.strategy_router import router as strategy_router  # ✅ NEW: strategy API

from backend.workflow_scheduler import register_handler
from backend.factory_engine import FACTORY_ENGINE
from backend.api.workflow_scheduler_router import scheduler as workflow_scheduler
from backend.ewc.wealth_runs import WealthRunStore
from backend.ewc.core_plays import CORE_PLAYS_SEED
from backend.ewc.revenue_loop import RevenueLoopRunner
from backend.ewc.revenue_store import RevenueCycleStore
from backend.corporate_memory import CorporateMemory
from autonomous.workflow_queue import WorkflowQueueRepository
from autonomous.automation_worker import AutomationWorker
from backend.corporate_memory import CorporateMemory
from backend.audit_log import log_event
from backend.branding import (
    DEFAULT_BRANDING,
    STATIC_BRANDING_DIR,
    ensure_branding_file,
    load_branding,
    reset_branding,
    update_branding,
)
from backend.corporate_memory import BUSINESS_DB_PATH
from backend.atom_master_agent import AtomPresidentAgent
from backend.services.dfy_income_engine import start_dfy_worker

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = PROJECT_ROOT / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
STATIC_BRANDING_DIR.mkdir(parents=True, exist_ok=True)

# Load environment from project root explicitly
load_dotenv(dotenv_path=PROJECT_ROOT / ".env", override=True)

API_TOKEN = os.getenv("FALLAT_API_TOKEN")
if not API_TOKEN:
    raise RuntimeError("FALLAT_API_TOKEN is required for authenticated operations")
# Temporarily disabled - allow server to start with expired Stripe key
# if not os.getenv("STRIPE_SECRET_KEY"):
#     raise RuntimeError("STRIPE_SECRET_KEY is required for payment and wealth operations")

COMMAND_CENTER_CANDIDATES = [
    PROJECT_ROOT / "command_center.html",
    PROJECT_ROOT / "backend" / "command_center.html",
    PROJECT_ROOT / "frontend" / "command_center.html",
]
for candidate in COMMAND_CENTER_CANDIDATES:
    if candidate.exists():
        COMMAND_CENTER_PATH = candidate
        break
else:
    COMMAND_CENTER_PATH = COMMAND_CENTER_CANDIDATES[0]

FUTURISTIC_STYLE = """
:root {
    --bg-primary: #020617;
    --bg-secondary: #0f172a;
    --card-bg: rgba(15, 23, 42, 0.78);
    --accent: #22d3ee;
    --accent-strong: #38bdf8;
    --text-primary: #e2e8f0;
    --text-muted: rgba(226, 232, 240, 0.72);
    --border: rgba(34, 211, 238, 0.32);
    --shadow: 0 22px 42px rgba(2, 8, 23, 0.72);
    --radius: 22px;
}

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    min-height: 100vh;
    background: radial-gradient(circle at top, rgba(34, 211, 238, 0.18), transparent 55%),
                radial-gradient(900px at 80% 10%, rgba(56, 189, 248, 0.16), transparent 70%),
                linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
    color: var(--text-primary);
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

a {
    color: var(--accent);
    text-decoration: none;
}

a:hover {
    color: var(--accent-strong);
}

main.dashboard {
    max-width: 1200px;
    margin: 0 auto;
    padding: 56px 32px 80px;
}

.card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    padding: 28px;
    backdrop-filter: blur(18px);
    margin-bottom: 28px;
}

.card h1 {
    margin: 0 0 12px;
    font-size: 2rem;
    font-weight: 700;
}

.card h2 {
    margin: 0 0 14px;
    font-size: 1.25rem;
    font-weight: 600;
}

.metric-grid {
    display: grid;
    gap: 18px;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.metric {
    background: rgba(15, 23, 42, 0.9);
    border-radius: var(--radius);
    padding: 18px;
    border: 1px solid rgba(34, 211, 238, 0.18);
}

.metric .value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--accent-strong);
}

.metric .label {
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.08rem;
    opacity: 0.7;
}

.quick-links {
    list-style: none;
    padding: 0;
    margin: 0;
}

.quick-links li {
    padding: 6px 0;
}
"""

DEFAULT_COMMAND_CENTER_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Fallat CrewAI Command Center</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
__FALLAT_STYLE__
    </style>
</head>
<body>
    <main class="dashboard">
        <section class="card">
            <h1 data-brand="headline">Fallat CrewAI Command Center</h1>
            <p data-brand="tagline">Local agentic OS operations hub</p>
            <p data-brand="message">Connect revenue departments, monitor automation, and launch workflows from a single offline-ready console.</p>
        </section>
        <section class="card">
            <h2>System Snapshot</h2>
            <div class="metric-grid" id="system-metrics">
                <div class="metric">
                    <div class="value" id="requests-today">0</div>
                    <div class="label">Requests handled</div>
                </div>
                <div class="metric">
                    <div class="value" id="uptime-hours">0h</div>
                    <div class="label">Runtime</div>
                </div>
                <div class="metric">
                    <div class="value" id="connected-modules">0</div>
                    <div class="label">Active modules</div>
                </div>
            </div>
        </section>
        <section class="card">
            <h2>Quick Links</h2>
            <ul class="quick-links">
                <li><a href="/docs">Interactive API reference</a></li>
                <li><a href="/redoc">Schema explorer</a></li>
                <li><a href="https://fallat.ai" target="_blank" rel="noopener">Knowledge base</a></li>
            </ul>
        </section>
    </main>
    <script>
    async function refreshSnapshot() {
        try {
            const response = await fetch('/api/system/status');
            if (!response.ok) return;
            const payload = await response.json();
            document.getElementById('requests-today').textContent = payload.metrics.total_requests ?? 0;
            document.getElementById('uptime-hours').textContent = payload.metrics.uptime_hours ?? '0h';
            document.getElementById('connected-modules').textContent = payload.metrics.connected_modules ?? 0;
        } catch (error) {
            console.warn('Unable to refresh system snapshot', error);
        }
    }
    refreshSnapshot();
    setInterval(refreshSnapshot, 30000);
    </script>
</body>
</html>
"""

app_state: Dict[str, Any] = {
    "startup_time": datetime.now(timezone.utc),
    "total_requests": 0,
    "vector_memory_ready": False,
    "credential_vault_ready": False,
    "last_command_center_render": None,
}

configure_logging()
logger = logging.getLogger(__name__)

stripe_processor = None
atom_agent = AtomPresidentAgent()


def _check_database_health() -> tuple[bool, str]:
    try:
        with sqlite3.connect(BUSINESS_DB_PATH) as conn:
            conn.execute("SELECT 1")
        return True, "ok"
    except Exception as exc:  # pragma: no cover - diagnostic info
        logger.warning("Database health check failed: %s", exc)
        return False, str(exc)


def _stripe_health() -> tuple[bool, str]:
    if stripe_processor and stripe_processor.stripe_config.get("configured"):
        mode = "test" if stripe_processor.stripe_config.get("test_mode") else "live"
        return True, f"configured ({mode})"
    if os.getenv("STRIPE_SECRET_KEY"):
        return False, "configured env vars but initialisation failed"
    return False, "not configured"


async def _start_autonomy_worker_on_boot() -> None:
    if os.getenv("AUTONOMY_WORKER_ENABLED", "true").lower() not in {"1", "true", "yes"}:
        logger.info("Autonomy worker disabled via AUTONOMY_WORKER_ENABLED")
        return
    try:
        worker = getattr(app.state, "autonomy_worker", None)
        if worker is None:
            factory = getattr(app.state, "autonomy_worker_factory", None)
            if not factory:
                logger.warning("Autonomy worker factory missing; skipping worker startup")
                return
            worker = factory()
            app.state.autonomy_worker = worker
        # Recover any in-progress tasks so the worker can resume safely
        try:
            worker.queue_repository.recover_in_progress_items(claimed_by=worker.worker_id)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Autonomy worker recovery failed: %s", exc)
        if not worker.is_running():
            app.state.autonomy_worker_task = asyncio.create_task(worker.start())
            logger.info("Autonomy worker %s started", worker.worker_id)
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Failed to start autonomy worker: %s", exc)


async def _stop_autonomy_worker() -> None:
    worker = getattr(app.state, "autonomy_worker", None)
    if worker and worker.is_running():
        try:
            await worker.stop()
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to stop autonomy worker cleanly: %s", exc)
    task = getattr(app.state, "autonomy_worker_task", None)
    if task:
        task.cancel()


app = FastAPI(
    title="Fallat CrewAI Command Center",
    description="Unified agentic OS for revenue generation and operations",
    version=os.getenv("FALLAT_APP_VERSION", "0.1.0"),
    default_response_class=JSONResponse,
)

raw_origins = os.getenv("FALLAT_ALLOWED_ORIGINS")
default_origins = ["http://localhost:8000", "http://127.0.0.1:8000"]
if raw_origins:
    allowed_origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
    if not allowed_origins:
        allowed_origins = default_origins
else:
    allowed_origins = default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# Factory for autonomy worker instances
def _init_autonomy_worker() -> AutomationWorker:
    worker_id = os.getenv("AUTONOMY_WORKER_ID", "autonomy-worker")
    memory = CorporateMemory()
    queue_repo = WorkflowQueueRepository()
    return AutomationWorker(
        corporate_memory=memory,
        queue_repository=queue_repo,
        worker_id=worker_id,
    )


app.state.autonomy_worker_factory = _init_autonomy_worker


# Helper: map channels to departments for queue routing
def _channel_to_department(channels: List[str] | None) -> str:
    if not channels:
        return "marketing"
    lowered = [c.lower() for c in channels]
    if any("billing" in c or "checkout" in c for c in lowered):
        return "payments"
    if any("email" in c or "social" in c or "ads" in c or "paid" in c for c in lowered):
        return "marketing"
    if any("sales" in c or "crm" in c for c in lowered):
        return "sales"
    if any("product" in c or "website" in c or "app" in c for c in lowered):
        return "product"
    if any("ops" in c or "operations" in c for c in lowered):
        return "operations"
    return "marketing"


def _enqueue_task(
    title: str,
    department: str,
    priority: str,
    description: str | None,
    metadata: Dict[str, Any],
) -> None:
    corp_mem = CorporateMemory()
    queue_repo = WorkflowQueueRepository()
    task = corp_mem.create_task(
        {
            "objective_id": None,
            "title": title,
            "department": department,
            "assigned_agent": metadata.get("agent"),
            "status": "pending",
            "priority": priority if priority in {"critical", "high", "medium", "low"} else "medium",
            "due_date": None,
            "description": description,
            "dependencies": [],
            "metadata": metadata,
        }
    )
    queue_repo.enqueue_from_task(task)


def _scheduled_revenue_cycle(payload: Dict[str, Any]) -> Dict[str, Any]:
    market_context = payload.get("market_context") or {"signal": "auto", "budget": 25}
    runner = RevenueLoopRunner()
    result = runner.run(market_context)
    store = RevenueCycleStore()
    persisted = store.record_cycle(market_context, result.__dict__)
    # enqueue follow-up tasks
    _enqueue_task(
        "Activate revenue play - marketing launch",
        "marketing",
        "high",
        "Launch campaigns from revenue play report",
        {"market_context": market_context, "cycle": persisted},
    )
    _enqueue_task(
        "Product delivery - revenue module",
        "product",
        "medium",
        "Implement automation module spec and approved module",
        {"cycle": persisted},
    )
    _enqueue_task(
        "Operations & finance checks",
        "operations",
        "medium",
        "Validate operational readiness and billing hooks",
        {"cycle": persisted},
    )
    return {"cycle": persisted}


def _scheduled_core_play(payload: Dict[str, Any]) -> Dict[str, Any]:
    play_id = payload.get("play_id")
    target_play = None
    if play_id:
        for p in CORE_PLAYS_SEED:
            if p.get("id") == play_id:
                target_play = p
                break
    if target_play is None:
        target_play = CORE_PLAYS_SEED[0]

    run_store = WealthRunStore()
    run = run_store.create_run(target_play)
    channels = target_play.get("execution_plan", {}).get("channels", [])
    department = _channel_to_department(channels if isinstance(channels, list) else [])
    priority = (target_play.get("risk_tier") or "medium").lower()
    for step in run.get("steps", []):
        _enqueue_task(
            f"Wealth: {target_play.get('name')} - {step.get('key') or 'step'}",
            department,
            priority,
            step.get("desc") or target_play.get("description"),
            {
                "play_id": target_play.get("id"),
                "run_id": run.get("run_id"),
                "step_key": step.get("key"),
                "channels": channels,
                "tags": target_play.get("tags", []),
                "agent": step.get("agent"),
            },
        )
    return {"run": run}


def _scheduled_stream_review(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Periodic review of revenue streams to decide boost/pause/kill."""
    corp_mem = CorporateMemory()
    queue_repo = WorkflowQueueRepository()
    # Pull recent tasks and products as a proxy for streams; enqueue review tasks
    stream_review = {
        "title": "Revenue stream review",
        "department": "finance",
        "priority": "high",
        "description": "Assess streams, revenue, CAC/refund; recommend boost/pause/kill.",
        "metadata": {"scope": "streams_review"},
    }
    growth_followup = {
        "title": "Growth actions from stream review",
        "department": "marketing",
        "priority": "medium",
        "description": "Execute growth actions on approved streams; pause underperformers.",
        "metadata": {"scope": "streams_review"},
    }
    ops_followup = {
        "title": "Ops adjustments from stream review",
        "department": "operations",
        "priority": "medium",
        "description": "Apply operational changes for streams flagged in review.",
        "metadata": {"scope": "streams_review"},
    }
    for task_def in (stream_review, growth_followup, ops_followup):
        task = corp_mem.create_task(
            {
                "objective_id": None,
                "title": task_def["title"],
                "department": task_def["department"],
                "assigned_agent": None,
                "status": "pending",
                "priority": task_def["priority"],
                "due_date": None,
                "description": task_def["description"],
                "dependencies": [],
                "metadata": task_def["metadata"],
            }
        )
        queue_repo.enqueue_from_task(task)
    return {"status": "scheduled"}


def _ensure_autonomy_jobs() -> None:
    """Ensure autonomous revenue jobs are scheduled."""
    # Register handlers once
    register_handler("autonomy.run_revenue_cycle", _scheduled_revenue_cycle)
    register_handler("autonomy.execute_core_play", _scheduled_core_play)
    register_handler("autonomy.review_streams", _scheduled_stream_review)

    existing = {job.id for job in workflow_scheduler.list_jobs()}

    if "autonomy.run_revenue_cycle" not in existing:
        workflow_scheduler.add_job(
            job_id="autonomy.run_revenue_cycle",
            handler="autonomy.run_revenue_cycle",
            payload={"market_context": {"signal": "auto", "budget": 25}},
            schedule_type="interval",
            schedule_value="60",  # run continuously (every 60s)
        )

    if "autonomy.execute_core_play" not in existing:
        workflow_scheduler.add_job(
            job_id="autonomy.execute_core_play",
            handler="autonomy.execute_core_play",
            payload={"play_id": None},
            schedule_type="interval",
            schedule_value="120",  # run continuously (every 120s)
        )

    if "autonomy.review_streams" not in existing:
        workflow_scheduler.add_job(
            job_id="autonomy.review_streams",
            handler="autonomy.review_streams",
            payload={},
            schedule_type="interval",
            schedule_value="300",  # review streams every 5 minutes
        )


INTEGRATION_REQUIREMENTS: Dict[str, List[str]] = {
    # Stripe is already correct
    "stripe": ["STRIPE_SECRET_KEY", "STRIPE_PUBLISHABLE_KEY"],

    # Matches your .env: SMTP_EMAIL + SMTP_PASSWORD
    "email": ["SMTP_EMAIL", "SMTP_PASSWORD"],

    # Will stay false until you actually add Twitter keys (that’s fine for now)
    "social": ["TWITTER_API_KEY", "TWITTER_API_SECRET"],

    # We’re using Ollama, not LOCALAI_ENDPOINT
    "llm": ["OLLAMA_HOST"],
}

REGISTERED_ROUTERS = [
    vector_memory_router,
    embedding_router,
    credentials_router,
    integration_registry_router,
    audit_router,
    workflow_scheduler_router,
    approval_router,
    notification_router,
    agents_router,
    model_router,
    real_estate_router,
    trading_router,
    support_router,
    plugin_router,
    permission_router,
    dashboard_router,
    corporate_router,
    wealth_router,
    revenue_loop_router,
    autonomy_worker_router,
    library_router,
    factory_router,
    campaign_router,
    stripe_router,
    content_engine_router,
    guardian_router,
    strategy_router,  # ✅ NEW: Strategic Vision / Earnetics C-Suite
]


# Initialise shared services -------------------------------------------------
try:
    vector_store = VectorMemoryStore()
    configure_memory_store(vector_store)
    app.state.vector_store = vector_store
    app_state["vector_memory_ready"] = True
    logger.info("Vector memory store initialised")
except VectorMemoryError as exc:  # pragma: no cover - defensive
    logger.exception("Unable to initialise vector memory store: %s", exc)

try:
    credential_vault = CredentialVault()
    configure_credential_vault(credential_vault)
    app.state.credential_vault = credential_vault
    app_state["credential_vault_ready"] = True
    logger.info("Credential vault ready")
except CredentialVaultError as exc:
    logger.warning("Credential vault unavailable: %s", exc)

ensure_branding_file()

if os.getenv("STRIPE_SECRET_KEY"):
    try:
        from backend.stripe_integration import StripePaymentProcessor

        stripe_processor = StripePaymentProcessor()
        configuration = stripe_processor.configure_from_environment()
        if configuration.get("success"):
            logger.info(
                "Stripe processor initialised (account=%s, test_mode=%s)",
                configuration.get("account_id"),
                configuration.get("test_mode"),
            )
        else:
            logger.warning("Stripe integration not configured: %s", configuration.get("error"))
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Unable to initialise Stripe integration: %s", exc)


# Authentication -------------------------------------------------------------
async def verify_request_token(
    request: Request,
    x_fallat_token: Optional[str] = Header(default=None, convert_underscores=False, alias="X-Fallat-Token"),
    x_api_token: Optional[str] = Header(default=None, convert_underscores=False, alias="X-Api-Token"),
) -> None:
    # Allow localhost traffic without a token to keep the Command Center usable during setup
    if request.client and request.client.host in {"127.0.0.1", "localhost", "::1"}:
        return
    token = x_fallat_token or x_api_token or request.query_params.get("token")
    # If a token is provided, enforce it; otherwise allow (especially for local UI)
    if token and not auth.verify_token(token):
        raise HTTPException(status_code=401, detail="Invalid or missing API token")


protected_dependencies: List[Depends] = []
protected_dependencies = [Depends(verify_request_token)]

# Rate limiting --------------------------------------------------------------
rate_limit_per_min = int(os.getenv("FALLAT_RATE_LIMIT_PER_MIN", "60"))
app.state.rate_limiter = RateLimiter(limit=rate_limit_per_min, window_seconds=60)

for router in REGISTERED_ROUTERS:
    app.include_router(router, dependencies=protected_dependencies)


# Lifecycle hooks -------------------------------------------------------------
@app.on_event("startup")
async def _startup_autonomy_worker() -> None:
    await _start_autonomy_worker_on_boot()
    _ensure_autonomy_jobs()
    start_dfy_worker()
    try:
        await FACTORY_ENGINE.start()
    except Exception:  # pragma: no cover
        logger.exception("Factory engine failed to start")


@app.on_event("shutdown")
async def _shutdown_autonomy_worker() -> None:
    await _stop_autonomy_worker()
    try:
        await FACTORY_ENGINE.stop()
    except Exception:
        logger.warning("Factory engine stop failed", exc_info=True)


# Middleware -----------------------------------------------------------------
@app.middleware("http")
async def track_requests(request: Request, call_next):
    app_state["total_requests"] += 1
    response = await call_next(request)
    return response


# Helpers --------------------------------------------------------------------
def _render_command_center() -> str:
    if COMMAND_CENTER_PATH.exists():
        html = COMMAND_CENTER_PATH.read_text(encoding="utf-8")
    else:
        html = DEFAULT_COMMAND_CENTER_TEMPLATE
    if "__FALLAT_STYLE__" in html:
        html = html.replace("__FALLAT_STYLE__", FUTURISTIC_STYLE)
    if "{FUTURISTIC_STYLE}" in html:
        html = html.replace("{FUTURISTIC_STYLE}", FUTURISTIC_STYLE)
    app_state["last_command_center_render"] = datetime.now(timezone.utc).isoformat()
    return html


# Routes ---------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def root_page() -> HTMLResponse:
    return HTMLResponse(content=_render_command_center())


@app.get("/command_center", response_class=HTMLResponse)
async def command_center_view() -> HTMLResponse:
    return HTMLResponse(content=_render_command_center())


@app.get("/health")
def healthcheck() -> Dict[str, Any]:
    db_ok, db_message = _check_database_health()
    stripe_ok, stripe_message = _stripe_health()
    vault_ok = app_state["credential_vault_ready"]
    vector_ok = app_state["vector_memory_ready"]
    overall = "ok" if all([db_ok, stripe_ok or not os.getenv("STRIPE_SECRET_KEY"), vault_ok, vector_ok]) else "degraded"
    return {
        "status": overall,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "database": {"ok": db_ok, "message": db_message},
            "credential_vault": {"ok": vault_ok},
            "vector_memory": {"ok": vector_ok},
            "stripe": {"ok": stripe_ok, "message": stripe_message},
        },
    }


@app.get("/atom/doctrine")
def get_atom_doctrine() -> Dict[str, Any]:
    return atom_agent.doctrine()


class AgentRequest(BaseModel):
    agent_name: str
    agent_role: str
    agent_purpose: str


class CloneRequest(BaseModel):
    base_agent: str
    new_agent: str
    directive: str


class AtomChatRequest(BaseModel):
    message: str


@app.post("/atom/generate_agent")
def create_custom_agent(req: AgentRequest):
    return atom_agent.generate_agent(req.agent_name, req.agent_role, req.agent_purpose)


@app.post("/atom/clone_agent")
def clone_agent(req: CloneRequest):
    return atom_agent.clone_agent(req.base_agent, req.new_agent, req.directive)


@app.post("/atom/chat")
async def atom_chat(req: AtomChatRequest):
    return await atom_agent.chat(req.message)


@app.post("/atom/run_planner")
def run_atom_planner() -> Dict[str, Any]:
    atom_agent.guarded_execute("strategic_cycle", {"risks": []})
    return atom_agent.run_strategic_cycle()


@app.post("/atom/evolve")
def evolve_atom() -> Dict[str, Any]:
    atom_agent.guarded_execute("doctrine_evolution", {"risks": []})
    return atom_agent.run_self_evolution()


@app.get("/api/system/status", dependencies=protected_dependencies)
def system_status() -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    uptime = now - app_state["startup_time"]
    uptime_hours = round(uptime.total_seconds() / 3600, 2)
    return {
        "status": "online",
        "timestamp": now.isoformat(),
        "metrics": {
            "uptime_hours": uptime_hours,
            "total_requests": app_state["total_requests"],
            "connected_modules": len(REGISTERED_ROUTERS),
        },
        "services": {
            "vector_memory": "ready" if app_state["vector_memory_ready"] else "unavailable",
            "credential_vault": "ready" if app_state["credential_vault_ready"] else "unavailable",
        },
    }


@app.get("/api/system/integrations", dependencies=protected_dependencies)
def integration_statuses() -> Dict[str, Any]:
    def _status(keys: List[str]) -> Dict[str, Any]:
        configured = all(os.getenv(key) for key in keys)
        missing = [key for key in keys if not os.getenv(key)]
        message = None if configured else f"Missing: {', '.join(missing)}"
        return {"configured": configured, "message": message}

    return {name: _status(keys) for name, keys in INTEGRATION_REQUIREMENTS.items()}


@app.get("/api/branding", dependencies=protected_dependencies)
def get_branding() -> Dict[str, Any]:
    return load_branding()


@app.put("/api/branding", dependencies=protected_dependencies)
def put_branding(payload: Dict[str, Any]) -> Dict[str, Any]:
    updated = update_branding(payload)
    return updated


@app.post("/api/branding/reset", dependencies=protected_dependencies)
def post_reset_branding() -> Dict[str, Any]:
    return reset_branding()


@app.post("/api/branding/logo", dependencies=protected_dependencies)
async def upload_branding_logo(file: UploadFile = File(...)) -> Dict[str, Any]:
    filename = Path(file.filename or "").name
    if not filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    target = STATIC_BRANDING_DIR / filename
    target.write_bytes(await file.read())
    branding = update_branding({"logo_url": f"/static/branding/{filename}"})
    return branding


# Metadata endpoints ---------------------------------------------------------
@app.post("/api/stripe/webhook")
async def stripe_webhook(request: Request) -> Dict[str, Any]:
    if stripe_processor is None:
        raise HTTPException(status_code=503, detail="Stripe integration not configured")

    signature = request.headers.get("Stripe-Signature")
    if not signature:
        raise HTTPException(status_code=400, detail="Missing Stripe-Signature header")

    payload = await request.body()
    try:
        event = stripe_processor.construct_event(payload, signature)
    except ValueError as exc:
        logger.warning("Stripe webhook signature invalid: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Stripe webhook parsing error: %s", exc)
        raise HTTPException(status_code=400, detail="Unable to parse webhook") from exc

    event_type = event.get("type", "unknown")
    log_event(
        "stripe.webhook",
        status="received",
        agent="stripe_webhook",
        message=event_type,
        details={"event_id": event.get("id")},
    )
    return {"status": "received"}


@app.get("/api/system/summary", dependencies=protected_dependencies)
def system_summary() -> Dict[str, Any]:
    return {
        "status": "online",
        "version": app.version,
        "startup_time": app_state["startup_time"].isoformat(),
        "last_render": app_state["last_command_center_render"],
        "modules": [router.prefix for router in REGISTERED_ROUTERS],
    }


__all__ = ["app"]

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main_server:app",
        host=os.getenv("FALLAT_HOST", "0.0.0.0"),
        port=int(os.getenv("FALLAT_PORT", os.getenv("PORT", "8000"))),
        reload=os.getenv("FALLAT_RELOAD", "false").lower() in {"1", "true", "yes"},
    )
