# backend/tools/handlers/stripe_tools.py
from __future__ import annotations

from typing import Any, Dict

try:
    import stripe
except ImportError:
    stripe = None


def stripe_get_account(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool: READ_ONLY (payments.read equivalent)
    Returns basic Stripe account info for diagnostics.
    Requires STRIPE_SECRET_KEY env var already configured in your system.
    """
    if stripe is None:
        return {"error": "stripe library not installed", "status": "unavailable"}
    
    # Optional: allow passing api_key explicitly ONLY if your vault injects it.
    api_key = args.get("api_key")
    if api_key:
        stripe.api_key = api_key
    elif not stripe.api_key:
        # Try to get from environment
        import os
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
    
    if not stripe.api_key:
        return {"error": "Stripe API key not configured", "status": "unavailable"}

    try:
        acct = stripe.Account.retrieve()
        return {
            "id": acct.get("id"),
            "country": acct.get("country"),
            "default_currency": acct.get("default_currency"),
            "charges_enabled": acct.get("charges_enabled"),
            "payouts_enabled": acct.get("payouts_enabled"),
            "details_submitted": acct.get("details_submitted"),
            "business_type": acct.get("business_type"),
            "status": "success",
        }
    except Exception as e:
        return {"error": str(e), "status": "error"}


def stripe_get_recent_payments(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool: READ_ONLY
    Get recent Stripe payments/charges.
    """
    if stripe is None:
        return {"error": "stripe library not installed", "status": "unavailable"}
    
    api_key = args.get("api_key")
    if api_key:
        stripe.api_key = api_key
    elif not stripe.api_key:
        import os
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
    
    if not stripe.api_key:
        return {"error": "Stripe API key not configured", "status": "unavailable"}

    limit = int(args.get("limit", 10))
    try:
        charges = stripe.Charge.list(limit=limit)
        payments = []
        for charge in charges.data:
            payments.append({
                "id": charge.id,
                "amount": charge.amount / 100,  # Convert from cents
                "currency": charge.currency,
                "status": charge.status,
                "created": charge.created,
                "customer": charge.customer,
            })
        return {
            "payments": payments,
            "count": len(payments),
            "status": "success",
        }
    except Exception as e:
        return {"error": str(e), "status": "error"}


def stripe_create_product(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool: PAYMENTS
    Create a Stripe product.
    """
    if stripe is None:
        return {"error": "stripe library not installed", "status": "unavailable"}
    
    api_key = args.get("api_key")
    if api_key:
        stripe.api_key = api_key
    elif not stripe.api_key:
        import os
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
    
    if not stripe.api_key:
        return {"error": "Stripe API key not configured", "status": "unavailable"}

    name = args.get("name") or args.get("product_name")
    description = args.get("description") or args.get("product_description") or name
    price = float(args.get("price") or args.get("unit_amount") or 0)
    
    if not name:
        return {"error": "Product name is required", "status": "error"}
    
    try:
        # Create product
        product = stripe.Product.create(
            name=name,
            description=description,
        )
        
        # Create price if price > 0
        price_obj = None
        if price > 0:
            price_obj = stripe.Price.create(
                product=product.id,
                unit_amount=int(price * 100),  # Convert to cents
                currency=args.get("currency", "usd"),
            )
        
        return {
            "product_id": product.id,
            "product_name": product.name,
            "price_id": price_obj.id if price_obj else None,
            "price": price,
            "status": "success",
        }
    except Exception as e:
        return {"error": str(e), "status": "error"}
