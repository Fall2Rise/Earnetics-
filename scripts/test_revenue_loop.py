#!/usr/bin/env python3
"""
Integration test for the Revenue Loop Orchestrator.
"""
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from backend.ewc.revenue_orchestrator import run_earnings_workflow_once

async def test_revenue_loop():
    load_dotenv(override=True)
    print("🚀 Testing Revenue Loop Orchestrator...")
    
    try:
        results = await run_earnings_workflow_once()
        print("\n✅ Workflow Completed Successfully!")
        print("-" * 60)
        import json
        print(json.dumps(results, indent=2, default=str))
        print("-" * 60)
        
        # Basic assertions
        assert "rnd" in results, "Missing R&D result"
        assert "strategy" in results, "Missing Strategy result"
        assert "product" in results, "Missing Product result"
        assert "content" in results, "Missing Content result"
        assert "email" in results, "Missing Email result"
        assert "campaign" in results, "Missing Campaign result"
        
        print("✅ All department outputs verified.")
        
    except Exception as e:
        print(f"\n❌ Workflow Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_revenue_loop())
