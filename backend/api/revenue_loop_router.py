from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.main import RevenueFlowRunner

router = APIRouter(prefix="/api/revenue-loop", tags=["revenue-loop"])
_runner = RevenueFlowRunner()


class FlowRequest(BaseModel):
    flow_name: str = Field(default="revenue_loop")
    initial_state: Dict[str, Any] | None = None


@router.get("/flows")
def list_flows():
    return {"flows": list(_runner.flows.keys())}


@router.post("/run")
def run_flow(request: FlowRequest):
    try:
        result_state = _runner.run(
            flow_name=request.flow_name,
            initial_state=request.initial_state,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"status": "completed", "flow_name": request.flow_name, "state": result_state}
