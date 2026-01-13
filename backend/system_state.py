from typing import Dict, Any

# Global system state shared across modules
global_state: Dict[str, Any] = {
    "SAFE_MODE": False,
    "MAIL_SENDING_PAUSED": False,
    "AGENT_EXECUTION_PAUSED": False,
}

def is_safe_mode() -> bool:
    return global_state["SAFE_MODE"]

def is_mail_paused() -> bool:
    return global_state["MAIL_SENDING_PAUSED"]

def is_agent_paused() -> bool:
    return global_state["AGENT_EXECUTION_PAUSED"]
