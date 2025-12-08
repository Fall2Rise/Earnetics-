"""
Final System Audit
Checks all critical components before launch.
"""
import os
import sys
import importlib.util
from pathlib import Path
from dotenv import load_dotenv

# Load env
load_dotenv()

def check_env_var(key, required=True):
    val = os.getenv(key)
    if val:
        print(f"✅ ENV: {key} is set.")
        return True
    else:
        if required:
            print(f"❌ ENV: {key} is MISSING!")
        else:
            print(f"⚠️  ENV: {key} is missing (Optional).")
        return False

def check_module(name):
    if name in sys.modules:
        print(f"✅ DEP: {name} is loaded.")
        return True
    elif importlib.util.find_spec(name) is not None:
        print(f"✅ DEP: {name} is installed.")
        return True
    else:
        print(f"❌ DEP: {name} is NOT installed!")
        return False

def check_dir(path):
    p = Path(path)
    if p.exists() and p.is_dir():
        print(f"✅ DIR: {path} exists.")
        return True
    else:
        try:
            p.mkdir(parents=True, exist_ok=True)
            print(f"✅ DIR: {path} created.")
            return True
        except Exception as e:
            print(f"❌ DIR: {path} missing and could not be created: {e}")
            return False

def check_imagemagick():
    # MoviePy relies on ImageMagick for TextClip. 
    # This is a rough check.
    from moviepy.config import get_setting
    try:
        binary = get_setting("IMAGEMAGICK_BINARY")
        if binary and os.path.exists(binary):
             print(f"✅ BIN: ImageMagick found at {binary}")
        else:
             print(f"⚠️  BIN: ImageMagick NOT found. Text in videos might fail (Audio/BG only).")
    except:
        print(f"⚠️  BIN: Could not check ImageMagick.")

print("--- STARTING FINAL SYSTEM AUDIT ---\n")

# 1. Environment Variables
print("--- Checking Environment ---")
check_env_var("STRIPE_SECRET_KEY")
check_env_var("GOOGLE_API_KEY")
check_env_var("OPENROUTER_API_KEY")
check_env_var("SMTP_EMAIL")
check_env_var("SMTP_PASSWORD")
check_env_var("SMTP_SERVER")

# 2. Dependencies
print("\n--- Checking Dependencies ---")
check_module("fastapi")
check_module("uvicorn")
check_module("stripe")
check_module("google.generativeai")
check_module("moviepy")
check_module("gTTS")

# 3. Directories
print("\n--- Checking Directories ---")
check_dir("static")
check_dir("static/generated_videos")
check_dir("backend/services")
check_dir("backend/api")

# 4. ImageMagick (Special Check)
print("\n--- Checking Binary Dependencies ---")
check_imagemagick()

print("\n--- AUDIT COMPLETE ---")
