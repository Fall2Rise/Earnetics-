from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.strategic_vision_assembly import StrategicVisionAssembly

# Single shared instance of the strategic engine
assembly = StrategicVisionAssembly()

router = APIRouter(
    prefix="/api/strategy",
    tags=["strategy"],
)


class StrategicVisionRequest(BaseModel):
    """Request body for generating a strategic vision."""
    time_horizon: str = "5_year"  # e.g. "12_months", "3_year", "5_year"


class StrategicDecisionRequest(BaseModel):
    """Request body for coordinating a C-suite decision."""
    decision_type: str = "market_expansion"  # e.g. "market_expansion", "technology_investment"
    target_market: Optional[str] = None
    payload: Dict[str, Any] = {}  # extra context (funnels, offers, etc.)


@router.post("/vision/generate")
async def generate_strategic_vision(req: StrategicVisionRequest) -> Dict[str, Any]:
    """
    Generate a comprehensive strategic vision for Earnetics.

    Calls StrategicVisionAssembly.generate_comprehensive_strategic_vision()
    and returns the full plan: goals, allocations, roadmap, metrics, etc.
    """
    try:
        vision = await assembly.generate_comprehensive_strategic_vision(req.time_horizon)
        return vision
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate vision: {exc}") from exc


@router.post("/decision/coordinate")
async def coordinate_c_suite_decision(req: StrategicDecisionRequest) -> Dict[str, Any]:
    """
    Run a full C-suite coordination cycle for a strategic decision.

    CEO: high-level decision
    CFO: financial risk and budget view
    COO: operational readiness
    """
    context: Dict[str, Any] = {"decision_type": req.decision_type}
    if req.target_market:
        context["target_market"] = req.target_market
    if req.payload:
        context.update(req.payload)

    try:
        result = await assembly.coordinate_c_suite_decision(context)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to coordinate decision: {exc}") from exc


@router.get("/dashboard")
def strategic_dashboard() -> Dict[str, Any]:
    """
    High-level strategic dashboard for Earnetics.

    Aggregates CEO/CFO/COO views into one payload.
    """
    try:
        return assembly.get_strategic_vision_dashboard()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load strategic dashboard: {exc}") from exc
