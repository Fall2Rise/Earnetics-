"""
100x Content Engine Router
API endpoints for the Content Engine.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from backend.services.content_engine_service import ContentEngineService

router = APIRouter(prefix="/api/content-engine", tags=["content-engine"])
service = ContentEngineService()

class GenerateRequest(BaseModel):
    topic: str
    tone: str = "viral"

class RepurposeRequest(BaseModel):
    master_content_id: str
    master_text: str

class DistributeRequest(BaseModel):
    asset_id: str
    platforms: List[str]

@router.get("/list")
async def list_content(type: Optional[str] = None, limit: int = 50):
    """List generated content assets."""
    from backend.services.content_service import content_service
    return {"assets": content_service.list_content(type, limit)}

@router.post("/generate")
async def generate_master(request: GenerateRequest):
    """Generate master long-form content."""
    try:
        return await service.generate_master_content(request.topic, request.tone)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/repurpose")
async def repurpose_content(request: RepurposeRequest):
    """Repurpose master content into multi-platform formats."""
    try:
        return await service.repurpose_content(request.master_content_id, request.master_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/distribute")
async def distribute_content(request: DistributeRequest):
    """Distribute content to selected platforms."""
    # In a real app, we'd fetch the assets by ID. Here we mock it.
    mock_assets = {"id": request.asset_id, "type": "video"} 
    try:
        return await service.distribute_content(mock_assets, request.platforms)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/{content_id}")
async def get_analytics(content_id: str):
    """Get engagement analytics for a piece of content."""
    try:
        return await service.get_analytics(content_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
