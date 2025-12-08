import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.getcwd())

# Load env vars
load_dotenv(override=True)

from backend.stripe_integration import StripePaymentProcessor

def create_mastermind_product():
    print("--- 💳 CREATING STRIPE PRODUCT: AUTOMATION MASTERMIND ---")
    
    api_key = os.getenv("STRIPE_SECRET_KEY")
    if not api_key:
        print("ERROR: STRIPE_SECRET_KEY not found in .env")
        return

    processor = StripePaymentProcessor()
    # Configure manually to ensure key is set
    processor.configure_stripe(api_key)

    try:
        # Creating as a monthly subscription for MRR
        result = processor.create_product_with_price(
            name="Automation Mastermind",
            description="Premium AI Automation Certification & Community Access",
            unit_amount=497.00,
            interval="month"
        )
        print("\n✅ SUCCESS! Product Created.")
        print(f"Product ID: {result['product_id']}")
        print(f"Price ID: {result['price_id']}")
        print(f"Amount: ${result['amount']}/month")
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")

if __name__ == "__main__":
    import traceback
    try:
        with open("stripe_debug.log", "w", encoding="utf-8") as f:
            f.write("Starting script...\n")
            sys.stdout = f
            sys.stderr = f
            create_mastermind_product()
            f.write("Script finished.\n")
    except Exception as e:
        with open("stripe_debug.log", "a", encoding="utf-8") as f:
            f.write(f"CRITICAL FAILURE: {e}\n")
            traceback.print_exc(file=f)
