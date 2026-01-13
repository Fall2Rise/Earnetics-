"""
Agent Tools API: knowledge.search/fetch/extract/cite/remember
"""
from typing import List, Dict, Any, Optional
from pathlib import Path

from earnetics.knowledge_router.router import KnowledgeRouter
from earnetics.knowledge_store.store import KnowledgeStore
from earnetics.knowledge_store.schema import KnowledgeRecord, CitationObject


class KnowledgeTools:
    """Agent tools for knowledge operations"""
    
    def __init__(self):
        self.router = KnowledgeRouter()
        self.store = KnowledgeStore()
    
    def search(self, query: str, sources: Optional[List[str]] = None,
               tiers: Optional[List[int]] = None, 
               time_window_hours: Optional[int] = None,
               limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search knowledge base
        
        Returns list of references with metadata
        """
        # Route query
        results = self.router.route(query, sources=sources, tiers=tiers)
        
        # Also search store
        store_results = self.store.search(
            query, sources=sources, tiers=tiers,
            time_window_hours=time_window_hours, limit=limit
        )
        
        # Combine and dedupe
        refs = []
        seen_ids = set()
        
        for result in results:
            ref_id = result.get("id")
            if ref_id and ref_id not in seen_ids:
                refs.append({
                    "id": ref_id,
                    "title": result.get("title"),
                    "url": result.get("url"),
                    "source_id": result.get("source_id"),
                    "tier": result.get("tier"),
                    "trust_score": result.get("trust_score"),
                    "summary": result.get("summary"),
                    "rationale": result.get("rationale")
                })
                seen_ids.add(ref_id)
        
        for record in store_results:
            if record.id not in seen_ids:
                refs.append({
                    "id": record.id,
                    "title": record.title,
                    "url": record.url,
                    "source_id": record.source_id,
                    "tier": record.tier,
                    "trust_score": record.trust_score,
                    "summary": record.summary
                })
                seen_ids.add(record.id)
        
        return refs[:limit]
    
    def fetch(self, ref: Dict[str, Any]) -> KnowledgeRecord:
        """
        Fetch full content for a reference
        
        Returns KnowledgeRecord with content_text and citation
        """
        ref_id = ref.get("id")
        source_id = ref.get("source_id")
        
        # Try store first
        if ref_id:
            record = self.store.get(ref_id)
            if record:
                return record
        
        # Fetch from source
        source = self.router.sources.get(source_id)
        if source and source.can_fetch():
            return source.fetch(ref)
        
        raise ValueError(f"Cannot fetch reference: {ref}")
    
    def extract(self, ref: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured data from knowledge record
        
        schema: {"entities": ["person", "organization"], "steps": bool, "checklist": bool}
        """
        record = self.fetch(ref)
        
        extracted = {}
        
        # Extract entities if requested
        if schema.get("entities"):
            # Simple entity extraction (can be enhanced with NLP)
            extracted["entities"] = record.entities
        
        # Extract steps if requested
        if schema.get("steps"):
            # Look for numbered lists or step patterns
            import re
            steps = re.findall(r'(?:^|\n)\s*(?:\d+\.|Step \d+:|-\s*)(.+?)(?=\n|$)', record.content_text, re.MULTILINE)
            extracted["steps"] = [s.strip() for s in steps]
        
        # Extract checklist if requested
        if schema.get("checklist"):
            import re
            checklist = re.findall(r'(?:^|\n)\s*[-*✓]\s*(.+?)(?=\n|$)', record.content_text, re.MULTILINE)
            extracted["checklist"] = [c.strip() for c in checklist]
        
        return extracted
    
    def cite(self, ref: Dict[str, Any]) -> CitationObject:
        """
        Get citation object for a reference
        """
        record = self.fetch(ref)
        
        if record.citation:
            return record.citation
        
        # Create citation if missing
        return CitationObject(
            source_id=record.source_id,
            url=record.url,
            retrieved_at=record.retrieved_at,
            published_at=record.published_at,
            provenance=f"{record.source_id}_connector",
            confidence=record.trust_score / 100.0
        )
    
    def remember(self, record: KnowledgeRecord) -> bool:
        """
        Store knowledge record in Tier 0 Vault + embed/index
        
        Agents use this to store learned knowledge
        """
        # Store in knowledge store
        success = self.store.store(record)
        
        # TODO: Trigger embedding/indexing
        # This would integrate with vector store
        
        return success
