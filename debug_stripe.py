import sys
print("Starting debug...")
try:
    import stripe
    print("Stripe imported.")
    from dotenv import load_dotenv
    print("Dotenv imported.")
    import backend.stripe_integration
    print("Backend module imported.")
except Exception as e:
    print(f"Error: {e}")
