"""
Truth Library schemas for validated playbooks, SOPs, strategies, experiments
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import hashlib


class AssetStatus(str, Enum):
    DRAFT = "draft"
    VALIDATED = "validated"
    DEPRECATED = "deprecated"


class AssetType(str, Enum):
    REFERENCE = "reference"  # facts/specs
    SOP = "sop"  # step workflow
    PLAYBOOK = "playbook"  # workflow + monetization + KPIs
    STRATEGY = "strategy"  # thesis + positioning
    EXPERIMENT = "experiment"  # hypothesis → setup → results → next


@dataclass
class TruthLibraryAsset:
    """Truth Library asset with versioning and validation"""
    asset_id: str
    type: AssetType
    title: str
    status: AssetStatus
    version: int
    last_verified_at: Optional[str]  # ISO8601
    citations: List[Dict[str, Any]]  # CitationObjects as dicts
    confidence: float  # 0-1
    owner: str
    tags: List[str]
    
    # Content
    content: Dict[str, Any]  # Type-specific content
    
    # Validation requirements
    measurable_results: Optional[Dict[str, Any]] = None  # Required for validated playbooks
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    deprecated_at: Optional[str] = None
    deprecated_reason: Optional[str] = None
    
    def __post_init__(self):
        """Validate asset requirements"""
        if self.status == AssetStatus.VALIDATED:
            if self.type in [AssetType.PLAYBOOK, AssetType.EXPERIMENT]:
                if not self.measurable_results:
                    raise ValueError(f"Validated {self.type.value} must include measurable_results")
            if not self.last_verified_at:
                self.last_verified_at = datetime.utcnow().isoformat()
    
    @classmethod
    def create_id(cls, title: str, type: AssetType) -> str:
        """Generate deterministic asset ID"""
        content = f"{title}:{type.value}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "type": self.type.value,
            "title": self.title,
            "status": self.status.value,
            "version": self.version,
            "last_verified_at": self.last_verified_at,
            "citations": self.citations,
            "confidence": self.confidence,
            "owner": self.owner,
            "tags": self.tags,
            "content": self.content,
            "measurable_results": self.measurable_results,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "deprecated_at": self.deprecated_at,
            "deprecated_reason": self.deprecated_reason
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TruthLibraryAsset':
        return cls(
            asset_id=data["asset_id"],
            type=AssetType(data["type"]),
            title=data["title"],
            status=AssetStatus(data["status"]),
            version=data["version"],
            last_verified_at=data.get("last_verified_at"),
            citations=data.get("citations", []),
            confidence=data.get("confidence", 0.5),
            owner=data["owner"],
            tags=data.get("tags", []),
            content=data["content"],
            measurable_results=data.get("measurable_results"),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            updated_at=data.get("updated_at", datetime.utcnow().isoformat()),
            deprecated_at=data.get("deprecated_at"),
            deprecated_reason=data.get("deprecated_reason")
        )
