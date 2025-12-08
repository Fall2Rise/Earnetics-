"""Encrypted credential vault for Fallat_CrewAI.

This module stores API keys and other secrets in an encrypted SQLite database
so credentials never leave the local machine. Secrets are encrypted using a
Fernet key that operators must provide via the CREDENTIAL_VAULT_KEY environment
variable (generate with :func:`CredentialVault.generate_key`).
"""

from __future__ import annotations

import base64
import json
import os
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from cryptography.fernet import Fernet, InvalidToken

__all__ = [
    "CredentialVault",
    "CredentialVaultError",
    "VaultSecret",
]

ISO_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
DEFAULT_DB_PATH = Path(os.getenv("CREDENTIAL_VAULT_DB", "credential_vault.db"))


class CredentialVaultError(RuntimeError):
    """Raised when the credential vault cannot fulfill an operation."""


def _utcnow() -> str:
    return datetime.utcnow().strftime(ISO_FORMAT)


def _load_fernet(key: str) -> Fernet:
    try:
        # Accept either a raw 32-byte key or a base64-encoded key
        if len(key) == 32:
            token = base64.urlsafe_b64encode(key.encode())
        else:
            token = key.encode()
        cipher = Fernet(token)
    except (ValueError, TypeError) as exc:
        raise CredentialVaultError("Invalid CREDENTIAL_VAULT_KEY provided") from exc
    return cipher


@dataclass
class VaultSecret:
    service: str
    name: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_utcnow)
    updated_at: str = field(default_factory=_utcnow)

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "VaultSecret":
        return cls(
            service=row["service"],
            name=row["name"],
            metadata=json.loads(row["metadata"] or "{}"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


class CredentialVault:
    """Encrypted SQLite credential vault."""

    def __init__(self, db_path: Path = DEFAULT_DB_PATH, *, key: Optional[str] = None) -> None:
        self.db_path = db_path
        key = key or os.getenv("CREDENTIAL_VAULT_KEY")
        if not key:
            raise CredentialVaultError(
                "Missing CREDENTIAL_VAULT_KEY environment variable. "
                "Generate one with CredentialVault.generate_key()."
            )
        self._fernet = _load_fernet(key)
        self._ensure_schema()

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def generate_key() -> str:
        """Return a new base64-encoded Fernet key."""
        return Fernet.generate_key().decode()

    def _connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS credentials (
                    service TEXT NOT NULL,
                    name TEXT NOT NULL,
                    secret BLOB NOT NULL,
                    metadata TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (service, name)
                )
                """
            )
            conn.commit()

    # ------------------------------------------------------------------ actions
    def store_secret(
        self,
        service: str,
        name: str,
        secret: str,
        *,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> VaultSecret:
        metadata_json = json.dumps(metadata or {})
        now = _utcnow()
        encrypted = self._fernet.encrypt(secret.encode())

        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO credentials (service, name, secret, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(service, name) DO UPDATE SET
                    secret = excluded.secret,
                    metadata = excluded.metadata,
                    updated_at = excluded.updated_at
                """,
                (service, name, encrypted, metadata_json, now, now),
            )
            conn.commit()

        return VaultSecret(service=service, name=name, metadata=json.loads(metadata_json), created_at=now, updated_at=now)

    def get_secret(self, service: str, name: str) -> Optional[str]:
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT secret FROM credentials WHERE service = ? AND name = ?",
                (service, name),
            )
            row = cur.fetchone()
        if not row:
            return None
        try:
            decrypted = self._fernet.decrypt(row["secret"])
        except InvalidToken as exc:
            raise CredentialVaultError("Unable to decrypt stored secret") from exc
        return decrypted.decode()

    def list_secrets(self, service: Optional[str] = None) -> List[VaultSecret]:
        query = "SELECT service, name, metadata, created_at, updated_at FROM credentials"
        params: List[Any] = []
        if service:
            query += " WHERE service = ?"
            params.append(service)
        query += " ORDER BY service, name"

        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            rows = cur.fetchall()
        return [VaultSecret.from_row(row) for row in rows]

    def delete_secret(self, service: str, name: str) -> bool:
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM credentials WHERE service = ? AND name = ?", (service, name))
            deleted = cur.rowcount
            conn.commit()
        return bool(deleted)

    def delete_service(self, service: str) -> int:
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM credentials WHERE service = ?", (service,))
            deleted = cur.rowcount
            conn.commit()
        return deleted

