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
            return f"❌ {name} is MISSING"
        else:
            return f"⚠️ {name} is MISSING (Optional)"
    
    masked = val[:4] + "*" * (len(val)-8) + val[-4:] if len(val) > 8 else "****"
    return f"✅ {name} is set: {masked}"

def check_stripe(key):
    if not key: return "❌ No Stripe Key to test"
    if not key.startswith("sk_live_"):
        return "❌ STRIPE_SECRET_KEY does not start with 'sk_live_'"

    try:
        headers = {"Authorization": f"Bearer {key}"}
        r = requests.get("https://api.stripe.com/v1/account", headers=headers)
        if r.status_code == 200:
            acc = r.json()
            return f"✅ Stripe API Key is VALID. Account: {acc.get('email')} ({acc.get('id')})"
        elif r.status_code == 401:
            return f"❌ Stripe API Key is EXPIRED/INVALID (401). Message: {r.json().get('error', {}).get('message')}"
        else:
            return f"⚠️ Stripe API returned status {r.status_code}"
    except Exception as e:
        return f"❌ Failed to connect to Stripe: {e}"

def check_files():
    results = []
    files = ["command_center.html", "backend/main_server.py", ".env"]
    for f in files:
        if os.path.exists(f):
            size = os.path.getsize(f)
            results.append(f"✅ File exists: {f} ({size} bytes)")
        else:
            results.append(f"❌ File MISSING: {f}")
    return "\n".join(results)

def main():
    output = []
    output.append("--- 🔍 STARTUP DIAGNOSTIC TOOL ---")
    
    if os.path.exists(".env"):
        load_dotenv()
        output.append("✅ .env file found loaded.")
    else:
        output.append("❌ .env file NOT FOUND!")
    
    stripe_key = os.getenv("STRIPE_SECRET_KEY")
    output.append(check_env_var("STRIPE_SECRET_KEY"))
    output.append(check_env_var("GOOGLE_API_KEY"))
    output.append(check_env_var("SMTP_EMAIL"))
    output.append(check_env_var("SMTP_PASSWORD"))
    output.append(check_env_var("FALLAT_API_TOKEN"))

    if stripe_key:
        output.append(check_stripe(stripe_key))

    if check_port(8000):
        output.append("⚠️ Port 8000 is currently IN USE (Server might already be running).")
    else:
        output.append("✅ Port 8000 is FREE.")

    output.append(check_files())
    output.append("--- DIAGNOSTIC COMPLETE ---")

    final_output = "\n".join(output)
    print(final_output)
    
    with open("diagnostic_results.md", "w", encoding="utf-8") as f:
        f.write(final_output)

if __name__ == "__main__":
    main()
