"""
Internal Earnetics Vault connector (Tier 0)
"""
from typing import List, Dict, Any
from datetime import datetime
import sqlite3
from pathlib import Path

from earnetics.knowledge_sources.base import KnowledgeSource
from earnetics.knowledge_store.schema import KnowledgeRecord, CitationObject
from backend.corporate_memory import BUSINESS_DB_PATH


class InternalVaultSource(KnowledgeSource):
    """Connector for internal Earnetics vault (Tier 0)"""
    
    def __init__(self, source_id: str, config: Dict[str, Any]):
        super().__init__(source_id, config)
        self.db_path = BUSINESS_DB_PATH
    
    def search(self, query: str, limit: int = 20, **kwargs) -> List[Dict[str, Any]]:
        """Search internal vault"""
        results = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Search knowledge articles
                cursor.execute("""
                    SELECT id, title, content, tags, source, created_at
                    FROM knowledge_articles
                    WHERE title LIKE ? OR content LIKE ? OR tags LIKE ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (f"%{query}%", f"%{query}%", f"%{query}%", limit))
                
                for row in cursor.fetchall():
                    results.append({
                        "id": f"vault_{row['id']}",
                        "title": row["title"],
                        "url": f"earnetics://vault/{row['id']}",
                        "summary": row["content"][:200] if row["content"] else "",
                        "source": row.get("source", "System"),
                        "created_at": row["created_at"]
                    })
        except Exception as e:
            print(f"Error searching internal vault: {e}")
        
        return results
    
    def fetch(self, ref: Dict[str, Any]) -> KnowledgeRecord:
        """Fetch from internal vault"""
        vault_id = ref.get("id", "").replace("vault_", "")
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, content, tags, source, created_at
                FROM knowledge_articles
                WHERE id = ?
            """, (vault_id,))
            
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Knowledge article {vault_id} not found")
            
            tags = []
            if row["tags"]:
                try:
                    import json
                    tags = json.loads(row["tags"]) if isinstance(row["tags"], str) else row["tags"]
                except:
                    tags = [row["tags"]] if row["tags"] else []
            
            record_id = KnowledgeRecord.create_id(
                self.source_id,
                f"earnetics://vault/{row['id']}",
                row["created_at"]
            )
            
            return KnowledgeRecord(
                id=record_id,
                source_id=self.source_id,
                tier=0,
                title=row["title"],
                url=f"earnetics://vault/{row['id']}",
                retrieved_at=datetime.utcnow().isoformat(),
                published_at=row["created_at"],
                tags=tags,
                summary=row["content"][:500] if row["content"] else "",
                content_text=row["content"] or "",
                trust_score=100,  # Internal vault is highest trust
                raw={"source": row.get("source", "System")}
                # No citation needed for Tier 0
            )
