"""
Kill Switch: Global toggle to disable all write actions instantly
"""
import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


class KillSwitch:
    """Global kill switch for write operations"""
    
    def __init__(self, config_path: Path = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "internet_gateway.json"
        self.config_path = config_path
        self._load_config()
    
    def _load_config(self):
        """Load kill switch state from config"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                kill_switch_config = config.get("kill_switch", {})
                self._writes_enabled = kill_switch_config.get("writes_enabled", False)
                self._global_enabled = kill_switch_config.get("global_enabled", True)
        except Exception as e:
            print(f"Error loading kill switch config: {e}")
            self._writes_enabled = False
            self._global_enabled = True
    
    def _save_config(self):
        """Save kill switch state to config"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            if "kill_switch" not in config:
                config["kill_switch"] = {}
            
            config["kill_switch"]["writes_enabled"] = self._writes_enabled
            config["kill_switch"]["global_enabled"] = self._global_enabled
            config["kill_switch"]["last_updated"] = datetime.utcnow().isoformat()
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving kill switch config: {e}")
    
    def is_write_allowed(self) -> bool:
        """Check if write operations are allowed"""
        if not self._global_enabled:
            return True  # If kill switch is disabled, allow writes
        
        return self._writes_enabled
    
    def enable_writes(self) -> bool:
        """Enable write operations"""
        if not self._global_enabled:
            return False  # Cannot enable if kill switch is disabled
        
        self._writes_enabled = True
        self._save_config()
        return True
    
    def disable_writes(self) -> bool:
        """Disable write operations (activate kill switch)"""
        self._writes_enabled = False
        self._save_config()
        return True
    
    def disable_gateway(self) -> bool:
        """Disable entire gateway (most restrictive)"""
        self._global_enabled = False
        self._writes_enabled = False
        self._save_config()
        return True
    
    def enable_gateway(self) -> bool:
        """Enable gateway (but writes may still be disabled)"""
        self._global_enabled = True
        self._save_config()
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get current kill switch status"""
        return {
            "global_enabled": self._global_enabled,
            "writes_enabled": self._writes_enabled,
            "write_actions_allowed": self.is_write_allowed()
        }
