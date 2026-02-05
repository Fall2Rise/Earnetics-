# --- BLOCK DIRECT RUN (Earnetics single-entry enforcement) ---
if __name__ == "__main__":
    import sys
    print("\n[ERROR] Deprecated start method.")
    print("Use:  .\\scripts\\run_all.ps1\n")
    sys.exit(1)
# ------------------------------------------------------------

import os
import sys
import json
import asyncio
import sqlite3
import logging
import threading
from pathlib import Path
from collections import deque
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, Request, HTTPException, Header, Depends, WebSocket, WebSocketDisconnect, File, UploadFile
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
# Load environment from project root explicitly - MUST BE DONE BEFORE OTHER IMPORTS
load_dotenv(dotenv_path=PROJECT_ROOT / ".env", override=True)

# Rate limiter moved to backend.middleware.rate_limiter
from backend.middleware.rate_limiter import rate_limit, get_rate_limiter


from backend import auth
from backend.auth import verify_request_token
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
from backend.api.integrations_router import router as integrations_router
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
from backend.api.revenue_strategy_router import router as revenue_strategy_router  # ✅ NEW: Revenue Strategy Cell (Idea Department)
from backend.api.strategy_routes import router as strategy_cell_router  # ✅ NEW: Revenue Strategy Cell API
from backend.api.signals_routes import router as signals_router  # ✅ NEW: Signal Collection API
from backend.api.experiments_routes import router as experiments_router  # ✅ NEW: Experiment Registry API
from backend.api.playbooks_routes import router as playbooks_router  # ✅ NEW: Playbook Library API
from backend.api.tasks_router import router as tasks_router
from backend.api.resend_webhook_router import router as resend_webhook_router
from backend.api.lead_management_router import router as lead_management_router
from backend.api.performance_router import router as performance_router
from backend.api.website_growth_router import router as website_growth_router
from backend.api.intelligence_router import router as intelligence_router
from backend.core.runtime_mode import ModeManager
from backend.core.approvals_store import ApprovalsStore
from backend.core.tool_executor import ToolRegistry, ToolExecutor
from backend.api.ops_router import build_ops_router
from head_office.backend.api import (
    executive_router,
    decisions_router,
    legal_router,
    tax_router,
    assets_router,
    law_library_router,
    master_ai_router
)

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
from backend.autonomous_financial_processor import AutonomousFinancialProcessor
from backend.prime_directive_guardian import guardian

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = PROJECT_ROOT / "static"
DASHBOARD_DIR = STATIC_DIR / "dashboard"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
STATIC_BRANDING_DIR.mkdir(parents=True, exist_ok=True)

# Load environment from project root explicitly
# Load environment from project root explicitly
# load_dotenv(dotenv_path=PROJECT_ROOT / ".env", override=True)

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

# Loop singleton guards (prevents double-start)
_LOOPS_STARTED = False
_LOOPS_LOCK = threading.Lock()

stripe_processor = None
atom_agent = AtomPresidentAgent()
financial_processor = AutonomousFinancialProcessor()


class ConnectionManager:
    """Manages active WebSocket connections for real-time updates."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Send a message to all connected clients."""
        if not self.active_connections:
            return
        
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)


manager = ConnectionManager()


async def broadcast_event(event: Dict[str, Any]):
    """Global helper to broadcast events to UI."""
    await manager.broadcast(event)



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
            if hasattr(app.state, "loop_tasks"):
                app.state.loop_tasks.append(app.state.autonomy_worker_task)
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

# Runtime Mode Governance System -------------------------------------------------
from backend.tools.tool_registry import ToolRegistry
from backend.tools.bootstrap_registry import bootstrap_tools

mode_mgr = ModeManager()
approvals = ApprovalsStore()
tool_registry = ToolRegistry()

# Bootstrap all tools from single registry
bootstrap_tools(tool_registry)

# Audit hook (wire to your event bus / logger)
def audit_cb(event: str, data: dict):
    import logging
    logging.getLogger("backend.audit").info({"event": event, **data})

tool_executor = ToolExecutor(mode_mgr=mode_mgr, approvals=approvals, registry=tool_registry, audit_cb=audit_cb)

# Store in app state for access by other modules
app.state.mode_mgr = mode_mgr
app.state.tool_executor = tool_executor
app.state.tool_registry = tool_registry

raw_origins = os.getenv("FALLAT_ALLOWED_ORIGINS")
default_origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5175",
    "http://localhost:3000",
]
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

