import os
import smtplib
from dotenv import load_dotenv

load_dotenv(override=True)

print("--- DEBUGGING EMAIL CONNECTION ---")
host = os.getenv("SMTP_SERVER")
port = os.getenv("SMTP_PORT")
user = os.getenv("SMTP_EMAIL")
password = os.getenv("SMTP_PASSWORD")

print(f"Host: {host}")
print(f"Port: {port}")
print(f"User: {user}")
print(f"Pass: {'******' if password else 'None'}")

if not all([host, port, user, password]):
    print("❌ MISSING CREDENTIALS")
else:
    try:
        print("Attempting connection...")
        server = smtplib.SMTP(host, int(port))
        server.starttls()
        server.login(user, password)
        server.quit()
        print("✅ SUCCESS: Connected to SMTP server.")
    except Exception as e:
        print(f"❌ FAILED: {e}")
