#!/usr/bin/env python3
"""Quick system verification - prints results directly to console."""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("FINAL PRE-LAUNCH VERIFICATION")
print("=" * 60)

# 1. Check Critical Environment Variables
print("\n[1] ENVIRONMENT VARIABLES:")
critical_vars = {
    "STRIPE_SECRET_KEY": os.getenv("STRIPE_SECRET_KEY", ""),
    "SMTP_PASSWORD": os.getenv("SMTP_PASSWORD", ""),
    "SMTP_EMAIL": os.getenv("SMTP_EMAIL", ""),
    "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY", ""),
}

for key, val in critical_vars.items():
    status = "OK" if val and len(val) > 5 else "MISSING"
    masked = f"{val[:8]}..." if len(val) > 8 else "EMPTY"
    print(f"  {key}: [{status}] {masked if status == 'OK' else 'NOT SET'}")

# 2. Check Critical Files
print("\n[2] CRITICAL FILES:")
critical_files = [
    "backend/main_server.py",
    "backend/services/content_engine_service.py",
    "backend/services/video_factory.py",
    "backend/services/email_service.py",
    "backend/api/campaign_router.py",
    "backend/api/stripe_router.py",
    "backend/api/content_engine_router.py",
    ".env",
]

for filepath in critical_files:
    exists = os.path.exists(filepath)
    status = "OK" if exists else "MISSING"
    print(f"  {filepath}: [{status}]")

# 3. Check Python Dependencies
print("\n[3] PYTHON DEPENDENCIES:")
deps = ["fastapi", "uvicorn", "stripe", "moviepy", "gtts", "python-dotenv"]
for dep in deps:
    try:
        __import__(dep.replace("-", "_"))
        print(f"  {dep}: [OK]")
    except ImportError:
        print(f"  {dep}: [MISSING]")

# 4. Check Directories
print("\n[4] REQUIRED DIRECTORIES:")
dirs = ["static", "static/generated_videos", "backend/services", "backend/api"]
for d in dirs:
    exists = os.path.isdir(d)
    status = "OK" if exists else "MISSING"
    print(f"  {d}: [{status}]")

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)
