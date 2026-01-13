"""Email Campaign Management Router"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from backend.services.mailops_service import MailOpsService, Subscriber

router = APIRouter(prefix="/api/mailops", tags=["mailops"])
service = MailOpsService()

class SubscriberRequest(BaseModel):
    email: str
    first_name: Optional[str] = None
    tags: List[str] = []
    source: Optional[str] = "api"

class CampaignRequest(BaseModel):
    subject: str
    body: str
    target_segment: Dict[str, Any] = {}

@router.post("/subscribers")
def add_subscriber(req: SubscriberRequest):
    sub = Subscriber(
        email=req.email,
        first_name=req.first_name,
        tags=req.tags,
        source=req.source
    )
    return service.add_subscriber(sub)

@router.get("/subscribers")
def list_subscribers(limit: int = 50):
    return {"subscribers": service.list_subscribers(limit)}

@router.post("/campaigns")
def create_campaign(req: CampaignRequest):
    return service.create_campaign(req.subject, req.body, req.target_segment)

@router.post("/campaigns/{campaign_id}/send")
def send_campaign(campaign_id: int):
    try:
        return service.send_campaign(campaign_id)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/campaigns")
def list_campaigns(limit: int = 20):
    return {"campaigns": service.list_campaigns(limit)}

