"""
Head Office Data Models
Enterprise-grade schemas for owner operations
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class DecisionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    REQUEST_INFO = "request_info"


class ContractStatus(str, Enum):
    DRAFT = "draft"
    REVIEW = "review"
    REDLINED = "redlined"
    APPROVED = "approved"
    SIGNED = "signed"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"


class ComplianceStatus(str, Enum):
    ON_TRACK = "on_track"
    AT_RISK = "at_risk"
    OVERDUE = "overdue"
    COMPLETE = "complete"


class AssetCategory(str, Enum):
    DIGITAL = "digital"
    FINANCIAL = "financial"
    IP = "ip"
    PHYSICAL = "physical"
    ACCESS = "access"


class MasterAIMode(str, Enum):
    ADVISOR = "advisor"  # Recommend only
    OPERATOR = "operator"  # Low-risk execute
    EXECUTIVE = "executive"  # Requires approval tokens


@dataclass
class DecisionQueueItem:
    """Decision queue item for approvals"""
    id: str
    title: str
    category: str  # spend, publish, dns, legal, payout
    recommendation: str
    upside: str
    risk: str
    reversibility: str
    required_by: str  # ISO date
    cost: Optional[float] = None
    alternatives: List[str] = field(default_factory=list)
    status: DecisionStatus = DecisionStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "recommendation": self.recommendation,
            "upside": self.upside,
            "cost": self.cost,
            "risk": self.risk,
            "reversibility": self.reversibility,
            "alternatives": self.alternatives,
            "required_by": self.required_by,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata
        }


@dataclass
class Contract:
    """Contract entity"""
    id: str
    title: str
    party_name: str  # The "party" named in contract
    counterparty: str
    contract_type: str  # vendor, customer, partnership, etc.
    status: ContractStatus
    version: int = 1
    file_path: Optional[str] = None
    signed_date: Optional[str] = None
    expiry_date: Optional[str] = None
    value: Optional[float] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "party_name": self.party_name,
            "counterparty": self.counterparty,
            "contract_type": self.contract_type,
            "status": self.status.value,
            "version": self.version,
            "file_path": self.file_path,
            "signed_date": self.signed_date,
            "expiry_date": self.expiry_date,
            "value": self.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata
        }


@dataclass
class ContractScanResult:
    """Contract loophole scanner results"""
    contract_id: str
    risk_level: str  # high, medium, low
    executive_summary: str
    risk_map: Dict[str, List[str]] = field(default_factory=dict)  # category -> issues
    missing_items: List[str] = field(default_factory=list)
    redline_suggestions: List[Dict[str, Any]] = field(default_factory=list)
    negotiation_playbook: List[str] = field(default_factory=list)
    guarantee_detected: bool = False
    signature_recommendation: Optional[str] = None
    scanned_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "contract_id": self.contract_id,
            "risk_level": self.risk_level,
            "executive_summary": self.executive_summary,
            "risk_map": self.risk_map,
            "missing_items": self.missing_items,
            "redline_suggestions": self.redline_suggestions,
            "negotiation_playbook": self.negotiation_playbook,
            "guarantee_detected": self.guarantee_detected,
            "signature_recommendation": self.signature_recommendation,
            "scanned_at": self.scanned_at
        }


@dataclass
class ComplianceItem:
    """Compliance tracking item"""
    id: str
    title: str
    category: str  # filing, renewal, policy, obligation
    jurisdiction: str
    deadline: str  # ISO date
    status: ComplianceStatus
    obligation_source: Optional[str] = None  # contract_id, regulation_id, etc.
    completed_at: Optional[str] = None
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "jurisdiction": self.jurisdiction,
            "deadline": self.deadline,
            "status": self.status.value,
            "obligation_source": self.obligation_source,
            "completed_at": self.completed_at,
            "notes": self.notes,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


@dataclass
class TaxTask:
    """Tax filing task"""
    id: str
    title: str
    tax_type: str  # federal, state, local, payroll, etc.
    filing_period: str  # 2024, Q1-2024, etc.
    deadline: str  # ISO date
    status: str = "pending"
    documents: List[str] = field(default_factory=list)
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "tax_type": self.tax_type,
            "filing_period": self.filing_period,
            "deadline": self.deadline,
            "status": self.status,
            "documents": self.documents,
            "notes": self.notes,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


@dataclass
class Asset:
    """Asset inventory item"""
    id: str
    name: str
    category: AssetCategory
    owner: str  # email or user_id
    criticality: str  # critical, high, medium, low
    description: str = ""
    access_info: Optional[str] = None
    renewal_date: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category.value,
            "owner": self.owner,
            "criticality": self.criticality,
            "description": self.description,
            "access_info": self.access_info,
            "renewal_date": self.renewal_date,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


@dataclass
class AssetAlert:
    """Safety radar alert"""
    id: str
    asset_id: str
    alert_type: str  # expiry, dns_change, suspicious_login, etc.
    severity: str  # critical, warning, info
    message: str
    detected_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    resolved_at: Optional[str] = None
    resolved_by: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "asset_id": self.asset_id,
            "alert_type": self.alert_type,
            "severity": self.severity,
            "message": self.message,
            "detected_at": self.detected_at,
            "resolved_at": self.resolved_at,
            "resolved_by": self.resolved_by
        }


@dataclass
class LawLibraryEntry:
    """Law library entry"""
    id: str
    title: str
    shelf: str  # contract_law, corporate, employment, etc.
    jurisdiction: str
    applicability_tags: List[str] = field(default_factory=list)
    summary: str = ""
    compliance_checklist: List[str] = field(default_factory=list)
    risk_level: str = "medium"
    primary_sources: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "shelf": self.shelf,
            "jurisdiction": self.jurisdiction,
            "applicability_tags": self.applicability_tags,
            "summary": self.summary,
            "compliance_checklist": self.compliance_checklist,
            "risk_level": self.risk_level,
            "primary_sources": self.primary_sources,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


@dataclass
class MasterAIAction:
    """Master AI action record"""
    id: str
    request: str
    mode: MasterAIMode
    action_type: str
    approval_required: bool
    approval_token: Optional[str] = None
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    audit_log_link: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "request": self.request,
            "mode": self.mode.value,
            "action_type": self.action_type,
            "approval_required": self.approval_required,
            "approval_token": self.approval_token,
            "status": self.status,
            "result": self.result,
            "audit_log_link": self.audit_log_link,
            "created_at": self.created_at,
            "completed_at": self.completed_at
        }


@dataclass
class AuditLogEvent:
    """Audit log event"""
    id: str
    actor: str  # user_id or "master_ai"
    action_type: str
    resource: str  # resource_id or resource_type
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    diff: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "actor": self.actor,
            "action_type": self.action_type,
            "resource": self.resource,
            "timestamp": self.timestamp,
            "diff": self.diff,
            "metadata": self.metadata
        }
