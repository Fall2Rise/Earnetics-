"""
Lead Management API Router
Provides endpoints for viewing and managing scraped leads, marketing recipients, and subscribers
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Optional
from datetime import datetime
import sqlite3
from backend.corporate_memory import BUSINESS_DB_PATH
from backend.services.lead_generation_service import LeadGenerationService
from backend.services.mailops_service import MailOpsService

router = APIRouter(prefix="/api/leads", tags=["lead-management"])

@router.get("/scraped")
def get_scraped_leads(
    limit: int = Query(100, ge=1, le=1000),
    qualified_only: bool = Query(False),
    added_to_list: bool = Query(None),
    source_domain: Optional[str] = None
) -> Dict:
    """Get all scraped leads"""
    try:
        lead_service = LeadGenerationService()
        leads = lead_service.get_scraped_leads(limit=limit, qualified_only=qualified_only)
        
        # Filter by added_to_list if specified
        if added_to_list is not None:
            leads = [l for l in leads if bool(l.get("added_to_list")) == added_to_list]
        
        # Filter by source_domain if specified
        if source_domain:
            leads = [l for l in leads if source_domain.lower() in l.get("source_domain", "").lower()]
        
        return {
            "leads": leads,
            "total": len(leads),
            "qualified_count": len([l for l in leads if l.get("qualified")]),
            "added_to_list_count": len([l for l in leads if l.get("added_to_list")])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scraped/stats")
def get_scraped_leads_stats() -> Dict:
    """Get statistics about scraped leads"""
    try:
        lead_service = LeadGenerationService()
        all_leads = lead_service.get_scraped_leads(limit=10000, qualified_only=False)
        
        # Group by source domain
        by_domain = {}
        for lead in all_leads:
            domain = lead.get("source_domain", "unknown")
            if domain not in by_domain:
                by_domain[domain] = {"total": 0, "qualified": 0, "added": 0}
            by_domain[domain]["total"] += 1
            if lead.get("qualified"):
                by_domain[domain]["qualified"] += 1
            if lead.get("added_to_list"):
                by_domain[domain]["added"] += 1
        
        return {
            "total_leads": len(all_leads),
            "qualified_leads": len([l for l in all_leads if l.get("qualified")]),
            "added_to_list": len([l for l in all_leads if l.get("added_to_list")]),
            "by_domain": by_domain
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scraped/{lead_id}/qualify")
def qualify_lead(lead_id: int, qualified: bool = True) -> Dict:
    """Mark a lead as qualified or unqualified"""
    try:
        lead_service = LeadGenerationService()
        result = lead_service.qualify_lead(lead_id, qualified)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scraped/{lead_id}/add-to-list")
def add_lead_to_list(lead_id: int) -> Dict:
    """Add a scraped lead to the email subscriber list"""
    try:
        lead_service = LeadGenerationService()
        result = lead_service.add_leads_to_email_list(lead_ids=[lead_id])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/marketing/recipients")
def get_marketing_recipients(
    limit: int = Query(100, ge=1, le=1000),
    campaign_id: Optional[int] = None
) -> Dict:
    """Get all emails that have been sent marketing campaigns"""
    try:
        mailops = MailOpsService()
        
        # Get all campaigns
        campaigns = mailops.list_campaigns(limit=1000)
        
        # Get recipients from campaign events
        with sqlite3.connect(BUSINESS_DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = """
                SELECT DISTINCT
                    subscriber_email as email,
                    campaign_id,
                    timestamp as sent_at,
                    event_type
                FROM mailops_events
                WHERE event_type = 'sent'
            """
            params = []
            if campaign_id:
                query += " AND campaign_id = ?"
                params.append(campaign_id)
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            recipients = [dict(row) for row in cursor.fetchall()]
        
        # Enrich with campaign info
        campaign_map = {c["id"]: c for c in campaigns}
        for recipient in recipients:
            campaign = campaign_map.get(recipient.get("campaign_id"))
            if campaign:
                recipient["campaign_subject"] = campaign.get("subject")
                recipient["campaign_name"] = campaign.get("subject", "Unknown Campaign")
        
        return {
            "recipients": recipients,
            "total": len(recipients),
            "unique_emails": len(set(r["email"] for r in recipients))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/marketing/recipients/stats")
def get_marketing_recipients_stats() -> Dict:
    """Get statistics about marketing recipients"""
    try:
        mailops = MailOpsService()
        campaigns = mailops.list_campaigns(limit=1000)
        
        with sqlite3.connect(BUSINESS_DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get all sent emails
            cursor.execute("""
                SELECT 
                    campaign_id,
                    COUNT(DISTINCT subscriber_email) as unique_recipients,
                    COUNT(*) as total_sent
                FROM mailops_events
                WHERE event_type = 'sent'
                GROUP BY campaign_id
            """)
            campaign_stats = [dict(row) for row in cursor.fetchall()]
            
            # Get opens and clicks
            cursor.execute("""
                SELECT 
                    event_type,
                    COUNT(DISTINCT subscriber_email) as unique_count,
                    COUNT(*) as total_count
                FROM mailops_events
                WHERE event_type IN ('opened', 'clicked')
                GROUP BY event_type
            """)
            engagement_stats = {row["event_type"]: dict(row) for row in cursor.fetchall()}
        
        return {
            "total_campaigns": len(campaigns),
            "campaign_stats": campaign_stats,
            "engagement": engagement_stats,
            "total_sent": sum(s["total_sent"] for s in campaign_stats)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/subscribers")
def get_subscribers(
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    source: Optional[str] = None,
    tag: Optional[str] = None
) -> Dict:
    """Get all subscribers, optionally filtered by subscription category"""
    try:
        mailops = MailOpsService()
        subscribers = mailops.list_subscribers(limit=limit)
        
        # Filter by status
        if status:
            subscribers = [s for s in subscribers if s.get("status") == status]
        
        # Filter by source
        if source:
            subscribers = [s for s in subscribers if source.lower() in (s.get("source") or "").lower()]
        
        # Filter by tag
        if tag:
            subscribers = [s for s in subscribers if tag in (s.get("tags") or [])]
        
        # Group by subscription category (source or tags)
        by_category = {}
        for sub in subscribers:
            # Determine category from source or tags
            category = "General"
            if sub.get("source"):
                if "scraped" in sub.get("source", "").lower():
                    category = "Scraped Leads"
                elif "campaign" in sub.get("source", "").lower():
                    category = "Campaign Signups"
                elif "manual" in sub.get("source", "").lower():
                    category = "Manual Additions"
                else:
                    category = sub.get("source", "General")
            
            # Also check tags for categories
            tags = sub.get("tags", [])
            if tags:
                for t in tags:
                    if "product" in t.lower() or "subscription" in t.lower():
                        category = f"Product: {t}"
                        break
            
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(sub)
        
        return {
            "subscribers": subscribers,
            "total": len(subscribers),
            "by_category": {k: len(v) for k, v in by_category.items()},
            "categories": by_category
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/subscribers/stats")
def get_subscribers_stats() -> Dict:
    """Get statistics about subscribers"""
    try:
        mailops = MailOpsService()
        all_subscribers = mailops.list_subscribers(limit=10000)
        
        # Group by status
        by_status = {}
        for sub in all_subscribers:
            status = sub.get("status", "unknown")
            by_status[status] = by_status.get(status, 0) + 1
        
        # Group by source
        by_source = {}
        for sub in all_subscribers:
            source = sub.get("source", "unknown")
            by_source[source] = by_source.get(source, 0) + 1
        
        # Group by tags
        by_tag = {}
        for sub in all_subscribers:
            tags = sub.get("tags", [])
            for tag in tags:
                by_tag[tag] = by_tag.get(tag, 0) + 1
        
        return {
            "total_subscribers": len(all_subscribers),
            "by_status": by_status,
            "by_source": by_source,
            "by_tag": by_tag,
            "active_count": by_status.get("active", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
