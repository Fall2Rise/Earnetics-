from __future__ import annotations

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Header, Request

from backend import auth
from backend.corporate_memory import CorporateMemory
from autonomous.workflow_queue import WorkflowQueueRepository
from datetime import datetime
from backend.ewc import (
    CORE_PLAYS_SEED,
    ExecutionRouter,
    OpportunityEngine,
    RevenueCycleStore,
    RiskGuard,
    SensingHub,
    WealthCovenant,
    WealthFeedback,
    WealthKnowledgeGraph,
    WealthPortfolio,
    WealthRunStore,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/wealth", tags=["wealth"])


def verify_auth(
    x_api_token: str | None = Header(default=None, convert_underscores=False, alias="X-Api-Token"),
    x_fallat_token: str | None = Header(default=None, convert_underscores=False, alias="X-Fallat-Token"),
) -> None:
    token = x_api_token or x_fallat_token
    if not token:
        return  # allow local/unauthenticated when global deps already enforced
    if not auth.verify_token(token):
        raise HTTPException(status_code=401, detail="Invalid API token")


def rate_limit(request: Request) -> None:
    limiter = getattr(request.app.state, "rate_limiter", None)
    if limiter is None:
        return
    if not limiter.allow("wealth"):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")


def get_cycle_store() -> RevenueCycleStore:
    if not hasattr(router, "_cycle_store_instance"):
        router._cycle_store_instance = RevenueCycleStore()  # type: ignore[attr-defined]
    return router._cycle_store_instance  # type: ignore[attr-defined]


class EarneticsWealthCore:
    """Singleton facade for the Earnetics Wealth Core stack."""

    def __init__(self) -> None:
        self.covenant = WealthCovenant()
        self.sensing_hub = SensingHub()
        self.knowledge_graph = WealthKnowledgeGraph()
        self.opportunity_engine = OpportunityEngine(self.sensing_hub, self.knowledge_graph)
        self.portfolio = WealthPortfolio()
        self.execution_router = ExecutionRouter(self.portfolio)
        self.feedback = WealthFeedback(self.portfolio)
        self.risk_guard = RiskGuard(self.covenant)
        self._seed_core_plays()

    def _seed_core_plays(self) -> None:
        seeded = self.portfolio.seed_core_plays(CORE_PLAYS_SEED)
        if seeded > 0:
            logger.info("EWC initialized with %d core plays", seeded)

    def status(self) -> Dict[str, Any]:
        return self.portfolio.summary()

    def list_plays(self) -> List[Dict[str, Any]]:
        return self.portfolio.list_plays()

    def get_play(self, play_id: str) -> Dict[str, Any] | None:
        return self.portfolio.get_play(play_id)

    def list_opportunities(self) -> List[Dict[str, Any]]:
        return self.opportunity_engine.list_opportunities()

    def launch_play(self, play_definition: Dict[str, Any]) -> Dict[str, Any]:
        risk_result = self.risk_guard.validate_play(play_definition)
        if not risk_result["approved"]:
            return risk_result
        play = self.portfolio.add_play(play_definition)
        self.execution_router.launch_play(play)
        return {"status": "launched", "play": play}

    def update_play(self, play_id: str, action: str) -> Dict[str, Any]:
        if action == "pause":
            play = self.portfolio.pause_play(play_id)
        elif action == "boost":
            play = self.portfolio.boost_play(play_id)
        else:
            raise ValueError("Unsupported action")
        return {"status": action, "play": play}

    def get_core_plays(self) -> List[Dict[str, Any]]:
        return CORE_PLAYS_SEED

    def validate_play_for_execution(self, play: Dict[str, Any]) -> None:
        risk_result = self.risk_guard.validate_play(play)
        if not risk_result["approved"]:
            raise HTTPException(
                status_code=422,
                detail=f"Play validation failed: {risk_result.get('reason', 'Unknown reason')}"
            )


def get_ewc() -> EarneticsWealthCore:
    if not hasattr(router, "_ewc_instance"):
        router._ewc_instance = EarneticsWealthCore()  # type: ignore[attr-defined]
    return router._ewc_instance  # type: ignore[attr-defined]


def get_run_store() -> WealthRunStore:
    if not hasattr(router, "_run_store_instance"):
        router._run_store_instance = WealthRunStore()  # type: ignore[attr-defined]
    return router._run_store_instance  # type: ignore[attr-defined]


def get_queue_repo() -> WorkflowQueueRepository:
    if not hasattr(router, "_queue_repo"):
        router._queue_repo = WorkflowQueueRepository()  # type: ignore[attr-defined]
    return router._queue_repo  # type: ignore[attr-defined]


def get_corporate_memory() -> CorporateMemory:
    if not hasattr(router, "_corp_mem"):
        router._corp_mem = CorporateMemory()  # type: ignore[attr-defined]
    return router._corp_mem  # type: ignore[attr-defined]


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


def _enqueue_wealth_run_steps(play: Dict[str, Any], run: Dict[str, Any]) -> None:
    queue_repo = get_queue_repo()
    corp_mem = get_corporate_memory()
    channels = play.get("execution_plan", {}).get("channels", [])
    department = _channel_to_department(channels if isinstance(channels, list) else [])
    priority = (play.get("risk_tier") or "medium").lower()
    now = datetime.utcnow().isoformat()

    for step in run.get("steps", []):
        title = f"Wealth: {play.get('name')} - {step.get('key') or 'step'}"
        task = corp_mem.create_task(
            {
                "objective_id": None,
                "title": title,
                "department": department,
                "assigned_agent": step.get("agent"),
                "status": "pending",
                "priority": priority if priority in {"critical", "high", "medium", "low"} else "medium",
                "due_date": None,
                "description": step.get("desc") or play.get("description"),
                "dependencies": [],
                "metadata": {
                    "play_id": play.get("id"),
                    "run_id": run.get("run_id"),
                    "step_key": step.get("key"),
                    "channels": channels,
                    "tags": play.get("tags", []),
                },
                "created_at": now,
                "updated_at": now,
            }
        )
        queue_repo.enqueue_from_task(task)


def _enqueue_revenue_cycle_tasks(market_context: Dict[str, Any], cycle: Dict[str, Any]) -> None:
    queue_repo = get_queue_repo()
    corp_mem = get_corporate_memory()
    tasks: List[Dict[str, Any]] = []

    tasks.append(
        {
            "title": "Activate revenue play - marketing launch",
            "department": "marketing",
            "priority": "high",
            "description": "Launch campaigns from revenue play report",
            "metadata": {"market_context": market_context, "cycle": cycle},
        }
    )
    tasks.append(
        {
            "title": "Product delivery - revenue module",
            "department": "product",
            "priority": "medium",
            "description": "Implement automation module spec and approved module",
            "metadata": {"cycle": cycle},
        }
    )
    tasks.append(
        {
            "title": "Operations & finance checks",
            "department": "operations",
            "priority": "medium",
            "description": "Validate operational readiness and billing hooks",
            "metadata": {"cycle": cycle},
        }
    )

    for task_def in tasks:
        task = corp_mem.create_task(
            {
                "objective_id": None,
                "title": task_def["title"],
                "department": task_def["department"],
                "assigned_agent": None,
                "status": "pending",
                "priority": task_def["priority"],
                "due_date": None,
                "description": task_def.get("description"),
                "dependencies": [],
                "metadata": task_def.get("metadata", {}),
            }
        )
        queue_repo.enqueue_from_task(task)


@router.get("/status")
def wealth_status(
    _: None = Depends(verify_auth),
    __: None = Depends(rate_limit),
) -> Dict[str, Any]:
    return get_ewc().status()


@router.get("/plays")
def list_wealth_plays(
    _: None = Depends(verify_auth),
    __: None = Depends(rate_limit),
) -> Dict[str, Any]:
    plays = get_ewc().list_plays()
    return {"plays": plays, "count": len(plays)}


@router.get("/opportunities")
def list_wealth_opportunities(
    _: None = Depends(verify_auth),
    __: None = Depends(rate_limit),
) -> Dict[str, Any]:
    opportunities = get_ewc().list_opportunities()
    return {"opportunities": opportunities, "count": len(opportunities)}


@router.post("/plays/launch")
def launch_wealth_play(
    request: Dict[str, Any],
    _: None = Depends(verify_auth),
    __: None = Depends(rate_limit),
) -> Dict[str, Any]:
    try:
        return get_ewc().launch_play(request)
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Failed to launch wealth play")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/plays/{play_id}/pause")
def pause_wealth_play(
    play_id: str,
    _: None = Depends(verify_auth),
    __: None = Depends(rate_limit),
) -> Dict[str, Any]:
    try:
        return get_ewc().update_play(play_id, "pause")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Failed to pause wealth play")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/plays/{play_id}/boost")
