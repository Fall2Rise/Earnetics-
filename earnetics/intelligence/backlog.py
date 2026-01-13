"""
Intelligence Department: Opportunity Backlog (Kanban)
"""
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from earnetics.revenue_loop.opportunity import Opportunity
from backend.corporate_memory import BUSINESS_DB_PATH


class OpportunityBacklog:
    """Kanban-style opportunity backlog"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(Path(BUSINESS_DB_PATH).parent / "opportunity_backlog.db")
        self._ensure_schema()
    
    def _ensure_schema(self):
        """Create database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS opportunities (
                    opportunity_id TEXT PRIMARY KEY,
                    niche TEXT NOT NULL,
                    offer_type TEXT NOT NULL,
                    hypothesis TEXT NOT NULL,
                    target TEXT,
                    required_assets TEXT,
                    expected_roi REAL,
                    time_to_first_dollar INTEGER,
                    risks TEXT,
                    compliance_notes TEXT,
                    sources TEXT,
                    recommended_next_action TEXT,
                    status TEXT NOT NULL,
                    score REAL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_status 
                ON opportunities(status)
            """)
            
            conn.commit()
    
    def add(self, opportunity: Opportunity, score: float) -> bool:
        """Add opportunity to backlog"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                now = datetime.utcnow().isoformat()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO opportunities
                    (opportunity_id, niche, offer_type, hypothesis, target,
                     required_assets, expected_roi, time_to_first_dollar,
                     risks, compliance_notes, sources, recommended_next_action,
                     status, score, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    opportunity.opportunity_id,
                    opportunity.niche,
                    opportunity.offer_type,
                    opportunity.hypothesis,
                    opportunity.target,
                    json.dumps(opportunity.required_assets),
                    opportunity.expected_roi,
                    opportunity.time_to_first_dollar,
                    json.dumps(opportunity.risks),
                    opportunity.compliance_notes,
                    json.dumps(opportunity.sources),
                    opportunity.recommended_next_action,
                    opportunity.status,
                    score,
                    opportunity.created_at,
                    now
                ))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding opportunity: {e}")
            return False
    
    def update_status(self, opportunity_id: str, status: str) -> bool:
        """Update opportunity status (Kanban move)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE opportunities
                    SET status = ?, updated_at = ?
                    WHERE opportunity_id = ?
                """, (status, datetime.utcnow().isoformat(), opportunity_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating status: {e}")
            return False
    
    def get_by_status(self, status: str) -> List[Opportunity]:
        """Get opportunities by status"""
        opportunities = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM opportunities WHERE status = ?
                    ORDER BY score DESC, created_at DESC
                """, (status,))
                
                for row in cursor.fetchall():
                    opp = Opportunity(
                        opportunity_id=row["opportunity_id"],
                        niche=row["niche"],
                        offer_type=row["offer_type"],
                        hypothesis=row["hypothesis"],
                        target=row["target"],
                        required_assets=json.loads(row["required_assets"]),
                        expected_roi=row["expected_roi"],
                        time_to_first_dollar=row["time_to_first_dollar"],
                        risks=json.loads(row["risks"]),
                        compliance_notes=row["compliance_notes"],
                        sources=json.loads(row["sources"]),
                        recommended_next_action=row["recommended_next_action"],
                        created_at=row["created_at"],
                        updated_at=row["updated_at"],
                        status=row["status"]
                    )
                    opportunities.append(opp)
        except Exception as e:
            print(f"Error getting opportunities: {e}")
        
        return opportunities
    
    def get_all(self) -> Dict[str, List[Opportunity]]:
        """Get all opportunities organized by status (Kanban columns)"""
        statuses = ["intake", "triage", "synthesis", "experiment", "validated", "sent_to_exec", "deployed"]
        return {status: self.get_by_status(status) for status in statuses}
