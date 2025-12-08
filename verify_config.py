from dotenv import load_dotenv
import os

load_dotenv(override=True)

with open('config_status.txt', 'w', encoding='utf-8') as f:
    f.write("=== CONFIGURATION STATUS ===\n\n")
    
    google = os.getenv('GOOGLE_API_KEY')
    f.write(f"GOOGLE_API_KEY: {'✅ SET' if google else '❌ MISSING'}\n")
    if google:
        f.write(f"  Value starts with: {google[:10]}...\n")
    
    openrouter = os.getenv('OPENROUTER_API_KEY')
    f.write(f"\nOPENROUTER_API_KEY: {'✅ SET' if openrouter else '❌ MISSING'}\n")
    if openrouter:
        f.write(f"  Value starts with: {openrouter[:10]}...\n")
    
    smtp_email = os.getenv('SMTP_EMAIL')
    smtp_pass = os.getenv('SMTP_PASSWORD')
    f.write(f"\nSMTP_EMAIL: {smtp_email if smtp_email else '❌ MISSING'}\n")
    f.write(f"SMTP_PASSWORD: {'✅ SET' if smtp_pass else '❌ MISSING'}\n")
    if smtp_pass:
        f.write(f"  Length: {len(smtp_pass)} chars (should be 16)\n")

print("Config status written to config_status.txt")
