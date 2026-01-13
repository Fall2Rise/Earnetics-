"""
Truth Library Publisher: manages validated playbooks, SOPs, strategies
"""
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from earnetics.truth_library.schema import TruthLibraryAsset, AssetStatus, AssetType
from backend.corporate_memory import BUSINESS_DB_PATH


class TruthLibraryPublisher:
    """Manages Truth Library assets with versioning and validation"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(Path(BUSINESS_DB_PATH).parent / "truth_library.db")
        self._ensure_schema()
    
    def _ensure_schema(self):
        """Create database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS truth_assets (
                    asset_id TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL,
                    last_verified_at TEXT,
                    citations TEXT,
                    confidence REAL,
                    owner TEXT NOT NULL,
                    tags TEXT,
                    content TEXT NOT NULL,
                    measurable_results TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    deprecated_at TEXT,
                    deprecated_reason TEXT,
                    PRIMARY KEY (asset_id, version)
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_status_type 
                ON truth_assets(status, type)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tags 
                ON truth_assets(tags)
            """)
            
            conn.commit()
    
    def publish(self, asset: TruthLibraryAsset) -> bool:
        """Publish or update asset"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if asset exists, get latest version
                cursor.execute("""
                    SELECT MAX(version) FROM truth_assets WHERE asset_id = ?
                """, (asset.asset_id,))
                row = cursor.fetchone()
                latest_version = row[0] if row[0] else 0
                
                # If updating, increment version
                if latest_version > 0:
                    asset.version = latest_version + 1
                
                now = datetime.utcnow().isoformat()
                asset.updated_at = now
                
                cursor.execute("""
                    INSERT INTO truth_assets
                    (asset_id, version, type, title, status, last_verified_at,
                     citations, confidence, owner, tags, content, measurable_results,
                     created_at, updated_at, deprecated_at, deprecated_reason)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    asset.asset_id,
                    asset.version,
                    asset.type.value,
                    asset.title,
                    asset.status.value,
                    asset.last_verified_at,
                    json.dumps(asset.citations),
                    asset.confidence,
                    asset.owner,
                    json.dumps(asset.tags),
                    json.dumps(asset.content),
                    json.dumps(asset.measurable_results) if asset.measurable_results else None,
                    asset.created_at,
                    asset.updated_at,
                    asset.deprecated_at,
                    asset.deprecated_reason
                ))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error publishing asset: {e}")
            return False
    
    def validate(self, asset_id: str, measurable_results: Dict[str, Any], 
                 verified_by: str) -> bool:
        """Validate an asset (change status to validated)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get latest version
                cursor.execute("""
                    SELECT * FROM truth_assets 
                    WHERE asset_id = ? 
                    ORDER BY version DESC LIMIT 1
                """, (asset_id,))
                row = cursor.fetchone()
                
                if not row:
                    return False
                
                # Create new validated version
                asset = self._row_to_asset(row)
                asset.status = AssetStatus.VALIDATED
                asset.last_verified_at = datetime.utcnow().isoformat()
                asset.measurable_results = measurable_results
                asset.owner = verified_by
                asset.version = asset.version + 1
                
                return self.publish(asset)
        except Exception as e:
            print(f"Error validating asset: {e}")
            return False
    
    def deprecate(self, asset_id: str, reason: str, deprecated_by: str) -> bool:
        """Deprecate an asset"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM truth_assets 
                    WHERE asset_id = ? 
                    ORDER BY version DESC LIMIT 1
                """, (asset_id,))
                row = cursor.fetchone()
                
                if not row:
                    return False
                
                asset = self._row_to_asset(row)
                asset.status = AssetStatus.DEPRECATED
                asset.deprecated_at = datetime.utcnow().isoformat()
                asset.deprecated_reason = reason
                asset.owner = deprecated_by
                asset.version = asset.version + 1
                
                return self.publish(asset)
        except Exception as e:
            print(f"Error deprecating asset: {e}")
            return False
    
    def get(self, asset_id: str, version: Optional[int] = None) -> Optional[TruthLibraryAsset]:
        """Get asset by ID and version (latest if not specified)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if version:
                    cursor.execute("""
                        SELECT * FROM truth_assets 
                        WHERE asset_id = ? AND version = ?
                    """, (asset_id, version))
                else:
                    cursor.execute("""
                        SELECT * FROM truth_assets 
                        WHERE asset_id = ? 
                        ORDER BY version DESC LIMIT 1
                    """, (asset_id,))
                
                row = cursor.fetchone()
                if row:
                    return self._row_to_asset(row)
        except Exception as e:
            print(f"Error retrieving asset: {e}")
        return None
    
    def search(self, query: str, asset_type: Optional[AssetType] = None,
               status: Optional[AssetStatus] = None, limit: int = 20) -> List[TruthLibraryAsset]:
        """Search truth library"""
        results = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                sql = """
                    SELECT DISTINCT asset_id, MAX(version) as max_version
                    FROM truth_assets
                    WHERE 1=1
                """
                params = []
                
                if query:
                    sql += " AND (title LIKE ? OR content LIKE ? OR tags LIKE ?)"
                    search_term = f"%{query}%"
                    params.extend([search_term, search_term, search_term])
                
                if asset_type:
                    sql += " AND type = ?"
                    params.append(asset_type.value)
                
                if status:
                    sql += " AND status = ?"
                    params.append(status.value)
                
                sql += " GROUP BY asset_id ORDER BY MAX(updated_at) DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(sql, params)
                
                for row in cursor.fetchall():
                    asset = self.get(row["asset_id"], row["max_version"])
                    if asset:
                        results.append(asset)
        except Exception as e:
            print(f"Error searching truth library: {e}")
        
        return results
    
    def _row_to_asset(self, row: sqlite3.Row) -> TruthLibraryAsset:
        """Convert database row to TruthLibraryAsset"""
        return TruthLibraryAsset(
            asset_id=row["asset_id"],
            type=AssetType(row["type"]),
            title=row["title"],
            status=AssetStatus(row["status"]),
            version=row["version"],
            last_verified_at=row["last_verified_at"],
            citations=json.loads(row["citations"] or "[]"),
            confidence=row["confidence"] or 0.5,
            owner=row["owner"],
            tags=json.loads(row["tags"] or "[]"),
            content=json.loads(row["content"]),
            measurable_results=json.loads(row["measurable_results"]) if row["measurable_results"] else None,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deprecated_at=row["deprecated_at"],
            deprecated_reason=row["deprecated_reason"]
        )
