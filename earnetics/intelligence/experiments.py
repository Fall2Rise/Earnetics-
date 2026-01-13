"""
Intelligence Department: Experiments workflow
"""
from typing import Dict, Any, Optional, List
from datetime import datetime

from earnetics.revenue_loop.opportunity import Opportunity
from earnetics.truth_library.publisher import TruthLibraryPublisher
from earnetics.truth_library.schema import TruthLibraryAsset, AssetType, AssetStatus


class ExperimentsWorkflow:
    """Experiments workflow: run micro-tests and record results"""
    
    def __init__(self):
        self.library = TruthLibraryPublisher()
    
    def create_experiment(self, opportunity: Opportunity, 
                         hypothesis: str,
                         setup: Dict[str, Any]) -> Dict[str, Any]:
        """Create experiment from opportunity"""
        experiment_id = f"exp_{opportunity.opportunity_id}_{datetime.utcnow().strftime('%Y%m%d')}"
        
        content = {
            "experiment_id": experiment_id,
            "opportunity_id": opportunity.opportunity_id,
            "hypothesis": hypothesis,
            "setup": setup,
            "status": "running",
            "started_at": datetime.utcnow().isoformat()
        }
        
        asset = TruthLibraryAsset(
            asset_id=experiment_id,
            type=AssetType.EXPERIMENT,
            title=f"Experiment: {opportunity.niche}",
            status=AssetStatus.DRAFT,
            version=1,
            last_verified_at=None,
            citations=opportunity.sources,
            confidence=0.5,
            owner="Experimenter",
            tags=["experiment", opportunity.niche],
            content=content
        )
        
        success = self.library.publish(asset)
        
        return {
            "success": success,
            "experiment_id": experiment_id,
            "opportunity_id": opportunity.opportunity_id
        }
    
    def record_results(self, experiment_id: str, results: Dict[str, Any],
                      conclusion: str, next_steps: List[Any]) -> Dict[str, Any]:
        """Record experiment results"""
        asset = self.library.get(experiment_id)
        if not asset:
            return {"success": False, "message": "Experiment not found"}
        
        # Update content with results
        asset.content.update({
            "results": results,
            "conclusion": conclusion,
            "next_steps": next_steps,
            "completed_at": datetime.utcnow().isoformat(),
            "status": "completed"
        })
        
        asset.status = AssetStatus.VALIDATED
        asset.last_verified_at = datetime.utcnow().isoformat()
        asset.measurable_results = results
        
        success = self.library.publish(asset)
        
        return {
            "success": success,
            "experiment_id": experiment_id,
            "status": "completed"
        }
