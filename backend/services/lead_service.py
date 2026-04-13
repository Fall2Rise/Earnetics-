import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

DB_PATH = Path("business_database.db")

class LeadService:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._ensure_table()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _ensure_table(self):
        with self._get_connection() as conn:
            # Main leads table (used for scraped leads too)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT,
                    name TEXT,
                    source TEXT,
                    source_domain TEXT,
                    status TEXT DEFAULT 'new', -- new, qualified, unqualified
                    score INTEGER DEFAULT 0,
                    qualified INTEGER DEFAULT 0,
                    added_to_list INTEGER DEFAULT 0,
                    metadata TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email)")
            
            # Marketing recipients table (simplified)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS marketing_recipients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT,
                    campaign_id INTEGER,
                    event_type TEXT, -- sent, opened, clicked
                    sent_at TEXT,
                    metadata TEXT
                )
            """)

    def add_lead(self, email: str, name: Optional[str] = None, source: str = "manual", metadata: Dict = None) -> Dict[str, Any]:
        """Add a new lead to the database."""
        now = datetime.utcnow().isoformat()
        meta_json = json.dumps(metadata or {})
        
        # Extract domain from source if possible or use metadata
        source_domain = metadata.get('source_domain') if metadata else None
        if not source_domain and '@' in email:
            source_domain = email.split('@')[-1]

        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Check exist
            cursor.execute("SELECT id FROM leads WHERE email = ?", (email,))
            existing = cursor.fetchone()
            if existing:
                return {"status": "exists", "id": existing[0]}
            
            cursor.execute("""
                INSERT INTO leads (email, name, source, source_domain, status, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, 'new', ?, ?, ?)
            """, (email, name, source, source_domain, meta_json, now, now))
            lead_id = cursor.lastrowid
            
        return {"status": "created", "id": lead_id, "email": email}

    def get_leads(self, status: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        query = "SELECT * FROM leads"
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
            d['metadata'] = json.loads(d['metadata'] or '{}')
            results.append(d)
        return results

    def get_scraped_leads(self, limit: int = 50, qualified_only: bool = False, added_to_list: Optional[bool] = None, source_domain: Optional[str] = None) -> Dict[str, Any]:
        query = "SELECT * FROM leads WHERE 1=1"
        params = []
        
        if qualified_only:
            query += " AND qualified = 1"
        if added_to_list is not None:
            query += " AND added_to_list = ?"
            params.append(1 if added_to_list else 0)
        if source_domain:
            query += " AND source_domain = ?"
            params.append(source_domain)
            
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            
            # Get counts
            total = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
            qualified_count = conn.execute("SELECT COUNT(*) FROM leads WHERE qualified=1").fetchone()[0]
            added_count = conn.execute("SELECT COUNT(*) FROM leads WHERE added_to_list=1").fetchone()[0]

        leads = []
        for row in rows:
            d = dict(row)
            d['metadata'] = json.loads(d['metadata'] or '{}')
            leads.append(d)
            
        return {
            "leads": leads,
            "total": total,
            "qualified_count": qualified_count,
            "added_to_list_count": added_count
        }

    def get_scraped_stats(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
            qualified = conn.execute("SELECT COUNT(*) FROM leads WHERE qualified=1").fetchone()[0]
            added = conn.execute("SELECT COUNT(*) FROM leads WHERE added_to_list=1").fetchone()[0]
            
            # Group by domain
            cursor = conn.execute("SELECT source_domain, COUNT(*) as count FROM leads GROUP BY source_domain LIMIT 10")
            by_domain = {row[0]: {"total": row[1], "qualified": 0, "added": 0} for row in cursor.fetchall() if row[0]}
            
        return {
            "total_leads": total,
            "qualified_leads": qualified,
            "added_to_list": added,
            "by_domain": by_domain
        }

    def get_subscribers(self, limit: int = 50, status: Optional[str] = None, source: Optional[str] = None, tag: Optional[str] = None) -> Dict[str, Any]:
        """Get leads that are marked as subscribers (added_to_list=1)."""
        query = "SELECT * FROM leads WHERE added_to_list = 1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        if source:
            query += " AND source = ?"
            params.append(source)
        # Tag filtering would require JSON parsing if tags are in metadata, skipping for now or simple like match
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            
            total = conn.execute("SELECT COUNT(*) FROM leads WHERE added_to_list=1").fetchone()[0]

        subscribers = []
        categories = {} # Group by source as "category" for now
        
        for row in rows:
            d = dict(row)
            d['metadata'] = json.loads(d['metadata'] or '{}')
            d['tags'] = d['metadata'].get('tags', [])
            subscribers.append(d)
            
            cat = d.get('source', 'Unknown')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(d)
            
        return {
            "subscribers": subscribers,
            "total": total,
            "categories": categories,
            "by_category": {k: len(v) for k, v in categories.items()}
        }

    def get_subscribers_stats(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) FROM leads WHERE added_to_list=1").fetchone()[0]
            active = conn.execute("SELECT COUNT(*) FROM leads WHERE added_to_list=1 AND status='active'").fetchone()[0]
            
            # Group by source
            cursor = conn.execute("SELECT source, COUNT(*) FROM leads WHERE added_to_list=1 GROUP BY source")
            by_source = {row[0]: row[1] for row in cursor.fetchall() if row[0]}
            
        return {
            "total_subscribers": total,
            "active_count": active,
            "by_source": by_source,
            "by_status": {"active": active, "total": total},
            "by_tag": {} # Placeholder
        }

    def qualify_lead(self, lead_id: int, qualified: bool) -> bool:
        with self._get_connection() as conn:
            status = 'qualified' if qualified else 'unqualified'
            conn.execute("UPDATE leads SET qualified = ?, status = ? WHERE id = ?", (1 if qualified else 0, status, lead_id))
        return True

    def add_to_list(self, lead_id: int) -> bool:
        with self._get_connection() as conn:
            conn.execute("UPDATE leads SET added_to_list = 1 WHERE id = ?", (lead_id,))
        return True

    def update_lead_status(self, lead_id: int, status: str) -> bool:
        now = datetime.utcnow().isoformat()
        with self._get_connection() as conn:
            cursor = conn.execute("UPDATE leads SET status = ?, updated_at = ? WHERE id = ?", (status, now, lead_id))
            return cursor.rowcount > 0

lead_service = LeadService()
