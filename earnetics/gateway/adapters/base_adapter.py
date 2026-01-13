"""
Base Adapter: Abstract base class for all gateway adapters
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime


class BaseAdapter(ABC):
    """Base class for all gateway adapters"""
    
    def __init__(self, config: Dict[str, Any], credential_vault=None):
        self.config = config
        self.credential_vault = credential_vault
        self.enabled = config.get("enabled", True)
        self.requires_internet = config.get("requires_internet", True)
    
    @abstractmethod
    def execute(self, action: str, params: Dict[str, Any], 
               agent_id: str, role: str) -> Dict[str, Any]:
        """
        Execute adapter action
        
        Returns: {
            "success": bool,
            "data": Any,
            "metadata": Dict,
            "citation": Dict,
            "error": Optional[str]
        }
        """
        pass
    
    def is_enabled(self) -> bool:
        """Check if adapter is enabled"""
        return self.enabled
    
    def requires_internet_connection(self) -> bool:
        """Check if adapter requires internet"""
        return self.requires_internet
    
    def create_citation(self, url: str, retrieved_at: Optional[str] = None) -> Dict[str, Any]:
        """Create citation object for this adapter"""
        if retrieved_at is None:
            retrieved_at = datetime.utcnow().isoformat()
        
        return {
            "source_id": self.__class__.__name__,
            "url": url,
            "retrieved_at": retrieved_at,
            "provenance": f"{self.__class__.__name__}_adapter",
            "confidence": 0.8
        }
