import asyncio
import sys
import os

# Ensure backend package imports resolve
sys.path.append(os.getcwd())

from backend.llm.gateway import LLMGateway

async def test():
    print("\n--- 🧪 Starting LLM Gateway Test (Test Run #2 Fixes) ---\n")
    
    # 1. Health Check
    print("1. Checking Health...")
    health = await LLMGateway.health_check()
    print(f"Health Status: {health}")
    
    if not health["ollama_reachable"]:
        print("❌ Ollama is not reachable! Make sure 'ollama serve' is running.")
        return

    # 2. Worker Model Test
    print("\n2. Testing Worker Model (Fast)...")
    try:
        res = await LLMGateway.chat(
            messages=[{"role": "user", "content": "Say 'Worker Online'."}],
            agent_id="webscraper", # Should route to worker
            max_tokens=20
        )
        print(f"Result: {res.ok}")
        print(f"Model Used: {res.model}")
        print(f"Content: {res.content}")
        print(f"Latency: {res.latency_ms:.2f}ms")
    except Exception as e:
        print(f"❌ Worker Test Failed: {e}")

    # 3. Strategist Model Test
    print("\n3. Testing Strategist Model (Smart)...")
    try:
        res = await LLMGateway.chat(
            messages=[{"role": "user", "content": "Say 'Strategist Online'."}],
            agent_id="akasha", # Should route to strategist
            max_tokens=20
        )
        print(f"Result: {res.ok}")
        print(f"Model Used: {res.model}")
        print(f"Content: {res.content}")
    except Exception as e:
        print(f"❌ Strategist Test Failed: {e}")
    
    # 4. Generate Mode Fallback Test
    print("\n4. Testing Generate Mode...")
    try:
        res = await LLMGateway.generate(
            prompt="Reply with 'Generate Mode Works'",
            agent_id="test_agent",
            max_tokens=20
        )
        print(f"Result: {res.ok}")
        print(f"Content: {res.content}")
    except Exception as e:
        print(f"❌ Generate Mode Test Failed: {e}")

    print("\n--- ✅ Test Complete ---")

if __name__ == "__main__":
    try:
        asyncio.run(test())
    except KeyboardInterrupt:
        print("\nTest cancelled.")
