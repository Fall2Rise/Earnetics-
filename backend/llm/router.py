import os
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# Agents that require higher intelligence/reasoning
STRATEGIST_AGENTS = {
    "akasha", "atlas", "strategos", "quant", "veridia", 
    "executive", "strategy", "genesis", "revenue_loop"
}

class LLMRouter:
    def __init__(self):
        self.worker_model = os.getenv("OLLAMA_WORKER_MODEL", "llama3.1:8b")
        self.strategist_model = os.getenv("OLLAMA_STRATEGIST_MODEL", "qwen2.5:14b")
        self.fallback_enabled = os.getenv("LLM_FALLBACK_TO_WORKER", "true").lower() == "true"

    def select_model(self, agent_id: str = None, department: str = None) -> str:
        """
        Select the appropriate model based on agent identity or department.
        """
        # Clean inputs
        agent_id = (agent_id or "").lower()
        department = (department or "").lower()

        # Check if high-tier model is required
        if agent_id in STRATEGIST_AGENTS or department in STRATEGIST_AGENTS:
            return self.strategist_model
        
        # Check specific keywords in department
        if any(x in department for x in ["executive", "strategy", "intelligence", "analysis"]):
            return self.strategist_model

        # Default to worker model
        return self.worker_model

    def get_fallback_model(self, current_model: str) -> str | None:
        """
        Get fallback model if the current one fails.
        """
        if not self.fallback_enabled:
            return None
            
        # If we failed on strategist, try worker
        if current_model == self.strategist_model:
            return self.worker_model
            
        return None
