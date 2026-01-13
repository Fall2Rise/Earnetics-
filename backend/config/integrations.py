"""Integration requirements configuration."""

from typing import Dict, List

INTEGRATION_REQUIREMENTS: Dict[str, List[str]] = {
    # Stripe is already correct
    "stripe": ["STRIPE_SECRET_KEY", "STRIPE_PUBLISHABLE_KEY"],

    # Matches your .env: SMTP_EMAIL + SMTP_PASSWORD
    "email": ["SMTP_EMAIL", "SMTP_PASSWORD"],

    # Will stay false until you actually add Twitter keys (that's fine for now)
    "social": ["TWITTER_API_KEY", "TWITTER_API_SECRET"],

    # We're using Ollama, not LOCALAI_ENDPOINT
    "llm": ["OLLAMA_HOST"],
}
