"""
Head Office Database Service
Local-first SQLite with repository pattern
"""
import sqlite3
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from backend.corporate_memory import BUSINESS_DB_PATH


class HeadOfficeDB:
    """Database service for Head Office module"""
    
    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            db_path = Path(BUSINESS_DB_PATH).parent / "head_office.db"
        self.db_path = Path(db_path)
        self._ensure_schema()
    
    def _ensure_schema(self):
        """Create database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Decision Queue
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS decision_queue (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    recommendation TEXT NOT NULL,
                    upside TEXT NOT NULL,
                    cost REAL,
                    risk TEXT NOT NULL,
                    reversibility TEXT NOT NULL,
                    alternatives TEXT,  -- JSON array
                    required_by TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    metadata TEXT,  -- JSON
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Contracts
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contracts (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    party_name TEXT NOT NULL,
                    counterparty TEXT NOT NULL,
                    contract_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    version INTEGER DEFAULT 1,
                    file_path TEXT,
                    signed_date TEXT,
                    expiry_date TEXT,
                    value REAL,
                    metadata TEXT,  -- JSON
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Contract Scan Results
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contract_scans (
                    contract_id TEXT PRIMARY KEY,
                    risk_level TEXT NOT NULL,
                    executive_summary TEXT NOT NULL,
                    risk_map TEXT,  -- JSON
                    missing_items TEXT,  -- JSON array
                    redline_suggestions TEXT,  -- JSON array
                    negotiation_playbook TEXT,  -- JSON array
                    guarantee_detected INTEGER DEFAULT 0,
                    signature_recommendation TEXT,
                    scanned_at TEXT NOT NULL,
                    FOREIGN KEY (contract_id) REFERENCES contracts(id)
                )
            """)
            
            # Compliance Items
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS compliance_items (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    jurisdiction TEXT NOT NULL,
                    deadline TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'on_track',
                    obligation_source TEXT,
                    completed_at TEXT,
                    notes TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Tax Tasks
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tax_tasks (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    tax_type TEXT NOT NULL,
                    filing_period TEXT NOT NULL,
                    deadline TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    documents TEXT,  -- JSON array
                    notes TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Assets
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS assets (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    owner TEXT NOT NULL,
                    criticality TEXT NOT NULL,
                    description TEXT,
                    access_info TEXT,
                    renewal_date TEXT,
                    metadata TEXT,  -- JSON
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Asset Alerts
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS asset_alerts (
                    id TEXT PRIMARY KEY,
                    asset_id TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    detected_at TEXT NOT NULL,
                    resolved_at TEXT,
                    resolved_by TEXT,
                    FOREIGN KEY (asset_id) REFERENCES assets(id)
                )
            """)
            
            # Law Library
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS law_library (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    shelf TEXT NOT NULL,
                    jurisdiction TEXT NOT NULL,
                    applicability_tags TEXT,  -- JSON array
                    summary TEXT,
                    compliance_checklist TEXT,  -- JSON array
                    risk_level TEXT DEFAULT 'medium',
                    primary_sources TEXT,  -- JSON array
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Master AI Actions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS master_ai_actions (
                    id TEXT PRIMARY KEY,
                    request TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    approval_required INTEGER DEFAULT 0,
                    approval_token TEXT,
                    status TEXT DEFAULT 'pending',
                    result TEXT,  -- JSON
                    audit_log_link TEXT,
                    created_at TEXT NOT NULL,
                    completed_at TEXT
                )
            """)
            
            # Audit Log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id TEXT PRIMARY KEY,
                    actor TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    resource TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    diff TEXT,  -- JSON
                    metadata TEXT  -- JSON
                )
            """)
            
            # Indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_decision_status ON decision_queue(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_decision_category ON decision_queue(category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_compliance_deadline ON compliance_items(deadline)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_compliance_status ON compliance_items(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tax_deadline ON tax_tasks(deadline)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_asset_category ON assets(category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_asset_owner ON assets(owner)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_alert_severity ON asset_alerts(severity)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_law_shelf ON law_library(shelf)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_actor ON audit_log(actor)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp)")
            
            conn.commit()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        return sqlite3.connect(self.db_path)


# Global instance
_db_instance: Optional[HeadOfficeDB] = None


def get_db() -> HeadOfficeDB:
    """Get database instance (singleton)"""
    global _db_instance
    if _db_instance is None:
        _db_instance = HeadOfficeDB()
    return _db_instance
