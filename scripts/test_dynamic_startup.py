import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.ewc.revenue_orchestrator import run_earnings_workflow_once

# Configure logging to stdout
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("RevenueOrchestrator")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)

async def main():
    print("--- Test Run 1 ---")
    await run_earnings_workflow_once()
    print("\n--- Test Run 2 ---")
    await run_earnings_workflow_once()

if __name__ == "__main__":
    asyncio.run(main())
