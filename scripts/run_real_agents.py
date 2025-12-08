import asyncio
import os
import sys
from pathlib import Path

# Ensure backend package imports resolve
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.real_ai_agents import run_real_autonomous_cycle, get_real_agent_status

async def main():
    print("\n🤖 AI REVENUE COMMAND CENTER - REAL AGENT MODE")
    print("==================================================")
    
    # Check Real Mode
    real_mode = os.getenv("FALLAT_REAL_MODE", "False").lower() == "true"
    print(f"REAL MODE: {'ENABLED ✅' if real_mode else 'DISABLED ❌ (Simulation)'}")
    if not real_mode:
        print("To enable real actions, set FALLAT_REAL_MODE=True")
    
    print("\nInitializing Agents...")
    status = get_real_agent_status()
    print(f"✅ {status['total_agents']} Agents Online")
    print(f"   - Executive: {status['divisions']['Executive Board']}")
    print(f"   - Finance: {status['divisions']['Finance & Revenue']}")
    print(f"   - Tech: {status['divisions']['Tech & Infrastructure']}")
    
    print("\nStarting Autonomous Loop (Press Ctrl+C to stop)...")
    print("-" * 50)
    
    try:
        while True:
            print("\n[🔄 CYCLE START] Running autonomous decision cycle...")
            result = await run_real_autonomous_cycle()
            
            summary = result.get("summary", {})
            print(f"   > Decisions: {len(summary.get('key_decisions', []))}")
            print(f"   > Confidence: {summary.get('overall_confidence', 0):.1f}%")
            
            actions = summary.get("priority_actions", [])
            if actions:
                print(f"   > ⚡ ACTIONS REQUIRED: {len(actions)}")
                for action in actions:
                    print(f"     - {action.get('agent')}: {action.get('analysis')[:80]}...")
            else:
                print("   > No immediate actions required.")
                
            await asyncio.sleep(10) # Wait 10 seconds between cycles
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping Autonomous Agents...")

if __name__ == "__main__":
    asyncio.run(main())
