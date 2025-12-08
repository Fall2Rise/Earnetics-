import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# List of keys to check (from validate_secrets.py)
CRITICAL_SECRETS = [
    'STRIPE_SECRET_KEY', 'STRIPE_PUBLISHABLE_KEY', 'STRIPE_WEBHOOK_SECRET',
    'SMTP_SERVER', 'SMTP_PORT', 'SMTP_EMAIL', 'SMTP_PASSWORD',
    'LLM_PROVIDER', 'FALLAT_API_TOKEN'
]

OPTIONAL_SECRETS = [
    'TWITTER_API_KEY', 'TWITTER_API_SECRET', 'TWITTER_ACCESS_TOKEN', 'TWITTER_ACCESS_SECRET',
    'SHOPIFY_STORE_URL', 'SHOPIFY_ADMIN_API_TOKEN',
    'AFFILIATE_API_BASE_URL', 'AFFILIATE_API_KEY',
    'OPENAI_API_KEY'
]

with open("env_status.txt", "w") as f:
    f.write("--- Environment Variable Check ---\n")
    f.write("Legend: [OK] = Present, [MISSING] = Not set\n\n")

    f.write("CRITICAL:\n")
    for key in CRITICAL_SECRETS:
        val = os.getenv(key)
        status = "[OK]" if val else "[MISSING]"
        f.write(f"{key}: {status}\n")

    f.write("\nOPTIONAL:\n")
    for key in OPTIONAL_SECRETS:
        val = os.getenv(key)
        status = "[OK]" if val else "[MISSING]"
        f.write(f"{key}: {status}\n")
