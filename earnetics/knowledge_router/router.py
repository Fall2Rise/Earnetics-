"""
Knowledge Router: chooses best sources based on intent
"""
from typing import List, Dict, Any, Optional
import json
from pathlib import Path

from earnetics.knowledge_store.schema import KnowledgeRecord
from earnetics.knowledge_sources.base import KnowledgeSource
from earnetics.knowledge_sources.internal_vault import InternalVaultSource
from earnetics.knowledge_sources.internet_archive_wayback import WaybackSource
from earnetics.knowledge_sources.wikipedia import WikipediaSource
from earnetics.knowledge_sources.wikidata import WikidataSource


class KnowledgeRouter:
    """Routes queries to appropriate knowledge sources based on intent"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or Path(__file__).parent.parent / "config" / "knowledge_sources.json"
        self.sources: Dict[str, KnowledgeSource] = {}
        self._load_config()
        self._initialize_sources()
    
    def _load_config(self):
        """Load knowledge sources configuration"""
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)
    
    def _initialize_sources(self):
        """Initialize available knowledge source connectors"""
        for source_config in self.config.get("sources", []):
            if not source_config.get("enabled", True):
                continue
            
            source_id = source_config["source_id"]
            
            # Initialize based on source type
            if source_id == "earnetics_vault":
                self.sources[source_id] = InternalVaultSource(source_id, source_config)
            elif source_id == "wayback":
                self.sources[source_id] = WaybackSource(source_id, source_config)
            elif source_id == "wikipedia":
                self.sources[source_id] = WikipediaSource(source_id, source_config)
            elif source_id == "wikidata":
                self.sources[source_id] = WikidataSource(source_id, source_config)
            # Additional connectors can be added here as they're implemented
    
    def route(self, query: str, intent: Optional[str] = None, 
              sources: Optional[List[str]] = None,
              tiers: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        """
        Route query to appropriate sources based on intent
        
        Intent detection:
        - Internal ops / "how do we do X in Earnetics?" → Tier 0 first
        - Entity facts / definitions → Wikidata/Wikipedia
        - Research claims → OpenAlex/Crossref/arXiv/Semantic Scholar
        - Security/spec correctness → NIST/RFC/W3C/MITRE
        - Implementation/debug → official docs + GitHub + StackOverflow
        - Historical/removed pages → Wayback
        """
        if intent is None:
            intent = self._detect_intent(query)
        
        # Determine which sources to query
        if sources:
            source_ids = [s for s in sources if s in self.sources]
        else:
            source_ids = self._select_sources_by_intent(intent, tiers)
        
        results = []
        for source_id in source_ids:
            source = self.sources.get(source_id)
            if not source or not source.can_search():
                continue
            
            try:
                search_results = source.search(query, limit=10)
                for result in search_results:
                    result["source_id"] = source_id
                    result["tier"] = source.tier
                    result["trust_score"] = source.trust_score
                    result["rationale"] = f"Matched {intent} intent via {source_id}"
                results.extend(search_results)
            except Exception as e:
                print(f"Error querying {source_id}: {e}")
        
        # Rank results
        results = self._rank_results(results, intent)
        
        return results
    
    def _detect_intent(self, query: str) -> str:
        """Detect query intent"""
        query_lower = query.lower()
        
        # Internal operations
        if any(phrase in query_lower for phrase in ["how do we", "earnetics", "our system", "internal"]):
            return "internal_ops"
        
        # Entity facts / definitions
        if any(phrase in query_lower for phrase in ["what is", "definition", "who is", "entity"]):
            return "entity_facts"
        
        # Research claims
        if any(phrase in query_lower for phrase in ["research", "study", "paper", "academic", "scholarly"]):
            return "research"
        
        # Security / specs
        if any(phrase in query_lower for phrase in ["security", "spec", "standard", "rfc", "nist", "compliance"]):
            return "security_spec"
        
        # Implementation / debug
        if any(phrase in query_lower for phrase in ["how to", "implement", "code", "api", "debug", "error"]):
            return "implementation"
        
        # Historical / removed pages
        if any(phrase in query_lower for phrase in ["archive", "wayback", "removed", "deleted", "historical"]):
            return "historical"
        
        return "general"
    
    def _select_sources_by_intent(self, intent: str, tiers: Optional[List[int]] = None) -> List[str]:
        """Select sources based on intent"""
        source_map = {
            "internal_ops": ["earnetics_vault"],
            "entity_facts": ["wikidata", "wikipedia"],
            "research": ["openalex", "crossref", "arxiv", "semantic_scholar"],
            "security_spec": ["nist", "rfc", "w3c", "mitre_attack"],
            "implementation": ["github_docs", "stackoverflow"],
            "historical": ["wayback"],
            "general": ["earnetics_vault", "wikidata", "wikipedia"]
        }
        
        source_ids = source_map.get(intent, ["earnetics_vault"])
        
        # Filter by tier if specified
        if tiers:
            filtered = []
            for source_id in source_ids:
                source = self.sources.get(source_id)
                if source and source.tier in tiers:
                    filtered.append(source_id)
            return filtered
        
        return source_ids
    
    def _rank_results(self, results: List[Dict[str, Any]], intent: str) -> List[Dict[str, Any]]:
        """Rank results by relevance"""
        # Sort by trust_score, then by tier (lower is better for internal)
        results.sort(key=lambda x: (
            -x.get("trust_score", 0),  # Higher trust first
            x.get("tier", 999) if intent == "internal_ops" else -x.get("tier", 0)  # Tier 0 first for internal
        ), reverse=True)
        
        return results
