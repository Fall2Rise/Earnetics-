import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

DB_PATH = Path("business_database.db")

class CampaignService:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._ensure_table()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _ensure_table(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS campaigns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    type TEXT, -- email, social, multi
                    status TEXT DEFAULT 'draft', -- draft, scheduled, active, completed, paused
                    content_asset_id INTEGER,
                    target_audience_filter TEXT, -- JSON filter for leads
                    schedule_at TEXT,
                    metadata TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS campaign_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_id INTEGER,
                    event_type TEXT, -- sent, error, clicked, opened
                    details TEXT,
                    created_at TEXT
                )
            """)

    def create_campaign(self, name: str, type: str, content_asset_id: Optional[int] = None, target_filter: Dict = None, schedule_at: Optional[str] = None) -> Dict[str, Any]:
        """Create a new marketing campaign."""
        now = datetime.utcnow().isoformat()
        filter_json = json.dumps(target_filter or {})
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO campaigns (name, type, content_asset_id, target_audience_filter, schedule_at, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 'draft', ?, ?)
            """, (name, type, content_asset_id, filter_json, schedule_at, now, now))
            campaign_id = cursor.lastrowid
            
        return {
            "id": campaign_id,
            "name": name,
            "status": "draft",
            "type": type
        }

    def list_campaigns(self, status: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        query = "SELECT * FROM campaigns"
        params = []
        if status:
            query += " WHERE status = ?"
            params.append(status)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            
        results = []
        for row in rows:
            d = dict(row)
            d['target_audience_filter'] = json.loads(d['target_audience_filter'] or '{}')
            d['metadata'] = json.loads(d['metadata'] or '{}')
            results.append(d)
        return results

    def update_status(self, campaign_id: int, status: str) -> bool:
        now = datetime.utcnow().isoformat()
        with self._get_connection() as conn:
            conn.execute("UPDATE campaigns SET status = ?, updated_at = ? WHERE id = ?", (status, now, campaign_id))
        return True

    def log_event(self, campaign_id: int, event_type: str, details: Dict = None):
        now = datetime.utcnow().isoformat()
        details_json = json.dumps(details or {})
        with self._get_connection() as conn:
            conn.execute("INSERT INTO campaign_events (campaign_id, event_type, details, created_at) VALUES (?, ?, ?, ?)", (campaign_id, event_type, details_json, now))

campaign_service = CampaignService()
