"""Integration registry metadata for Fallat_CrewAI.

This module enumerates first-party connectors (payments, affiliate, ecommerce)
and reports whether required credentials have been provided via the credential
vault/keyring/environment. It allows the UI to surface which integrations are
ready and which still need configuration.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, Iterable, List, Optional

from backend.credentials_store import has_secret
from backend.audit_log import log_event


@dataclass
class IntegrationDescriptor:
    slug: str
    name: str
    category: str
    required_credentials: List[str]
    optional_credentials: List[str] = field(default_factory=list)
    description: str = ""

    def status(self) -> Dict[str, object]:
        missing_required = [key for key in self.required_credentials if not has_secret(key)]
        missing_optional = [key for key in self.optional_credentials if not has_secret(key)]

        return {
            "slug": self.slug,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "required_credentials": self.required_credentials,
            "optional_credentials": self.optional_credentials,
            "missing_required": missing_required,
            "missing_optional": missing_optional,
            "ready": not missing_required,
        }


PAYMENT_CONNECTORS: List[IntegrationDescriptor] = [
    IntegrationDescriptor(
        slug="stripe",
        name="Stripe Payments",
        category="payments",
        description="Accept credit card payments, create products and payment links.",
        required_credentials=["STRIPE_SECRET_KEY"],
        optional_credentials=["STRIPE_WEBHOOK_SECRET"],
    ),
    IntegrationDescriptor(
        slug="paypal",
        name="PayPal Commerce",
        category="payments",
        description="Classic PayPal REST integration for digital sales.",
        required_credentials=["PAYPAL_CLIENT_ID", "PAYPAL_CLIENT_SECRET"],
    ),
]

AFFILIATE_CONNECTORS: List[IntegrationDescriptor] = [
    IntegrationDescriptor(
        slug="clickbank",
        name="ClickBank",
        category="affiliate",
        description="Fetch top offers and create tracking links.",
        required_credentials=["CLICKBANK_API_KEY", "CLICKBANK_API_SECRET"],
    ),
    IntegrationDescriptor(
        slug="digistore24",
        name="Digistore24",
        category="affiliate",
        description="Monitor affiliate offers and commissions.",
        required_credentials=["DIGISTORE24_API_KEY"],
    ),
]

ECOMMERCE_CONNECTORS: List[IntegrationDescriptor] = [
    IntegrationDescriptor(
        slug="shopify",
        name="Shopify Store",
        category="ecommerce",
        description="Manage product listings and orders for Shopify stores.",
        required_credentials=["SHOPIFY_STORE_URL", "SHOPIFY_ADMIN_API_TOKEN"],
    ),
    IntegrationDescriptor(
        slug="gumroad",
        name="Gumroad",
        category="ecommerce",
        description="Create and manage digital product listings on Gumroad.",
        required_credentials=["GUMROAD_ACCESS_TOKEN"],
    ),
]

ALL_CONNECTORS: List[IntegrationDescriptor] = PAYMENT_CONNECTORS + AFFILIATE_CONNECTORS + ECOMMERCE_CONNECTORS


def iter_connectors(category: Optional[str] = None) -> Iterable[IntegrationDescriptor]:
    for connector in ALL_CONNECTORS:
        if category and connector.category != category:
            continue
        yield connector


def summarize_connectors(category: Optional[str] = None) -> List[Dict[str, object]]:
    return [connector.status() for connector in iter_connectors(category)]


def connectors_by_slug(slug: str) -> Optional[Dict[str, object]]:
    for connector in ALL_CONNECTORS:
        if connector.slug == slug:
            return connector.status()
    return None
