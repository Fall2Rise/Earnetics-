"""Validate presence of critical environment variables for Fallat CrewAI."""

from __future__ import annotations

import os
from typing import Dict, List

from dotenv import load_dotenv

load_dotenv()

CRITICAL_SECRETS: Dict[str, List[str]] = {
    'stripe': ['STRIPE_SECRET_KEY', 'STRIPE_PUBLISHABLE_KEY', 'STRIPE_WEBHOOK_SECRET'],
    'email': ['SMTP_SERVER', 'SMTP_PORT', 'SMTP_EMAIL', 'SMTP_PASSWORD'],
    'llm': ['LLM_PROVIDER'],
    'core': ['FALLAT_API_TOKEN'],
}

OPTIONAL_SECRETS: Dict[str, List[str]] = {
    'twitter': ['TWITTER_API_KEY', 'TWITTER_API_SECRET', 'TWITTER_ACCESS_TOKEN', 'TWITTER_ACCESS_SECRET'],
    'shopify': ['SHOPIFY_STORE_URL', 'SHOPIFY_ADMIN_API_TOKEN'],
    'affiliate': ['AFFILIATE_API_BASE_URL', 'AFFILIATE_API_KEY'],
}

def _check_keys(label: str, keys: List[str]) -> Dict[str, str]:
    report: Dict[str, str] = {}
    for key in keys:
        report[key] = 'present' if os.getenv(key) else 'missing'
    return {label: report}

def validate() -> Dict[str, Dict[str, str]]:
    status: Dict[str, Dict[str, str]] = {}
    for label, keys in CRITICAL_SECRETS.items():
        status.update(_check_keys(label, keys))
    for label, keys in OPTIONAL_SECRETS.items():
        status.update(_check_keys(label, keys))
    return status

def main() -> None:
    status = validate()
    missing_critical = [
        key
        for label, keys in CRITICAL_SECRETS.items()
        for key in keys
        if not os.getenv(key)
    ]
    print('Secret validation summary:')
    print()
    for label, report in status.items():
        print(f'[{label}]')
        for key, presence in report.items():
            print(f'  {key}: {presence}')
        print()
    if missing_critical:
        print('!! Missing critical secrets:')
        for key in missing_critical:
            print(f'  - {key}')
        raise SystemExit(1)
    print('All critical secrets present.')

if __name__ == '__main__':
    main()
