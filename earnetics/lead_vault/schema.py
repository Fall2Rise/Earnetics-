"""
Lead Vault schemas for PII storage with governance
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import hashlib


class EntityType(str, Enum):
    BUSINESS = "business"
    PERSON = "person"


class ContactType(str, Enum):
    WORK = "work"
    MOBILE = "mobile"
    PERSONAL = "personal"


class LegalBasis(str, Enum):
    PUBLIC_BUSINESS_CONTACT = "public_business_contact"
    OPT_IN = "opt_in"
    UNKNOWN = "unknown"


class ConsentStatus(str, Enum):
    UNKNOWN = "unknown"
    YES = "yes"
    NO = "no"


@dataclass
class ContactInfo:
    """Contact information with verification"""
    value: str
    verified: bool = False
    type: ContactType = ContactType.WORK
    verified_at: Optional[str] = None


@dataclass
class ComplianceInfo:
    """Compliance and consent information"""
    legal_basis: LegalBasis = LegalBasis.UNKNOWN
    consent: Dict[str, ConsentStatus] = field(default_factory=lambda: {
        "email": ConsentStatus.UNKNOWN,
        "sms": ConsentStatus.UNKNOWN,
        "call": ConsentStatus.UNKNOWN
    })
    allowed_channels: List[str] = field(default_factory=lambda: ["email"])
    do_not_contact: bool = False
    suppression_reason: Optional[str] = None


@dataclass
class SourceInfo:
    """Source information for lead"""
    source_type: str  # scrape, import, form_optin, partner
    source_url: str
    collected_at: str  # ISO8601
    collector_agent: str


@dataclass
class LeadRecord:
    """Lead record with PII governance"""
    lead_id: str
    entity_type: EntityType
    name: str
    business_name: Optional[str] = None
    role: Optional[str] = None
    emails: List[ContactInfo] = field(default_factory=list)
    phones: List[ContactInfo] = field(default_factory=list)
    addresses: List[Dict[str, str]] = field(default_factory=list)
    profiles: List[Dict[str, str]] = field(default_factory=list)
    source: Optional[SourceInfo] = None
    compliance: ComplianceInfo = field(default_factory=ComplianceInfo)
    tags: List[str] = field(default_factory=list)
    scores: Dict[str, float] = field(default_factory=lambda: {
        "fit": 0.0,
        "intent": 0.0,
        "priority": 0.0
    })
    notes: str = ""
    last_verified_at: Optional[str] = None
    expires_at: Optional[str] = None
    
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    @classmethod
    def create_id(cls, name: str, entity_type: EntityType, source_url: str) -> str:
        """Generate deterministic lead ID"""
        content = f"{name}:{entity_type.value}:{source_url}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "lead_id": self.lead_id,
            "entity_type": self.entity_type.value,
            "name": self.name,
            "business_name": self.business_name,
            "role": self.role,
            "emails": [{"value": e.value, "verified": e.verified, "type": e.type.value} for e in self.emails],
            "phones": [{"value": p.value, "verified": p.verified, "type": p.type.value} for p in self.phones],
            "addresses": self.addresses,
            "profiles": self.profiles,
            "source": {
                "source_type": self.source.source_type,
                "source_url": self.source.source_url,
                "collected_at": self.source.collected_at,
                "collector_agent": self.source.collector_agent
            } if self.source else None,
            "compliance": {
                "legal_basis": self.compliance.legal_basis.value,
                "consent": {k: v.value for k, v in self.compliance.consent.items()},
                "allowed_channels": self.compliance.allowed_channels,
                "do_not_contact": self.compliance.do_not_contact,
                "suppression_reason": self.compliance.suppression_reason
            },
            "tags": self.tags,
            "scores": self.scores,
            "notes": self.notes,
            "last_verified_at": self.last_verified_at,
            "expires_at": self.expires_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LeadRecord':
        emails = [ContactInfo(**e) if isinstance(e, dict) else e for e in data.get("emails", [])]
        phones = [ContactInfo(**p) if isinstance(p, dict) else p for p in data.get("phones", [])]
        
        source = None
        if data.get("source"):
            source = SourceInfo(**data["source"])
        
        compliance_data = data.get("compliance", {})
        compliance = ComplianceInfo(
            legal_basis=LegalBasis(compliance_data.get("legal_basis", "unknown")),
            consent={k: ConsentStatus(v) if isinstance(v, str) else v 
                    for k, v in compliance_data.get("consent", {}).items()},
            allowed_channels=compliance_data.get("allowed_channels", ["email"]),
            do_not_contact=compliance_data.get("do_not_contact", False),
            suppression_reason=compliance_data.get("suppression_reason")
        )
        
        return cls(
            lead_id=data["lead_id"],
            entity_type=EntityType(data["entity_type"]),
            name=data["name"],
            business_name=data.get("business_name"),
            role=data.get("role"),
            emails=emails,
            phones=phones,
            addresses=data.get("addresses", []),
            profiles=data.get("profiles", []),
            source=source,
            compliance=compliance,
            tags=data.get("tags", []),
            scores=data.get("scores", {}),
            notes=data.get("notes", ""),
            last_verified_at=data.get("last_verified_at"),
            expires_at=data.get("expires_at"),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            updated_at=data.get("updated_at", datetime.utcnow().isoformat())
        )


@dataclass
class LeadEvidence:
    """Evidence for lead (html snapshot, text snippet, wayback snapshot)"""
    evidence_id: str
    lead_id: str
    type: str  # html_snapshot, text_snippet, wayback_snapshot
    url: str
    captured_at: str  # ISO8601
    citation: Dict[str, Any]  # CitationObject as dict
    
    @classmethod
    def create_id(cls, lead_id: str, url: str) -> str:
        """Generate deterministic evidence ID"""
        content = f"{lead_id}:{url}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
