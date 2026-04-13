from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict
from pydantic import BaseModel
from backend.services.campaign_service import campaign_service

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])

class CampaignCreate(BaseModel):
    name: str
    type: str = "email"
    content_asset_id: Optional[int] = None
    target_filter: Optional[Dict] = {}
    schedule_at: Optional[str] = None

@router.get("/")
def list_campaigns(status: Optional[str] = None, limit: int = 50):
    return {"campaigns": campaign_service.list_campaigns(status, limit)}

@router.post("/")
def create_campaign(campaign: CampaignCreate):
    return campaign_service.create_campaign(
        campaign.name, 
        campaign.type, 
        campaign.content_asset_id, 
        campaign.target_filter, 
        campaign.schedule_at
    )

@router.post("/{campaign_id}/start")
def start_campaign(campaign_id: int):
    # In a real system, this would trigger the CampaignRunner worker
    campaign_service.update_status(campaign_id, "active")
    return {"status": "started", "id": campaign_id}

@router.post("/{campaign_id}/pause")
def pause_campaign(campaign_id: int):
    campaign_service.update_status(campaign_id, "paused")
    return {"status": "paused", "id": campaign_id}
