"""
Search Adapter: Web search functionality (can use internal or external providers)
"""
from typing import Dict, Any, Optional
from datetime import datetime

from earnetics.gateway.adapters.base_adapter import BaseAdapter
from earnetics.knowledge_store.store import KnowledgeStore
from earnetics.knowledge_router.router import KnowledgeRouter


class SearchAdapter(BaseAdapter):
    """Search adapter - uses internal knowledge router by default"""
    
    def __init__(self, config: Dict[str, Any], credential_vault=None):
        super().__init__(config, credential_vault)
        adapter_config = config.get("adapters", {}).get("search_adapter", {})
        self.default_provider = adapter_config.get("default_provider", "internal")
        self.providers = adapter_config.get("providers", {})
        
        # Initialize internal search (offline-first)
        self.knowledge_router = KnowledgeRouter()
        self.knowledge_store = KnowledgeStore()
    
    def execute(self, action: str, params: Dict[str, Any],
               agent_id: str, role: str) -> Dict[str, Any]:
        """Execute search action"""
        query = params.get("query")
        if not query:
            return {
                "success": False,
                "error": "Query parameter required",
                "data": None,
                "metadata": {},
                "citation": {}
            }
        
        recency_days = params.get("recency_days")
        sources_hint = params.get("sources_hint")
        
        try:
            # Use internal knowledge router (offline-first)
            results = self.knowledge_router.route(
                query,
                sources=sources_hint,
                tiers=None
            )
            
            # Also search knowledge store
            store_results = self.knowledge_store.search(
                query,
                sources=sources_hint,
                time_window_hours=recency_days * 24 if recency_days else None,
                limit=20
            )
            
            # Combine and format results
            formatted_results = []
            seen_ids = set()
            
            for result in results:
                ref_id = result.get("id")
                if ref_id and ref_id not in seen_ids:
                    formatted_results.append({
                        "id": ref_id,
                        "title": result.get("title"),
                        "url": result.get("url"),
                        "summary": result.get("summary", ""),
                        "source_id": result.get("source_id"),
                        "tier": result.get("tier"),
                        "trust_score": result.get("trust_score")
                    })
                    seen_ids.add(ref_id)
            
            for record in store_results:
                if record.id not in seen_ids:
                    formatted_results.append({
                        "id": record.id,
                        "title": record.title,
                        "url": record.url,
                        "summary": record.summary,
                        "source_id": record.source_id,
                        "tier": record.tier,
                        "trust_score": record.trust_score
                    })
                    seen_ids.add(record.id)
            
            citation = self.create_citation(f"search://internal?q={query}")
            
            return {
                "success": True,
                "data": {
                    "results": formatted_results[:20],  # Limit to 20
                    "query": query,
                    "total": len(formatted_results)
                },
                "metadata": {
                    "provider": "internal",
                    "sources_searched": sources_hint or "all",
                    "recency_days": recency_days
                },
                "citation": citation,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": None,
                "metadata": {},
                "citation": {}
            }
