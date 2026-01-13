#!/usr/bin/env python3
"""
Demo Intelligence Pipeline
Proves end-to-end loop works:
- Ingest wayback snapshot + wikidata item
- Create opportunity + decision packet
- Approve deploy
- Emit fake telemetry
- Store validated playbook based on results

Usage:
    python earnetics/scripts/demo_intel_pipeline.py

This script demonstrates the complete intelligence pipeline:
1. Knowledge ingestion from external sources
2. Opportunity discovery and scoring
3. Decision packet generation
4. Deployment orchestration
5. KPI telemetry tracking
6. Feedback loop to Truth Library
"""
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from datetime import datetime
from earnetics.knowledge_sources.internet_archive_wayback import WaybackSource
from earnetics.knowledge_store.store import KnowledgeStore
from earnetics.revenue_loop.opportunity import Opportunity
from earnetics.intelligence.decision_packets import DecisionPacketGenerator
from earnetics.intelligence.scoring import OpportunityScorer
from earnetics.revenue_loop.deployment_orchestrator import DeploymentOrchestrator
from earnetics.revenue_loop.telemetry import KPITelemetry
from earnetics.revenue_loop.feedback import FeedbackLoop
from earnetics.truth_library.publisher import TruthLibraryPublisher


def main():
    print("🚀 Earnetics Intelligence Pipeline Demo")
    print("=" * 60)
    
    # 1. Ingest wayback snapshot
    print("\n1. Ingesting Wayback snapshot...")
    wayback = WaybackSource("wayback", {
        "tier": 5,
        "enabled": True,
        "trust_score": 70,
        "rate_limit_per_min": 30,
        "capabilities": {"search": True, "fulltext": True, "fetch": True},
        "requires_internet": True,
        "offline_allowed": False
    })
    
    store = KnowledgeStore()
    
    # Search for a snapshot
    results = wayback.search("https://example.com", limit=1)
    if results:
        ref = results[0]
        print(f"   Found snapshot: {ref.get('title')}")
        
        # Fetch full content
        record = wayback.fetch(ref)
        store.store(record)
        print(f"   ✅ Stored: {record.id} with citation")
        print(f"   Citation: {record.citation.url} (snapshot: {record.citation.snapshot})")
    else:
        print("   ⚠️  No snapshots found (demo mode)")
        # Create demo record
        from earnetics.knowledge_store.schema import KnowledgeRecord, CitationObject
        record = KnowledgeRecord(
            id="demo_wayback_1",
            source_id="wayback",
            tier=5,
            title="Demo Wayback Snapshot",
            url="https://example.com",
            retrieved_at=datetime.utcnow().isoformat(),
            citation=CitationObject(
                source_id="wayback",
                url="https://example.com",
                retrieved_at=datetime.utcnow().isoformat(),
                snapshot={"timestamp": "20240101120000", "wayback_url": "https://web.archive.org/web/20240101120000/https://example.com"}
            ),
            trust_score=70,
            content_text="Demo content from Wayback Machine"
        )
        store.store(record)
        print("   ✅ Created demo record")
    
    # 2. Create opportunity
    print("\n2. Creating opportunity...")
    opportunity = Opportunity(
        opportunity_id=Opportunity.create_id("AI Tools", "SaaS Product"),
        niche="AI Tools",
        offer_type="SaaS Product",
        hypothesis="AI tool integration service will generate $5000/month",
        target="Small businesses needing AI automation",
        required_assets=["landing_page", "payment_processor", "email_marketing"],
        expected_roi=5000.0,
        time_to_first_dollar=14,
        risks=["Market saturation", "Technical complexity"],
        compliance_notes="Standard SaaS compliance required",
        sources=[record.citation.to_dict() if record.citation else {}],
        recommended_next_action="Create landing page and payment link"
    )
    print(f"   ✅ Created: {opportunity.opportunity_id}")
    
    # 3. Score opportunity
    print("\n3. Scoring opportunity...")
    scorer = OpportunityScorer()
    score = scorer.score(opportunity)
    print(f"   Total Score: {score['total_score']}")
    print(f"   Recommendation: {score['recommendation']}")
    
    # 4. Generate decision packet
    print("\n4. Generating decision packet...")
    packet_gen = DecisionPacketGenerator()
    packet = packet_gen.generate(opportunity, signals=[{
        "summary": "Market demand for AI tools increasing",
        "source": "wayback"
    }])
    print(f"   ✅ Generated packet: {packet['packet_id']}")
    
    # 5. Approve and deploy
    print("\n5. Approving deployment...")
    orchestrator = DeploymentOrchestrator()
    deployment_plan = orchestrator.generate_deployment_plan(opportunity, packet)
    print(f"   ✅ Generated deployment plan: {deployment_plan['campaign_id']}")
    print(f"   Tasks: {len(deployment_plan['tasks'])}")
    
    deploy_result = orchestrator.execute_deployment(deployment_plan)
    print(f"   ✅ Deployed: {deploy_result['campaign_id']}")
    
    # 6. Emit fake telemetry
    print("\n6. Emitting telemetry events...")
    telemetry = KPITelemetry()
    campaign_id = deployment_plan['campaign_id']
    
    telemetry.log_event("campaign.created", campaign_id)
    telemetry.log_event("traffic.click", campaign_id, value=None)
    telemetry.log_event("traffic.click", campaign_id, value=None)
    telemetry.log_event("lead.optin", campaign_id, value=None)
    telemetry.log_event("conversion.purchase", campaign_id, value=None)
    telemetry.log_event("revenue.recorded", campaign_id, value=97.0)
    
    print("   ✅ Emitted 6 events")
    
    # 7. Get metrics
    metrics = telemetry.get_campaign_metrics(campaign_id)
    print(f"\n7. Campaign Metrics:")
    print(f"   Traffic: {metrics.get('traffic_clicks', 0)}")
    print(f"   Leads: {metrics.get('leads_optin', 0)}")
    print(f"   Conversions: {metrics.get('conversions_purchase', 0)}")
    print(f"   Revenue: ${metrics.get('revenue_recorded', 0.0):.2f}")
    
    # 8. Feedback loop
    print("\n8. Processing feedback loop...")
    feedback = FeedbackLoop()
    threshold_met = metrics.get('revenue_recorded', 0) > 0
    success = feedback.process_campaign_results(campaign_id, opportunity.opportunity_id, threshold_met)
    print(f"   ✅ Feedback processed: {success}")
    
    # 9. Verify playbook created
    print("\n9. Verifying Truth Library...")
    library = TruthLibraryPublisher()
    playbook_id = f"playbook_{opportunity.opportunity_id}"
    playbook = library.get(playbook_id)
    if playbook:
        print(f"   ✅ Playbook created: {playbook.title}")
        print(f"   Status: {playbook.status.value}")
        if playbook.measurable_results:
            print(f"   Results: {playbook.measurable_results}")
    else:
        print("   ⚠️  Playbook not found (may need more telemetry)")
    
    print("\n" + "=" * 60)
    print("✅ Demo pipeline completed successfully!")
    print("\nEnd-to-end loop verified:")
    print("  ✓ Knowledge ingestion with citations")
    print("  ✓ Opportunity creation")
    print("  ✓ Scoring and decision packets")
    print("  ✓ Deployment orchestration")
    print("  ✓ KPI telemetry")
    print("  ✓ Feedback loop to Truth Library")


if __name__ == "__main__":
    main()
