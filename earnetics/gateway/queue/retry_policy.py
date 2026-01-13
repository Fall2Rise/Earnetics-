"""
Retry Policy: Determines which errors should be retried
"""
from typing import Tuple, Optional


class RetryPolicy:
    """Determines retry behavior for different error types"""
    
    # Transient errors that should be retried
    RETRYABLE_STATUS_CODES = [429, 500, 502, 503, 504]
    RETRYABLE_ERRORS = [
        "timeout",
        "connection",
        "temporary",
        "rate limit",
        "server error"
    ]
    
    @classmethod
    def should_retry(cls, error: Optional[str] = None, status_code: Optional[int] = None) -> Tuple[bool, Optional[str]]:
        """
        Determine if error should be retried
        
        Returns: (should_retry, reason)
        """
        # Check status code
        if status_code and status_code in cls.RETRYABLE_STATUS_CODES:
            return True, f"Retryable status code: {status_code}"
        
        # Check error message
        if error:
            error_lower = error.lower()
            for retryable in cls.RETRYABLE_ERRORS:
                if retryable in error_lower:
                    return True, f"Retryable error: {error}"
        
        # Permanent errors should not be retried
        if status_code and 400 <= status_code < 500 and status_code != 429:
            return False, f"Client error (not retryable): {status_code}"
        
        # Unknown errors: retry once
        if error:
            return True, "Unknown error - will retry once"
        
        return False, "No retry needed"
