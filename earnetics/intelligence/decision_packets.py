"""
Intelligence Department: Decision Packet generator
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from earnetics.revenue_loop.opportunity import Opportunity
from earnetics.lead_vault.store import LeadVaultStore


class DecisionPacketGenerator:
    """Generates 1-page structured Decision Packets for Executive"""
    
    def __init__(self):
        self.lead_vault = LeadVaultStore()
    
    def generate(self, opportunity: Opportunity, signals: List[Dict[str, Any]],
                 lead_vault_query: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate Decision Packet
        
        Returns structured packet ready for Executive review
        """
        # Get target segment from Lead Vault if query provided
        segment_info = {}
        if lead_vault_query:
            leads = self.lead_vault.search(lead_vault_query, user_id="system", limit=100)
            segment_info = {
                "segment_size": len(leads),
                "segment_query": lead_vault_query
            }
        
        packet = {
            "packet_id": f"dp_{opportunity.opportunity_id}_{datetime.utcnow().strftime('%Y%m%d')}",
            "opportunity_id": opportunity.opportunity_id,
            "generated_at": datetime.utcnow().isoformat(),
            
            # Opportunity Summary
            "opportunity": {
                "niche": opportunity.niche,
                "offer_type": opportunity.offer_type,
                "hypothesis": opportunity.hypothesis,
                "expected_roi": opportunity.expected_roi,
                "time_to_first_dollar": opportunity.time_to_first_dollar
            },
            
            # Why Now
            "why_now": {
                "signals": signals,
                "citations": opportunity.sources,
                "timing_rationale": self._generate_timing_rationale(signals)
            },
            
            # Offer Angle
            "offer_angle": {
                "target_segment": opportunity.target,
                "segment_info": segment_info,
                "value_proposition": self._generate_value_proposition(opportunity)
            },
            
            # Assets List
            "assets": {
                "required": opportunity.required_assets,
                "available": [],  # TODO: Check what's available
                "missing": opportunity.required_assets
            },
            
            # KPI Plan
            "kpi_plan": {
                "primary_metric": "revenue",
                "target": opportunity.expected_roi,
                "timeframe_days": opportunity.time_to_first_dollar,
                "secondary_metrics": ["leads", "conversions", "engagement"]
            },
            
            # Risk & Compliance
            "risk_compliance": {
                "risks": opportunity.risks,
                "compliance_notes": opportunity.compliance_notes,
                "mitigation": self._generate_mitigation(opportunity.risks)
            },
            
            # Deploy Plan Link
            "deploy_plan": {
                "status": "pending",
                "plan_id": None  # Generated when approved
            }
        }
        
        return packet
    
    def _generate_timing_rationale(self, signals: List[Dict[str, Any]]) -> str:
        """Generate timing rationale from signals"""
        if not signals:
            return "No specific timing signals identified"
        
        signal_summary = ", ".join([s.get("summary", "")[:50] for s in signals[:3]])
        return f"Recent signals indicate opportunity: {signal_summary}"
    
    def _generate_value_proposition(self, opportunity: Opportunity) -> str:
        """Generate value proposition"""
        return f"{opportunity.offer_type} for {opportunity.niche} targeting {opportunity.target}"
    
    def _generate_mitigation(self, risks: List[str]) -> List[str]:
        """Generate risk mitigation strategies"""
        mitigations = []
        for risk in risks:
            if "compliance" in risk.lower():
                mitigations.append("Legal review before deployment")
            elif "technical" in risk.lower():
                mitigations.append("Technical validation and testing")
            elif "market" in risk.lower():
                mitigations.append("Market validation and pilot")
            else:
                mitigations.append("Monitor and adjust strategy")
        return mitigations
