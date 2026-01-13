"""
Lead Tools: ingest, search, verify, suppress, export, audit
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from earnetics.lead_vault.store import LeadVaultStore
from earnetics.lead_vault.schema import LeadRecord, LeadEvidence, EntityType, SourceInfo, ContactInfo, ContactType, ComplianceInfo, LegalBasis


class LeadTools:
    """Agent tools for Lead Vault operations"""
    
    def __init__(self):
        self.vault = LeadVaultStore()
    
    def ingest(self, records: List[Dict[str, Any]], evidence: Optional[List[Dict[str, Any]]] = None,
               user_id: str = "system") -> Dict[str, Any]:
        """
        Ingest lead records with evidence
        
        Records should include contact info, source, compliance
        """
        ingested = []
        errors = []
        
        for record_data in records:
            try:
                lead = self._dict_to_lead(record_data)
                if self.vault.store(lead, user_id):
                    ingested.append(lead.lead_id)
                    
                    # Store evidence if provided
                    if evidence:
                        for ev in evidence:
                            if ev.get("lead_id") == lead.lead_id:
                                # Store evidence (implementation needed)
                                pass
                else:
                    errors.append(f"Failed to store {record_data.get('name', 'unknown')}")
            except Exception as e:
                errors.append(f"Error ingesting record: {e}")
        
        return {
            "success": len(ingested) > 0,
            "ingested_count": len(ingested),
            "ingested_ids": ingested,
            "errors": errors
        }
    
    def search(self, filters: Dict[str, Any], user_id: str = "system", limit: int = 100) -> List[Dict[str, Any]]:
        """Search leads with permission gating"""
        leads = self.vault.search(filters, user_id, limit)
        return [lead.to_dict() for lead in leads]
    
    def verify(self, lead_id: str, method: str, user_id: str = "system") -> Dict[str, Any]:
        """Verify lead contact information"""
        lead = self.vault.get(lead_id, user_id)
        if not lead:
            return {"success": False, "message": "Lead not found"}
        
        # Update verification status
        # This would integrate with verification service
        return {
            "success": True,
            "lead_id": lead_id,
            "method": method,
            "verified_at": datetime.utcnow().isoformat()
        }
    
    def suppress(self, lead_id: str, reason: str, user_id: str = "system") -> Dict[str, Any]:
        """Suppress lead (add to do-not-contact list)"""
        success = self.vault.suppress(lead_id, reason, user_id)
        return {
            "success": success,
            "lead_id": lead_id,
            "reason": reason
        }
    
    def export(self, segment_id: str, channel_rules: Dict[str, Any], user_id: str = "system") -> List[Dict[str, Any]]:
        """Export leads with permission gating and channel rules"""
        leads = self.vault.export(segment_id, channel_rules, user_id)
        return [lead.to_dict() for lead in leads]
    
    def audit(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query audit log"""
        # Implementation would query audit log
        return []
    
    def _dict_to_lead(self, data: Dict[str, Any]) -> LeadRecord:
        """Convert dict to LeadRecord"""
        from datetime import datetime
        
        emails = [ContactInfo(**e) if isinstance(e, dict) else e for e in data.get("emails", [])]
        phones = [ContactInfo(**p) if isinstance(p, dict) else p for p in data.get("phones", [])]
        
        source_data = data.get("source", {})
        source = SourceInfo(
            source_type=source_data.get("source_type", "unknown"),
            source_url=source_data.get("source_url", ""),
            collected_at=source_data.get("collected_at", datetime.utcnow().isoformat()),
            collector_agent=source_data.get("collector_agent", "system")
        )
        
        compliance_data = data.get("compliance", {})
        compliance = ComplianceInfo(
            legal_basis=LegalBasis(compliance_data.get("legal_basis", "unknown")),
            consent=compliance_data.get("consent", {}),
            allowed_channels=compliance_data.get("allowed_channels", ["email"]),
            do_not_contact=compliance_data.get("do_not_contact", False),
            suppression_reason=compliance_data.get("suppression_reason")
        )
        
        lead_id = LeadRecord.create_id(
            data.get("name", "unknown"),
            EntityType(data.get("entity_type", "person")),
            source.source_url
        )
        
        return LeadRecord(
            lead_id=lead_id,
            entity_type=EntityType(data.get("entity_type", "person")),
            name=data.get("name", ""),
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
            notes=data.get("notes", "")
        )
