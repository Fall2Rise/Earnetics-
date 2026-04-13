import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

DB_PATH = Path("business_database.db")

class ContentService:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._ensure_table()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _ensure_table(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS content_assets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    type TEXT,
                    content TEXT,
                    status TEXT DEFAULT 'draft',
                    metadata TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)

    def save_content(self, title: str, content: str, type: str = "text", status: str = "draft", metadata: Dict = None) -> Dict[str, Any]:
        """Save generated content."""
        now = datetime.utcnow().isoformat()
        meta_json = json.dumps(metadata or {})
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO content_assets (title, type, content, status, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (title, type, content, status, meta_json, now, now))
            asset_id = cursor.lastrowid
            
        return {"status": "saved", "id": asset_id, "title": title}

    def list_content(self, type: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        query = "SELECT * FROM content_assets"
        params = []
        if type:
            query += " WHERE type = ?"
            params.append(type)
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

content_service = ContentService()
