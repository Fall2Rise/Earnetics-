import os
import sys
import socket
import requests
from dotenv import load_dotenv

def check_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def check_env_var(name, required=True):
    val = os.getenv(name)
    if not val:
        if required:
            print(f"❌ {name} is MISSING")
        else:
            print(f"⚠️ {name} is MISSING (Optional)")
        return None
    
    masked = val[:4] + "*" * (len(val)-8) + val[-4:] if len(val) > 8 else "****"
    print(f"✅ {name} is set: {masked}")
    return val

def check_stripe(key):
    if not key: return
    if not key.startswith("sk_live_"):
        print("❌ STRIPE_SECRET_KEY does not start with 'sk_live_'")
        return

    print("🔄 Testing Stripe Key connectivity...")
    try:
        headers = {"Authorization": f"Bearer {key}"}
        r = requests.get("https://api.stripe.com/v1/account", headers=headers)
        if r.status_code == 200:
            print("✅ Stripe API Key is VALID and working.")
            acc = r.json()
            print(f"   Account: {acc.get('email')} ({acc.get('id')})")
        elif r.status_code == 401:
            print("❌ Stripe API Key is EXPIRED or INVALID (401 Unauthorized).")
            print(f"   Message: {r.json().get('error', {}).get('message')}")
        else:
            print(f"⚠️ Stripe API returned status {r.status_code}")
    except Exception as e:
        print(f"❌ Failed to connect to Stripe: {e}")

def check_files():
    files = ["command_center.html", "backend/main_server.py", ".env"]
    for f in files:
        if os.path.exists(f):
            size = os.path.getsize(f)
            print(f"✅ File exists: {f} ({size} bytes)")
        else:
            print(f"❌ File MISSING: {f}")

def main():
    print("--- 🔍 STARTUP DIAGNOSTIC TOOL ---")
    
    # 1. Check .env
    if os.path.exists(".env"):
        load_dotenv()
        print("✅ .env file found loaded.")
    else:
        print("❌ .env file NOT FOUND!")
        return

    # 2. Check Keys
    stripe_key = check_env_var("STRIPE_SECRET_KEY")
    check_env_var("GOOGLE_API_KEY")
    check_env_var("SMTP_EMAIL")
    check_env_var("SMTP_PASSWORD")

    # 3. Validate Stripe
    if stripe_key:
        check_stripe(stripe_key)

    # 4. Check Server Port
    if check_port(8000):
        print("⚠️ Port 8000 is currently IN USE (Server might already be running).")
    else:
        print("✅ Port 8000 is FREE.")

    # 5. Check Critical Files
    check_files()

    print("--- DIAGNOSTIC COMPLETE ---")

if __name__ == "__main__":
    main()
