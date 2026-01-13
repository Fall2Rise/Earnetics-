"""API routes for Experiment Registry."""

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.audit_log import log_event
from backend.departments.revenue_strategy_cell.experiment_registry import ExperimentRegistry
from backend.departments.revenue_strategy_cell.decision_rules import DecisionRules

router = APIRouter(prefix="/experiments", tags=["experiments"])


class UpdateExperimentRequest(BaseModel):
    status: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    decision: Optional[str] = None


@router.get("/active")
def get_active_experiments() -> Dict[str, Any]:
    """Get all active experiments."""
    registry = ExperimentRegistry()
    experiments = registry.list_active_experiments()
    
    return {
        "experiments": experiments,
        "count": len(experiments),
        "wip_limit": 2,
        "can_launch": registry.can_launch_experiment(),
    }


@router.post("/update")
def update_experiment(
    experiment_id: str, request: UpdateExperimentRequest
) -> Dict[str, Any]:
    """Update experiment status and results."""
    registry = ExperimentRegistry()
    
    exp = registry.update_experiment(
        experiment_id=experiment_id,
        status=request.status,
        result=request.result,
        decision=request.decision,
    )
    
    if not exp:
        raise HTTPException(status_code=404, detail=f"Experiment {experiment_id} not found")
    
    # Apply decision rules if result provided
    if request.result:
        rules = DecisionRules()
        decision = rules.evaluate_experiment(experiment_id, request.result)
        if decision:
            registry.update_experiment(experiment_id, decision=decision)
            exp = registry.get_experiment(experiment_id)
    
    log_event(
        "experiment.updated",
        agent="api",
        message=f"Experiment {experiment_id} updated",
        details={"status": request.status, "decision": exp.get("decision")},
    )
    
    return {"experiment": exp}

