"""
Rate Limiting Middleware
Lightweight token bucket limiter to protect critical endpoints
"""
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer
from collections import deque
from datetime import datetime, timezone
from typing import Dict

class RateLimiter:
    """Lightweight token bucket limiter to protect critical endpoints."""

    def __init__(self, limit: int = 60, window_seconds: int = 60) -> None:
        self.limit = max(1, limit)
        self.window = max(1, window_seconds)
        self._events: Dict[str, deque[float]] = {}

    def allow(self, key: str) -> bool:
        now = datetime.now(timezone.utc).timestamp()
        bucket = self._events.setdefault(key, deque())
        # purge expired entries
        cutoff = now - self.window
        while bucket and bucket[0] < cutoff:
            bucket.popleft()
        if len(bucket) >= self.limit:
            return False
        bucket.append(now)
        return True


# Global rate limiter instance
_rate_limiter = RateLimiter(limit=60, window_seconds=60)

def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance"""
    return _rate_limiter

def rate_limit(request: Request) -> None:
    """Dependency for rate limiting"""
    client_ip = request.client.host if request.client else "unknown"
    if not _rate_limiter.allow(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
