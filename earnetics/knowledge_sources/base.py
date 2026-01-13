"""
Base class for knowledge source connectors
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from earnetics.knowledge_store.schema import KnowledgeRecord, CitationObject


class KnowledgeSource(ABC):
    """Base class for all knowledge source connectors"""
    
    def __init__(self, source_id: str, config: Dict[str, Any]):
        self.source_id = source_id
        self.config = config
        self.tier = config.get("tier", 0)
        self.enabled = config.get("enabled", True)
        self.trust_score = config.get("trust_score", 50)
        self.requires_internet = config.get("requires_internet", True)
        self.offline_allowed = config.get("offline_allowed", False)
        self.rate_limit_per_min = config.get("rate_limit_per_min", 60)
    
    @abstractmethod
    def search(self, query: str, limit: int = 20, **kwargs) -> List[Dict[str, Any]]:
        """Search the knowledge source. Returns list of result metadata."""
        pass
    
    @abstractmethod
    def fetch(self, ref: Dict[str, Any]) -> KnowledgeRecord:
        """Fetch full content for a reference. Returns KnowledgeRecord with citation."""
        pass
    
    def can_search(self) -> bool:
        """Check if source supports search"""
        return self.config.get("capabilities", {}).get("search", False)
    
    def can_fetch(self) -> bool:
        """Check if source supports fetch"""
        return self.config.get("capabilities", {}).get("fetch", False)
    
    def can_fulltext(self) -> bool:
        """Check if source supports fulltext"""
        return self.config.get("capabilities", {}).get("fulltext", False)
    
    def create_citation(self, url: str, retrieved_at: Optional[str] = None, 
                       published_at: Optional[str] = None,
                       snapshot: Optional[Dict[str, str]] = None) -> CitationObject:
        """Create citation object for this source"""
        if retrieved_at is None:
            retrieved_at = datetime.utcnow().isoformat()
        
        return CitationObject(
            source_id=self.source_id,
            url=url,
            retrieved_at=retrieved_at,
            published_at=published_at,
            snapshot=snapshot,
            provenance=f"{self.source_id}_connector",
            confidence=min(self.trust_score / 100.0, 1.0)
        )