def boost_wealth_play(
    play_id: str,
    _: None = Depends(verify_auth),
    __: None = Depends(rate_limit),
) -> Dict[str, Any]:
    try:
        return get_ewc().update_play(play_id, "boost")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Failed to boost wealth play")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/core_plays")
def get_core_plays(
    _: None = Depends(verify_auth),
    __: None = Depends(rate_limit),
) -> Dict[str, Any]:
    core_plays = get_ewc().get_core_plays()
    return {"core_plays": core_plays, "count": len(core_plays)}


@router.post("/autonomous_cycle")
def run_autonomous_cycle(
    market_context: Dict[str, Any],
    _: None = Depends(verify_auth),
    __: None = Depends(rate_limit),
) -> Dict[str, Any]:
    try:
        portfolio = get_ewc().portfolio
        result = portfolio.run_autonomous_cycle(market_context)
        persisted = get_cycle_store().record_cycle(market_context, result)
        _enqueue_revenue_cycle_tasks(market_context, persisted)
        return {"status": "completed", "cycle": persisted}
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Failed to run autonomous revenue cycle")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/plays/{play_id}/execute")
def execute_wealth_play(
    play_id: str,
    _: None = Depends(verify_auth),
    __: None = Depends(rate_limit),
) -> Dict[str, Any]:
    try:
        ewc = get_ewc()
        run_store = get_run_store()

        play = ewc.get_play(play_id)
        if not play:
            raise HTTPException(status_code=404, detail=f"Play {play_id} not found")

        ewc.validate_play_for_execution(play)

        run = run_store.create_run(play)
        _enqueue_wealth_run_steps(play, run)

        return run
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to execute wealth play")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/plays/{play_id}/runs")
def list_play_runs(
    play_id: str,
    _: None = Depends(verify_auth),
    __: None = Depends(rate_limit),
) -> Dict[str, Any]:
    try:
        ewc = get_ewc()
        run_store = get_run_store()

        play = ewc.get_play(play_id)
        if not play:
            raise HTTPException(status_code=404, detail=f"Play {play_id} not found")

        runs = run_store.list_runs_for_play(play_id)

        return {"play_id": play_id, "runs": runs}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to list play runs")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/runs/{run_id}")
def get_run(
    run_id: str,
    _: None = Depends(verify_auth),
    __: None = Depends(rate_limit),
) -> Dict[str, Any]:
    try:
        run_store = get_run_store()

        run = run_store.get_run(run_id)
        if not run:
            raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

        return {"run": run}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to get run")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
