"""
Unified data contracts for Knowledge Store
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import hashlib
import json


@dataclass
class CitationObject:
    """Mandatory citation for external knowledge"""
    source_id: str
    url: str
    retrieved_at: str  # ISO8601
    published_at: Optional[str] = None  # ISO8601
    snapshot: Optional[Dict[str, str]] = None  # For Wayback: {"timestamp": "YYYYMMDDhhmmss", "wayback_url": ""}
    provenance: str = ""  # connector_name + method
    confidence: float = 1.0  # 0-1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "url": self.url,
            "retrieved_at": self.retrieved_at,
            "published_at": self.published_at,
            "snapshot": self.snapshot,
            "provenance": self.provenance,
            "confidence": self.confidence
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CitationObject':
        return cls(
            source_id=data["source_id"],
            url=data["url"],
            retrieved_at=data["retrieved_at"],
            published_at=data.get("published_at"),
            snapshot=data.get("snapshot"),
            provenance=data.get("provenance", ""),
            confidence=data.get("confidence", 1.0)
        )


@dataclass
class KnowledgeRecord:
    """Unified knowledge record with mandatory citations for external sources"""
    id: str
    source_id: str
    tier: int  # 0-6
    title: str
    url: str
    retrieved_at: str  # ISO8601
    published_at: Optional[str] = None  # ISO8601
    authors: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    summary: str = ""
    content_text: str = ""
    content_chunks: List[str] = field(default_factory=list)
    embedding_ids: List[str] = field(default_factory=list)
    citation: Optional[CitationObject] = None  # Mandatory for tier > 0
    trust_score: int = 0  # 0-100
    raw: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate that external knowledge has citations"""
        if self.tier > 0 and self.citation is None:
            raise ValueError(f"KnowledgeRecord from tier {self.tier} must include CitationObject")

    @classmethod
    def create_id(cls, source_id: str, url: str, retrieved_at: Optional[str] = None) -> str:
        """Generate deterministic ID"""
        timestamp = retrieved_at or datetime.utcnow().isoformat()
        content = f"{source_id}:{url}:{timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source_id": self.source_id,
            "tier": self.tier,
            "title": self.title,
            "url": self.url,
            "retrieved_at": self.retrieved_at,
            "published_at": self.published_at,
            "authors": self.authors,
            "entities": self.entities,
            "tags": self.tags,
            "summary": self.summary,
            "content_text": self.content_text,
            "content_chunks": self.content_chunks,
            "embedding_ids": self.embedding_ids,
            "citation": self.citation.to_dict() if self.citation else None,
            "trust_score": self.trust_score,
            "raw": self.raw
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeRecord':
        citation = None
        if data.get("citation"):
            citation = CitationObject.from_dict(data["citation"])
        return cls(
            id=data["id"],
            source_id=data["source_id"],
            tier=data["tier"],
            title=data["title"],
            url=data["url"],
            retrieved_at=data["retrieved_at"],
            published_at=data.get("published_at"),
            authors=data.get("authors", []),
            entities=data.get("entities", []),
            tags=data.get("tags", []),
            summary=data.get("summary", ""),
            content_text=data.get("content_text", ""),
            content_chunks=data.get("content_chunks", []),
            embedding_ids=data.get("embedding_ids", []),
            citation=citation,
            trust_score=data.get("trust_score", 0),
            raw=data.get("raw", {})
        )
