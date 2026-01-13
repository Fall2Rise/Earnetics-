"""
Radio Tools: subscribe, latest, pause/resume
"""
from typing import List, Dict, Any, Optional
from earnetics.services.knowledge_radio_service import KnowledgeRadioService
from earnetics.knowledge_store.store import KnowledgeStore


class RadioTools:
    """Agent tools for Knowledge Radio"""
    
    def __init__(self):
        self.radio = KnowledgeRadioService()
        self.store = KnowledgeStore()
    
    def subscribe(self, agent_id: str, topics: Optional[List[str]] = None,
                  tiers: Optional[List[int]] = None,
                  max_items_per_hour: int = 3) -> Dict[str, Any]:
        """
        Subscribe agent to Knowledge Radio
        
        Returns subscription confirmation
        """
        # Check throttle
        if not self.radio.check_throttle(agent_id):
            return {
                "success": False,
                "message": "Throttle limit exceeded. Wait before accessing radio."
            }
        
        # Record access
        self.radio.record_access(agent_id)
        
        return {
            "success": True,
            "agent_id": agent_id,
            "topics": topics or self.radio.config.get("topics", []),
            "tiers": tiers or [1, 2, 3, 4, 5, 6],
            "max_items_per_hour": max_items_per_hour,
            "subscribed_at": datetime.utcnow().isoformat()
        }
    
    def latest(self, topics: Optional[List[str]] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get latest brief cards from radio
        
        Agents do NOT ingest these into live prompt; they store and retrieve later
        """
        # Search store for radio-tagged items
        query = " ".join(topics) if topics else "radio"
        results = self.store.search(query, limit=limit)
        
        # Filter by radio tag
        radio_items = [r for r in results if any(tag.startswith("radio:") for tag in r.tags)]
        
        return [{
            "id": r.id,
            "headline": r.title,
            "topic": next((t.replace("radio:", "") for t in r.tags if t.startswith("radio:")), "general"),
            "why_it_matters": r.summary,
            "actionable_angle": r.raw.get("actionable_angle", "") if r.raw else "",
            "keywords": [t for t in r.tags if not t.startswith("radio:")],
            "citations": [r.citation.to_dict()] if r.citation else [],
            "priority": r.raw.get("priority", 3) if r.raw else 3,
            "created_at": r.retrieved_at
        } for r in radio_items[:limit]]
    
    def pause(self, agent_id: str) -> Dict[str, Any]:
        """Pause agent's radio subscription"""
        # In a full implementation, this would update subscription state
        return {
            "success": True,
            "agent_id": agent_id,
            "status": "paused",
            "paused_at": datetime.utcnow().isoformat()
        }
    
    def resume(self, agent_id: str) -> Dict[str, Any]:
        """Resume agent's radio subscription"""
        return {
            "success": True,
            "agent_id": agent_id,
            "status": "active",
            "resumed_at": datetime.utcnow().isoformat()
        }
