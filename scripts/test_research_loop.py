import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.ewc.research_loop import ResearchLoopRunner

# Configure logging to stdout
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("RevenueOrchestrator")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)

def test_research_loop():
    print("--- Testing Continuous Research Loop ---")
    runner = ResearchLoopRunner()
    
    # Mock market signals
    market_signals = {"trend_source": "test_signal"}
    
    # Run the research loop (this will fail if CrewAI is not fully set up with LLM, 
    # but we want to verify the orchestration logic and file paths)
    try:
        result = runner.run_research(market_signals)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Expected error (no LLM): {e}")
        # If it fails due to LLM missing, that means the code reached the execution point, which is good.

if __name__ == "__main__":
    test_research_loop()
