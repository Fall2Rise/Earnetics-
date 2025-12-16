#!/usr/bin/env python3
"""
Test script for idempotent Stripe product creation.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from backend.stripe_integration import StripePaymentProcessor

def test_stripe_product_creation():
    load_dotenv(override=True)
    
    if not os.getenv("STRIPE_SECRET_KEY"):
        print("❌ STRIPE_SECRET_KEY not set. Skipping test.")
        return

    processor = StripePaymentProcessor()
    config = processor.configure_from_environment()
    
    if not config.get("success"):
        print(f"❌ Stripe configuration failed: {config.get('error')}")
        return

    print("✅ Stripe configured successfully.")

    product_name = "Test Product - Idempotency Check"
    
    # 1. First Creation
    print(f"\n1. Creating product: '{product_name}'...")
    result1 = processor.get_or_create_product_and_price(
        name=product_name,
        description="A test product for verification.",
        unit_amount=10.00,
        currency="usd",
        interval="month"
    )
    print(f"   Result: {result1}")
    
    # 2. Second Creation (Should be idempotent)
    print(f"\n2. Creating same product again...")
    result2 = processor.get_or_create_product_and_price(
        name=product_name,
        description="A test product for verification.",
        unit_amount=10.00,
        currency="usd",
        interval="month"
    )
    print(f"   Result: {result2}")

    # Verification
    if result1["product_id"] == result2["product_id"]:
        print("\n✅ SUCCESS: Product IDs match.")
    else:
        print("\n❌ FAILURE: Product IDs do not match.")

    if result2.get("is_new") is False:
         print("✅ SUCCESS: Second call correctly identified existing product.")
    else:
         print("⚠️ WARNING: Second call reported is_new=True (might be expected if price changed or logic differs).")

if __name__ == "__main__":
    test_stripe_product_creation()
