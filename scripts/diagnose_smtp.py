#!/usr/bin/env python3
"""Diagnose SMTP password issues."""

import os
from dotenv import load_dotenv

load_dotenv()

password = os.getenv("SMTP_PASSWORD", "")

print("=== SMTP PASSWORD DIAGNOSTIC ===\n")

# Check if password exists
if not password:
    print("❌ PROBLEM: SMTP_PASSWORD is empty in .env file")
    print("\nSOLUTION: Add the App Password to your .env file")
    exit(1)

print(f"✅ Password found in .env")
print(f"   Length: {len(password)} characters")
print(f"   First 4 chars: {password[:4]}...")
print(f"   Last 4 chars: ...{password[-4:]}")

# Check for common issues
issues = []

if " " in password:
    issues.append("⚠️  Contains SPACES - App passwords should have no spaces")
    
if len(password) != 16:
    issues.append(f"⚠️  Length is {len(password)}, should be exactly 16 characters")
    
if password.startswith('"') or password.startswith("'"):
    issues.append("⚠️  Has quotes around it - remove quotes from .env file")

if not password.replace(" ", "").isalnum():
    issues.append("⚠️  Contains special characters - App passwords are only letters/numbers")

if issues:
    print("\n❌ ISSUES FOUND:")
    for issue in issues:
        print(f"   {issue}")
    print("\n💡 FIX:")
    print("   1. Open .env file")
    print("   2. Find line: SMTP_PASSWORD=...")
    print("   3. Replace with: SMTP_PASSWORD=<your-16-char-password>")
    print("   4. Make sure there are NO spaces, NO quotes")
    print("   5. Save the file")
else:
    print("\n✅ Password format looks correct")
    print("\n🔍 Testing SMTP connection...")
    
    import smtplib
    server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    port = int(os.getenv("SMTP_PORT", "587"))
    email = os.getenv("SMTP_EMAIL", "")
    
    try:
        smtp = smtplib.SMTP(server, port, timeout=10)
        smtp.starttls()
        smtp.login(email, password)
        smtp.quit()
        print("✅ SUCCESS! SMTP login works!")
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ AUTHENTICATION FAILED: {e}")
        print("\n💡 POSSIBLE CAUSES:")
        print("   1. Wrong App Password - generate a NEW one")
        print("   2. Account locked - visit: https://accounts.google.com/DisplayUnlockCaptcha")
        print("   3. Less secure apps blocked - use App Password instead")
    except Exception as e:
        print(f"❌ CONNECTION ERROR: {e}")
