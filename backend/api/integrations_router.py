"""Integration management API routes."""

from __future__ import annotations

import os
from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from backend.credential_vault import CredentialVault, CredentialVaultError
from backend.config.integrations import INTEGRATION_REQUIREMENTS
from backend.auth import verify_request_token
from backend.audit_log import log_event
from backend.system_state import global_state

router = APIRouter(prefix="/api/integrations", tags=["integrations"])

protected_dependencies = [Depends(verify_request_token)]


def _get_credential_vault() -> Optional[CredentialVault]:
    """Get credential vault instance from app state."""
    try:
        from backend.main_server import app
        return getattr(app.state, "credential_vault", None)
    except Exception:
        return None


def _get_integration_value(integration_name: str, env_var: str) -> Optional[str]:
    """Get integration value from vault (first) or env var (fallback)."""
    vault = _get_credential_vault()
    if vault:
        try:
            secret = vault.get_secret(service=integration_name, name=env_var)
            if secret:
                return secret
        except Exception:
            pass
    
    # Fallback to environment variable
    return os.getenv(env_var)


class IntegrationConfigPayload(BaseModel):
    credentials: Dict[str, str]
    test_connection: bool = False


class TestResult(BaseModel):
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None


@router.get("/status")
def get_integration_status():
    """Get status of all integrations (checks vault first, then env vars)."""
    status = {}
    vault = _get_credential_vault()
    
    for name, env_vars in INTEGRATION_REQUIREMENTS.items():
        missing = []
        found_in_vault = []
        
        for env_var in env_vars:
            value = _get_integration_value(name, env_var)
            if not value:
                missing.append(env_var)
            else:
                # Check if it came from vault
                if vault:
                    try:
                        vault_secret = vault.get_secret(service=name, name=env_var)
                        if vault_secret:
                            found_in_vault.append(env_var)
                    except Exception:
                        pass
        
        status[name] = {
            "status": "connected" if not missing else "disconnected",
            "missing_vars": missing,
            "found_in_vault": found_in_vault,
            "production_mode": not global_state.get("SAFE_MODE", False)
        }
    
    return status


@router.post("/{integration_name}/configure", dependencies=protected_dependencies)
def configure_integration(integration_name: str, payload: IntegrationConfigPayload):
    """Configure an integration by storing credentials in the vault."""
    if integration_name not in INTEGRATION_REQUIREMENTS:
        raise HTTPException(status_code=404, detail=f"Integration '{integration_name}' not found")
    
    required_vars = INTEGRATION_REQUIREMENTS[integration_name]
    
    # Validate all required credentials are provided
    missing = [var for var in required_vars if var not in payload.credentials]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required credentials: {', '.join(missing)}"
        )
    
    vault = _get_credential_vault()
    if not vault:
        raise HTTPException(
            status_code=503,
            detail="Credential vault is not available. Please set CREDENTIAL_VAULT_KEY environment variable."
        )
    
    # Store each credential in the vault
    stored = []
    for env_var, value in payload.credentials.items():
        if env_var in required_vars:
            try:
                vault.store_secret(
                    service=integration_name,
                    name=env_var,
                    secret=value,
                    metadata={"source": "ui_config", "integration": integration_name}
                )
                stored.append(env_var)
            except CredentialVaultError as e:
                raise HTTPException(status_code=500, detail=f"Failed to store {env_var}: {str(e)}")
    
    log_event(
        "integration.configured",
        agent="system",
        message=f"Configured integration '{integration_name}' via UI",
        details={"integration": integration_name, "credentials_stored": stored}
    )
    
    # Test connection if requested
    test_result = None
    if payload.test_connection:
        test_result = _test_integration(integration_name)
    
    return {
        "status": "success",
        "integration": integration_name,
        "credentials_stored": stored,
        "test_result": test_result.dict() if test_result else None
    }


@router.post("/{integration_name}/test", dependencies=protected_dependencies)
def test_integration(integration_name: str):
    """Test an integration connection."""
    if integration_name not in INTEGRATION_REQUIREMENTS:
        raise HTTPException(status_code=404, detail=f"Integration '{integration_name}' not found")
    
    result = _test_integration(integration_name)
    return result.dict()


def _test_integration(integration_name: str) -> TestResult:
    """Test integration connection (internal helper)."""
    required_vars = INTEGRATION_REQUIREMENTS[integration_name]
    
    # Check if all credentials are available
    missing = []
    for env_var in required_vars:
        value = _get_integration_value(integration_name, env_var)
        if not value:
            missing.append(env_var)
    
    if missing:
        return TestResult(
            success=False,
            message=f"Missing credentials: {', '.join(missing)}",
            details={"missing": missing}
        )
    
    # Test based on integration type
    try:
        if integration_name == "stripe":
            return _test_stripe_integration()
        elif integration_name == "email":
            return _test_email_integration()
        elif integration_name == "social":
            return _test_social_integration()
        elif integration_name == "llm":
            return _test_llm_integration()
        else:
            return TestResult(
                success=True,
                message="Credentials are present (validation not implemented for this integration)",
                details={"integration": integration_name}
            )
    except Exception as e:
        return TestResult(
            success=False,
            message=f"Test failed: {str(e)}",
            details={"integration": integration_name, "error": str(e)}
        )


