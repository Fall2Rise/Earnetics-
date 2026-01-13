"""
Revenue Loop: Feedback Loop
Updates Truth Library based on campaign results
"""
from typing import Dict, Any, Optional
from datetime import datetime

from earnetics.revenue_loop.telemetry import KPITelemetry
from earnetics.truth_library.publisher import TruthLibraryPublisher
from earnetics.truth_library.schema import TruthLibraryAsset, AssetType, AssetStatus


class FeedbackLoop:
    """Feedback loop from campaign results to Truth Library"""
    
    def __init__(self):
        self.telemetry = KPITelemetry()
        self.library = TruthLibraryPublisher()
    
    def process_campaign_results(self, campaign_id: str, 
                                 opportunity_id: str,
                                 threshold_met: bool) -> bool:
        """
        Process campaign results and update Truth Library
        
        If campaign meets thresholds → create/upgrade Truth Library Playbook to validated
        If campaign fails → create Experiment result and adjust scoring
        """
        metrics = self.telemetry.get_campaign_metrics(campaign_id)
        if not metrics:
            return False
        
        if threshold_met:
            # Create validated playbook
            return self._create_validated_playbook(campaign_id, opportunity_id, metrics)
        else:
            # Create experiment result
            return self._create_experiment_result(campaign_id, opportunity_id, metrics)
    
    def _create_validated_playbook(self, campaign_id: str, opportunity_id: str,
                                   metrics: Dict[str, Any]) -> bool:
        """Create validated playbook from successful campaign"""
        try:
            asset_id = f"playbook_{opportunity_id}"
            
            # Check if playbook exists
            existing = self.library.get(asset_id)
            
            content = {
                "campaign_id": campaign_id,
                "opportunity_id": opportunity_id,
                "workflow": [
                    "Create landing page",
                    "Generate marketing copy",
                    "Set up tracking",
                    "Drive traffic",
                    "Capture leads",
                    "Follow-up sequence"
                ],
                "monetization": {
                    "offer_type": "digital_product",  # TODO: Get from opportunity
                    "pricing_strategy": "one-time"
                }
            }
            
            measurable_results = {
                "traffic_clicks": metrics.get("traffic_clicks", 0),
                "leads_optin": metrics.get("leads_optin", 0),
                "conversions_purchase": metrics.get("conversions_purchase", 0),
                "revenue_recorded": metrics.get("revenue_recorded", 0.0),
                "conversion_rate": (
                    metrics.get("conversions_purchase", 0) / max(metrics.get("traffic_clicks", 1), 1)
                ) * 100,
                "roi": metrics.get("revenue_recorded", 0.0)
            }
            
            if existing:
                # Upgrade to validated
                asset = existing
                asset.status = AssetStatus.VALIDATED
                asset.last_verified_at = datetime.utcnow().isoformat()
                asset.measurable_results = measurable_results
                asset.content.update(content)
            else:
                # Create new
                asset = TruthLibraryAsset(
                    asset_id=asset_id,
                    type=AssetType.PLAYBOOK,
                    title=f"Validated Playbook: {campaign_id}",
                    status=AssetStatus.VALIDATED,
                    version=1,
                    last_verified_at=datetime.utcnow().isoformat(),
                    citations=[],
                    confidence=0.9,
                    owner="FeedbackLoop",
                    tags=["validated", "playbook", campaign_id],
                    content=content,
                    measurable_results=measurable_results
                )
            
            return self.library.publish(asset)
        except Exception as e:
            print(f"Error creating validated playbook: {e}")
            return False
    
    def _create_experiment_result(self, campaign_id: str, opportunity_id: str,
                                  metrics: Dict[str, Any]) -> bool:
        """Create experiment result from failed campaign"""
        try:
            asset_id = f"experiment_{campaign_id}"
            
            content = {
                "campaign_id": campaign_id,
                "opportunity_id": opportunity_id,
                "hypothesis": "Campaign would generate revenue",
                "setup": {
                    "tasks": ["landing_page", "copy", "tracking", "traffic", "lead_capture", "followup"]
                },
                "results": {
                    "traffic_clicks": metrics.get("traffic_clicks", 0),
                    "leads_optin": metrics.get("leads_optin", 0),
                    "conversions_purchase": metrics.get("conversions_purchase", 0),
                    "revenue_recorded": metrics.get("revenue_recorded", 0.0)
                },
                "conclusion": "Campaign did not meet thresholds",
                "next_steps": [
                    "Analyze failure points",
                    "Adjust targeting",
                    "Optimize conversion funnel",
                    "Retest with modifications"
                ]
            }
            
            asset = TruthLibraryAsset(
                asset_id=asset_id,
                type=AssetType.EXPERIMENT,
                title=f"Experiment Result: {campaign_id}",
                status=AssetStatus.VALIDATED,  # Experiments are validated results
                version=1,
                last_verified_at=datetime.utcnow().isoformat(),
                citations=[],
                confidence=0.7,
                owner="FeedbackLoop",
                tags=["experiment", "failed", campaign_id],
                content=content,
                measurable_results={
                    "traffic": metrics.get("traffic_clicks", 0),
                    "leads": metrics.get("leads_optin", 0),
                    "conversions": metrics.get("conversions_purchase", 0),
                    "revenue": metrics.get("revenue_recorded", 0.0)
                }
            )
            
            return self.library.publish(asset)
        except Exception as e:
            print(f"Error creating experiment result: {e}")
            return False
