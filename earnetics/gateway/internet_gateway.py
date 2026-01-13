"""
Internet Gateway: Central gateway for all agent internet access
Enforces RBAC, allowlists, rate limits, audit logs, and kill switch
"""
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import uuid

from earnetics.gateway.security.kill_switch import KillSwitch
from earnetics.gateway.security.rate_limiter import RateLimiter
from earnetics.gateway.security.domain_rules import DomainRules
from earnetics.gateway.security.audit_logger import AuditLogger
from earnetics.gateway.security.credential_vault import CredentialVault
from earnetics.gateway.security.approval_tokens import ApprovalTokenManager
from earnetics.gateway.adapters.http_reader import HTTPReaderAdapter
from earnetics.gateway.adapters.search_adapter import SearchAdapter
from earnetics.gateway.adapters.email_adapter import EmailAdapter
from earnetics.gateway.adapters.social_adapter import SocialAdapter
from earnetics.gateway.adapters.stripe_adapter import StripeAdapter
from earnetics.gateway.queue.task_queue import TaskQueue
from earnetics.gateway.queue.retry_policy import RetryPolicy


class InternetGateway:
    """Main Internet Gateway - single point of control for all network access"""
    
    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "internet_gateway.json"
        self.config_path = config_path
        self._load_config()
        self._initialize_components()
    
    def _load_config(self):
        """Load gateway configuration"""
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)
    
    def _initialize_components(self):
        """Initialize security and adapter components"""
        # Security components
        self.kill_switch = KillSwitch(self.config_path)
        self.rate_limiter = RateLimiter(self.config)
        self.domain_rules = DomainRules()
        self.audit_logger = AuditLogger(
            enabled=self.config.get("logging", {}).get("audit_enabled", True)
        )
        self.credential_vault = CredentialVault()
        self.approval_tokens = ApprovalTokenManager()
        
        # Load permissions
        permissions_path = Path(__file__).parent.parent / "config" / "permissions.json"
        with open(permissions_path, 'r') as f:
            self.permissions = json.load(f)
        
        # Task queue
        self.task_queue = TaskQueue(self.config)
        
        # Adapters
        self.adapters = {}
        adapters_config = self.config.get("adapters", {})
        
        # HTTP Reader (MVP - read-only)
        if adapters_config.get("http_reader", {}).get("enabled", True):
            self.adapters["http_reader"] = HTTPReaderAdapter(self.config, self.credential_vault)
        
        # Search Adapter (MVP - uses internal knowledge router)
        if adapters_config.get("search_adapter", {}).get("enabled", True):
            self.adapters["search_adapter"] = SearchAdapter(self.config, self.credential_vault)
        
        # Write Adapters (Phase 2)
        if adapters_config.get("email_adapter", {}).get("enabled", True):
            self.adapters["email_adapter"] = EmailAdapter(self.config, self.credential_vault)
        
        if adapters_config.get("social_adapter", {}).get("enabled", True):
            self.adapters["social_adapter"] = SocialAdapter(self.config, self.credential_vault)
        
        if adapters_config.get("stripe_adapter", {}).get("enabled", True):
            self.adapters["stripe_adapter"] = StripeAdapter(self.config, self.credential_vault)
    
    def _check_permissions(self, agent_id: str, role: str, action: str) -> Tuple[bool, Optional[str]]:
        """Check if agent has permission for action"""
        role_config = self.permissions.get("roles", {}).get(role, {})
        if not role_config:
            role_config = self.permissions.get("roles", {}).get("DEFAULT", {})
        
        # Check if action exists
        action_config = self.permissions.get("actions", {}).get(action)
        if not action_config:
            return False, f"Unknown action: {action}"
        
        action_type = action_config.get("type", "read")
        
        # Check read permissions
        if action_type == "read":
            allowed_actions = role_config.get("read", [])
            if action in allowed_actions:
                return True, None
            return False, f"Action {action} not in read permissions for role {role}"
        
        # Check write permissions
        elif action_type == "write":
            # Check kill switch first
            if not self.kill_switch.is_write_allowed():
                return False, "kill_switch: Write operations disabled"
            
            allowed_actions = role_config.get("write", [])
            if action not in allowed_actions:
                return False, f"Action {action} not in write permissions for role {role}"
            
            # Check if approval token required
            requires_approval = role_config.get("requires_approval_token", False)
            if requires_approval:
                # Approval token check will be done in execute method
                pass
            
            return True, None
        
        return False, f"Unknown action type: {action_type}"
    
    def _check_approval_token(self, action: str, approval_token: Optional[str],
                             role: str) -> Tuple[bool, Optional[str]]:
        """Validate approval token for write actions"""
        role_config = self.permissions.get("roles", {}).get(role, {})
        requires_approval = role_config.get("requires_approval_token", False)
        
        if not requires_approval:
            return True, None  # No approval needed
        
        if not approval_token:
            return False, "approval_token_required: Write action requires approval token"
        
        # Validate token
        is_valid, reason = self.approval_tokens.validate_token(approval_token, action)
        if not is_valid:
            return False, f"approval_token_invalid: {reason}"
        
        return True, None
    
    def execute(self, agent_id: str, role: str, action: str, params: Dict[str, Any],
               approval_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute gateway action with full security checks
        
        Returns: {
            "success": bool,
            "status": "allowed|blocked|failed|success",
            "data": Any,
            "error": Optional[str],
            "policy_reason": Optional[str],
            "audit_id": str
        }
        """
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Check permissions
        has_permission, perm_reason = self._check_permissions(agent_id, role, action)
        if not has_permission:
            audit_id = self.audit_logger.log(
                agent_id=agent_id,
                role=role,
                action=action,
                target=params.get("url", "unknown"),
                status="blocked",
                policy_reason=perm_reason,
                request_id=request_id,
                latency_ms=int((time.time() - start_time) * 1000)
            )
            return {
                "success": False,
                "status": "blocked",
                "data": None,
                "error": perm_reason,
                "policy_reason": perm_reason,
                "audit_id": audit_id
            }
        
        # Check approval token for write actions
        action_config = self.permissions.get("actions", {}).get(action, {})
        if action_config.get("type") == "write":
            token_valid, token_reason = self._check_approval_token(action, approval_token, role)
            if not token_valid:
                audit_id = self.audit_logger.log(
                    agent_id=agent_id,
                    role=role,
                    action=action,
                    target=params.get("url", "unknown"),
                    status="blocked",
                    policy_reason=token_reason,
                    request_id=request_id,
                    latency_ms=int((time.time() - start_time) * 1000)
                )
                return {
                    "success": False,
                    "status": "blocked",
                    "data": None,
                    "error": token_reason,
                    "policy_reason": token_reason,
                    "audit_id": audit_id
                }
        
        # Extract domain for allowlist/rate limit checks
        url = params.get("url", "")
        domain = self.domain_rules.normalize_domain(url) if url else None
        
        # Check allowlist/denylist
        action_type = action_config.get("type", "read")
        domain_allowed, domain_reason = self.domain_rules.is_allowed(url, action_type) if url else (True, None)
        if not domain_allowed:
            audit_id = self.audit_logger.log(
                agent_id=agent_id,
                role=role,
                action=action,
                target=url,
                status="blocked",
                policy_reason=domain_reason,
                request_id=request_id,
                latency_ms=int((time.time() - start_time) * 1000)
            )
            return {
                "success": False,
                "status": "blocked",
                "data": None,
                "error": domain_reason,
                "policy_reason": domain_reason,
                "audit_id": audit_id
            }
        
        # Check rate limits
        role_config = self.permissions.get("roles", {}).get(role, {})
        strict_mode = role_config.get("rate_limit_mode") == "strict"
        rate_allowed, rate_reason = self.rate_limiter.check_rate_limit(domain, agent_id, strict_mode)
        if not rate_allowed:
            audit_id = self.audit_logger.log(
                agent_id=agent_id,
                role=role,
                action=action,
                target=url or "search",
                status="blocked",
                policy_reason=rate_reason,
                request_id=request_id,
                latency_ms=int((time.time() - start_time) * 1000)
            )
            return {
                "success": False,
                "status": "blocked",
                "data": None,
                "error": rate_reason,
                "policy_reason": rate_reason,
                "audit_id": audit_id
            }
        
        # Record rate limit
        self.rate_limiter.record_request(domain, agent_id)
        
        # Route to appropriate adapter
        adapter_result = None
        error = None
        
        try:
            if action in ["web.fetch", "web.head"]:
                adapter = self.adapters.get("http_reader")
                if not adapter:
                    raise ValueError("HTTP reader adapter not available")
                adapter_result = adapter.execute(action, params, agent_id, role)
            elif action == "web.search":
                adapter = self.adapters.get("search_adapter")
                if not adapter:
                    raise ValueError("Search adapter not available")
                adapter_result = adapter.execute(action, params, agent_id, role)
            elif action == "email.send":
                adapter = self.adapters.get("email_adapter")
                if not adapter:
                    raise ValueError("Email adapter not available")
                adapter_result = adapter.execute(action, params, agent_id, role)
            elif action == "social.post":
                adapter = self.adapters.get("social_adapter")
                if not adapter:
                    raise ValueError("Social adapter not available")
                adapter_result = adapter.execute(action, params, agent_id, role)
            elif action in ["stripe.read", "stripe.write"]:
                adapter = self.adapters.get("stripe_adapter")
                if not adapter:
                    raise ValueError("Stripe adapter not available")
                adapter_result = adapter.execute(action, params, agent_id, role)
            else:
                raise ValueError(f"No adapter available for action: {action}")
            
            if not adapter_result.get("success"):
                error = adapter_result.get("error", "Adapter execution failed")
        except Exception as e:
            error = str(e)
            adapter_result = {
                "success": False,
                "error": error,
                "data": None,
                "metadata": {},
                "citation": {}
            }
        
        # Determine final status
        latency_ms = int((time.time() - start_time) * 1000)
        
        if adapter_result and adapter_result.get("success"):
            status = "success"
            response_code = adapter_result.get("data", {}).get("status_code", 200)
            response_bytes = len(str(adapter_result.get("data", {}).get("text", "")))
        elif error:
            # Check if error is retryable
            should_retry, retry_reason = RetryPolicy.should_retry(error)
            if should_retry and self.task_queue.enabled:
                # Enqueue for retry
                self.task_queue.enqueue(agent_id, role, action, params, error)
                status = "failed_queued"
            else:
                status = "failed"
            response_code = None
            response_bytes = None
        else:
            status = "failed"
            response_code = None
            response_bytes = None
        
        # Log audit entry
        audit_id = self.audit_logger.log(
            agent_id=agent_id,
            role=role,
            action=action,
            target=url or "search",
            status=status,
            method=params.get("method", "GET"),
            request_id=request_id,
            latency_ms=latency_ms,
            response_code=response_code,
            response_bytes=response_bytes,
            error_message=error
        )
        
        return {
            "success": adapter_result.get("success", False) if adapter_result else False,
            "status": status,
            "data": adapter_result.get("data") if adapter_result else None,
            "metadata": adapter_result.get("metadata", {}) if adapter_result else {},
            "citation": adapter_result.get("citation", {}) if adapter_result else {},
            "error": error,
            "policy_reason": None,
            "audit_id": audit_id
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get gateway status"""
        return {
            "enabled": self.config.get("enabled", True),
            "kill_switch": self.kill_switch.get_status(),
            "rate_limits": self.rate_limiter.get_stats(),
            "adapters": {
                name: {
                    "enabled": adapter.is_enabled(),
                    "requires_internet": adapter.requires_internet_connection()
                }
                for name, adapter in self.adapters.items()
            },
            "audit_stats": self.audit_logger.get_stats(hours=1)
        }
