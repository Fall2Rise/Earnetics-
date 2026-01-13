"""
Knowledge Store: metadata DB + raw cache + vector index
"""
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from earnetics.knowledge_store.schema import KnowledgeRecord, CitationObject
from backend.corporate_memory import BUSINESS_DB_PATH


class KnowledgeStore:
    """Unified knowledge store with metadata DB, cache, and vector index"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(Path(BUSINESS_DB_PATH).parent / "knowledge_store.db")
        self.cache_dir = Path(self.db_path).parent / "knowledge_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()
    
    def _ensure_schema(self):
        """Create database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Main knowledge records table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_records (
                    id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    tier INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    retrieved_at TEXT NOT NULL,
                    published_at TEXT,
                    authors TEXT,
                    entities TEXT,
                    tags TEXT,
                    summary TEXT,
                    content_text TEXT,
                    content_chunks TEXT,
                    embedding_ids TEXT,
                    citation TEXT,
                    trust_score INTEGER,
                    raw TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Indexes for fast search
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_source_tier 
                ON knowledge_records(source_id, tier)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tags 
                ON knowledge_records(tags)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_retrieved_at 
                ON knowledge_records(retrieved_at)
            """)
            
            conn.commit()
    
    def store(self, record: KnowledgeRecord) -> bool:
        """Store knowledge record"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                now = datetime.utcnow().isoformat()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO knowledge_records
                    (id, source_id, tier, title, url, retrieved_at, published_at,
                     authors, entities, tags, summary, content_text, content_chunks,
                     embedding_ids, citation, trust_score, raw, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record.id,
                    record.source_id,
                    record.tier,
                    record.title,
                    record.url,
                    record.retrieved_at,
                    record.published_at,
                    json.dumps(record.authors),
                    json.dumps(record.entities),
                    json.dumps(record.tags),
                    record.summary,
                    record.content_text,
                    json.dumps(record.content_chunks),
                    json.dumps(record.embedding_ids),
                    json.dumps(record.citation.to_dict()) if record.citation else None,
                    record.trust_score,
                    json.dumps(record.raw),
                    now,
                    now
                ))
                
                conn.commit()
                
                # Cache raw content
                cache_file = self.cache_dir / f"{record.id}.txt"
                cache_file.write_text(record.content_text, encoding='utf-8')
                
                return True
        except Exception as e:
            print(f"Error storing knowledge record: {e}")
            return False
    
    def get(self, record_id: str) -> Optional[KnowledgeRecord]:
        """Retrieve knowledge record by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM knowledge_records WHERE id = ?", (record_id,))
                row = cursor.fetchone()
                
                if row:
                    return self._row_to_record(row)
        except Exception as e:
            print(f"Error retrieving record: {e}")
        return None
    
    def search(self, query: str, sources: Optional[List[str]] = None,
               tiers: Optional[List[int]] = None, limit: int = 20,
               time_window_hours: Optional[int] = None) -> List[KnowledgeRecord]:
        """Search knowledge records"""
        results = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                sql = "SELECT * FROM knowledge_records WHERE 1=1"
                params = []
                
                # Text search
                sql += " AND (title LIKE ? OR summary LIKE ? OR content_text LIKE ?)"
                search_term = f"%{query}%"
                params.extend([search_term, search_term, search_term])
                
                # Source filter
                if sources:
                    placeholders = ','.join(['?'] * len(sources))
                    sql += f" AND source_id IN ({placeholders})"
                    params.extend(sources)
                
                # Tier filter
                if tiers:
                    placeholders = ','.join(['?'] * len(tiers))
                    sql += f" AND tier IN ({placeholders})"
                    params.extend([str(t) for t in tiers])
                
                # Time window
                if time_window_hours:
                    cutoff = datetime.utcnow().timestamp() - (time_window_hours * 3600)
                    cutoff_iso = datetime.fromtimestamp(cutoff).isoformat()
                    sql += " AND retrieved_at >= ?"
                    params.append(cutoff_iso)
                
                sql += " ORDER BY trust_score DESC, retrieved_at DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(sql, params)
                
                for row in cursor.fetchall():
                    record = self._row_to_record(row)
                    if record:
                        results.append(record)
        except Exception as e:
            print(f"Error searching knowledge: {e}")
        
        return results
    
    def _row_to_record(self, row: sqlite3.Row) -> Optional[KnowledgeRecord]:
        """Convert database row to KnowledgeRecord"""
        try:
            citation = None
            if row["citation"]:
                citation_data = json.loads(row["citation"])
                citation = CitationObject.from_dict(citation_data)
            
            # Load cached content if available
            content_text = row["content_text"]
            if not content_text or len(content_text) < 100:
                cache_file = self.cache_dir / f"{row['id']}.txt"
                if cache_file.exists():
                    content_text = cache_file.read_text(encoding='utf-8')
            
            return KnowledgeRecord(
                id=row["id"],
                source_id=row["source_id"],
                tier=row["tier"],
                title=row["title"],
                url=row["url"],
                retrieved_at=row["retrieved_at"],
                published_at=row["published_at"],
                authors=json.loads(row["authors"] or "[]"),
                entities=json.loads(row["entities"] or "[]"),
                tags=json.loads(row["tags"] or "[]"),
                summary=row["summary"] or "",
                content_text=content_text or "",
                content_chunks=json.loads(row["content_chunks"] or "[]"),
                embedding_ids=json.loads(row["embedding_ids"] or "[]"),
                citation=citation,
                trust_score=row["trust_score"] or 0,
                raw=json.loads(row["raw"] or "{}")
            )
        except Exception as e:
            print(f"Error converting row to record: {e}")
            return None
