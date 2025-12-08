import os
import stripe
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def create_custom_product():
    print("\n💰 CREATE NEW REVENUE STREAM")
    print("-" * 30)
    
    if not stripe.api_key:
        print("❌ ERROR: STRIPE_SECRET_KEY not found in .env")
        return

    try:
        name = input("Product Name (e.g., 'VIP Coaching'): ")
        if not name: return

        desc = input("Description: ")
        
        while True:
            try:
                price_input = input("Price in USD (e.g., 97.00): ")
                price_cents = int(float(price_input) * 100)
                break
            except ValueError:
                print("Invalid price. Please enter a number like 97.00")

        interval = input("Billing Interval (month/year/once) [month]: ").lower() or "month"
        if interval not in ['month', 'year', 'once']:
            interval = 'month'

        print(f"\nCreating '{name}' at ${price_cents/100:.2f}/{interval}...")
        
        # Create Product
        product = stripe.Product.create(
            name=name,
            description=desc,
        )

        # Create Price
        if interval == 'once':
            price = stripe.Price.create(
                product=product.id,
                unit_amount=price_cents,
                currency="usd",
            )
        else:
            price = stripe.Price.create(
                product=product.id,
                unit_amount=price_cents,
                currency="usd",
                recurring={"interval": interval},
            )

        # Log Success
        success_msg = (
            f"✅ SUCCESS: Created '{name}'\n"
            f"   - Product ID: {product.id}\n"
            f"   - Price ID:   {price.id}\n"
            f"   - Amount:     ${price_cents/100:.2f}/{interval}"
        )
        print("\n" + success_msg)
        
        # Append to log file
        with open("revenue_creation_result.txt", "a", encoding="utf-8") as f:
            f.write(f"\n--- Custom Stream Created at {os.getenv('COMPUTERNAME', 'LOCAL')} ---\n")
            f.write(success_msg + "\n")

    except Exception as e:
        print(f"\n❌ FAILED: {e}")

if __name__ == "__main__":
    create_custom_product()