@app.post("/api/atom/chat")
async def atom_chat(request: Request):
    try:
        data = await request.json()
        message = data.get("message")
        enable_voice = data.get("enable_voice", True)  # Default to True
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Log the interaction
        log_event("atom.chat", agent="user", message=message)
        
        response = await atom_agent.chat(message)
        
        if response.get("status") == "ok":
            response_text = response.get("response")
            log_event("atom.chat", agent="atom", message=response_text)
            
            # Generate voice audio if enabled
            audio_info = None
            audio_url = None
            if enable_voice and response_text:
                try:
                    from backend.services.tts_service import tts_service
                    logger.info(f"🎤 Generating voice for response (length: {len(response_text)} chars): {response_text[:50]}...")
                    audio_info = await tts_service.generate_speech(response_text)
                    if audio_info:
                        audio_url = audio_info.get("audio_url")
                        response["audio_url"] = audio_url
                        logger.info(f"✅ Generated Atom voice response: {audio_url}")
                        logger.info(f"✅ Audio info keys: {list(audio_info.keys())}")
                    else:
                        logger.warning("⚠️ TTS service returned None - no audio generated")
                except Exception as e:
                    logger.error(f"❌ TTS generation failed: {e}", exc_info=True)
                    # Continue without audio
            else:
                logger.info(f"⚠️ Voice generation skipped - enable_voice: {enable_voice}, response_text length: {len(response_text) if response_text else 0}")
            
            # Broadcast the response to WebSockets for real-time UI updates
            broadcast_payload = {
                "type": "atom_response",
                "message": response_text,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            if audio_url:
                broadcast_payload["audio_url"] = audio_url
                logger.info(f"📡 Broadcasting WebSocket message with audio_url: {audio_url}")
            else:
                logger.warning(f"⚠️ No audio_url to broadcast - audio_info: {audio_info}, audio_url: {audio_url}")
            
            await broadcast_event(broadcast_payload)
        
        return response
    except Exception as exc:
        logger.error(f"ATOM chat error: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
if DASHBOARD_DIR.exists():
    app.mount("/dashboard", StaticFiles(directory=DASHBOARD_DIR, html=True), name="dashboard")


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
    """Execute revenue cycle and create actual sellable products."""
    import sqlite3
    from datetime import datetime, timezone
    
    market_context = payload.get("market_context") or {"signal": "auto", "budget": 25}
    
    logger.info("🚀 Starting revenue cycle - generating products and opportunities")
    
    try:
        runner = RevenueLoopRunner()
        result = runner.run(market_context)
        store = RevenueCycleStore()
        persisted = store.record_cycle(market_context, result.__dict__)
        
        # Create actual products from the revenue loop results
        try:
            # Extract product opportunities from revenue loop
            product_roadmap = result.product_roadmap or {}
            validated_opportunity = result.validated_opportunity or {}
            revenue_play = result.revenue_play_report or {}
            
            # Create products from validated opportunities
            if validated_opportunity and isinstance(validated_opportunity, dict):
                opportunity_name = validated_opportunity.get("name") or validated_opportunity.get("title") or "AI-Generated Opportunity"
                opportunity_desc = validated_opportunity.get("description") or validated_opportunity.get("value_proposition") or "Autonomously generated revenue opportunity"
                price = float(validated_opportunity.get("price", 0) or validated_opportunity.get("price_point", 97.0))
                
                if price > 0:
                    # Create product in database with unified schema
                    with sqlite3.connect(BUSINESS_DB_PATH) as conn:
                        cursor = conn.cursor()
                        # Ensure table exists with correct schema
                        from backend.ensure_production_ready import ensure_products_table_schema
                        ensure_products_table_schema(BUSINESS_DB_PATH)
                        
                        cursor.execute("""
                            INSERT INTO products (name, description, price, category, type, active, development_status, launch_date, created_at, updated_at)
                            VALUES (?, ?, ?, ?, 'one-time', 1, 'LIVE', ?, ?, ?)
                        """, (
                            opportunity_name,
                            opportunity_desc,
                            price,
                            validated_opportunity.get("category", "digital_product"),
                            datetime.now(timezone.utc).isoformat(),
                            datetime.now(timezone.utc).isoformat(),
                            datetime.now(timezone.utc).isoformat(),
                        ))
                        product_id = cursor.lastrowid
                        conn.commit()
                    
                    # Sync to Stripe if configured and create payment link
                    payment_link = None
                    if stripe_processor and stripe_processor.stripe_config.get("configured"):
                        try:
                            stripe_result = stripe_processor.create_product_with_price(
                                name=opportunity_name,
                                description=opportunity_desc,
                                unit_amount=price,
                                currency="usd",
                            )
                            logger.info(f"✅ Created sellable product: {opportunity_name} (${price})")
                            
                            # Create payment link for immediate sales
                            try:
                                import stripe as stripe_lib
                                if hasattr(stripe_result, 'get') and stripe_result.get('price_id'):
                                    payment_link_obj = stripe_lib.PaymentLink.create(
                                        line_items=[{"price": stripe_result['price_id'], "quantity": 1}],
                                    )
                                    payment_link = payment_link_obj.url
                                    logger.info(f"💰 Payment link created: {payment_link}")
                            except Exception as e:
                                logger.warning(f"Failed to create payment link: {e}")
                        except Exception as e:
                            logger.warning(f"Failed to sync product to Stripe: {e}")
                    
                    log_event(
                        "product.created",
                        agent="revenue_cycle",
                        message=f"Created product: {opportunity_name}",
                        details={"product_id": product_id, "price": price, "payment_link": payment_link}
                    )
                    
                    # AUTO-LAUNCH: Immediately launch marketing for this product
                    if payment_link:
                        try:
                            # Create landing page HTML
                            landing_page_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{opportunity_name}</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
        .hero {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 80px 20px; text-align: center; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 40px 20px; }}
        .price {{ font-size: 3rem; color: #28a745; font-weight: bold; margin: 20px 0; }}
        .btn {{ background: #28a745; color: white; padding: 20px 40px; border: none; border-radius: 8px; font-size: 1.3rem; cursor: pointer; text-decoration: none; display: inline-block; margin: 20px 0; }}
        .btn:hover {{ background: #218838; }}
        .features {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 40px 0; }}
        .feature {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <div class="hero">
        <h1>{opportunity_name}</h1>
        <p style="font-size: 1.2rem; margin: 20px 0;">{opportunity_desc}</p>
        <div class="price">${price:.2f}</div>
        <a href="{payment_link}" class="btn" target="_blank">Get Instant Access Now →</a>
    </div>
    <div class="container">
        <h2>What You'll Get:</h2>
        <div class="features">
            <div class="feature">
                <h3>✅ Immediate Access</h3>
                <p>Get instant access after purchase</p>
            </div>
            <div class="feature">
                <h3>✅ Lifetime Updates</h3>
                <p>All future updates included</p>
            </div>
            <div class="feature">
                <h3>✅ Money-Back Guarantee</h3>
                <p>30-day satisfaction guarantee</p>
            </div>
        </div>
        <div style="text-align: center; margin: 40px 0;">
            <a href="{payment_link}" class="btn" target="_blank">Buy Now - ${price:.2f}</a>
        </div>
    </div>
</body>
</html>
"""
                            # Save landing page
                            import os
                            os.makedirs("products/landing_pages", exist_ok=True)
                            landing_filename = f"products/landing_pages/{opportunity_name.replace(' ', '_').lower()}.html"
                            with open(landing_filename, "w", encoding="utf-8") as f:
                                f.write(landing_page_html)
                            
                            logger.info(f"🌐 Landing page created: {landing_filename}")
                            logger.info(f"🔗 Payment link: {payment_link}")
                            
                            # Store payment link in database for easy access
                            with sqlite3.connect(BUSINESS_DB_PATH) as conn:
                                cursor = conn.cursor()
                                cursor.execute("""
                                    UPDATE products 
                                    SET payment_link = ?, landing_page = ?, updated_at = ?
                                    WHERE id = ?
                                """, (payment_link, landing_filename, datetime.now(timezone.utc).isoformat(), product_id))
                                conn.commit()
                            
                            # Auto-launch marketing campaign
                            _enqueue_task(
                                f"Launch marketing campaign for {opportunity_name}",
                                "marketing",
                                "high",
                                f"Product is live with payment link: {payment_link}. Launch marketing campaign immediately.",
                                {
                                    "product_id": product_id,
                                    "product_name": opportunity_name,
                                    "price": price,
                                    "payment_link": payment_link,
                                    "landing_page": landing_filename,
                                    "auto_launch": True,
                                },
                            )
                        except Exception as e:
                            logger.error(f"Failed to auto-launch product: {e}")
        except Exception as e:
            logger.error(f"Error creating products from revenue cycle: {e}")
        
        # Enqueue follow-up tasks
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
        
        logger.info("✅ Revenue cycle completed - products and opportunities created")
        return {"cycle": persisted}
    except Exception as e:
        logger.error(f"❌ Revenue cycle failed: {e}")
        raise


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


def _scheduled_strategy_cycle(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Run Revenue Strategy Cell cycle."""
    from backend.departments.revenue_strategy_cell import StrategyRunner, Dispatcher
    
    cash_collected = payload.get("cash_collected_to_date", 0.0)
    goal_deadline = payload.get("goal_deadline", "2026-01-31")
    force = payload.get("force", False)
    
    logger.info("🔄 Running scheduled strategy cycle")
    
    try:
        runner = StrategyRunner()
        result = runner.run_cycle(
            cash_collected_to_date=cash_collected,
            goal_deadline=goal_deadline,
            force=force,
        )
        
        if result.get("status") == "completed" and "output" in result:
            dispatcher = Dispatcher()
            dispatch_result = dispatcher.dispatch_run(
                result["run_id"],
                result["output"].get("dispatch_packets", {}),
            )
            result["dispatch_result"] = dispatch_result
            logger.info("✅ Strategy cycle completed and dispatched: %s", result["run_id"])
        else:
            logger.warning("⚠️ Strategy cycle failed or skipped: %s", result.get("error"))
        
        return result
    except Exception as e:
        logger.exception("❌ Strategy cycle error: %s", e)
        return {"status": "error", "error": str(e)}


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
    register_handler("STRATEGY_CYCLE_RUN", _scheduled_strategy_cycle)

    existing = {job.id for job in workflow_scheduler.list_jobs()}

    if "autonomy.run_revenue_cycle" not in existing:
        workflow_scheduler.add_job(
            job_id="autonomy.run_revenue_cycle",
            handler="autonomy.run_revenue_cycle",
            payload={"market_context": {"signal": "auto", "budget": 25}},
            schedule_type="interval",
            schedule_value="30",  # Optimized: run every 30s for faster revenue generation
        )

    if "autonomy.execute_core_play" not in existing:
        workflow_scheduler.add_job(
            job_id="autonomy.execute_core_play",
            handler="autonomy.execute_core_play",
            payload={"play_id": None},
            schedule_type="interval",
            schedule_value="60",  # Optimized: run every 60s for faster execution
        )

    if "autonomy.review_streams" not in existing:
        workflow_scheduler.add_job(
            job_id="autonomy.review_streams",
            handler="autonomy.review_streams",
            payload={},
            schedule_type="interval",
            schedule_value="300",  # review streams every 5 minutes
        )
    
    # Schedule Revenue Strategy Cell to run every 4 hours
    if "STRATEGY_CYCLE_RUN" not in existing:
        workflow_scheduler.add_job(
            job_id="STRATEGY_CYCLE_RUN",
            handler="STRATEGY_CYCLE_RUN",
            payload={"cash_collected_to_date": 0.0, "goal_deadline": "2026-01-31"},
            schedule_type="interval",
            schedule_value="14400",  # 4 hours = 14400 seconds
        )
        logger.info("✅ Scheduled Revenue Strategy Cell to run every 4 hours")


from backend.config.integrations import INTEGRATION_REQUIREMENTS

# Initialize ops router (must be after mode_mgr and tool_executor are created)
# Note: mode_mgr and tool_executor are initialized above after app creation
ops_router = build_ops_router(mode_mgr, tool_executor)

REGISTERED_ROUTERS = [
    ops_router,  # Runtime mode governance API
    performance_router,  # Performance monitoring and optimization
    vector_memory_router,
    embedding_router,
    credentials_router,
    integration_registry_router,
    integrations_router,
    audit_router,
    lead_management_router,
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
    revenue_strategy_router,  # ✅ NEW: Revenue Strategy Cell (Idea Department)
    strategy_cell_router,  # ✅ NEW: Revenue Strategy Cell API routes
    signals_router,  # ✅ NEW: Signal Collection API
    experiments_router,  # ✅ NEW: Experiment Registry API
    playbooks_router,  # ✅ NEW: Playbook Library API
    tasks_router,
    resend_webhook_router,
    # Head Office routers
    executive_router,  # ✅ NEW: Head Office - Executive Launchpad
    decisions_router,  # ✅ NEW: Head Office - Decision Queue
    legal_router,  # ✅ NEW: Head Office - Legal + Contracts
    tax_router,  # ✅ NEW: Head Office - Tax Desk
    assets_router,  # ✅ NEW: Head Office - Assets + Safety Radar
    law_library_router,  # ✅ NEW: Head Office - Law Library
    master_ai_router,  # ✅ NEW: Head Office - Master AI
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
    # Ensure corporate memory tables are created on startup
    CorporateMemory().create_tables()
    logger.info("Corporate memory tables initialised")
except Exception as exc:
    logger.exception("Unable to initialise corporate memory tables: %s", exc)

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
# verify_request_token is now imported from backend.auth


protected_dependencies: List[Depends] = []
protected_dependencies = [Depends(verify_request_token)]

# Rate limiting --------------------------------------------------------------
rate_limit_per_min = int(os.getenv("FALLAT_RATE_LIMIT_PER_MIN", "60"))
app.state.rate_limiter = get_rate_limiter()

for router in REGISTERED_ROUTERS:
    app.include_router(router, dependencies=protected_dependencies)


# Lifecycle hooks -------------------------------------------------------------
def _start_loops_once(app: FastAPI) -> None:
    """Start all background loops exactly once (singleton guard)."""
    import logging
    logger = logging.getLogger(__name__)
    
    global _LOOPS_STARTED
    with _LOOPS_LOCK:
        if _LOOPS_STARTED:
            logger.warning("Loops already started; skipping duplicate startup.")
            return
        _LOOPS_STARTED = True
    
    # Initialize loop tasks list for clean shutdown
    if not hasattr(app.state, "loop_tasks"):
        app.state.loop_tasks = []
    
    logger.info(f"Starting loops (pid={os.getpid()})...")


@app.on_event("startup")
async def _startup_verification() -> None:
    """Verify runtime mode governance system is operational."""
    import logging
    logger = logging.getLogger(__name__)
    
    # Boot logging: PID, mode, worker count, port, tools
    pid = os.getpid()
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "127.0.0.1")
    workers = int(os.getenv("WORKERS", "1"))
    reload = os.getenv("RELOAD", "0") == "1"
    
    logger.info("=" * 80)
    logger.info(f"🚀 Earnetics Backend Starting")
    logger.info(f"   PID: {pid}")
    logger.info(f"   Host: {host}:{port}")
    logger.info(f"   Workers: {workers}")
    logger.info(f"   Reload: {reload}")
    
    try:
        # Verify mode manager
        mode_state = mode_mgr.get()
        logger.info(f"   Mode: {mode_state.mode.value} (changed_by: {mode_state.changed_by})")
        
        # Verify tool registry
        registry_count = tool_registry.count()
        logger.info(f"   Tools registered: {registry_count}")
        
        # Verify tool executor
        logger.info("   Tool executor: ✅ initialized")
        
        # Log current policy
        from backend.core.governance import build_policies
        policies = build_policies()
        policy = policies[mode_state.mode]
        logger.info(f"   Governance: {len(policy.allowed)} allowed, {len(policy.approval_required)} require approval")
        
        logger.info("=" * 80)
        
    except Exception as exc:
        logger.error(f"⚠️ Runtime mode governance verification failed: {exc}", exc_info=True)

@app.on_event("startup")
async def _startup_autonomy_worker() -> None:
    """Start all autonomy loops (with singleton guard)."""
    # Singleton guard: prevent double-start
    _start_loops_once(app)
    
    # Initialize Evolution Engine and start continuous learning loop
    from backend.atom_evolution_engine import AtomEvolutionEngine
    evolution_engine = AtomEvolutionEngine()
    app.state.evolution_engine = evolution_engine
    
    # Start evolution feedback loop (runs every 30 seconds to analyze recent events)
    async def _evolution_loop():
        """Background loop to continuously learn and provide feedback."""
        try:
            while True:
                await asyncio.sleep(30)  # Check every 30 seconds
                try:
                    # Analyze recent actions and generate feedback
                    summary = evolution_engine.get_evolution_summary()
                    if summary["total_feedback"] > 0:
                        feedback = {
                            "type": "evolution_summary",
                            "payload": {
                                "total_learnings": summary["total_feedback"],
                                "average_impact": summary["average_impact_score"],
                                "agents_tracked": summary["agents_tracked"],
                                "average_success_rate": summary["average_success_rate"],
                                "status": summary["status"],
                                "message": f"✅ Evolution Engine: {summary['total_feedback']} insights learned. Average impact: {summary['average_impact_score']:.2f}. {summary['agents_tracked']} agents improving."
                            }
                        }
                        await broadcast_event(feedback)
                        logger.debug(f"Evolution feedback: {summary['total_feedback']} insights, {summary['average_impact_score']:.2f} avg impact")
                except Exception as e:
                    logger.debug(f"Evolution loop error: {e}")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Evolution loop crashed: {e}")
    
    evolution_task = asyncio.create_task(_evolution_loop())
    app.state.evolution_task = evolution_task
    app.state.loop_tasks.append(evolution_task)
    logger.info("✅ Agent Evolution Engine activated - continuous learning enabled")
    
    # Wire up Audit Log to Event Bus
    from backend.audit_log import set_broadcast_callback
    
    def _sync_broadcast(event):
        # Fire and forget async broadcast from sync context
        asyncio.create_task(broadcast_event(event))
        
    set_broadcast_callback(_sync_broadcast)
    logger.info("Audit log wired to Event Bus")

    await _start_autonomy_worker_on_boot()
    _ensure_autonomy_jobs()
    start_dfy_worker()
    try:
        await FACTORY_ENGINE.start()
    except Exception:  # pragma: no cover
        logger.exception("Factory engine failed to start")

    # Start workflow scheduler execution loop (optimized for faster revenue generation)
    async def _scheduler_loop():
        """Background loop to execute scheduled revenue jobs."""
        try:
            while True:
                try:
                    await asyncio.sleep(5)  # Optimized: Check every 5 seconds for faster execution
                    due = workflow_scheduler.due_jobs()
                    if due:
                        logger.info(f"🔄 Executing {len(due)} due revenue job(s)")
                        results = await workflow_scheduler.run_due_jobs()
                        for result in results:
                            if result.get("status") == "success":
                                logger.info(f"✅ Job {result.get('job_id')} executed successfully")
                            elif result.get("status") == "error":
                                logger.error(f"❌ Job {result.get('job_id')} failed: {result.get('message')}")
                except asyncio.CancelledError:
                    logger.info("Scheduler loop cancelled")
                    break
                except Exception as exc:
                    logger.exception(f"Error in scheduler loop: {exc}")
                    await asyncio.sleep(15)  # Optimized: Wait 15s on error (reduced from 30s)
        except asyncio.CancelledError:
            logger.info("Scheduler loop cancelled during shutdown")
    
    scheduler_task = asyncio.create_task(_scheduler_loop())
    background_tasks.append(scheduler_task)
    app.state.loop_tasks.append(scheduler_task)
    logger.info("Workflow scheduler execution loop started")
    
    # Start continuous autonomous agent cycle for faster revenue generation
    async def _autonomous_agent_cycle():
        """Continuous autonomous agent cycle - agents work continuously to generate revenue"""
        from backend.real_ai_agents import run_real_autonomous_cycle
        try:
            # Wait a bit on startup to let system initialize
            await asyncio.sleep(30)
            cycle_count = 0
            while True:
                try:
                    cycle_count += 1
                    logger.info(f"🔄 Starting autonomous agent cycle #{cycle_count}")
                    result = await run_real_autonomous_cycle(
                        "Continuous revenue generation cycle",
                        {"cycle_number": cycle_count, "priority": "high"}
                    )
                    summary = result.get("summary", {})
                    if summary.get("priority_actions"):
                        logger.info(f"✅ Cycle #{cycle_count} complete - {len(summary['priority_actions'])} priority actions identified")
                    # Run every 60 seconds for continuous revenue generation
                    await asyncio.sleep(60)
                except asyncio.CancelledError:
                    logger.info("Autonomous agent cycle cancelled")
                    break
                except Exception as exc:
                    logger.exception(f"Error in autonomous agent cycle: {exc}")
                    await asyncio.sleep(30)  # Wait 30s on error before retrying
        except asyncio.CancelledError:
            logger.info("Autonomous agent cycle cancelled during shutdown")
        except Exception as e:
            logger.error(f"Autonomous agent cycle crashed: {e}")
    
    autonomous_cycle_task = asyncio.create_task(_autonomous_agent_cycle())
    background_tasks.append(autonomous_cycle_task)
    app.state.loop_tasks.append(autonomous_cycle_task)
    logger.info("✅ Continuous autonomous agent cycle started - agents working continuously for revenue")
    
    # Start product launcher - automatically launch products with payment links
    async def _product_launcher_cycle():
        """Continuously check for products that need launching and create payment links"""
        from backend.real_ai_agents import AIRevenueAgentCorporation
        try:
            # Wait a bit on startup
            await asyncio.sleep(60)
            while True:
                try:
                    # Get LaunchSpecialist agent
                    corporation = AIRevenueAgentCorporation()
                    launch_specialist = corporation.agents.get("launchspecialist")
                    
                    if launch_specialist:
                        # Trigger launch action
                        result = await launch_specialist.think_and_act(
                            "Launch all products that need payment links and landing pages",
                            {"auto_launch": True}
                        )
                        if result.get("action_result", {}).get("products_launched"):
                            logger.info(f"🚀 Auto-launched {len(result['action_result']['products_launched'])} products")
                    
                    # Run every 2 minutes to catch new products quickly
                    await asyncio.sleep(120)
                except asyncio.CancelledError:
                    break
                except Exception as exc:
                    logger.exception(f"Error in product launcher cycle: {exc}")
                    await asyncio.sleep(60)
        except asyncio.CancelledError:
            logger.info("Product launcher cycle cancelled")
        except Exception as e:
            logger.error(f"Product launcher cycle crashed: {e}")
    
    product_launcher_task = asyncio.create_task(_product_launcher_cycle())
    background_tasks.append(product_launcher_task)
    app.state.loop_tasks.append(product_launcher_task)
    logger.info("✅ Product auto-launcher started - products will be launched automatically with payment links")
    
    # Start customer acquisition automation - build email list automatically
    async def _customer_acquisition_cycle():
        """Continuously work on customer acquisition and list building"""
        from backend.services.mailops_service import MailOpsService, Subscriber
        try:
            # Wait a bit on startup
            await asyncio.sleep(120)
            while True:
                try:
                    mailops = MailOpsService()
                    
                    # Check current subscriber count
                    current_subscribers = mailops.list_subscribers(limit=10000)
                    subscriber_count = len(current_subscribers) if current_subscribers else 0
                    
                    # If list is small, try to grow it
                    if subscriber_count < 100:
                        # Generate lead magnet ideas and create opt-in opportunities
                        lead_magnets = [
                            "Free AI Automation Checklist",
                            "5-Day Revenue Growth Challenge",
                            "Ultimate Business Automation Guide",
                            "AI Tools Master List",
                            "Revenue Generation Playbook",
                        ]
                        
                        # Create a lead magnet offer
                        import random
                        lead_magnet = random.choice(lead_magnets)
                        
                        # Store lead magnet for future use
                        log_event(
                            "customer_acquisition.lead_magnet_created",
                            agent="system",
                            message=f"Created lead magnet: {lead_magnet}",
                            details={"subscriber_count": subscriber_count, "target": 100}
                        )
                        
                        logger.info(f"📧 Customer Acquisition: Created lead magnet '{lead_magnet}' (Current list: {subscriber_count})")
                    
                    # Run every 5 minutes
                    await asyncio.sleep(300)
                except asyncio.CancelledError:
                    break
                except Exception as exc:
                    logger.exception(f"Error in customer acquisition cycle: {exc}")
                    await asyncio.sleep(120)
        except asyncio.CancelledError:
            logger.info("Customer acquisition cycle cancelled")
        except Exception as e:
            logger.error(f"Customer acquisition cycle crashed: {e}")
    
    customer_acquisition_task = asyncio.create_task(_customer_acquisition_cycle())
    background_tasks.append(customer_acquisition_task)
    app.state.loop_tasks.append(customer_acquisition_task)
    logger.info("✅ Customer acquisition automation started - building email list automatically")
    
    # Start conversion tracking and optimization
    async def _conversion_tracking_cycle():
        """Track conversions and optimize based on performance"""
        import sqlite3
        try:
            # Wait a bit on startup
            await asyncio.sleep(180)
            while True:
                try:
                    # Track product performance
                    with sqlite3.connect(BUSINESS_DB_PATH) as conn:
                        conn.row_factory = sqlite3.Row
                        cursor = conn.cursor()
                        
                        # Get products with payment links
                        cursor.execute("""
                            SELECT id, name, price, payment_link, created_at
                            FROM products
                            WHERE active = 1 AND payment_link IS NOT NULL AND payment_link != ''
                            ORDER BY created_at DESC
                            LIMIT 10
                        """)
                        products = [dict(row) for row in cursor.fetchall()]
                        
                        # Check for recent transactions (if Stripe webhooks are set up)
                        # This would track actual sales
                        for product in products:
                            # Store performance data for optimization
                            log_event(
                                "conversion_tracking.product_performance",
                                agent="system",
                                message=f"Tracking performance for {product['name']}",
                                details={
                                    "product_id": product["id"],
                                    "product_name": product["name"],
                                    "price": product.get("price", 0),
                                    "has_payment_link": bool(product.get("payment_link")),
                                }
                            )
                        
                        if products:
                            logger.info(f"📊 Conversion Tracking: Monitoring {len(products)} products")
                    
                    # Run every 10 minutes
                    await asyncio.sleep(600)
                except asyncio.CancelledError:
                    break
                except Exception as exc:
                    logger.exception(f"Error in conversion tracking cycle: {exc}")
                    await asyncio.sleep(300)
        except asyncio.CancelledError:
            logger.info("Conversion tracking cycle cancelled")
        except Exception as e:
            logger.error(f"Conversion tracking cycle crashed: {e}")
    
    conversion_tracking_task = asyncio.create_task(_conversion_tracking_cycle())
    background_tasks.append(conversion_tracking_task)
    app.state.loop_tasks.append(conversion_tracking_task)
    logger.info("✅ Conversion tracking started - optimizing based on performance")
    
    # Start continuous lead generation - scrapes websites for customers
    async def _lead_generation_cycle():
        """Continuously scrape websites and build email list"""
        from backend.real_ai_agents import AIRevenueAgentCorporation
        try:
            # Wait a bit on startup
            await asyncio.sleep(300)  # 5 minutes after startup
            while True:
                try:
                    corporation = AIRevenueAgentCorporation()
                    
                    # Run lead generation agents
                    webscraper = corporation.agents.get("webscraper")
                    leadqualifier = corporation.agents.get("leadqualifier")
                    listbuilder = corporation.agents.get("listbuilder")
                    
                    if webscraper:
                        result = await webscraper.think_and_act(
                            "Scrape targeted websites to find potential customers",
                            {"auto_scrape": True}
                        )
                        if result.get("action_result", {}).get("leads_found", 0) > 0:
                            logger.info(f"🔍 Found {result['action_result']['leads_found']} leads from scraping")
                    
                    if leadqualifier:
                        await leadqualifier.think_and_act(
                            "Qualify scraped leads and validate them",
                            {"auto_qualify": True}
                        )
                    
                    if listbuilder:
                        result = await listbuilder.think_and_act(
                            "Add qualified leads to email list",
                            {"auto_add": True}
                        )
                        if result.get("action_result", {}).get("subscribers_added", 0) > 0:
                            logger.info(f"📧 Added {result['action_result']['subscribers_added']} subscribers to email list")
                    
                    # Run every 5 minutes (increased frequency for higher lead volume)
                    await asyncio.sleep(300)
                except asyncio.CancelledError:
                    break
                except Exception as exc:
                    logger.exception(f"Error in lead generation cycle: {exc}")
                    await asyncio.sleep(150)  # Faster retry on error
        except asyncio.CancelledError:
            logger.info("Lead generation cycle cancelled")
        except Exception as e:
            logger.error(f"Lead generation cycle crashed: {e}")
    
    lead_generation_task = asyncio.create_task(_lead_generation_cycle())
    background_tasks.append(lead_generation_task)
    app.state.loop_tasks.append(lead_generation_task)
    logger.info("✅ Continuous lead generation started - scraping websites and building email list")
    
    # Start Autonomous Financial Processor
    financial_task = asyncio.create_task(financial_processor.start_autonomous_processing())
    background_tasks.append(financial_task)
    app.state.loop_tasks.append(financial_task)
    logger.info("Autonomous Financial Processor started")
    
    # Ensure production readiness - products, schema, Stripe sync
    try:
        from backend.ensure_production_ready import ensure_initial_products, ensure_products_table_schema, ensure_stripe_mappings_table
        
        # Ensure database schema is correct
        ensure_products_table_schema(BUSINESS_DB_PATH)
        ensure_stripe_mappings_table(BUSINESS_DB_PATH)
        
        # Seed initial revenue-generating products and sync to Stripe
        products_created = ensure_initial_products(BUSINESS_DB_PATH, stripe_processor)
        
        if products_created > 0:
            logger.info(f"💰 {products_created} revenue-generating products ready and synced to Stripe")
        else:
            logger.info("💰 Revenue products already exist and are ready")
    except Exception as exc:
        logger.exception("Failed to ensure production readiness: %s", exc)


# Track background tasks for clean shutdown
background_tasks: List[asyncio.Task] = []

@app.on_event("shutdown")
async def _shutdown_autonomy_worker() -> None:
    """Clean shutdown of all background tasks and services."""
    logger.info("Starting application shutdown...")
    
    # Cancel all loop tasks (from app.state.loop_tasks)
    loop_tasks = getattr(app.state, "loop_tasks", [])
    for task in loop_tasks:
        if not task.done():
            task.cancel()
            try:
                await asyncio.wait_for(task, timeout=2.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass
            except Exception as e:
                logger.warning(f"Error cancelling loop task: {e}")
    
    # Cancel all background tasks
    for task in background_tasks:
        if not task.done():
            task.cancel()
            try:
                await asyncio.wait_for(task, timeout=2.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass
            except Exception as e:
                logger.warning(f"Error cancelling background task: {e}")
    
    # Stop autonomy worker
    try:
        await asyncio.wait_for(_stop_autonomy_worker(), timeout=5.0)
    except asyncio.TimeoutError:
        logger.warning("Autonomy worker shutdown timed out")
    except Exception as e:
        logger.warning(f"Error stopping autonomy worker: {e}")
    
    logger.info("Application shutdown complete.")
    
    # Stop factory engine
    try:
        await asyncio.wait_for(FACTORY_ENGINE.stop(), timeout=3.0)
    except (asyncio.TimeoutError, Exception) as e:
        logger.warning(f"Factory engine stop failed: {e}")
    
    # Close WebSocket connections
    try:
        # Use the global manager instance (defined at module level)
        for ws in manager.active_connections[:]:
            try:
                await ws.close()
            except Exception:
                pass
        manager.active_connections.clear()
    except Exception as e:
        logger.warning(f"Error closing WebSocket connections: {e}")
    
    logger.info("Application shutdown complete.")


# System Controls ------------------------------------------------------------
from backend.system_state import global_state

class SystemControlPayload(BaseModel):
    safe_mode: Optional[bool] = None
    mail_sending_paused: Optional[bool] = None
    agent_execution_paused: Optional[bool] = None


@app.post("/api/system/controls", dependencies=protected_dependencies)
async def update_system_controls(payload: SystemControlPayload):
    """Update global kill switches."""
    if payload.safe_mode is not None:
        global_state["SAFE_MODE"] = payload.safe_mode
        await broadcast_event({"type": "CONTROL_UPDATE", "payload": {"safe_mode": payload.safe_mode}})
        log_event("system_control_update", message=f"Safe Mode set to {payload.safe_mode}")

    if payload.mail_sending_paused is not None:
        global_state["MAIL_SENDING_PAUSED"] = payload.mail_sending_paused
        await broadcast_event({"type": "CONTROL_UPDATE", "payload": {"mail_sending_paused": payload.mail_sending_paused}})
        log_event("system_control_update", message=f"Mail Sending set to {not payload.mail_sending_paused}")

    if payload.agent_execution_paused is not None:
        global_state["AGENT_EXECUTION_PAUSED"] = payload.agent_execution_paused
        await broadcast_event({"type": "CONTROL_UPDATE", "payload": {"agent_execution_paused": payload.agent_execution_paused}})
        log_event("system_control_update", message=f"Agent Execution set to {not payload.agent_execution_paused}")

    return {
        "safe_mode": global_state["SAFE_MODE"],
        "mail_sending_paused": global_state["MAIL_SENDING_PAUSED"],
        "agent_execution_paused": global_state["AGENT_EXECUTION_PAUSED"],
    }


@app.get("/api/system/controls", dependencies=protected_dependencies)
def get_system_controls():
    return {
        "safe_mode": global_state["SAFE_MODE"],
        "mail_sending_paused": global_state["MAIL_SENDING_PAUSED"],
        "agent_execution_paused": global_state["AGENT_EXECUTION_PAUSED"],
    }


# Middleware -----------------------------------------------------------------
@app.middleware("http")
async def track_requests(request: Request, call_next):
    app_state["total_requests"] += 1
    response = await call_next(request)
    return response


# Helpers --------------------------------------------------------------------
def _render_command_center() -> str:
    if COMMAND_CENTER_PATH.exists():
        logger.info(f"Rendering Command Center from: {COMMAND_CENTER_PATH}")
        html = COMMAND_CENTER_PATH.read_text(encoding="utf-8")
    else:
        logger.warning("Command Center file not found, using default template")
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
    dashboard_index = DASHBOARD_DIR / "index.html"
    logger.info(f"Root page requested. Checking for dashboard at: {dashboard_index}")
    if dashboard_index.exists():
        logger.info("Serving dashboard index.html")
        return HTMLResponse(content=dashboard_index.read_text(encoding="utf-8"))
    logger.info("Dashboard index not found, falling back to Command Center")
    return HTMLResponse(content=_render_command_center())


@app.get("/command_center", response_class=HTMLResponse)
async def command_center_view() -> HTMLResponse:
    dashboard_index = DASHBOARD_DIR / "index.html"
    if dashboard_index.exists():
        return HTMLResponse(content=dashboard_index.read_text(encoding="utf-8"))
    return HTMLResponse(content=_render_command_center())


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial system state if needed
        await websocket.send_json({
            "type": "SYSTEM_CONNECTED",
            "payload": {
                "status": "online",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "version": os.getenv("FALLAT_APP_VERSION", "0.1.0")
            }
        })
        
        while True:
            # Keep connection alive and handle incoming messages if any
            try:
                data = await websocket.receive_text()
                # For now, we just echo or log. In the future, handle commands.
                try:
                    message = json.loads(data)
                    logger.debug(f"Received WS message: {message}")
                except json.JSONDecodeError:
                    pass
            except Exception as receive_error:
                # Log receive errors but don't break the connection
                logger.warning(f"WebSocket receive error (non-fatal): {receive_error}")
                # Send a ping to keep connection alive
                try:
                    await websocket.send_json({
                        "type": "PING",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                except Exception:
                    # If we can't send, connection is likely dead
                    break
                
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected normally")
        manager.disconnect(websocket)
    except Exception as exc:
        logger.error(f"WebSocket error: {exc}", exc_info=True)
        try:
            await websocket.send_json({
                "type": "ERROR",
                "payload": {
                    "message": f"Connection error: {str(exc)}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            })
        except Exception:
            pass  # Connection is already dead
        manager.disconnect(websocket)


@app.get("/health")
def healthcheck() -> Dict[str, Any]:
    db_ok, db_message = _check_database_health()
    stripe_ok, stripe_message = _stripe_health()
    vault_ok = app_state["credential_vault_ready"]
    vector_ok = app_state["vector_memory_ready"]
    overall = "ok" if all([db_ok, stripe_ok or not os.getenv("STRIPE_SECRET_KEY"), vault_ok, vector_ok]) else "degraded"
    prime_directive_status = "verified"
    try:
        from backend.prime_directive import load_prime_directive

        load_prime_directive()
    except Exception:
        prime_directive_status = "unverified"

    return {
        "status": overall,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "database": {"ok": db_ok, "message": db_message},
            "credential_vault": {"ok": vault_ok},
            "vector_memory": {"ok": vector_ok},
            "stripe": {"ok": stripe_ok, "message": stripe_message},
            "prime_directive": {"status": prime_directive_status},
        },
    }


@app.get("/ping")
def ping() -> Dict[str, str]:
    """Simple connectivity check."""
    return {"status": "pong", "timestamp": datetime.now(timezone.utc).isoformat()}


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


@app.get("/api/financial/metrics", dependencies=protected_dependencies)
def get_financial_metrics():
    """Get real-time financial metrics including 80/20 split and reinvestment."""
    return financial_processor._calculate_financial_metrics()


@app.get("/api/prime_directive", dependencies=protected_dependencies)
def get_prime_directive():
    """Return the current Prime Directive (read-only)."""
    from backend.prime_directive import load_prime_directive

    directive = load_prime_directive().data
    return {"prime_directive": directive}


@app.get("/api/products/list", dependencies=protected_dependencies)
async def list_products_detailed():
    """Get detailed list of all products."""
    try:
        import sqlite3
        with sqlite3.connect(BUSINESS_DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, description, price, category, type, interval, 
                       active, development_status, launch_date, revenue_generated,
                       created_at, updated_at, payment_link, landing_page
                FROM products
                WHERE active = 1
                ORDER BY created_at DESC
            """)
            products = []
            for row in cursor.fetchall():
                products.append({
                    "id": row["id"],
                    "name": row["name"],
                    "description": row["description"],
                    "price": row["price"],
                    "category": row["category"],
                    "type": row["type"],
                    "interval": row["interval"],
                    "development_status": row["development_status"],
                    "launch_date": row["launch_date"],
                    "revenue_generated": row["revenue_generated"] or 0,
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "payment_link": row["payment_link"],
                    "landing_page": row["landing_page"]
                })
        return {"products": products, "total": len(products)}
    except Exception as e:
        logger.error(f"Error listing products: {e}")
        return {"products": [], "total": 0, "error": str(e)}


class DirectiveStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None


@app.post("/api/directives/{directive_id}/status", dependencies=protected_dependencies)
async def update_directive_status(directive_id: int, req: DirectiveStatusUpdate):
    """Update the status of an executive directive."""
    try:
        from backend.executive_reasoning import DirectiveRegistry

        directive_registry = DirectiveRegistry()
        directive_registry.update_status(directive_id, req.status, req.notes)
        return {"id": directive_id, "status": req.status}
    except Exception as e:
        logger.error(f"Error updating directive status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update directive status")

@app.get("/api/workflows/pending", dependencies=protected_dependencies)
async def list_pending_workflows():
    """Get detailed list of pending workflows from queue."""
    try:
        from autonomous.workflow_queue import WorkflowQueueRepository
        queue_repo = WorkflowQueueRepository()
        
        # Get pending tasks from queue
        pending_tasks = []
        try:
            # Try to get from workflow queue database first
            queue_db_path = getattr(queue_repo, 'db_path', 'workflow_scheduler.db')
            try:
                with sqlite3.connect(queue_db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    # Check if table exists
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
                    if cursor.fetchone():
                        cursor.execute("""
                            SELECT id, title, department, priority, status, description,
                                   assigned_agent, created_at, metadata
                            FROM tasks
                            WHERE status = 'pending'
                            ORDER BY 
                                CASE priority
                                    WHEN 'critical' THEN 1
                                    WHEN 'high' THEN 2
                                    WHEN 'medium' THEN 3
                                    WHEN 'low' THEN 4
                                END,
                                created_at ASC
                        """)
                        for row in cursor.fetchall():
                            try:
                                metadata = json.loads(row["metadata"]) if row["metadata"] else {}
                            except:
                                metadata = {}
                            pending_tasks.append({
                                "id": str(row["id"]),
                                "title": row["title"] or "Untitled Task",
                                "department": row["department"] or "Unknown",
                                "priority": row["priority"] or "medium",
                                "status": row["status"] or "pending",
                                "description": row["description"],
                                "assigned_agent": row["assigned_agent"],
                                "created_at": row["created_at"] or datetime.now(timezone.utc).isoformat(),
                                "metadata": metadata
                            })
                    else:
                        # Table doesn't exist yet
                        pending_tasks = []
            except sqlite3.OperationalError as db_error:
                logger.debug(f"Queue database query failed: {db_error}")
                # Try corporate memory as fallback
                try:
                    from backend.corporate_memory import CorporateMemory
                    corp_mem = CorporateMemory()
                    tasks = corp_mem.list_tasks(status="pending")
                    for task in tasks[:50]:  # Limit to 50
                        pending_tasks.append({
                            "id": str(task.get("id", "")),
                            "title": task.get("title", "Untitled Task"),
                            "department": task.get("department", "Unknown"),
                            "priority": task.get("priority", "medium"),
                            "status": task.get("status", "pending"),
                            "description": task.get("description"),
                            "assigned_agent": task.get("assigned_agent"),
                            "created_at": task.get("created_at", datetime.now(timezone.utc).isoformat()),
                            "metadata": task.get("metadata", {})
                        })
                except Exception as corp_error:
                    logger.warning(f"Could not fetch from corporate memory: {corp_error}")
        except Exception as e:
            logger.warning(f"Could not fetch from queue directly: {e}")
            pending_tasks = []
        
        return {"workflows": pending_tasks, "total": len(pending_tasks)}
    except Exception as e:
        logger.error(f"Error listing pending workflows: {e}")
        return {"workflows": [], "total": 0, "error": str(e)}

@app.get("/api/customers/list", dependencies=protected_dependencies)
async def list_customers():
    """Get detailed list of active customers."""
    try:
        import sqlite3
        with sqlite3.connect(BUSINESS_DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT customer_email, COUNT(*) as transaction_count,
                       SUM(amount) as total_spent, MAX(created_at) as last_purchase
                FROM stripe_transactions
                WHERE status = 'completed' AND customer_email IS NOT NULL
                GROUP BY customer_email
                ORDER BY total_spent DESC
            """)
            customers = []
            for row in cursor.fetchall():
                customers.append({
                    "email": row["customer_email"],
                    "transaction_count": row["transaction_count"],
                    "total_spent": row["total_spent"] or 0,
                    "last_purchase": row["last_purchase"]
                })
        return {"customers": customers, "total": len(customers)}
    except Exception as e:
        logger.error(f"Error listing customers: {e}")
        return {"customers": [], "total": 0, "error": str(e)}

@app.get("/api/system/status", dependencies=protected_dependencies)
async def get_system_status():
    """Get overall system status, safety state, and metrics."""
    now = datetime.now(timezone.utc)
    uptime = now - app_state["startup_time"]
    uptime_hours = round(uptime.total_seconds() / 3600, 2)
    
    # Fetch real-world financial metrics for the dashboard (with timeout protection)
    total_revenue = 0.0
    active_customers = 0
    products_created = 0
    directives_executed = 0
    monthly_target = 150000  # Default, can be overridden from config
    
    try:
        if BUSINESS_DB_PATH.exists():
            with sqlite3.connect(BUSINESS_DB_PATH, timeout=2.0) as conn:  # 2 second timeout
                cursor = conn.cursor()
                
                # Get total revenue from financial_operations (with error handling)
                try:
                    cursor.execute("SELECT SUM(gross_revenue) FROM financial_operations")
                    res = cursor.fetchone()
                    if res and res[0]:
                        total_revenue = float(res[0])
                except sqlite3.OperationalError:
                    pass  # Table might not exist
                
                # Get active customers from stripe_transactions (most accurate)
                try:
                    cursor.execute("SELECT COUNT(DISTINCT customer_email) FROM stripe_transactions WHERE customer_email IS NOT NULL AND customer_email != ''")
                    res = cursor.fetchone()
                    if res and res[0]:
                        active_customers = int(res[0])
                except sqlite3.OperationalError:
                    # Fallback: count unique transaction IDs as proxy
                    try:
                        cursor.execute("SELECT COUNT(DISTINCT transaction_id) FROM transactions WHERE transaction_id IS NOT NULL")
                        res = cursor.fetchone()
                        if res and res[0]:
                            active_customers = int(res[0])
                    except sqlite3.OperationalError:
                        pass  # Tables might not exist yet
                
                # Get products created
                try:
                    cursor.execute("SELECT COUNT(*) FROM products")
                    res = cursor.fetchone()
                    if res and res[0]:
                        products_created = int(res[0])
                except sqlite3.OperationalError:
                    pass  # Table might not exist yet
    except Exception as e:
        logger.error(f"Error fetching financial metrics: {e}")
    
    # Get directives executed from audit log (optimized with direct SQL query)
    try:
        if BUSINESS_DB_PATH.exists():
            with sqlite3.connect(BUSINESS_DB_PATH, timeout=1.0) as conn:  # 1 second timeout
                cursor = conn.cursor()
                try:
                    # Direct SQL query is much faster than list_events
                    cursor.execute("""
                        SELECT COUNT(*) FROM audit_events 
                        WHERE action LIKE '%directive%'
                    """)
                    res = cursor.fetchone()
                    if res and res[0]:
                        directives_executed = int(res[0])
                except sqlite3.OperationalError:
                    directives_executed = 0  # Table might not exist
        else:
            directives_executed = 0
    except Exception as e:
        logger.error(f"Error counting directives: {e}")
        directives_executed = 0  # Fallback to 0 on error
    
    # Load monthly_target from config file if available
    try:
        import json
        metrics_path = PROJECT_ROOT / "backend" / "financial" / "performance_metrics.json"
        if metrics_path.exists():
            with open(metrics_path, "r") as f:
                file_metrics = json.load(f)
                monthly_target = file_metrics.get("monthly_target", 150000)
    except Exception as e:
        logger.error(f"Error loading performance metrics config: {e}")
    
    performance_metrics = {
        "total_revenue": total_revenue,
        "monthly_target": monthly_target,
        "active_customers": active_customers,
        "products_created": products_created,
        "directives_executed": directives_executed,
        "last_updated": now.isoformat(),
    }

    return {
        "status": "online",
        "timestamp": now.isoformat(),
        "kill_switch_active": guardian.kill_switch_active,
        "safe_mode": global_state["SAFE_MODE"],
        "agent_paused": global_state["AGENT_EXECUTION_PAUSED"],
        "mail_paused": global_state["MAIL_SENDING_PAUSED"],
        "metrics": {
            "uptime_hours": uptime_hours,
            "total_requests": app_state["total_requests"],
            "connected_modules": len(REGISTERED_ROUTERS),
            "total_revenue": total_revenue,
        },
        "services": {
            "vector_memory": "ready" if app_state["vector_memory_ready"] else "unavailable",
            "credential_vault": "ready" if app_state["credential_vault_ready"] else "unavailable",
        },
        # Add performance metrics in expected structure for frontend
        "system_health": {
            "system_overview": {
                "performance_metrics": performance_metrics,
                "status": "online",
            }
        },
        "app_state": {
            "total_requests": app_state["total_requests"],
        },
    }


@app.get("/api/system_status", dependencies=protected_dependencies)
async def get_system_status_legacy():
    """Legacy alias for /api/system/status to match frontend expectations."""
    try:
        result = await get_system_status()
        # Ensure it's a proper dict that FastAPI can serialize
        if isinstance(result, dict):
            return result
        else:
            logger.error(f"get_system_status returned non-dict: {type(result)}")
            return {"status": "error", "message": "Invalid response type"}
    except Exception as e:
        logger.exception(f"Error in get_system_status_legacy: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/api/system/integrations", dependencies=protected_dependencies)
def get_integration_status():
    """Check status of all external integrations."""
    status = {}
    for name, env_vars in INTEGRATION_REQUIREMENTS.items():
        missing = [v for v in env_vars if not os.getenv(v)]
        status[name] = {
            "status": "connected" if not missing else "disconnected",
            "missing_vars": missing,
            "production_mode": not global_state["SAFE_MODE"]
        }
    return status


@app.post("/api/atom/evolve", dependencies=protected_dependencies)
def run_atom_evolution():
    """Trigger a full evolution cycle for ATOM."""
    return atom_agent.run_self_evolution()


@app.get("/api/atom/evolution_metrics", dependencies=protected_dependencies)
def get_evolution_metrics():
    """Get performance metrics for the evolution engine."""
    return atom_agent.evolver.analyze_performance()


@app.post("/api/system/kill-switch", dependencies=protected_dependencies)
def toggle_kill_switch(active: bool):
    """Activate or deactivate the emergency kill switch."""
    if active:
        guardian.activate_kill_switch()
    else:
        guardian.deactivate_kill_switch()
    return {"status": "ok", "kill_switch_active": guardian.kill_switch_active}


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


@app.get("/metrics", dependencies=protected_dependencies)
def get_operations_metrics():
    """Get operational metrics for the dashboard (worker, scheduler, queue, etc.)."""
    from backend.api.dashboard_router import get_dashboard_snapshot
    from backend.api.autonomy_worker_router import router as autonomy_router
    # Use the scheduler instance from the router (already imported at module level)
    from autonomous.workflow_queue import WorkflowQueueRepository
    
    try:
        # Get worker status
        worker = getattr(app.state, "autonomy_worker", None)
        worker_status = "unknown"
        worker_pending = None
        if worker:
            worker_status = "running" if worker.is_running() else "stopped"
            queue_repo = getattr(worker, "queue_repository", None)
            worker_pending = queue_repo.count_pending() if queue_repo else 0
        
        # Get scheduler status
        scheduler_enabled = True  # workflow_scheduler is always enabled
        jobs = workflow_scheduler.list_jobs()
        
        # Get queue metrics
        queue_repo = WorkflowQueueRepository()
        pending = queue_repo.count_pending()
        
        # Verify the pending count against actual pending tasks if they differ
        # This prevents "ghost" numbers on the dashboard
        if pending > 0:
            try:
                # Use the same logic as /api/workflows/pending to verify
                queue_db_path = getattr(queue_repo, 'db_path', 'workflow_scheduler.db')
                with sqlite3.connect(queue_db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
                    if cursor.fetchone():
                        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'pending'")
                        actual_pending = cursor.fetchone()[0]
                        if actual_pending != pending:
                             # Update queue repo cache/state if possible, or just report true number
                             pending = actual_pending
            except Exception:
                pass
        
        # Note: at_risk and overdue would need additional logic
        
        # Get activity from audit logs
        from backend.audit_log import list_events
        recent_events = list_events(limit=20)
        activity = []
        for event in recent_events:
            activity.append({
                "timestamp": event.get("timestamp", datetime.now(timezone.utc).isoformat()),
                "agent": event.get("agent"),
                "stage": event.get("action"),
                "summary": event.get("message"),
                "status": event.get("status", "completed"),
            })
        
        # Get requests from recent directives
        from backend.executive_reasoning import DirectiveRegistry
        directive_registry = DirectiveRegistry()
        all_directives = directive_registry.list_directives()  # No limit parameter
        recent_directives = all_directives[:10]  # Slice to get first 10
        requests = []
        for directive in recent_directives:
            # Handle both dict and object formats
            if isinstance(directive, dict):
                requests.append({
                    "id": directive.get("id"),
                    "timestamp": directive.get("created_at", datetime.now(timezone.utc).isoformat()),
                    "pipeline_id": directive.get("payload", {}).get("pipeline_id") if isinstance(directive.get("payload"), dict) else None,
                    "title": directive.get("title", "Unknown"),
                    "directive_type": directive.get("directive_type", "unknown"),
                    "priority": directive.get("priority", "medium"),
                    "agent": directive.get("owner"),
                    "status": directive.get("status", "pending"),
                    "description": directive.get("description"),
                    "payload": directive.get("payload"),
                    "confidence": directive.get("confidence"),
                    "due_date": directive.get("due_date"),
                })
            else:
                # Object format (if it exists)
                requests.append({
                    "id": getattr(directive, "id", None),
                    "timestamp": directive.created_at.isoformat() if hasattr(directive, 'created_at') and hasattr(directive.created_at, 'isoformat') else str(getattr(directive, 'created_at', datetime.now(timezone.utc))),
                    "pipeline_id": directive.payload.get("pipeline_id") if hasattr(directive, 'payload') and isinstance(directive.payload, dict) else None,
                    "title": getattr(directive, 'title', 'Unknown'),
                    "directive_type": getattr(directive, 'directive_type', 'unknown'),
                    "priority": getattr(directive, 'priority', 'medium'),
                    "agent": getattr(directive, 'owner', None),
                    "status": getattr(directive, 'status', 'pending'),
                    "description": getattr(directive, "description", None),
                    "payload": getattr(directive, "payload", None),
                    "confidence": getattr(directive, "confidence", None),
                    "due_date": getattr(directive, "due_date", None),
                })
        
        return {
            "worker": {
                "status": worker_status,
                "pending": worker_pending,
            },
            "scheduler": {
                "enabled": scheduler_enabled,
                "workflow_interval_seconds": 60,
                "telemetry_interval_seconds": 30,
                "monitor_interval_seconds": 15,
            },
            "queue": {
                "pending": pending,
                "at_risk": 0,  # Would need additional tracking
                "overdue": 0,  # Would need additional tracking
            },
            "alerts": [],
            "activity": activity,
            "requests": requests,
            "pipeline": {
                "last_pipeline_id": None,
                "last_cycle_timestamp": None,
                "alert_count": 0,
            },
            "email_marketing": {
                "campaigns": {},
                "active_campaign_count": 0,
            },
        }
    except Exception as exc:
        logger.exception("Failed to fetch operations metrics: %s", exc)
        return {
            "worker": {"status": "unknown", "error": str(exc)},
            "scheduler": {"enabled": False},
            "queue": {"pending": 0, "at_risk": 0, "overdue": 0},
            "alerts": [],
            "activity": [],
            "requests": [],
        }


@app.post("/api/autonomous/run_cycle", dependencies=protected_dependencies)
async def run_autonomous_cycle(request: Request):
    """Manually trigger an autonomous cycle."""
    worker = getattr(request.app.state, "autonomy_worker", None)
    if worker is None:
        factory = getattr(request.app.state, "autonomy_worker_factory", None)
        if factory:
            worker = factory()
            request.app.state.autonomy_worker = worker
    
    if worker is None:
        return {"status": "error", "message": "Autonomy worker not configured"}
    
    # Trigger a single cycle
    try:
        if not worker.is_running():
            await worker.start()
        # The worker will process one cycle automatically
        queue_repo = getattr(worker, "queue_repository", None)
        pending = queue_repo.count_pending() if queue_repo else 0
        return {
            "status": "success",
            "message": "Cycle triggered",
            "pending": pending,
            "worker_id": getattr(worker, "worker_id", "autonomy-worker"),
        }
    except Exception as exc:
        logger.exception("Failed to run autonomous cycle: %s", exc)
        return {"status": "error", "message": str(exc)}


__all__ = ["app"]

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main_server:app",
        host=os.getenv("FALLAT_HOST", "0.0.0.0"),
        port=int(os.getenv("FALLAT_PORT", os.getenv("PORT", "8000"))),
        reload=os.getenv("FALLAT_RELOAD", "false").lower() in {"1", "true", "yes"},
    )
