from __future__ import annotations
from typing import Any, Dict
from backend.services.lead_service import lead_service
from backend.services.content_service import content_service
from backend.services.campaign_service import campaign_service

def add_lead_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool: Add a lead to the CRM.
    Args: {"email": "...", "name": "...", "source": "..."}
    """
    email = args.get("email")
    if not email:
        return {"error": "Email is required"}
    
    return lead_service.add_lead(
        email=email,
        name=args.get("name"),
        source=args.get("source", "agent_tool"),
        metadata=args.get("metadata")
    )

def save_content_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool: Save generated content (blog, ad copy, etc.)
    Args: {"title": "...", "content": "...", "type": "..."}
    """
    title = args.get("title") or "Untitled Content"
    content = args.get("content")
    if not content:
        return {"error": "Content body is required"}
        
    return content_service.save_content(
        title=title,
        content=content,
        type=args.get("type", "text"),
        status="draft"
    )

def create_campaign_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool: Create a marketing campaign.
    Args: {"name": "...", "type": "email|social", "schedule_at": "..."}
    """
    name = args.get("name")
    if not name:
        return {"error": "Campaign name is required"}
        
    return campaign_service.create_campaign(
        name=name,
        type=args.get("type", "email"),
        content_asset_id=args.get("content_asset_id"),
        schedule_at=args.get("schedule_at")
    )
