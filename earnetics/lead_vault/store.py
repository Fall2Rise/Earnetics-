"""
Lead Vault Store: PII storage with governance, audit, suppression
"""
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from earnetics.lead_vault.schema import LeadRecord, LeadEvidence, EntityType
from backend.corporate_memory import BUSINESS_DB_PATH


class LeadVaultStore:
    """Lead Vault with PII governance, audit logs, suppression"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(Path(BUSINESS_DB_PATH).parent / "lead_vault.db")
        self._ensure_schema()
    
    def _ensure_schema(self):
        """Create database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Lead records
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lead_records (
                    lead_id TEXT PRIMARY KEY,
                    entity_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    business_name TEXT,
                    role TEXT,
                    emails TEXT,
                    phones TEXT,
                    addresses TEXT,
                    profiles TEXT,
                    source TEXT,
                    compliance TEXT NOT NULL,
                    tags TEXT,
                    scores TEXT,
                    notes TEXT,
                    last_verified_at TEXT,
                    expires_at TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Lead evidence
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lead_evidence (
                    evidence_id TEXT PRIMARY KEY,
                    lead_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    url TEXT NOT NULL,
                    captured_at TEXT NOT NULL,
                    citation TEXT NOT NULL,
                    FOREIGN KEY (lead_id) REFERENCES lead_records(lead_id)
                )
            """)
            
            # Audit log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lead_audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    lead_id TEXT,
                    details TEXT,
                    ip_address TEXT
                )
            """)
            
            # Suppression list
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS suppression_list (
                    lead_id TEXT PRIMARY KEY,
                    reason TEXT NOT NULL,
                    suppressed_at TEXT NOT NULL,
                    suppressed_by TEXT NOT NULL
                )
            """)
            
            # Indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_entity_type 
                ON lead_records(entity_type)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_compliance_dnc 
                ON lead_records(compliance)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_lead 
                ON lead_audit_log(lead_id)
            """)
            
            conn.commit()
    
    def store(self, lead: LeadRecord, user_id: str) -> bool:
        """Store lead record with audit"""
        try:
            # Check suppression
            if self._is_suppressed(lead.lead_id):
                self._audit(user_id, "store_blocked", lead.lead_id, {"reason": "suppressed"})
                return False
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                now = datetime.utcnow().isoformat()
                lead.updated_at = now
                
                cursor.execute("""
                    INSERT OR REPLACE INTO lead_records
                    (lead_id, entity_type, name, business_name, role,
                     emails, phones, addresses, profiles, source, compliance,
                     tags, scores, notes, last_verified_at, expires_at,
                     created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    lead.lead_id,
                    lead.entity_type.value,
                    lead.name,
                    lead.business_name,
                    lead.role,
                    json.dumps([e.__dict__ for e in lead.emails]),
                    json.dumps([p.__dict__ for p in lead.phones]),
                    json.dumps(lead.addresses),
                    json.dumps(lead.profiles),
                    json.dumps(lead.source.__dict__) if lead.source else None,
                    json.dumps(lead.compliance.__dict__),
                    json.dumps(lead.tags),
                    json.dumps(lead.scores),
                    lead.notes,
                    lead.last_verified_at,
                    lead.expires_at,
                    lead.created_at,
                    lead.updated_at
                ))
                
                conn.commit()
                
                self._audit(user_id, "store", lead.lead_id)
                return True
        except Exception as e:
            print(f"Error storing lead: {e}")
            return False
    
    def get(self, lead_id: str, user_id: str) -> Optional[LeadRecord]:
        """Get lead with audit"""
        self._audit(user_id, "read", lead_id)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM lead_records WHERE lead_id = ?", (lead_id,))
                row = cursor.fetchone()
                
                if row:
                    return self._row_to_lead(row)
        except Exception as e:
            print(f"Error retrieving lead: {e}")
        return None
    
    def search(self, filters: Dict[str, Any], user_id: str, limit: int = 100) -> List[LeadRecord]:
        """Search leads with audit"""
        self._audit(user_id, "search", None, {"filters": filters})
        
        results = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                sql = "SELECT * FROM lead_records WHERE 1=1"
                params = []
                
                # Apply filters
                if filters.get("entity_type"):
                    sql += " AND entity_type = ?"
                    params.append(filters["entity_type"])
                
                if filters.get("tags"):
                    sql += " AND tags LIKE ?"
                    params.append(f"%{filters['tags']}%")
                
                if filters.get("do_not_contact") is not None:
                    # Parse compliance JSON to check do_not_contact
                    # Simplified: check in compliance field
                    pass
                
                # Suppression enforcement
                sql += " AND lead_id NOT IN (SELECT lead_id FROM suppression_list)"
                
                sql += " ORDER BY created_at DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(sql, params)
                
                for row in cursor.fetchall():
                    lead = self._row_to_lead(row)
                    if lead and not lead.compliance.do_not_contact:
                        results.append(lead)
        except Exception as e:
            print(f"Error searching leads: {e}")
        
        return results
    
    def suppress(self, lead_id: str, reason: str, user_id: str) -> bool:
        """Suppress lead"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Update compliance
                cursor.execute("""
                    UPDATE lead_records
                    SET compliance = json_set(compliance, '$.do_not_contact', true),
                        compliance = json_set(compliance, '$.suppression_reason', ?),
                        updated_at = ?
                    WHERE lead_id = ?
                """, (reason, datetime.utcnow().isoformat(), lead_id))
                
                # Add to suppression list
                cursor.execute("""
                    INSERT OR REPLACE INTO suppression_list
                    (lead_id, reason, suppressed_at, suppressed_by)
                    VALUES (?, ?, ?, ?)
                """, (lead_id, reason, datetime.utcnow().isoformat(), user_id))
                
                conn.commit()
                
                self._audit(user_id, "suppress", lead_id, {"reason": reason})
                return True
        except Exception as e:
            print(f"Error suppressing lead: {e}")
            return False
    
    def export(self, segment_id: str, channel_rules: Dict[str, Any], user_id: str) -> List[LeadRecord]:
        """Export leads with permission gating"""
        self._audit(user_id, "export", None, {"segment_id": segment_id, "channel_rules": channel_rules})
        
        # Get leads matching segment
        filters = channel_rules.get("filters", {})
        leads = self.search(filters, user_id, limit=10000)
        
        # Apply channel rules
        exported = []
        for lead in leads:
            # Check allowed channels
            if channel_rules.get("channel") not in lead.compliance.allowed_channels:
                continue
            
            # Check do_not_contact
            if lead.compliance.do_not_contact:
                continue
            
            exported.append(lead)
        
        return exported
    
    def _is_suppressed(self, lead_id: str) -> bool:
        """Check if lead is suppressed"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM suppression_list WHERE lead_id = ?", (lead_id,))
                return cursor.fetchone() is not None
        except:
            return False
    
    def _audit(self, user_id: str, action: str, lead_id: Optional[str] = None,
               details: Optional[Dict[str, Any]] = None):
        """Log audit event"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO lead_audit_log
                    (timestamp, user_id, action, lead_id, details)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    datetime.utcnow().isoformat(),
                    user_id,
                    action,
                    lead_id,
                    json.dumps(details) if details else None
                ))
                conn.commit()
        except Exception as e:
            print(f"Error logging audit: {e}")
    
    def _row_to_lead(self, row: sqlite3.Row) -> LeadRecord:
        """Convert database row to LeadRecord"""
        from earnetics.lead_vault.schema import SourceInfo, ComplianceInfo, ContactInfo, ContactType, LegalBasis, ConsentStatus
        
        emails_data = json.loads(row["emails"] or "[]")
        emails = [ContactInfo(
            value=e["value"],
            verified=e.get("verified", False),
            type=ContactType(e.get("type", "work"))
        ) for e in emails_data]
        
        phones_data = json.loads(row["phones"] or "[]")
        phones = [ContactInfo(
            value=p["value"],
            verified=p.get("verified", False),
            type=ContactType(p.get("type", "work"))
        ) for p in phones_data]
        
        source_data = json.loads(row["source"]) if row["source"] else None
        source = SourceInfo(**source_data) if source_data else None
        
        compliance_data = json.loads(row["compliance"])
        compliance = ComplianceInfo(
            legal_basis=LegalBasis(compliance_data.get("legal_basis", "unknown")),
            consent={k: ConsentStatus(v) if isinstance(v, str) else v 
                    for k, v in compliance_data.get("consent", {}).items()},
            allowed_channels=compliance_data.get("allowed_channels", ["email"]),
            do_not_contact=compliance_data.get("do_not_contact", False),
            suppression_reason=compliance_data.get("suppression_reason")
        )
        
        return LeadRecord(
            lead_id=row["lead_id"],
            entity_type=EntityType(row["entity_type"]),
            name=row["name"],
            business_name=row["business_name"],
            role=row["role"],
            emails=emails,
            phones=phones,
            addresses=json.loads(row["addresses"] or "[]"),
            profiles=json.loads(row["profiles"] or "[]"),
            source=source,
            compliance=compliance,
            tags=json.loads(row["tags"] or "[]"),
            scores=json.loads(row["scores"] or "{}"),
            notes=row["notes"] or "",
            last_verified_at=row["last_verified_at"],
            expires_at=row["expires_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )
