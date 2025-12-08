"""Email Campaign Management Router"""
from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from backend.services.email_service import EmailService

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])

email_service = EmailService()


class EmailCampaignRequest(BaseModel):
    subject: str
    body: str
    recipients: List[str]
    template: str | None = None
    scheduled_time: str | None = None


class EmailCampaignResponse(BaseModel):
    campaign_id: str
    status: str
    recipients_count: int
    created_at: str


@router.post("/email", response_model=EmailCampaignResponse)
def create_email_campaign(request: EmailCampaignRequest) -> Dict[str, Any]:
    """Send an email campaign to a list of recipients."""
    try:
        campaign_id = f"campaign_{len(request.recipients)}_{request.subject[:10]}"
        
        # Send emails
        sent_count = 0
        for recipient in request.recipients:
            try:
                email_service.send_email(
                    to_email=recipient,
                    subject=request.subject,
                    body=request.body
                )
                sent_count += 1
            except Exception as e:
                print(f"Failed to send to {recipient}: {e}")
        
        return {
            "campaign_id": campaign_id,
            "status": "completed" if sent_count > 0 else "failed",
            "recipients_count": sent_count,
            "created_at": "2025-11-29T00:00:00Z"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/email")
def list_email_campaigns() -> Dict[str, Any]:
    """List recent email campaigns."""
    # Placeholder - would normally query from database
    return {
        "campaigns": [],
        "total": 0
    }


@router.get("/email/{campaign_id}/stats")
def get_campaign_stats(campaign_id: str) -> Dict[str, Any]:
    """Get statistics for a specific campaign."""
    return {
        "campaign_id": campaign_id,
        "sent": 0,
        "opened": 0,
        "clicked": 0,
        "bounced": 0
    }
