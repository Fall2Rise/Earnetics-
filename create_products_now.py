import os
import stripe
from dotenv import load_dotenv

load_dotenv(override=True)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

products = [
    {"name": "24/7 AI Sales Agent", "price": 29700, "desc": "Rent a pre-configured AI Sales Agent to handle leads instantly."},
    {"name": "AI Content Engine", "price": 9700, "desc": "30 days of social content generated automatically every month."},
    {"name": "Automation Vault", "price": 4700, "desc": "Access to our library of best prompts, workflows, and templates."}
]

print("=== CREATING STRIPE PRODUCTS ===\n")

for p in products:
    try:
        print(f"Creating: {p['name']}...")
        
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
        
        print(f"✅ SUCCESS: {p['name']}")
        print(f"   Product ID: {product.id}")
        print(f"   Price ID: {price.id}")
        print(f"   Amount: ${p['price']/100:.2f}/mo\n")
        
    except Exception as e:
        print(f"❌ ERROR creating {p['name']}: {e}\n")

print("=== DONE ===")
