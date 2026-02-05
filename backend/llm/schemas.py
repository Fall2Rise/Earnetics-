from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from enum import Enum

class LLMProvider(str, Enum):
    OLLAMA = "ollama"
    OPENAI = "openai"  # Reserved for future local/compatible endpoints

class LLMMode(str, Enum):
    CHAT = "chat"
    GENERATE = "generate"

@dataclass
class LLMError:
    code: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LLMResponse:
    ok: bool
    provider: str
    model: str
    mode: str
    content: Optional[str]
    latency_ms: float
    error: Optional[LLMError] = None
    raw: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "provider": self.provider,
            "model": self.model,
            "mode": self.mode,
            "latency_ms": self.latency_ms,
            "content": self.content,
            "error": {
                "code": self.error.code,
                "message": self.error.message,
                "details": self.error.details
            } if self.error else None
        }

@dataclass
class LLMRequest:
    prompt: Optional[str] = None
    messages: Optional[List[Dict[str, str]]] = None
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stop: Optional[List[str]] = None
    stream: bool = False
    
    # Context for logging/routing
    agent_id: Optional[str] = None
    department: Optional[str] = None
    request_id: Optional[str] = None
