# Backend Configuration Module
# Centralizes all environment variable loading and configuration

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load .env from project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE, override=True)


def _normalize_env_path(env_value: Optional[str], default: str) -> Path:
    """
    Normalize path from environment variable.
    Converts backslashes to forward slashes for cross-platform compatibility.
    Path() handles both, but this ensures consistency.
    """
    if not env_value:
        return Path(default)
    # Replace backslashes with forward slashes for consistency
    normalized = env_value.replace("\\", "/")
    return Path(normalized)

class Settings:
    """Centralized configuration for the backend"""
    
    # Server Configuration
    HOST: str = os.getenv("FALLAT_HOST", "127.0.0.1")
    PORT: int = int(os.getenv("FALLAT_PORT", os.getenv("PORT", "8000")))
    RELOAD: bool = os.getenv("FALLAT_RELOAD", "false").lower() in {"1", "true", "yes"}
    APP_VERSION: str = os.getenv("FALLAT_APP_VERSION", "0.1.0")
    
    # Security
    API_TOKEN: Optional[str] = os.getenv("FALLAT_API_TOKEN")
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    # Database Paths
    BUSINESS_DB_PATH: Path = _normalize_env_path(os.getenv("BUSINESS_DB_PATH"), "business_database.db")
    AUDIT_LOG_DB: Path = _normalize_env_path(os.getenv("AUDIT_LOG_DB"), "audit_log.db")
    VECTOR_MEMORY_DB: Path = _normalize_env_path(os.getenv("VECTOR_MEMORY_DB"), "vector_memory.db")
    
    # Email Provider (Resend)
    RESEND_API_KEY: Optional[str] = os.getenv("RESEND_API_KEY")
    RESEND_FROM_EMAIL: str = os.getenv("RESEND_FROM_EMAIL", "noreply@earnetics.live")
    
    # Payment Provider (Stripe)
    STRIPE_SECRET_KEY: Optional[str] = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_PUBLISHABLE_KEY: Optional[str] = os.getenv("STRIPE_PUBLISHABLE_KEY")
    STRIPE_WEBHOOK_SECRET: Optional[str] = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    # Kill Switches (from system_state)
    SAFE_MODE: bool = False
    MAIL_SENDING_PAUSED: bool = False
    AGENT_EXECUTION_PAUSED: bool = False
    
    # Autonomy
    AUTONOMY_WORKER_ENABLED: bool = os.getenv("AUTONOMY_WORKER_ENABLED", "true").lower() in {"1", "true", "yes"}
    AUTONOMY_WORKER_ID: str = os.getenv("AUTONOMY_WORKER_ID", "autonomy-worker")
    
    # LLM Provider
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ollama")
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")
    
    # Rate Limiting
    RATE_LIMIT_PER_MIN: int = int(os.getenv("FALLAT_RATE_LIMIT_PER_MIN", "60"))
    
    @classmethod
    def validate(cls) -> list[str]:
        """Validate required settings and return list of warnings"""
        warnings = []
        
        if not cls.API_TOKEN:
            warnings.append("FALLAT_API_TOKEN not set - API will be unsecured")
        
        if not cls.RESEND_API_KEY:
            warnings.append("RESEND_API_KEY not set - emails will be simulated")
        
        if not cls.STRIPE_SECRET_KEY:
            warnings.append("STRIPE_SECRET_KEY not set - payments disabled")
        
        return warnings

# Singleton instance
settings = Settings()

# Validate on import
_warnings = settings.validate()
if _warnings:
    import logging
    logger = logging.getLogger(__name__)
    for warning in _warnings:
        logger.warning(f"Config: {warning}")
