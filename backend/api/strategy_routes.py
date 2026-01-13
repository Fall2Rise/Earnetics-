"""API routes for Revenue Strategy Cell."""

from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.audit_log import log_event
from backend.departments.revenue_strategy_cell import Dispatcher, StrategyRunner, StrategyStore

router = APIRouter(prefix="/strategy", tags=["strategy"])


class RunStrategyRequest(BaseModel):
    cash_collected_to_date: float = 0.0
    goal_deadline: str = "2026-01-31"
    force: bool = False
    notes: Optional[str] = None


@router.post("/run")
def run_strategy(request: RunStrategyRequest) -> Dict[str, Any]:
    """Run one strategy generation cycle."""
    try:
        runner = StrategyRunner()
        result = runner.run_cycle(
            cash_collected_to_date=request.cash_collected_to_date,
            goal_deadline=request.goal_deadline,
            force=request.force,
            notes=request.notes,
        )
        
        # If successful, dispatch tasks
        if result.get("status") == "completed" and "output" in result:
            dispatcher = Dispatcher()
            dispatch_result = dispatcher.dispatch_run(
                result["run_id"],
                result["output"].get("dispatch_packets", {}),
                force=request.force,
            )
            result["dispatch_result"] = dispatch_result
        
        log_event(
            "strategy.run",
            agent="strategy_cell",
            message=f"Strategy cycle run: {result.get('run_id')}",
            details={"status": result.get("status"), "duration_ms": result.get("duration_ms")},
        )
        
        return result
    except Exception as e:
        log_event(
            "strategy.run",
            agent="strategy_cell",
            status="error",
            message=str(e),
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/latest")
def get_latest_strategy() -> Dict[str, Any]:
    """Get the latest strategy run."""
    store = StrategyStore()
    latest = store.get_latest_run()
    
    if not latest:
        raise HTTPException(status_code=404, detail="No strategy runs found")
    
    import json
    output_json = json.loads(latest["output_json"])
    
    return {
        "run_id": latest["run_id"],
        "created_at": latest["created_at"],
        "status": latest["status"],
        "output": output_json,
    }


@router.get("/runs")
def list_runs(limit: int = 20) -> Dict[str, Any]:
    """List recent strategy runs."""
    store = StrategyStore()
    runs = store.list_runs(limit=limit)
    
    return {
        "runs": runs,
        "count": len(runs),
    }


@router.get("/plays")
def get_plays(run_id: Optional[str] = None) -> Dict[str, Any]:
    """Get play cards, optionally filtered by run_id."""
    store = StrategyStore()
    plays = store.get_plays(run_id=run_id)
    
    return {
        "plays": plays,
        "count": len(plays),
    }


@router.get("/experiments")
def get_experiments(run_id: Optional[str] = None) -> Dict[str, Any]:
    """Get experiments, optionally filtered by run_id."""
    store = StrategyStore()
    experiments = store.get_experiments(run_id=run_id)
    
    return {
        "experiments": experiments,
        "count": len(experiments),
    }


@router.get("/dispatch")
def get_dispatch_packets(
    run_id: Optional[str] = None, department: Optional[str] = None
) -> Dict[str, Any]:
    """Get dispatch packets, optionally filtered."""
    store = StrategyStore()
    packets = store.get_dispatch_packets(run_id=run_id, department=department)
    
    return {
        "packets": packets,
        "count": len(packets),
    }
