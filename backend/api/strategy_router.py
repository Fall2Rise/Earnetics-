from fastapi import APIRouter, HTTPException
from backend.services.strategy_service import (
    run_strategic_vision,
    run_csuite_coordination,
    run_revenue_cycle,
)

router = APIRouter(prefix="/api/strategy", tags=["strategy"])

@router.post("/vision/run")
async def run_vision():
    try:
        result = await run_strategic_vision()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/csuite/run")
async def run_csuite():
    try:
        result = await run_csuite_coordination()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/revenue_cycle/run")
async def run_revenue():
    try:
        result = await run_revenue_cycle()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
