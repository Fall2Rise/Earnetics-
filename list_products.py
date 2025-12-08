import os
import stripe
from dotenv import load_dotenv

load_dotenv(override=True)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

with open('stripe_products_list.txt', 'w', encoding='utf-8') as f:
    f.write("=== STRIPE PRODUCTS ===\n\n")
    try:
        products = stripe.Product.list(limit=10)
        for p in products.data:
            f.write(f"✅ {p.name}\n")
            # Get price for this product
            prices = stripe.Price.list(product=p.id, limit=1)
            if prices.data:
                price_obj = prices.data[0]
                amount = price_obj.unit_amount / 100
                interval = price_obj.recurring.get('interval', 'N/A') if price_obj.recurring else 'one-time'
                f.write(f"   Price: ${amount:.2f}/{interval}\n")
            f.write(f"   ID: {p.id}\n\n")
        f.write(f"\nTotal: {len(products.data)} products\n")
    except Exception as e:
        f.write(f"Error: {e}\n")

print("Products listed in stripe_products_list.txt")
