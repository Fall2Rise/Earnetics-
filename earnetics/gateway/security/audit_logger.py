"""
Audit Logger: Append-only audit log for all gateway actions
"""
import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from earnetics.gateway.security.sanitizer import Sanitizer
from backend.corporate_memory import BUSINESS_DB_PATH


class AuditLogger:
    """Append-only audit log for gateway actions"""
    
    def __init__(self, db_path: Optional[str] = None, enabled: bool = True):
        self.enabled = enabled
        self.db_path = db_path or str(Path(BUSINESS_DB_PATH).parent / "gateway_audit.db")
        self._ensure_schema()
    
    def _ensure_schema(self):
        """Create audit log database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gateway_audit_log (
                    audit_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    action TEXT NOT NULL,
                    method TEXT,
                    target TEXT NOT NULL,
                    request_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    policy_reason TEXT,
                    latency_ms INTEGER,
                    response_code INTEGER,
                    response_bytes INTEGER,
                    error_message TEXT,
                    metadata TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Indexes for fast queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON gateway_audit_log(timestamp)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_agent_action 
                ON gateway_audit_log(agent_id, action)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_status 
                ON gateway_audit_log(status)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_request_id 
                ON gateway_audit_log(request_id)
            """)
            
            conn.commit()
    
    def log(self, agent_id: str, role: str, action: str, target: str,
           status: str, policy_reason: Optional[str] = None,
           method: Optional[str] = None, request_id: Optional[str] = None,
           latency_ms: Optional[int] = None, response_code: Optional[int] = None,
           response_bytes: Optional[int] = None, error_message: Optional[str] = None,
           metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Log an audit entry
        
        Returns: audit_id
        """
        if not self.enabled:
            return ""
        
        audit_id = str(uuid.uuid4())
        request_id = request_id or str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        # Sanitize all inputs
        target_sanitized = Sanitizer.sanitize_url(target)
        metadata_sanitized = Sanitizer.redact_secrets(metadata or {})
        error_sanitized = Sanitizer._redact_string(error_message) if error_message else None
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO gateway_audit_log
                    (audit_id, timestamp, agent_id, role, action, method, target,
                     request_id, status, policy_reason, latency_ms, response_code,
                     response_bytes, error_message, metadata, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    audit_id,
                    timestamp,
                    agent_id,
                    role,
                    action,
                    method,
                    target_sanitized,
                    request_id,
                    status,
                    policy_reason,
                    latency_ms,
                    response_code,
                    response_bytes,
                    error_sanitized,
                    json.dumps(metadata_sanitized) if metadata_sanitized else None,
                    timestamp
                ))
                conn.commit()
        except Exception as e:
            print(f"Error logging audit entry: {e}")
        
        return audit_id
    
    def get_audit_log(self, agent_id: Optional[str] = None, action: Optional[str] = None,
                     status: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Query audit log"""
        entries = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                sql = "SELECT * FROM gateway_audit_log WHERE 1=1"
                params = []
                
                if agent_id:
                    sql += " AND agent_id = ?"
                    params.append(agent_id)
                
                if action:
                    sql += " AND action = ?"
                    params.append(action)
                
                if status:
                    sql += " AND status = ?"
                    params.append(status)
                
                sql += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(sql, params)
                
                for row in cursor.fetchall():
                    entry = dict(row)
                    if entry.get("metadata"):
                        try:
                            entry["metadata"] = json.loads(entry["metadata"])
                        except:
                            entry["metadata"] = {}
                    entries.append(entry)
        except Exception as e:
            print(f"Error querying audit log: {e}")
        
        return entries
    
    def get_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get audit log statistics"""
        cutoff = datetime.utcnow().timestamp() - (hours * 3600)
        cutoff_iso = datetime.fromtimestamp(cutoff).isoformat()
        
        stats = {
            "total_requests": 0,
            "by_status": {},
            "by_action": {},
            "by_role": {},
            "blocked_count": 0,
            "allowed_count": 0,
            "failed_count": 0
        }
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT status, action, role, COUNT(*) as count
                    FROM gateway_audit_log
                    WHERE timestamp >= ?
                    GROUP BY status, action, role
                """, (cutoff_iso,))
                
                for row in cursor.fetchall():
                    status, action, role, count = row
                    stats["total_requests"] += count
                    
                    stats["by_status"][status] = stats["by_status"].get(status, 0) + count
                    stats["by_action"][action] = stats["by_action"].get(action, 0) + count
                    stats["by_role"][role] = stats["by_role"].get(role, 0) + count
                    
                    if status == "blocked":
                        stats["blocked_count"] += count
                    elif status == "allowed" or status == "success":
                        stats["allowed_count"] += count
                    elif status == "failed":
                        stats["failed_count"] += count
        except Exception as e:
            print(f"Error getting audit stats: {e}")
        
        return stats
