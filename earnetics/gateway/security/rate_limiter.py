"""
Rate Limiter: Enforces global, per-domain, and per-agent rate limits
"""
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import time


class RateLimiter:
    """Rate limiter with global, domain, and agent-level limits"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        rate_limits = config.get("rate_limits", {})
        self.global_per_min = rate_limits.get("global_per_min", 120)
        self.per_domain_per_min = rate_limits.get("per_domain_per_min", 30)
        self.per_agent_per_min = rate_limits.get("per_agent_per_min", 20)
        self.strict_mode_per_min = rate_limits.get("strict_mode_per_min", 10)
        
        # Track requests: {bucket_key: [timestamps]}
        self._global_requests: list = []
        self._domain_requests: Dict[str, list] = defaultdict(list)
        self._agent_requests: Dict[str, list] = defaultdict(list)
        
        # Lock would be needed for thread safety (simplified for MVP)
    
    def _cleanup_old_requests(self):
        """Remove requests older than 1 minute"""
        one_minute_ago = time.time() - 60
        
        self._global_requests = [t for t in self._global_requests if t > one_minute_ago]
        
        for domain in list(self._domain_requests.keys()):
            self._domain_requests[domain] = [t for t in self._domain_requests[domain] if t > one_minute_ago]
            if not self._domain_requests[domain]:
                del self._domain_requests[domain]
        
        for agent in list(self._agent_requests.keys()):
            self._agent_requests[agent] = [t for t in self._agent_requests[agent] if t > one_minute_ago]
            if not self._agent_requests[agent]:
                del self._agent_requests[agent]
    
    def check_rate_limit(self, domain: Optional[str] = None, agent_id: Optional[str] = None,
                        strict_mode: bool = False) -> Tuple[bool, Optional[str]]:
        """
        Check if request is within rate limits
        
        Returns: (allowed, reason_if_blocked)
        """
        self._cleanup_old_requests()
        now = time.time()
        
        # Determine limits based on mode
        agent_limit = self.strict_mode_per_min if strict_mode else self.per_agent_per_min
        
        # Check global limit
        if len(self._global_requests) >= self.global_per_min:
            return False, f"Global rate limit exceeded ({self.global_per_min}/min)"
        
        # Check domain limit
        if domain:
            domain_requests = self._domain_requests.get(domain, [])
            if len(domain_requests) >= self.per_domain_per_min:
                return False, f"Domain rate limit exceeded for {domain} ({self.per_domain_per_min}/min)"
        
        # Check agent limit
        if agent_id:
            agent_requests = self._agent_requests.get(agent_id, [])
            if len(agent_requests) >= agent_limit:
                return False, f"Agent rate limit exceeded for {agent_id} ({agent_limit}/min)"
        
        # All checks passed
        return True, None
    
    def record_request(self, domain: Optional[str] = None, agent_id: Optional[str] = None):
        """Record a request for rate limiting"""
        now = time.time()
        self._global_requests.append(now)
        
        if domain:
            self._domain_requests[domain].append(now)
        
        if agent_id:
            self._agent_requests[agent_id].append(now)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current rate limit statistics"""
        self._cleanup_old_requests()
        return {
            "global": {
                "requests_last_minute": len(self._global_requests),
                "limit": self.global_per_min
            },
            "domains": {
                domain: {
                    "requests_last_minute": len(requests),
                    "limit": self.per_domain_per_min
                }
                for domain, requests in self._domain_requests.items()
            },
            "agents": {
                agent: {
                    "requests_last_minute": len(requests),
                    "limit": self.per_agent_per_min
                }
                for agent, requests in self._agent_requests.items()
            }
        }
