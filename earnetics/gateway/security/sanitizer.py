"""
Sanitizer: Redacts secrets from logs, headers, and request/response bodies
"""
import re
from typing import Dict, Any, Union, List


class Sanitizer:
    """Sanitizes sensitive data from logs and audit entries"""
    
    # Common secret patterns
    SECRET_PATTERNS = [
        r'api[_-]?key["\s:=]+([a-zA-Z0-9_\-]{20,})',
        r'secret[_-]?key["\s:=]+([a-zA-Z0-9_\-]{20,})',
        r'password["\s:=]+([^\s"\'<>]{3,})',
        r'token["\s:=]+([a-zA-Z0-9_\-]{20,})',
        r'authorization["\s:]+Bearer\s+([a-zA-Z0-9_\-\.]+)',
        r'x[_-]?api[_-]?token["\s:=]+([a-zA-Z0-9_\-]{20,})',
        r'stripe[_-]?secret["\s:=]+([a-zA-Z0-9_\-]{20,})',
        r'sk_[a-zA-Z0-9]{32,}',
        r'pk_[a-zA-Z0-9]{32,}',
        r'ghp_[a-zA-Z0-9]{36}',
        r'xoxb-[a-zA-Z0-9-]+',
    ]
    
    REDACTION_MARKER = "[REDACTED]"
    
    @classmethod
    def redact_secrets(cls, text: Union[str, Dict, List]) -> Union[str, Dict, List]:
        """Recursively redact secrets from text, dict, or list"""
        if isinstance(text, str):
            return cls._redact_string(text)
        elif isinstance(text, dict):
            return {k: cls.redact_secrets(v) for k, v in text.items()}
        elif isinstance(text, list):
            return [cls.redact_secrets(item) for item in text]
        else:
            return text
    
    @classmethod
    def _redact_string(cls, text: str) -> str:
        """Redact secrets from a string"""
        if not text:
            return text
        
        result = text
        
        # Apply secret patterns
        for pattern in cls.SECRET_PATTERNS:
            result = re.sub(pattern, cls.REDACTION_MARKER, result, flags=re.IGNORECASE)
        
        # Redact common header patterns
        result = re.sub(
            r'(?i)(authorization|api[_-]?key|secret|token|x[_-]?api[_-]?token):\s*[^\s]+',
            r'\1: ' + cls.REDACTION_MARKER,
            result
        )
        
        return result
    
    @classmethod
    def sanitize_headers(cls, headers: Dict[str, str]) -> Dict[str, str]:
        """Sanitize HTTP headers, redacting sensitive ones"""
        sensitive_headers = [
            'authorization', 'api-key', 'api_key', 'x-api-key', 'x-api-token',
            'secret', 'token', 'cookie', 'set-cookie',
            'stripe-secret', 'stripe_key'
        ]
        
        sanitized = {}
        for key, value in headers.items():
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in sensitive_headers):
                sanitized[key] = cls.REDACTION_MARKER
            else:
                sanitized[key] = cls._redact_string(value)
        
        return sanitized
    
    @classmethod
    def sanitize_url(cls, url: str) -> str:
        """Sanitize URL by redacting query parameters that might contain secrets"""
        try:
            from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
            
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            
            # Redact sensitive query params
            sensitive_params = ['key', 'token', 'secret', 'api_key', 'password', 'auth']
            sanitized_params = {}
            for key, values in query_params.items():
                if any(sensitive in key.lower() for sensitive in sensitive_params):
                    sanitized_params[key] = [cls.REDACTION_MARKER]
                else:
                    sanitized_params[key] = values
            
            # Reconstruct URL
            sanitized_query = urlencode(sanitized_params, doseq=True)
            sanitized = parsed._replace(query=sanitized_query)
            return urlunparse(sanitized)
        except Exception:
            # If URL parsing fails, just redact the whole thing if it looks suspicious
            if any(sensitive in url.lower() for sensitive in ['key=', 'token=', 'secret=', 'password=']):
                return cls.REDACTION_MARKER
            return url
    
    @classmethod
    def sanitize_audit_entry(cls, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize an entire audit entry"""
        sanitized = entry.copy()
        
        # Sanitize target URL
        if "target" in sanitized:
            sanitized["target"] = cls.sanitize_url(str(sanitized["target"]))
        
        # Sanitize headers if present
        if "headers" in sanitized:
            sanitized["headers"] = cls.sanitize_headers(sanitized["headers"])
        
        # Sanitize request/response bodies if present
        for key in ["request_body", "response_body", "payload"]:
            if key in sanitized:
                sanitized[key] = cls.redact_secrets(sanitized[key])
        
        # Sanitize metadata
        if "metadata" in sanitized:
            sanitized["metadata"] = cls.redact_secrets(sanitized["metadata"])
        
        return sanitized
