"""Revenue Strategy Cell API - Idea Department Integration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.audit_log import log_event

router = APIRouter(prefix="/api/revenue-strategy", tags=["revenue-strategy"])

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
STRATEGY_FILE = PROJECT_ROOT / "backend" / "revenue_strategy_cell_output.json"


class RevenuePlayRequest(BaseModel):
    """Request to generate or update revenue plays."""
    market_context: Optional[Dict[str, Any]] = None
    target_revenue: Optional[float] = None
    days_remaining: Optional[int] = None


class RevenuePlayResponse(BaseModel):
    """Response with revenue strategy data."""
    scoreboard: Dict[str, Any]
    top_plays: List[Dict[str, Any]]
    dispatch_packets: Dict[str, List[Dict[str, Any]]]
    today_execution_sprint: List[Dict[str, Any]]
    fail_safes: Dict[str, Any]
    next_data_needed: List[Dict[str, Any]]


@router.get("/current", response_model=RevenuePlayResponse)
def get_current_strategy() -> RevenuePlayResponse:
    """Get the current revenue strategy from the Idea Department."""
    try:
        if not STRATEGY_FILE.exists():
            raise HTTPException(
                status_code=404,
                detail="Revenue strategy not found. Run strategy generation first."
            )
        
        with open(STRATEGY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        log_event(
            "revenue_strategy.accessed",
            agent="idea_department",
            message="Current strategy retrieved"
        )
        
        return RevenuePlayResponse(**data)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid strategy file: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading strategy: {e}")


@router.get("/scoreboard")
def get_scoreboard() -> Dict[str, Any]:
    """Get just the scoreboard metrics."""
    try:
        if not STRATEGY_FILE.exists():
            return {
                "date": "2026-01-06",
                "days_remaining": 25,
                "cash_collected_to_date": 0,
                "cash_remaining": 150000,
                "required_daily_cash_pace": 6000,
                "pipeline_target": 18000,
                "today_focus": []
            }
        
        with open(STRATEGY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return data.get("scoreboard", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading scoreboard: {e}")


@router.get("/plays")
def get_top_plays(limit: int = 3) -> Dict[str, Any]:
    """Get top revenue plays."""
    try:
        if not STRATEGY_FILE.exists():
            return {"plays": []}
        
        with open(STRATEGY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        plays = data.get("top_plays", [])[:limit]
        return {"plays": plays, "count": len(plays)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading plays: {e}")


@router.get("/plays/{play_id}")
def get_play_details(play_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific revenue play."""
    try:
        if not STRATEGY_FILE.exists():
            raise HTTPException(status_code=404, detail="Strategy file not found")
        
        with open(STRATEGY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        plays = data.get("top_plays", [])
        play = next((p for p in plays if p.get("play_id") == play_id), None)
        
        if not play:
            raise HTTPException(status_code=404, detail=f"Play '{play_id}' not found")
        
        return {"play": play}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading play: {e}")


@router.get("/dispatch/{department}")
def get_department_dispatch(department: str) -> Dict[str, Any]:
    """Get dispatch packets for a specific department."""
    try:
        if not STRATEGY_FILE.exists():
            return {"tasks": []}
        
        with open(STRATEGY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        dispatch = data.get("dispatch_packets", {})
        department_key = department.lower().replace(" ", "_")
        
        # Map common department names
        department_map = {
            "growth": "growth",
            "traffic": "growth",
            "domains": "domains_webops",
            "webops": "domains_webops",
            "domains_webops": "domains_webops",
            "community": "community",
            "tools": "tools_product",
            "product": "tools_product",
            "tools_product": "tools_product",
            "ops": "ops",
            "operations": "ops"
        }
        
        mapped_dept = department_map.get(department_key, department_key)
        tasks = dispatch.get(mapped_dept, [])
        
        return {
            "department": mapped_dept,
            "tasks": tasks,
            "count": len(tasks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading dispatch: {e}")


@router.get("/sprint/today")
def get_today_sprint() -> Dict[str, Any]:
    """Get today's execution sprint schedule."""
    try:
        if not STRATEGY_FILE.exists():
            return {"timeblocks": []}
        
        with open(STRATEGY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        sprint = data.get("today_execution_sprint", [])
        return {"timeblocks": sprint, "count": len(sprint)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading sprint: {e}")


@router.post("/execute/{play_id}")
def execute_play(play_id: str) -> Dict[str, Any]:
    """Mark a revenue play as executed and log the action."""
    try:
        if not STRATEGY_FILE.exists():
            raise HTTPException(status_code=404, detail="Strategy file not found")
        
        with open(STRATEGY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        plays = data.get("top_plays", [])
        play = next((p for p in plays if p.get("play_id") == play_id), None)
        
        if not play:
            raise HTTPException(status_code=404, detail=f"Play '{play_id}' not found")
        
        log_event(
            "revenue_strategy.play_executed",
            agent="idea_department",
            message=f"Executing play: {play_id}",
            details={"play_title": play.get("title"), "target_buyer": play.get("target_buyer")}
        )
        
        return {
            "status": "executed",
            "play_id": play_id,
            "play_title": play.get("title"),
            "message": f"Play '{play_id}' execution logged. Check dispatch packets for department tasks."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing play: {e}")


@router.get("/status")
def get_strategy_status() -> Dict[str, Any]:
    """Get overall status of the Revenue Strategy Cell."""
    try:
        exists = STRATEGY_FILE.exists()
        
        if not exists:
            return {
                "status": "not_initialized",
                "message": "Revenue Strategy Cell has not been initialized. Strategy file not found.",
                "file_path": str(STRATEGY_FILE)
            }
        
        with open(STRATEGY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        scoreboard = data.get("scoreboard", {})
        plays_count = len(data.get("top_plays", []))
        dispatch_count = sum(len(tasks) for tasks in data.get("dispatch_packets", {}).values())
        
        return {
            "status": "active",
            "scoreboard": scoreboard,
            "plays_count": plays_count,
            "dispatch_tasks_count": dispatch_count,
            "file_path": str(STRATEGY_FILE),
            "message": f"Revenue Strategy Cell active with {plays_count} plays and {dispatch_count} dispatch tasks"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error reading strategy file: {e}",
            "file_path": str(STRATEGY_FILE)
        }

