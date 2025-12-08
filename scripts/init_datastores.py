#!/usr/bin/env python3
"""Initialize local databases used by Fallat CrewAI."""

from __future__ import annotations

import argparse
import logging

from backend.audit_log import AuditLogStore
from backend.corporate_memory import CorporateMemory
from backend.credential_vault import CredentialVault, CredentialVaultError
from backend.vector_memory import VectorMemoryStore

logger = logging.getLogger(__name__)


def initialize_datastores(include_vault: bool = False) -> None:
    """Create or update all local SQLite stores."""
    CorporateMemory()
    logger.info("Corporate memory database ready")

    AuditLogStore()
    logger.info("Audit log database ready")

    VectorMemoryStore()
    logger.info("Vector memory store ready")

    if include_vault:
        try:
            CredentialVault()
            logger.info("Credential vault ready")
        except CredentialVaultError as exc:
            logger.error("Unable to initialize credential vault: %s", exc)
            raise


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare Fallat CrewAI datastores.")
    parser.add_argument(
        "--include-vault",
        action="store_true",
        help="also verify that the credential vault can be opened (requires CREDENTIAL_VAULT_KEY)",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    initialize_datastores(include_vault=args.include_vault)
    logger.info("All datastores initialized")


if __name__ == "__main__":
    main()
