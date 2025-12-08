"""Centralised credential access for AI Revenue Command Center."""
from __future__ import annotations

import logging
import os
from typing import Optional

from backend.credential_vault import CredentialVault, CredentialVaultError

try:
    import keyring  # type: ignore
except ImportError:  # pragma: no cover - keyring optional at import time
    keyring = None  # type: ignore

_DEFAULT_SERVICE = "AIRevenueCommandCenter"
_logger = logging.getLogger(__name__)
_vault_checked = False
_vault_instance: Optional[CredentialVault] = None


def _get_vault() -> Optional[CredentialVault]:
    global _vault_checked, _vault_instance
    if not _vault_checked:
        key = os.getenv("CREDENTIAL_VAULT_KEY")
        if key:
            try:
                _vault_instance = CredentialVault(key=key)
            except CredentialVaultError as exc:  # pragma: no cover - misconfiguration
                _logger.debug("Credential vault unavailable: %s", exc)
                _vault_instance = None
        _vault_checked = True
    return _vault_instance


def get_secret(key: str, *, default: Optional[str] = None, service: str = _DEFAULT_SERVICE) -> Optional[str]:
    """Return the secret identified by *key*.

    Order of resolution:
    1. Credential vault (if configured via CREDENTIAL_VAULT_KEY)
    2. Windows Credential Manager via keyring (if installed and entry exists)
    3. Environment variable (os.getenv)
    4. Optional default value
    """
    value: Optional[str] = None
    vault = _get_vault()
    if vault is not None:
        try:
            value = vault.get_secret(service, key)
        except CredentialVaultError as exc:  # pragma: no cover - defensive
            _logger.debug("Credential vault lookup failed for %s/%s: %s", service, key, exc)
            value = None
    if value:
        return value
    if keyring is not None:
        try:
            value = keyring.get_password(service, key)
        except Exception:  # pragma: no cover - keyring failure
            value = None
    if value:
        return value
    return os.getenv(key, default)


def has_secret(key: str, service: str = _DEFAULT_SERVICE) -> bool:
    """Return True if the secret exists in the vault, keyring or environment."""
    vault = _get_vault()
    if vault is not None:
        try:
            if vault.get_secret(service, key) is not None:
                return True
        except CredentialVaultError:  # pragma: no cover - defensive
            pass
    if keyring is not None:
        try:
            if keyring.get_password(service, key):
                return True
        except Exception:  # pragma: no cover - keyring failure
            pass
    return os.getenv(key) is not None


def describe_secrets(keys: list[str], service: str = _DEFAULT_SERVICE) -> list[dict[str, str]]:
    """Return structured status information for the requested *keys*."""
    status: list[dict[str, str]] = []
    vault = _get_vault()
    vault_entries = set()
    if vault is not None:
        try:
            vault_entries = {entry.name for entry in vault.list_secrets(service=service)}
        except CredentialVaultError:  # pragma: no cover - defensive
            vault_entries = set()
    for key in keys:
        source = "missing"
        if key in vault_entries:
            source = "vault"
        elif keyring is not None:
            try:
                if keyring.get_password(service, key):
                    source = "credential_manager"
            except Exception:  # pragma: no cover - keyring failure
                source = "error"
        env_present = os.getenv(key)
        if source == "missing" and env_present:
            source = "environment"
        status.append({"key": key, "source": source})
    return status
