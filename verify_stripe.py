import os
import stripe
from dotenv import load_dotenv

load_dotenv(override=True)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

with open('final_stripe_check.txt', 'w', encoding='utf-8') as f:
    f.write("=== YOUR STRIPE PRODUCTS ===\n\n")
    try:
        products = stripe.Product.list(limit=20)
        
        # Expected products
        expected = [
            "Automation Mastermind",
            "24/7 AI Sales Agent", 
            "AI Content Engine",
            "Automation Vault"
        ]
        
        found_names = [p.name for p in products.data]
        
        f.write(f"Total products in Stripe: {len(products.data)}\n\n")
        
        for p in products.data:
            f.write(f"✅ {p.name}\n")
            prices = stripe.Price.list(product=p.id, limit=1)
            if prices.data:
                pr = prices.data[0]
                amount = pr.unit_amount / 100 if pr.unit_amount else 0
                interval = pr.recurring.get('interval') if pr.recurring else 'one-time'
                f.write(f"   ${amount:.2f}/{interval}\n")
            f.write(f"   ID: {p.id}\n\n")
        
        f.write("\n--- VERIFICATION ---\n")
        for expected_name in expected:
            if expected_name in found_names:
                f.write(f"✅ {expected_name}: FOUND\n")
            else:
                f.write(f"❌ {expected_name}: MISSING\n")
                
    except Exception as e:
        f.write(f"ERROR: {e}\n")

print("Done")
