"""
Revenue Loop: KPI Telemetry Logger
Tracks campaign events and metrics
"""
import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from backend.corporate_memory import BUSINESS_DB_PATH


class KPITelemetry:
    """KPI telemetry logger for revenue campaigns"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(Path(BUSINESS_DB_PATH).parent / "kpi_telemetry.db")
        self._ensure_schema()
    
    def _ensure_schema(self):
        """Create database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Telemetry events
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS telemetry_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    campaign_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    metadata TEXT,
                    value REAL,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Campaign metrics (aggregated)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS campaign_metrics (
                    campaign_id TEXT PRIMARY KEY,
                    opportunity_id TEXT,
                    traffic_clicks INTEGER DEFAULT 0,
                    leads_optin INTEGER DEFAULT 0,
                    conversions_purchase INTEGER DEFAULT 0,
                    revenue_recorded REAL DEFAULT 0.0,
                    emails_sent INTEGER DEFAULT 0,
                    emails_reply INTEGER DEFAULT 0,
                    emails_unsubscribe INTEGER DEFAULT 0,
                    last_updated TEXT NOT NULL
                )
            """)
            
            # Indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_campaign_event 
                ON telemetry_events(campaign_id, event_type)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON telemetry_events(timestamp)
            """)
            
            conn.commit()
    
    def log_event(self, event_type: str, campaign_id: str, 
                  metadata: Optional[Dict[str, Any]] = None,
                  value: Optional[float] = None) -> bool:
        """
        Log telemetry event
        
        Event types:
        - campaign.created
        - traffic.click
        - lead.optin
        - conversion.purchase
        - revenue.recorded
        - email.sent
        - email.reply
        - email.unsubscribe
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                now = datetime.utcnow().isoformat()
                
                cursor.execute("""
                    INSERT INTO telemetry_events
                    (event_type, campaign_id, timestamp, metadata, value, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    event_type,
                    campaign_id,
                    now,
                    json.dumps(metadata) if metadata else None,
                    value,
                    now
                ))
                
                # Update aggregated metrics
                self._update_campaign_metrics(campaign_id, event_type, value)
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error logging telemetry event: {e}")
            return False
    
    def _update_campaign_metrics(self, campaign_id: str, event_type: str, value: Optional[float]):
        """Update aggregated campaign metrics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get or create campaign metrics
            cursor.execute("""
                SELECT * FROM campaign_metrics WHERE campaign_id = ?
            """, (campaign_id,))
            row = cursor.fetchone()
            
            now = datetime.utcnow().isoformat()
            
            if not row:
                # Create new
                cursor.execute("""
                    INSERT INTO campaign_metrics
                    (campaign_id, last_updated)
                    VALUES (?, ?)
                """, (campaign_id, now))
            
            # Update based on event type
            updates = {}
            if event_type == "traffic.click":
                cursor.execute("""
                    UPDATE campaign_metrics 
                    SET traffic_clicks = traffic_clicks + 1, last_updated = ?
                    WHERE campaign_id = ?
                """, (now, campaign_id))
            elif event_type == "lead.optin":
                cursor.execute("""
                    UPDATE campaign_metrics 
                    SET leads_optin = leads_optin + 1, last_updated = ?
                    WHERE campaign_id = ?
                """, (now, campaign_id))
            elif event_type == "conversion.purchase":
                cursor.execute("""
                    UPDATE campaign_metrics 
                    SET conversions_purchase = conversions_purchase + 1, last_updated = ?
                    WHERE campaign_id = ?
                """, (now, campaign_id))
            elif event_type == "revenue.recorded" and value:
                cursor.execute("""
                    UPDATE campaign_metrics 
                    SET revenue_recorded = revenue_recorded + ?, last_updated = ?
                    WHERE campaign_id = ?
                """, (value, now, campaign_id))
            elif event_type == "email.sent":
                cursor.execute("""
                    UPDATE campaign_metrics 
                    SET emails_sent = emails_sent + 1, last_updated = ?
                    WHERE campaign_id = ?
                """, (now, campaign_id))
            elif event_type == "email.reply":
                cursor.execute("""
                    UPDATE campaign_metrics 
                    SET emails_reply = emails_reply + 1, last_updated = ?
                    WHERE campaign_id = ?
                """, (now, campaign_id))
            elif event_type == "email.unsubscribe":
                cursor.execute("""
                    UPDATE campaign_metrics 
                    SET emails_unsubscribe = emails_unsubscribe + 1, last_updated = ?
                    WHERE campaign_id = ?
                """, (now, campaign_id))
            
            conn.commit()
    
    def get_campaign_metrics(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get aggregated metrics for a campaign"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM campaign_metrics WHERE campaign_id = ?
                """, (campaign_id,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        "campaign_id": row["campaign_id"],
                        "opportunity_id": row["opportunity_id"],
                        "traffic_clicks": row["traffic_clicks"],
                        "leads_optin": row["leads_optin"],
                        "conversions_purchase": row["conversions_purchase"],
                        "revenue_recorded": row["revenue_recorded"],
                        "emails_sent": row["emails_sent"],
                        "emails_reply": row["emails_reply"],
                        "emails_unsubscribe": row["emails_unsubscribe"],
                        "last_updated": row["last_updated"]
                    }
        except Exception as e:
            print(f"Error getting campaign metrics: {e}")
        return None
    
    def get_events(self, campaign_id: Optional[str] = None,
                   event_type: Optional[str] = None,
                   limit: int = 100) -> List[Dict[str, Any]]:
        """Get telemetry events"""
        events = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                sql = "SELECT * FROM telemetry_events WHERE 1=1"
                params = []
                
                if campaign_id:
                    sql += " AND campaign_id = ?"
                    params.append(campaign_id)
                
                if event_type:
                    sql += " AND event_type = ?"
                    params.append(event_type)
                
                sql += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(sql, params)
                
                for row in cursor.fetchall():
                    events.append({
                        "id": row["id"],
                        "event_type": row["event_type"],
                        "campaign_id": row["campaign_id"],
                        "timestamp": row["timestamp"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "value": row["value"],
                        "created_at": row["created_at"]
                    })
        except Exception as e:
            print(f"Error getting events: {e}")
        
        return events
