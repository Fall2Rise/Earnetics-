#!/usr/bin/env python3
"""Test Google API Key connectivity."""

import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ GOOGLE_API_KEY not found in .env")
    exit(1)

print(f"✅ Found API Key: {api_key[:10]}...")

# Test the API
try:
    import google.generativeai as genai
    
    genai.configure(api_key=api_key)
    
    # List available models
    print("\n📋 Testing API connectivity...")
    models = genai.list_models()
    
    gemini_models = [m for m in models if 'gemini' in m.name.lower()]
    
    if gemini_models:
        print(f"✅ API KEY WORKS! Found {len(gemini_models)} Gemini models:")
        for model in gemini_models[:3]:
            print(f"   - {model.name}")
    else:
        print("⚠️  API works but no Gemini models found")
        
except Exception as e:
    print(f"❌ API TEST FAILED: {e}")
    print("\nPossible issues:")
    print("1. Generative Language API not enabled in Google Cloud")
    print("2. API key restrictions blocking access")
    print("3. Billing not enabled")
