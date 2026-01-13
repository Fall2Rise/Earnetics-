"""
Intelligence Department: Synthesis workflow
Converts opportunities into SOP/Playbook/Strategy assets
"""
from typing import Dict, Any, List
from earnetics.revenue_loop.opportunity import Opportunity
from earnetics.truth_library.publisher import TruthLibraryPublisher
from earnetics.truth_library.schema import TruthLibraryAsset, AssetType, AssetStatus


class SynthesisWorkflow:
    """Synthesis workflow: converts opportunities into Truth Library assets"""
    
    def __init__(self):
        self.library = TruthLibraryPublisher()
    
    def synthesize(self, opportunity: Opportunity, asset_type: AssetType = AssetType.PLAYBOOK) -> Dict[str, Any]:
        """
        Synthesize opportunity into Truth Library asset
        
        Converts opportunity into SOP/Playbook/Strategy
        """
        # Create asset content from opportunity
        content = {
            "opportunity_id": opportunity.opportunity_id,
            "niche": opportunity.niche,
            "offer_type": opportunity.offer_type,
            "hypothesis": opportunity.hypothesis,
            "target": opportunity.target,
            "required_assets": opportunity.required_assets,
            "workflow": self._generate_workflow(opportunity),
            "monetization": {
                "expected_roi": opportunity.expected_roi,
                "time_to_first_dollar": opportunity.time_to_first_dollar
            }
        }
        
        # Create asset
        asset_id = f"{asset_type.value}_{opportunity.opportunity_id}"
        asset = TruthLibraryAsset(
            asset_id=asset_id,
            type=asset_type,
            title=f"{asset_type.value.title()}: {opportunity.niche} - {opportunity.offer_type}",
            status=AssetStatus.DRAFT,
            version=1,
            last_verified_at=None,
            citations=opportunity.sources,
            confidence=0.7,  # Draft confidence
            owner="Synthesizer",
            tags=[opportunity.niche, opportunity.offer_type, "synthesized"],
            content=content
        )
        
        # Publish to library
        success = self.library.publish(asset)
        
        if success:
            # Update opportunity status
            opportunity.status = "synthesized"
        
        return {
            "success": success,
            "asset_id": asset_id,
            "opportunity_id": opportunity.opportunity_id,
            "asset_type": asset_type.value
        }
    
    def _generate_workflow(self, opportunity: Opportunity) -> List[str]:
        """Generate workflow steps from opportunity"""
        return [
            f"Research {opportunity.niche} market",
            f"Create {opportunity.offer_type} offer",
            f"Target {opportunity.target} segment",
            "Set up tracking and analytics",
            "Launch marketing campaign",
            "Monitor KPIs and optimize"
        ]
