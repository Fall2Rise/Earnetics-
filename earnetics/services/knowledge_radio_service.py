"""
Knowledge Radio Service: Continuous brief-card stream
"""
import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from earnetics.knowledge_store.store import KnowledgeStore
from earnetics.knowledge_store.schema import KnowledgeRecord, CitationObject


class KnowledgeRadioService:
    """Continuous brief-card stream from feeds"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or Path(__file__).parent.parent / "config" / "knowledge_radio.json"
        self.store = KnowledgeStore()
        self._load_config()
        self.throttle_tracker: Dict[str, Dict[str, int]] = {}  # agent_id -> {hour: count}
    
    def _load_config(self):
        """Load knowledge radio configuration"""
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)
    
    def generate_brief_card(self, topic: str, headline: str, 
                           why_it_matters: str, actionable_angle: str,
                           keywords: List[str], citations: List[Dict[str, Any]],
                           priority: int = 3) -> Dict[str, Any]:
        """
        Generate brief card
        
        Brief Cards are short, structured knowledge items for passive learning
        """
        return {
            "topic": topic,
            "headline": headline,
            "why_it_matters": why_it_matters,
            "actionable_angle": actionable_angle,
            "keywords": keywords,
            "citations": citations,
            "priority": priority,
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def ingest_feed(self, feed_id: str) -> List[Dict[str, Any]]:
        """Ingest from a feed and generate brief cards"""
        brief_cards = []
        
        feed_config = next((f for f in self.config.get("feeds", []) if f["feed_id"] == feed_id), None)
        if not feed_config or not feed_config.get("enabled"):
            return brief_cards
        
        # Stub implementation - would connect to actual feeds
        if feed_id == "gdelt":
            # GDELT stub
            brief_cards.append(self.generate_brief_card(
                topic="ai tools",
                headline="New AI tool released",
                why_it_matters="Could be integrated into Earnetics workflow",
                actionable_angle="Evaluate for revenue opportunity",
                keywords=["ai", "tools", "automation"],
                citations=[],
                priority=3
            ))
        elif feed_id == "rss":
            # RSS stub
            pass
        elif feed_id == "github_releases":
            # GitHub releases stub
            pass
        
        # Store brief cards as KnowledgeRecords
        for card in brief_cards:
            record = KnowledgeRecord(
                id=KnowledgeRecord.create_id("radio", card["headline"], card["created_at"]),
                source_id="knowledge_radio",
                tier=6,
                title=card["headline"],
                url=f"radio://brief/{card['created_at']}",
                retrieved_at=card["created_at"],
                summary=card["why_it_matters"],
                content_text=f"{card['headline']}\n\n{card['why_it_matters']}\n\n{card['actionable_angle']}",
                tags=[f"radio:{card['topic']}"] + card["keywords"],
                trust_score=65,  # Radio content is lower trust
                raw=card
            )
            self.store.store(record)
        
        return brief_cards
    
    async def run_radio_loop(self):
        """Main radio loop - runs continuously"""
        while True:
            try:
                cadence = self.config.get("cadence_minutes", 15)
                
                # Ingest from all enabled feeds
                for feed_config in self.config.get("feeds", []):
                    if feed_config.get("enabled"):
                        await self.ingest_feed(feed_config["feed_id"])
                
                # Wait for next cycle
                await asyncio.sleep(cadence * 60)
            except Exception as e:
                print(f"Error in radio loop: {e}")
                await asyncio.sleep(60)
    
    def check_throttle(self, agent_id: str) -> bool:
        """Check if agent has exceeded throttle limit"""
        current_hour = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        hour_key = current_hour.isoformat()
        
        if agent_id not in self.throttle_tracker:
            self.throttle_tracker[agent_id] = {}
        
        agent_tracker = self.throttle_tracker[agent_id]
        
        # Clean old hours
        cutoff = current_hour - timedelta(hours=1)
        agent_tracker = {k: v for k, v in agent_tracker.items() if k > cutoff.isoformat()}
        self.throttle_tracker[agent_id] = agent_tracker
        
        # Check limit
        count = agent_tracker.get(hour_key, 0)
        limit = self.config.get("throttle", {}).get("default_per_agent_per_hour", 3)
        
        return count < limit
    
    def record_access(self, agent_id: str):
        """Record agent access to radio"""
        current_hour = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        hour_key = current_hour.isoformat()
        
        if agent_id not in self.throttle_tracker:
            self.throttle_tracker[agent_id] = {}
        
        self.throttle_tracker[agent_id][hour_key] = self.throttle_tracker[agent_id].get(hour_key, 0) + 1
