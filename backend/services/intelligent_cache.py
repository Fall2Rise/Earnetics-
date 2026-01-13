"""
Intelligent Caching Service
Provides caching for database queries, API responses, and computed results
"""
import hashlib
import json
import time
import logging
from typing import Any, Optional, Callable, Dict
from datetime import datetime, timedelta
from functools import wraps
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

class IntelligentCache:
    """Intelligent caching with TTL, invalidation, and size limits"""
    
    def __init__(self, db_path: str = "cache.db", max_size_mb: int = 100):
        self.db_path = db_path
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self._ensure_schema()
        self._memory_cache: Dict[str, tuple] = {}  # key -> (value, expiry_time)
        self._hits = 0
        self._misses = 0
    
    def _ensure_schema(self):
        """Create cache database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    ttl_seconds INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TEXT,
                    size_bytes INTEGER
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_cache_created 
                ON cache_entries(created_at)
            """)
            
            conn.commit()
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        key_hash = hashlib.sha256(key_data.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        # Check memory cache first
        if key in self._memory_cache:
            value, expiry = self._memory_cache[key]
            if time.time() < expiry:
                self._hits += 1
                return value
            else:
                del self._memory_cache[key]
        
        # Check database cache
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                row = conn.execute("""
                    SELECT value, ttl_seconds, created_at
                    FROM cache_entries
                    WHERE key = ?
                """, (key,)).fetchone()
                
                if row:
                    created = datetime.fromisoformat(row['created_at'])
                    age = (datetime.now() - created).total_seconds()
                    
                    if age < row['ttl_seconds']:
                        # Cache hit - update access stats
                        value = json.loads(row['value'])
                        conn.execute("""
                            UPDATE cache_entries
                            SET access_count = access_count + 1,
                                last_accessed = CURRENT_TIMESTAMP
                            WHERE key = ?
                        """, (key,))
                        conn.commit()
                        
                        # Add to memory cache
                        self._memory_cache[key] = (value, time.time() + (row['ttl_seconds'] - age))
                        
                        self._hits += 1
                        return value
                    else:
                        # Expired - remove
                        conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
                        conn.commit()
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        
        self._misses += 1
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        """Set value in cache"""
        try:
            value_json = json.dumps(value)
            size_bytes = len(value_json.encode('utf-8'))
            
            # Check size limit
            if size_bytes > self.max_size_bytes * 0.1:  # Don't cache items > 10% of max
                return
            
            # Add to memory cache
            self._memory_cache[key] = (value, time.time() + ttl_seconds)
            
            # Persist to database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO cache_entries
                    (key, value, ttl_seconds, created_at, size_bytes, last_accessed)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (key, value_json, ttl_seconds, datetime.now().isoformat(), size_bytes))
                conn.commit()
                
                # Cleanup old entries if cache is too large
                self._cleanup_if_needed()
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    def invalidate(self, pattern: Optional[str] = None):
        """Invalidate cache entries matching pattern"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if pattern:
                    # Pattern matching (simple prefix match)
                    conn.execute("""
                        DELETE FROM cache_entries
                        WHERE key LIKE ?
                    """, (f"{pattern}%",))
                else:
                    # Clear all
                    conn.execute("DELETE FROM cache_entries")
                conn.commit()
            
            # Clear memory cache
            if pattern:
                keys_to_remove = [k for k in self._memory_cache.keys() if k.startswith(pattern)]
                for k in keys_to_remove:
                    del self._memory_cache[k]
            else:
                self._memory_cache.clear()
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
    
    def _cleanup_if_needed(self):
        """Clean up old entries if cache is too large"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get total size
                total_size = conn.execute("""
                    SELECT SUM(size_bytes) FROM cache_entries
                """).fetchone()[0] or 0
                
                if total_size > self.max_size_bytes:
                    # Remove oldest 20% of entries
                    conn.execute("""
                        DELETE FROM cache_entries
                        WHERE key IN (
                            SELECT key FROM cache_entries
                            ORDER BY last_accessed ASC
                            LIMIT (SELECT COUNT(*) / 5 FROM cache_entries)
                        )
                    """)
                    conn.commit()
                    
                    # Also remove expired from memory
                    now = time.time()
                    expired_keys = [k for k, (_, expiry) in self._memory_cache.items() if now >= expiry]
                    for k in expired_keys:
                        del self._memory_cache[k]
        except Exception as e:
            logger.error(f"Cache cleanup error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0.0
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                entry_count = conn.execute("SELECT COUNT(*) FROM cache_entries").fetchone()[0]
                total_size = conn.execute("SELECT SUM(size_bytes) FROM cache_entries").fetchone()[0] or 0
        except:
            entry_count = 0
            total_size = 0
        
        return {
            "hit_rate": hit_rate,
            "hits": self._hits,
            "misses": self._misses,
            "total_requests": total_requests,
            "cached_entries": entry_count,
            "total_size_mb": total_size / (1024 * 1024),
            "memory_cache_size": len(self._memory_cache)
        }


# Global cache instance
_cache: Optional[IntelligentCache] = None

def get_cache() -> IntelligentCache:
    """Get global cache instance"""
    global _cache
    if _cache is None:
        _cache = IntelligentCache()
    return _cache


def cached(prefix: str, ttl_seconds: int = 300):
    """Decorator for caching function results"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache()
            key = cache._generate_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                return result
            
            # Compute result
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(key, result, ttl_seconds)
            
            return result
        
        return wrapper
    return decorator
