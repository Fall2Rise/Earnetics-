"""
Intelligence Department: Triage workflow
"""
from typing import Dict, Any
from earnetics.revenue_loop.opportunity import Opportunity
from earnetics.intelligence.scoring import OpportunityScorer
from earnetics.intelligence.backlog import OpportunityBacklog


class TriageWorkflow:
    """Triage workflow for opportunities"""
    
    def __init__(self):
        self.scorer = OpportunityScorer()
        self.backlog = OpportunityBacklog()
    
    def triage(self, opportunity: Opportunity) -> Dict[str, Any]:
        """
        Triage opportunity: score and route to appropriate status
        
        Returns triage result with score and recommendation
        """
        # Score opportunity
        score_result = self.scorer.score(opportunity)
        
        # Determine status based on score
        if score_result["total_score"] >= 8:
            status = "synthesis"  # High score → ready for synthesis
        elif score_result["total_score"] >= 4:
            status = "triage"  # Medium score → needs more review
        else:
            status = "intake"  # Low score → needs more work
        
        opportunity.status = status
        
        # Add to backlog
        self.backlog.add(opportunity, score_result["total_score"])
        
        return {
            "opportunity_id": opportunity.opportunity_id,
            "score": score_result,
            "status": status,
            "recommendation": score_result["recommendation"]
        }
