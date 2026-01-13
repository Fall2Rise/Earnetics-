"""
Domain Rules: Validates allowlist/denylist and domain normalization
"""
import json
from pathlib import Path
from typing import List, Optional, Tuple
from urllib.parse import urlparse


class DomainRules:
    """Domain allowlist/denylist validation with wildcard support"""
    
    def __init__(self, config_path: Path = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "allowlists.json"
        self.config_path = config_path
        self._load_config()
    
    def _load_config(self):
        """Load allowlist/denylist configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                self.read_allowlist = set(config.get("read_allowlist", []))
                self.write_allowlist = set(config.get("write_allowlist", []))
                self.denylist = set(config.get("denylist", []))
                
                wildcard_rules = config.get("wildcard_rules", {})
                self.allowed_wildcards = wildcard_rules.get("allowed_subdomains", [])
                self.blocked_wildcards = wildcard_rules.get("blocked_subdomains", [])
        except Exception as e:
            print(f"Error loading domain rules: {e}")
            self.read_allowlist = set()
            self.write_allowlist = set()
            self.denylist = set()
            self.allowed_wildcards = []
            self.blocked_wildcards = []
    
    def normalize_domain(self, url: str) -> str:
        """Extract and normalize domain from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path
            
            # Remove port if present
            if ':' in domain:
                domain = domain.split(':')[0]
            
            # Remove www. prefix for normalization
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return domain.lower()
        except Exception as e:
            print(f"Error normalizing domain from {url}: {e}")
            return ""
    
    def _matches_wildcard(self, domain: str, pattern: str) -> bool:
        """Check if domain matches wildcard pattern"""
        if pattern.startswith("*."):
            suffix = pattern[2:]
            return domain.endswith("." + suffix) or domain == suffix
        return domain == pattern
    
    def is_allowed(self, url: str, action_type: str = "read") -> Tuple[bool, Optional[str]]:
        """
        Check if domain is allowed for action type
        
        Returns: (allowed, reason_if_blocked)
        """
        domain = self.normalize_domain(url)
        
        if not domain:
            return False, "Invalid domain"
        
        # Check denylist first (highest priority)
        for blocked in self.denylist:
            if domain == blocked or self._matches_wildcard(domain, blocked):
                return False, f"Domain {domain} is on denylist"
        
        # Check blocked wildcards
        for pattern in self.blocked_wildcards:
            if self._matches_wildcard(domain, pattern):
                return False, f"Domain {domain} matches blocked wildcard pattern"
        
        # Check action-specific allowlist
        if action_type == "read":
            allowlist = self.read_allowlist
        elif action_type == "write":
            allowlist = self.write_allowlist
        else:
            return False, f"Unknown action type: {action_type}"
        
        # Check exact match
        if domain in allowlist:
            return True, None
        
        # Check wildcard matches
        for pattern in self.allowed_wildcards:
            if self._matches_wildcard(domain, pattern):
                return True, None
        
        # Not in allowlist
        return False, f"Domain {domain} not in {action_type} allowlist"
    
    def add_to_allowlist(self, domain: str, action_type: str = "read") -> bool:
        """Add domain to allowlist (runtime modification)"""
        domain = self.normalize_domain(domain)
        if action_type == "read":
            self.read_allowlist.add(domain)
        elif action_type == "write":
            self.write_allowlist.add(domain)
        else:
            return False
        return True
    
    def add_to_denylist(self, domain: str) -> bool:
        """Add domain to denylist (runtime modification)"""
        domain = self.normalize_domain(domain)
        self.denylist.add(domain)
        return True
