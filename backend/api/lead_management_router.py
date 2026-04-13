from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from backend.services.lead_service import lead_service

router = APIRouter(prefix="/api/leads", tags=["leads"])

class LeadCreate(BaseModel):
    email: str
    name: Optional[str] = None
    source: str = "api"
    metadata: Optional[dict] = {}

# --- Generic Leads ---

@router.get("/")
def get_leads(status: Optional[str] = None, limit: int = 50):
    return {"leads": lead_service.get_leads(status, limit)}

@router.post("/")
def create_lead(lead: LeadCreate):
    return lead_service.add_lead(lead.email, lead.name, lead.source, lead.metadata)

# --- Scraped Leads (Frontend Panel) ---

@router.get("/scraped")
def get_scraped_leads(
    limit: int = 50,
    qualified_only: bool = False,
    added_to_list: Optional[bool] = None,
    source_domain: Optional[str] = None
):
    """Get scraped leads with filtering."""
    return lead_service.get_scraped_leads(limit, qualified_only, added_to_list, source_domain)

@router.get("/scraped/stats")
def get_scraped_stats():
    """Get statistics for scraped leads."""
    return lead_service.get_scraped_stats()

@router.post("/scraped/{lead_id}/qualify")
def qualify_lead(lead_id: int, qualified: bool = Query(True)):
    """Mark a lead as qualified."""
    success = lead_service.qualify_lead(lead_id, qualified)
    return {"status": "success", "lead_id": lead_id, "qualified": qualified}

@router.post("/scraped/{lead_id}/add-to-list")
def add_lead_to_list(lead_id: int):
    """Mark a lead as added to the marketing list."""
    success = lead_service.add_to_list(lead_id)
    return {"status": "success", "lead_id": lead_id, "added": True}

# --- Marketing Recipients (Placeholders) ---

@router.get("/marketing/recipients")
def get_marketing_recipients(limit: int = 50, campaign_id: Optional[int] = None):
    return {"recipients": [], "total": 0, "unique_emails": 0}

@router.get("/marketing/recipients/stats")
def get_marketing_stats():
    return {
        "total_campaigns": 0,
        "campaign_stats": [],
        "engagement": {},
        "total_sent": 0
    }

# --- Subscribers (Placeholders) ---

@router.get("/subscribers")
def get_subscribers(
    limit: int = 50,
    status: Optional[str] = None,
    source: Optional[str] = None,
    tag: Optional[str] = None
):
    return lead_service.get_subscribers(limit, status, source, tag)

@router.get("/subscribers/stats")
def get_subscribers_stats():
    return lead_service.get_subscribers_stats()
