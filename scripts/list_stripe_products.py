import os
import stripe
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

print("--- CHECKING STRIPE PRODUCTS ---")
try:
    products = stripe.Product.list(limit=10)
    for p in products.data:
        print(f"Product: {p.name} (ID: {p.id})")
except Exception as e:
    print(f"Error: {e}")
