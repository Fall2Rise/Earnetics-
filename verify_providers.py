import os
import sys
import asyncio
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.getcwd())

# Load env vars
load_dotenv(override=True)

from backend.llm_client import get_llm_client

async def test_provider(name, provider_id):
    print(f"\nTesting {name} ({provider_id})...")
    client = get_llm_client(provider=provider_id)
    
    if not client:
        print(f"❌ FAILED: Could not initialize client for {name}")
        return
        
    if not client.configured:
        print(f"❌ FAILED: Client not configured. Error: {client.init_error}")
        return
        
    print(f"✅ Client initialized. Model: {client.model}")
    
    # Try a simple generation
    try:
        print("  Sending request...")
        response = await client.generate("You are a helpful assistant.", "Say 'Hello' and nothing else.")
        print(f"  Response: {response.content}")
        print(f"✅ SUCCESS: {name} is working.")
    except Exception as e:
        print(f"❌ FAILED: Generation error: {e}")

class Logger:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "w", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

async def main():
    sys.stdout = Logger("provider_verification.log")
    print("--- 🧠 VERIFYING NEW LLM PROVIDERS ---")
    
    # Check if keys are present first
    keys = {
        "openrouter": "OPENROUTER_API_KEY",
        "google": "GOOGLE_API_KEY",
        "grok": "GROK_API_KEY"
    }
    
    for provider, key_name in keys.items():
        if not os.getenv(key_name):
            print(f"⚠️  SKIPPING {provider}: {key_name} is missing in .env")
            continue
        await test_provider(provider.upper(), provider)

if __name__ == "__main__":
    asyncio.run(main())
