# backend/routes/strategy_routes.py
from typing import Any, Dict
from fastapi import APIRouter
from pydantic import BaseModel

from backend.strategic_vision_assembly import strategic_vision_assembly

router = APIRouter(
    prefix="/api/strategy",
    tags=["strategy"],
)


class VisionRequest(BaseModel):
    time_horizon: str = "3_year"  # "1_year", "3_year", "5_year"


class DecisionRequest(BaseModel):
    decision_type: str
    payload: Dict[str, Any] = {}


@router.get("/dashboard")
def get_strategy_dashboard() -> Dict[str, Any]:
    """High-level strategic/financial/ops health for the Earnetics cockpit."""
    return strategic_vision_assembly.get_strategic_vision_dashboard()


@router.post("/vision")
async def generate_vision(req: VisionRequest) -> Dict[str, Any]:
    """Generate a fresh comprehensive vision snapshot."""
    return await strategic_vision_assembly.generate_comprehensive_strategic_vision(
        time_horizon=req.time_horizon
    )


@router.post("/coordinate-decision")
async def coordinate_decision(req: DecisionRequest) -> Dict[str, Any]:
    """
    Send a strategic decision context (e.g. 'market_expansion', 'offer_focus')
    and get a coordinated CEO/CFO/COO answer.
    """
    decision = {"decision_type": req.decision_type, **req.payload}
    return await strategic_vision_assembly.coordinate_c_suite_decision(decision)
