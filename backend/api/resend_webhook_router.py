"""Resend Webhook Handler for Email Events"""
from typing import Any, Dict
from fastapi import APIRouter, Request, HTTPException
from backend.services.mailops_service import MailOpsService
from backend.audit_log import log_event
import json

router = APIRouter(prefix="/api/webhooks/resend", tags=["webhooks"])
service = MailOpsService()

@router.post("/events")
async def resend_webhook(request: Request):
    """
    Handle Resend webhook events for email tracking.
    
    Events: email.sent, email.delivered, email.opened, email.clicked, 
            email.bounced, email.complained
    """
    try:
        payload = await request.json()
        event_type = payload.get("type")
        data = payload.get("data", {})
        
        email = data.get("to")
        subject = data.get("subject")
        
        # Map Resend event types to our event types
        event_mapping = {
            "email.sent": "sent",
            "email.delivered": "delivered",
            "email.opened": "opened",
            "email.clicked": "clicked",
            "email.bounced": "bounced",
            "email.complained": "complained"
        }
        
        our_event_type = event_mapping.get(event_type)
        
        if our_event_type and email:
            # Find campaign by subject (simplified - you may want better tracking)
            # In production, you'd embed campaign_id in email headers
            
            # Log the event
            log_event(
                f"mailops_{our_event_type}",
                email=email,
                subject=subject,
                event_type=event_type
            )
            
            # Update subscriber status if bounced or complained
            if our_event_type == "bounced":
                # Mark subscriber as bounced
                service._update_subscriber_status(email, "bounced")
            elif our_event_type == "complained":
                # Mark subscriber as unsubscribed
                service._update_subscriber_status(email, "unsubscribed")
        
        return {"status": "received"}
        
    except Exception as e:
        log_event("resend_webhook_error", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/health")
def webhook_health():
    """Health check for webhook endpoint"""
    return {"status": "ok", "webhook": "resend"}
