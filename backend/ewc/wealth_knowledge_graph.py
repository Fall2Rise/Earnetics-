from __future__ import annotations

from typing import Any, Dict, List


class WealthKnowledgeGraph:
    def __init__(self) -> None:
        self.nodes: Dict[str, Dict[str, Any]] = {}

    def upsert_node(self, node_id: str, payload: Dict[str, Any]) -> None:
        self.nodes[node_id] = payload

    def query(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [value for value in self.nodes.values() if self._matches(value, filters)]

    def _matches(self, item: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        return all(item.get(key) == value for key, value in filters.items())
