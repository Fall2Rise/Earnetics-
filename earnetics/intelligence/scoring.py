"""
Intelligence Department: Triage Scoring
"""
from typing import Dict, Any
from earnetics.revenue_loop.opportunity import Opportunity


class OpportunityScorer:
    """Scores opportunities for triage"""
    
    @staticmethod
    def score(opportunity: Opportunity) -> Dict[str, Any]:
        """
        Score opportunity: (RevenuePotential + Speed + Confidence + Actionability) - (Effort + Risk)
        Each dimension 1-5
        """
        revenue_potential = OpportunityScorer._score_revenue_potential(opportunity)
        speed = OpportunityScorer._score_speed(opportunity)
        confidence = OpportunityScorer._score_confidence(opportunity)
        actionability = OpportunityScorer._score_actionability(opportunity)
        effort = OpportunityScorer._score_effort(opportunity)
        risk = OpportunityScorer._score_risk(opportunity)
        
        total_score = (revenue_potential + speed + confidence + actionability) - (effort + risk)
        
        return {
            "total_score": total_score,
            "revenue_potential": revenue_potential,
            "speed": speed,
            "confidence": confidence,
            "actionability": actionability,
            "effort": effort,
            "risk": risk,
            "recommendation": "high" if total_score >= 8 else "medium" if total_score >= 4 else "low"
        }
    
    @staticmethod
    def _score_revenue_potential(opportunity: Opportunity) -> int:
        """Score 1-5 based on expected ROI"""
        if opportunity.expected_roi >= 10000:
            return 5
        elif opportunity.expected_roi >= 5000:
            return 4
        elif opportunity.expected_roi >= 1000:
            return 3
        elif opportunity.expected_roi >= 500:
            return 2
        return 1
    
    @staticmethod
    def _score_speed(opportunity: Opportunity) -> int:
        """Score 1-5 based on time to first dollar"""
        if opportunity.time_to_first_dollar <= 7:
            return 5
        elif opportunity.time_to_first_dollar <= 14:
            return 4
        elif opportunity.time_to_first_dollar <= 30:
            return 3
        elif opportunity.time_to_first_dollar <= 60:
            return 2
        return 1
    
    @staticmethod
    def _score_confidence(opportunity: Opportunity) -> int:
        """Score 1-5 based on sources and evidence"""
        source_count = len(opportunity.sources)
        if source_count >= 5:
            return 5
        elif source_count >= 3:
            return 4
        elif source_count >= 2:
            return 3
        elif source_count >= 1:
            return 2
        return 1
    
    @staticmethod
    def _score_actionability(opportunity: Opportunity) -> int:
        """Score 1-5 based on required assets and clarity"""
        asset_count = len(opportunity.required_assets)
        if asset_count <= 2 and opportunity.recommended_next_action:
            return 5
        elif asset_count <= 3:
            return 4
        elif asset_count <= 5:
            return 3
        elif asset_count <= 7:
            return 2
        return 1
    
    @staticmethod
    def _score_effort(opportunity: Opportunity) -> int:
        """Score 1-5 (higher = more effort = worse)"""
        asset_count = len(opportunity.required_assets)
        if asset_count >= 10:
            return 5
        elif asset_count >= 7:
            return 4
        elif asset_count >= 5:
            return 3
        elif asset_count >= 3:
            return 2
        return 1
    
    @staticmethod
    def _score_risk(opportunity: Opportunity) -> int:
        """Score 1-5 (higher = more risk = worse)"""
        risk_count = len(opportunity.risks)
        if risk_count >= 5:
            return 5
        elif risk_count >= 3:
            return 4
        elif risk_count >= 2:
            return 3
        elif risk_count >= 1:
            return 2
        return 1
