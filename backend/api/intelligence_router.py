"""
Intelligence Department API Router
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime

from fastapi import Request, Header, HTTPException
from backend import auth

async def verify_request_token(
    request: Request,
    x_fallat_token: Optional[str] = Header(default=None, convert_underscores=False, alias="X-Fallat-Token"),
    x_api_token: Optional[str] = Header(default=None, convert_underscores=False, alias="X-Api-Token"),
) -> None:
    """Verify request token - allows localhost without token"""
    if request.client and request.client.host in {"127.0.0.1", "localhost", "::1"}:
        return
    token = x_fallat_token or x_api_token or request.query_params.get("token")
    if token and not auth.verify_token(token):
        raise HTTPException(status_code=401, detail="Invalid or missing API token")
from earnetics.intelligence.scoring import OpportunityScorer
from earnetics.intelligence.triage import TriageWorkflow
from earnetics.intelligence.synthesis import SynthesisWorkflow
from earnetics.intelligence.experiments import ExperimentsWorkflow
from earnetics.intelligence.backlog import OpportunityBacklog
from earnetics.intelligence.decision_packets import DecisionPacketGenerator
from earnetics.revenue_loop.opportunity import Opportunity
from earnetics.truth_library.publisher import TruthLibraryPublisher
from earnetics.truth_library.schema import AssetType, AssetStatus
from earnetics.lead_vault.store import LeadVaultStore
from earnetics.revenue_loop.telemetry import KPITelemetry

router = APIRouter(prefix="/api/intelligence", tags=["intelligence"])

protected_dependencies = [Depends(verify_request_token)]


@router.get("/signals", dependencies=protected_dependencies)
async def get_signals(limit: int = 20, priority_min: int = 1):
    """Get ranked signals for Signal Dashboard"""
    try:
        from earnetics.knowledge_store.store import KnowledgeStore
        store = KnowledgeStore()
        
        # Get recent radio items (signals)
        results = store.search("radio:", limit=limit)
        
        signals = []
        for record in results:
            if record.raw and record.raw.get("priority", 0) >= priority_min:
                signals.append({
                    "id": record.id,
                    "headline": record.title,
                    "topic": next((t.replace("radio:", "") for t in record.tags if t.startswith("radio:")), "general"),
                    "why_it_matters": record.summary,
                    "actionable_angle": record.raw.get("actionable_angle", ""),
                    "priority": record.raw.get("priority", 3),
                    "created_at": record.retrieved_at,
                    "citations": [record.citation.to_dict()] if record.citation else []
                })
        
        # Sort by priority
        signals.sort(key=lambda x: x["priority"], reverse=True)
        
        return {"signals": signals[:limit], "total": len(signals)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/truth-library", dependencies=protected_dependencies)
async def list_truth_library(query: Optional[str] = None,
                            asset_type: Optional[str] = None,
                            status: Optional[str] = None,
                            limit: int = 50):
    """List Truth Library assets"""
    try:
        library = TruthLibraryPublisher()
        
        asset_type_enum = AssetType(asset_type) if asset_type else None
        status_enum = AssetStatus(status) if status else None
        
        assets = library.search(query or "", asset_type_enum, status_enum, limit)
        
        return {
            "assets": [asset.to_dict() for asset in assets],
            "total": len(assets)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/truth-library/{asset_id}", dependencies=protected_dependencies)
async def get_truth_asset(asset_id: str, version: Optional[int] = None):
    """Get specific Truth Library asset"""
    try:
        library = TruthLibraryPublisher()
        asset = library.get(asset_id, version)
        
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        return asset.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lead-vault", dependencies=protected_dependencies)
async def list_leads(entity_type: Optional[str] = None,
                    tags: Optional[str] = None,
                    limit: int = 100,
                    user_id: str = "system"):
    """List leads from Lead Vault (gated)"""
    try:
        vault = LeadVaultStore()
        
        filters = {}
        if entity_type:
            filters["entity_type"] = entity_type
        if tags:
            filters["tags"] = tags
        
        leads = vault.search(filters, user_id, limit)
        
        return {
            "leads": [lead.to_dict() for lead in leads],
            "total": len(leads)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/executive-inbox", dependencies=protected_dependencies)
async def get_executive_inbox(status: Optional[str] = None, limit: int = 20):
    """Get Decision Packets in Executive Inbox"""
    try:
        # In a full implementation, this would query a database
        # For now, return empty list
        return {
            "packets": [],
            "total": 0,
            "pending": 0,
            "approved": 0,
            "rejected": 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/executive-inbox/submit", dependencies=protected_dependencies)
async def submit_decision_packet(packet: Dict[str, Any]):
    """Submit Decision Packet to Executive Inbox"""
    try:
        from earnetics.tools.exec_tools import ExecTools
        exec_tools = ExecTools()
        result = exec_tools.submit_decision_packet(packet)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/executive-inbox/decide", dependencies=protected_dependencies)
async def decide_on_packet(packet_id: str, decision: str, note: Optional[str] = None, user_id: str = "executive"):
    """Executive decision on packet"""
    try:
        from earnetics.tools.exec_tools import ExecTools
        exec_tools = ExecTools()
        result = exec_tools.decide(packet_id, decision, user_id, note)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/opportunity-backlog", dependencies=protected_dependencies)
async def get_opportunity_backlog():
    """Get Opportunity Backlog (Kanban)"""
    try:
        backlog = OpportunityBacklog()
        all_opps = backlog.get_all()
        
        return {
            "columns": {
                "intake": [opp.to_dict() for opp in all_opps.get("intake", [])],
                "triage": [opp.to_dict() for opp in all_opps.get("triage", [])],
                "synthesis": [opp.to_dict() for opp in all_opps.get("synthesis", [])],
                "experiment": [opp.to_dict() for opp in all_opps.get("experiment", [])],
                "validated": [opp.to_dict() for opp in all_opps.get("validated", [])],
                "sent_to_exec": [opp.to_dict() for opp in all_opps.get("sent_to_exec", [])],
                "deployed": [opp.to_dict() for opp in all_opps.get("deployed", [])]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/opportunity-backlog/move", dependencies=protected_dependencies)
async def move_opportunity(opportunity_id: str, new_status: str):
    """Move opportunity to new status (Kanban)"""
    try:
        backlog = OpportunityBacklog()
        success = backlog.update_status(opportunity_id, new_status)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update status")
        
        return {"success": True, "opportunity_id": opportunity_id, "status": new_status}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/experiments", dependencies=protected_dependencies)
async def list_experiments(status: Optional[str] = None, limit: int = 20):
    """List experiments"""
    try:
        library = TruthLibraryPublisher()
        assets = library.search("", AssetType.EXPERIMENT, AssetStatus(status) if status else None, limit)
        
        return {
            "experiments": [asset.to_dict() for asset in assets],
            "total": len(assets)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/governance/audit", dependencies=protected_dependencies)
async def get_audit_log(lead_id: Optional[str] = None, limit: int = 100):
    """Get audit log for Lead Vault"""
    try:
        vault = LeadVaultStore()
        # In full implementation, this would query audit log
        return {
            "events": [],
            "total": 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaigns/{campaign_id}/metrics", dependencies=protected_dependencies)
async def get_campaign_metrics(campaign_id: str):
    """Get KPI metrics for a campaign"""
    try:
        telemetry = KPITelemetry()
        metrics = telemetry.get_campaign_metrics(campaign_id)
        
        if not metrics:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        return metrics
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
