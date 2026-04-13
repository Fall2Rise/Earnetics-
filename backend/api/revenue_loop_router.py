from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Use the newer runner and store
from backend.ewc.revenue_loop import RevenueLoopRunner
from backend.ewc.revenue_store import RevenueCycleStore

router = APIRouter(prefix="/api/revenue-loop", tags=["revenue-loop"])

# Initialize store
_store = RevenueCycleStore()
# Runner is stateless-ish, can init on demand or globally if config static
_runner = RevenueLoopRunner()

class RevenueLoopRunRequest(BaseModel):
    market_context: Dict[str, Any] = Field(default_factory=lambda: {"focus": "affiliate_marketing"})

class InjectToolsRequest(BaseModel):
    loop_id: Optional[str] = None
    tools: List[str]

@router.get("/history")
def list_revenue_history(limit: int = 50):
    """List historical revenue loop cycles."""
    return {"cycles": _store.list_cycles(limit=limit)}

@router.post("/run")
def run_revenue_loop(request: RevenueLoopRunRequest):
    """Trigger a new revenue loop execution."""
    try:
        # Run the loop
        result = _runner.run(market_context=request.market_context)
        
        # Convert dataclass to dict for storage
        # The result object has attributes: product_roadmap, validated_opportunity, etc.
        cycle_data = {
            "product_roadmap": result.product_roadmap,
            "validated_opportunity": result.validated_opportunity,
            "automation_module_spec": result.automation_module_spec,
            "approved_module": result.approved_module,
            "revenue_play_report": result.revenue_play_report
        }
        
        # Store the result
        record = _store.record_cycle(request.market_context, cycle_data)
        
        return {"status": "completed", "cycle": record}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@router.post("/inject-tools")
def inject_tools(request: InjectToolsRequest):
    """
    Configuration endpoint to 'inject' tools into the revenue loop.
    Currently updates a runtime config or logs the intent.
    """
    # In a real implementation, this might update agents.yaml or a database config
    # For now, we'll log it and pretend it persisted for the simulation
    print(f"Injecting tools {request.tools} into loop {request.loop_id}")
    return {
        "status": "success", 
        "message": f"Tools {request.tools} injected into revenue loop.",
        "active_tools": request.tools
    }
