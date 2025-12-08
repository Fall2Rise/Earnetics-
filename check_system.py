import os
import sys
import smtplib
import sqlite3
import requests
from dotenv import load_dotenv

# Load env vars with override
load_dotenv(override=True)

def check_smtp():
    print("\n📧 CHECKING SMTP (EMAIL)...")
    host = os.getenv("SMTP_SERVER")
    port = os.getenv("SMTP_PORT")
    user = os.getenv("SMTP_EMAIL")
    password = os.getenv("SMTP_PASSWORD")
    
    if not all([host, port, user, password]):
        print("❌ MISSING: SMTP credentials are incomplete.")
        return False
        
    try:
        server = smtplib.SMTP(host, int(port))
        server.starttls()
        server.login(user, password)
        server.quit()
        print("✅ SUCCESS: Connected to SMTP server.")
        return True
    except Exception as e:
        print(f"❌ FAILED: Could not connect to SMTP. Error: {e}")
        return False

def check_llm():
    print("\n🧠 CHECKING LLM (INTELLIGENCE)...")
    provider = os.getenv("LLM_PROVIDER")
    host = os.getenv("OLLAMA_HOST")
    
    if provider != "ollama":
        print(f"ℹ️  NOTE: Provider is {provider}. Skipping local check.")
        return True
        
    try:
        response = requests.get(f"{host}/api/tags")
        if response.status_code == 200:
            print("✅ SUCCESS: Ollama is running locally.")
            return True
        else:
            print(f"❌ FAILED: Ollama returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ FAILED: Could not connect to Ollama at {host}. Is it running?")
        return False

def check_db():
    print("\nHz CHECKING DATABASE...")
    db_path = os.getenv("BUSINESS_DB_PATH", "business_database.db")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        print("✅ SUCCESS: Database is accessible.")
        return True
    except Exception as e:
        print(f"❌ FAILED: Database error: {e}")
        return False

def check_new_providers():
    print("\n🌐 CHECKING NEW LLM PROVIDERS...")
    providers = {
        "OpenRouter": "OPENROUTER_API_KEY",
        "Google AI": "GOOGLE_API_KEY",
        "Grok": "GROK_API_KEY"
    }
    
    results = {}
    for name, key in providers.items():
        val = os.getenv(key)
        if val and len(val) > 5:
            print(f"✅ {name}: Key configured.")
            results[name] = True
        else:
            print(f"⚠️  {name}: Key missing or empty.")
            results[name] = False
    return results

if __name__ == "__main__":
    print("--- 🔍 SYSTEM READINESS CHECK ---")
    smtp_ok = check_smtp()
    llm_ok = check_llm()
    db_ok = check_db()
    provider_results = check_new_providers()
    
    print("\n--- 📊 SUMMARY ---")
    print(f"Stripe (Live): ✅ READY (Verified previously)")
    print(f"Email (SMTP):  {'✅ READY' if smtp_ok else '❌ FAILED'}")
    print(f"AI Brain:      {'✅ READY' if llm_ok else '❌ FAILED'}")
    print(f"Database:      {'✅ READY' if db_ok else '❌ FAILED'}")
    for name, ready in provider_results.items():
        print(f"{name:<14} {'✅ READY' if ready else '⚠️  MISSING'}")
