"""
Revenue Loop: Opportunity object schema
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import hashlib


@dataclass
class Opportunity:
    """Opportunity object for revenue loop"""
    opportunity_id: str
    niche: str
    offer_type: str
    hypothesis: str
    target: str  # Target segment description
    required_assets: List[str]
    expected_roi: float
    time_to_first_dollar: int  # days
    risks: List[str]
    compliance_notes: str
    sources: List[Dict[str, Any]]  # Citations
    recommended_next_action: str
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    status: str = "draft"  # draft, triaged, synthesized, experiment, validated, deployed
    
    @classmethod
    def create_id(cls, niche: str, offer_type: str) -> str:
        """Generate deterministic opportunity ID"""
        content = f"{niche}:{offer_type}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "opportunity_id": self.opportunity_id,
            "niche": self.niche,
            "offer_type": self.offer_type,
            "hypothesis": self.hypothesis,
            "target": self.target,
            "required_assets": self.required_assets,
            "expected_roi": self.expected_roi,
            "time_to_first_dollar": self.time_to_first_dollar,
            "risks": self.risks,
            "compliance_notes": self.compliance_notes,
            "sources": self.sources,
            "recommended_next_action": self.recommended_next_action,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "status": self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Opportunity':
        return cls(
            opportunity_id=data["opportunity_id"],
            niche=data["niche"],
            offer_type=data["offer_type"],
            hypothesis=data["hypothesis"],
            target=data["target"],
            required_assets=data.get("required_assets", []),
            expected_roi=data.get("expected_roi", 0.0),
            time_to_first_dollar=data.get("time_to_first_dollar", 30),
            risks=data.get("risks", []),
            compliance_notes=data.get("compliance_notes", ""),
            sources=data.get("sources", []),
            recommended_next_action=data.get("recommended_next_action", ""),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            updated_at=data.get("updated_at", datetime.utcnow().isoformat()),
            status=data.get("status", "draft")
        )
