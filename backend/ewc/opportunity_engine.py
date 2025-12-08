from __future__ import annotations

from typing import Any, Dict, List

from .sensing_hub import SensingHub
from .wealth_knowledge_graph import WealthKnowledgeGraph


class OpportunityEngine:
    def __init__(self, sensing_hub: SensingHub, knowledge_graph: WealthKnowledgeGraph) -> None:
        self.sensing_hub = sensing_hub
        self.knowledge_graph = knowledge_graph
        self._opportunities: List[Dict[str, Any]] = []

    def ingest_signal(self, signal: Dict[str, Any]) -> None:
        self._opportunities.append(signal)
        node_id = signal.get("id") or signal.get("keyword")
        if node_id:
            self.knowledge_graph.upsert_node(node_id, signal)

    def list_opportunities(self) -> List[Dict[str, Any]]:
        if not self._opportunities:
            discovery = self.sensing_hub.collect()
            return discovery.get("signals", [])
        return self._opportunities
