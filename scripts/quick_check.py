import requests
import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("STRIPE_SECRET_KEY", "NOT_FOUND")
print(f"KEY_SUFFIX: {key[-8:] if len(key)>8 else key}")

try:
    r = requests.get("http://localhost:8000")
    print(f"DASHBOARD_STATUS: {r.status_code}")
    if "AI Revenue Command Center" in r.text:
        print("DASHBOARD_CONTENT: VERIFIED")
    else:
        print("DASHBOARD_CONTENT: MISMATCH")
except Exception as e:
    print(f"DASHBOARD_ERROR: {e}")
