import os
import stripe
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def create_product(name, price_in_cents, description):
    print(f"\nCreating product: {name}...")
    try:
        product = stripe.Product.create(
            name=name,
            description=description,
        )
        
        price = stripe.Price.create(
            product=product.id,
            unit_amount=price_in_cents,
            currency="usd",
            recurring={"interval": "month"},
        )
        
        print(f"✅ SUCCESS: Created '{name}'")
        print(f"   - Product ID: {product.id}")
        print(f"   - Price ID:   {price.id}")
        print(f"   - Amount:     ${price_in_cents / 100:.2f}/mo")
        return True
    except Exception as e:
        print(f"❌ FAILED: Could not create '{name}'. Error: {e}")
        return False

if __name__ == "__main__":
    with open("revenue_creation_result.txt", "w", encoding="utf-8") as f:
        f.write("--- ADDING NEW REVENUE STREAMS TO STRIPE ---\n")
        
        if not stripe.api_key:
            f.write("❌ ERROR: STRIPE_SECRET_KEY not found in .env\n")
            exit(1)

        products = [
            {
                "name": "24/7 AI Sales Agent",
                "price": 29700, # $297.00
                "desc": "Rent a pre-configured AI Sales Agent to handle leads instantly."
            },
            {
                "name": "AI Content Engine",
                "price": 9700,  # $97.00
                "desc": "30 days of social content generated automatically every month."
            },
            {
                "name": "Automation Vault",
                "price": 4700,  # $47.00
                "desc": "Access to our library of best prompts, workflows, and templates."
            }
        ]

        success_count = 0
        for p in products:
            f.write(f"\nCreating product: {p['name']}...\n")
            try:
                product = stripe.Product.create(
                    name=p["name"],
                    description=p["desc"],
                )
                
                price = stripe.Price.create(
                    product=product.id,
                    unit_amount=p["price"],
                    currency="usd",
                    recurring={"interval": "month"},
                )
                
                f.write(f"✅ SUCCESS: Created '{p['name']}'\n")
                f.write(f"   - Product ID: {product.id}\n")
                f.write(f"   - Price ID:   {price.id}\n")
                f.write(f"   - Amount:     ${p['price'] / 100:.2f}/mo\n")
                success_count += 1
            except Exception as e:
                f.write(f"❌ FAILED: Could not create '{p['name']}'. Error: {e}\n")
                
        f.write(f"\n--- DONE: {success_count}/{len(products)} Products Created ---\n")