def _test_stripe_integration() -> TestResult:
    """Test Stripe integration."""
    secret_key = _get_integration_value("stripe", "STRIPE_SECRET_KEY")
    publishable_key = _get_integration_value("stripe", "STRIPE_PUBLISHABLE_KEY")
    
    if not secret_key or not publishable_key:
        return TestResult(
            success=False,
            message="Missing Stripe credentials",
            details={"missing": ["STRIPE_SECRET_KEY", "STRIPE_PUBLISHABLE_KEY"]}
        )
    
    try:
        import stripe
        stripe.api_key = secret_key
        
        # Test by retrieving account info
        account = stripe.Account.retrieve()
        test_mode = secret_key.startswith("sk_test_")
        
        return TestResult(
            success=True,
            message=f"Stripe connection successful (mode: {'test' if test_mode else 'live'})",
            details={
                "account_id": account.id if hasattr(account, 'id') else None,
                "test_mode": test_mode,
                "country": account.country if hasattr(account, 'country') else None
            }
        )
    except Exception as e:
        return TestResult(
            success=False,
            message=f"Stripe connection failed: {str(e)}",
            details={"error": str(e)}
        )


def _test_email_integration() -> TestResult:
    """Test email integration (SMTP)."""
    email = _get_integration_value("email", "SMTP_EMAIL")
    password = _get_integration_value("email", "SMTP_PASSWORD")
    
    if not email or not password:
        return TestResult(
            success=False,
            message="Missing email credentials",
            details={"missing": ["SMTP_EMAIL", "SMTP_PASSWORD"]}
        )
    
    # Basic validation - check email format
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return TestResult(
            success=False,
            message="Invalid email format",
            details={"email": email}
        )
    
    return TestResult(
        success=True,
        message="Email credentials are present (SMTP connection test not implemented)",
        details={"email": email}
    )


def _test_social_integration() -> TestResult:
    """Test social media integration."""
    api_key = _get_integration_value("social", "TWITTER_API_KEY")
    api_secret = _get_integration_value("social", "TWITTER_API_SECRET")
    
    if not api_key or not api_secret:
        return TestResult(
            success=False,
            message="Missing social media credentials",
            details={"missing": ["TWITTER_API_KEY", "TWITTER_API_SECRET"]}
        )
    
    return TestResult(
        success=True,
        message="Social media credentials are present (connection test not implemented)",
        details={"has_api_key": bool(api_key), "has_api_secret": bool(api_secret)}
    )


def _test_llm_integration() -> TestResult:
    """Test LLM integration (Ollama)."""
    ollama_host = _get_integration_value("llm", "OLLAMA_HOST")
    
    if not ollama_host:
        return TestResult(
            success=False,
            message="Missing Ollama host configuration",
            details={"missing": ["OLLAMA_HOST"]}
        )
    
    # Try to connect to Ollama
    try:
        try:
            import requests
        except ImportError:
            return TestResult(
                success=False,
                message="requests package not installed (pip install requests)",
                details={"error": "requests package missing"}
            )
        
        response = requests.get(f"{ollama_host}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return TestResult(
                success=True,
                message=f"Ollama connection successful (found {len(models)} models)",
                details={"host": ollama_host, "models_count": len(models)}
            )
        else:
            return TestResult(
                success=False,
                message=f"Ollama connection failed (status: {response.status_code})",
                details={"host": ollama_host, "status_code": response.status_code}
            )
    except Exception as e:
        return TestResult(
            success=False,
            message=f"Ollama connection failed: {str(e)}",
            details={"host": ollama_host, "error": str(e)}
        )


@router.delete("/{integration_name}", dependencies=protected_dependencies)
def remove_integration(integration_name: str):
    """Remove all credentials for an integration from the vault."""
    if integration_name not in INTEGRATION_REQUIREMENTS:
        raise HTTPException(status_code=404, detail=f"Integration '{integration_name}' not found")
    
    vault = _get_credential_vault()
    if not vault:
        raise HTTPException(
            status_code=503,
            detail="Credential vault is not available"
        )
    
    try:
        deleted = vault.delete_service(service=integration_name)
        log_event(
            "integration.removed",
            agent="system",
            message=f"Removed integration '{integration_name}' credentials",
            details={"integration": integration_name, "deleted_count": deleted}
        )
        
        return {
            "status": "success",
            "integration": integration_name,
            "credentials_deleted": deleted
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove integration: {str(e)}")


@router.get("/{integration_name}/requirements")
def get_integration_requirements(integration_name: str):
    """Get required credentials for an integration."""
    if integration_name not in INTEGRATION_REQUIREMENTS:
        raise HTTPException(status_code=404, detail=f"Integration '{integration_name}' not found")
    
    required_vars = INTEGRATION_REQUIREMENTS[integration_name]
    
    # Get descriptions for each variable
    descriptions = {
        "stripe": {
            "STRIPE_SECRET_KEY": "Your Stripe secret key (starts with sk_live_ or sk_test_)",
            "STRIPE_PUBLISHABLE_KEY": "Your Stripe publishable key (starts with pk_live_ or pk_test_)"
        },
        "email": {
            "SMTP_EMAIL": "Your SMTP email address",
            "SMTP_PASSWORD": "Your SMTP password or app password"
        },
        "social": {
            "TWITTER_API_KEY": "Your Twitter/X API key",
            "TWITTER_API_SECRET": "Your Twitter/X API secret"
        },
        "llm": {
            "OLLAMA_HOST": "Ollama API endpoint (e.g., http://localhost:11434)"
        }
    }
    
    requirements = []
    for var in required_vars:
        requirements.append({
            "name": var,
            "description": descriptions.get(integration_name, {}).get(var, f"{var} credential"),
            "required": True
        })
    
    return {
        "integration": integration_name,
        "requirements": requirements
    }
