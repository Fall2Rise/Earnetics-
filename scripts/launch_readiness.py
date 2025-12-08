#!/usr/bin/env python3
"""Final launch readiness check."""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("🚀 FINAL LAUNCH READINESS CHECK")
print("=" * 70)

all_good = True

# 1. Critical Environment Variables
print("\n[1] CRITICAL CREDENTIALS:")
checks = {
    "STRIPE_SECRET_KEY": os.getenv("STRIPE_SECRET_KEY", ""),
    "SMTP_PASSWORD": os.getenv("SMTP_PASSWORD", ""),
    "SMTP_EMAIL": os.getenv("SMTP_EMAIL", ""),
    "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY", ""),
}

for key, val in checks.items():
    if val and len(val) > 5:
        print(f"  ✅ {key}: Configured")
    else:
        print(f"  ❌ {key}: MISSING")
        all_good = False

# 2. Test SMTP
print("\n[2] EMAIL SERVICE:")
try:
    import smtplib
    server = os.getenv("SMTP_SERVER")
    port = int(os.getenv("SMTP_PORT", "587"))
    email = os.getenv("SMTP_EMAIL")
    password = os.getenv("SMTP_PASSWORD")
    
    smtp = smtplib.SMTP(server, port, timeout=10)
    smtp.starttls()
    smtp.login(email, password)
    smtp.quit()
    print("  ✅ SMTP: Connected and authenticated")
except Exception as e:
    print(f"  ❌ SMTP: Failed - {str(e)[:50]}")
    all_good = False

# 3. Test Stripe
print("\n[3] PAYMENT PROCESSING:")
try:
    import stripe
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
    products = stripe.Product.list(limit=1)
    print(f"  ✅ Stripe: Connected (API working)")
except Exception as e:
    print(f"  ❌ Stripe: Failed - {str(e)[:50]}")
    all_good = False

# 4. Test Google AI
print("\n[4] AI INTELLIGENCE:")
try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    models = list(genai.list_models())
    print(f"  ✅ Google AI: Connected ({len(models)} models available)")
except Exception as e:
    print(f"  ❌ Google AI: Failed - {str(e)[:50]}")
    all_good = False

# 5. Check Critical Files
print("\n[5] CORE SERVICES:")
critical_files = [
    "backend/main_server.py",
    "backend/services/content_engine_service.py",
    "backend/services/video_factory.py",
    "backend/api/campaign_router.py",
    "backend/api/stripe_router.py",
]

for filepath in critical_files:
    if os.path.exists(filepath):
        print(f"  ✅ {filepath}")
    else:
        print(f"  ❌ {filepath}: MISSING")
        all_good = False

print("\n" + "=" * 70)
if all_good:
    print("✅ ALL SYSTEMS GO - READY FOR LAUNCH")
    print("\nRun: .\\start_production.bat")
else:
    print("⚠️  SOME ISSUES DETECTED - Review above")
print("=" * 70)
