#!/usr/bin/env python3
"""Credential vault assistant for Fallat CrewAI."""

from __future__ import annotations

import argparse
import json
import sys

from backend.credential_vault import CredentialVault, CredentialVaultError


def cmd_generate_key(_: argparse.Namespace) -> None:
    print(CredentialVault.generate_key())


def cmd_status(args: argparse.Namespace) -> None:
    try:
        vault = CredentialVault()
        secrets = vault.list_secrets(args.service)
    except CredentialVaultError as exc:
        print(f"Vault not available: {exc}", file=sys.stderr)
        sys.exit(1)
    label = f"service '{args.service}'" if args.service else "all services"
    print(f"{len(secrets)} secrets stored for {label}.")


def cmd_list(args: argparse.Namespace) -> None:
    try:
        vault = CredentialVault()
        secrets = vault.list_secrets(args.service)
    except CredentialVaultError as exc:
        print(f"Vault not available: {exc}", file=sys.stderr)
        sys.exit(1)
    for secret in secrets:
        print(json.dumps(secret.__dict__, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Credential vault helper CLI.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub_generate = sub.add_parser("generate-key", help="output a new vault key")
    sub_generate.set_defaults(func=cmd_generate_key)

    sub_status = sub.add_parser("status", help="show vault status")
    sub_status.add_argument("--service", help="filter by service name")
    sub_status.set_defaults(func=cmd_status)

    sub_list = sub.add_parser("list", help="list secret metadata")
    sub_list.add_argument("--service", help="filter by service name")
    sub_list.set_defaults(func=cmd_list)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
