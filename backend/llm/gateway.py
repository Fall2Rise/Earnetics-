import os
import asyncio
import logging
import time
import hashlib
from typing import Optional, Dict, Any, List

from backend.llm.schemas import LLMRequest, LLMResponse, LLMError
from backend.llm.providers.ollama import OllamaProvider
from backend.llm.router import LLMRouter

logger = logging.getLogger(__name__)

class LLMGateway:
    _instance = None
    _semaphore = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMGateway, cls).__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self.ollama_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        self.provider = OllamaProvider(self.ollama_url)
        self.router = LLMRouter()
        
        # Concurrency control
        max_concurrency = int(os.getenv("LLM_MAX_CONCURRENCY", "2"))
        self._semaphore = asyncio.Semaphore(max_concurrency)
        
        self.retries = int(os.getenv("LLM_RETRIES", "2"))

    @classmethod
    async def chat(cls, 
                   messages: List[Dict[str, str]], 
                   agent_id: str = None, 
                   department: str = None,
                   system_prompt: str = None,
                   temperature: float = 0.7,
                   max_tokens: int = None) -> LLMResponse:
        """
        Public static entry point for Chat.
        """
        gateway = cls()
        request = LLMRequest(
            messages=messages,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            agent_id=agent_id,
            department=department
        )
        return await gateway._process_request(request, mode="chat")

    @classmethod
    async def generate(cls, 
                       prompt: str, 
                       agent_id: str = None, 
                       department: str = None,
                       system_prompt: str = None,
                       temperature: float = 0.7,
                       max_tokens: int = None) -> LLMResponse:
        """
        Public static entry point for Generate.
        """
        gateway = cls()
        request = LLMRequest(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            agent_id=agent_id,
            department=department
        )
        return await gateway._process_request(request, mode="generate")

    async def _process_request(self, request: LLMRequest, mode: str) -> LLMResponse:
        # 1. Routing
        model = self.router.select_model(request.agent_id, request.department)
        
        # 2. Concurrency Control
        async with self._semaphore:
            for attempt in range(self.retries + 1):
                try:
                    # Log attempt (securely)
                    self._log_attempt(request, model, attempt)
                    
                    # 3. Execution
                    if mode == "chat":
                        response = await self.provider.chat(model, request)
                    else:
                        response = await self.provider.generate(model, request)

                    # 4. Success or Retry
                    if response.ok:
                        logger.info(f"LLM Success | Model: {model} | Latency: {response.latency_ms:.0f}ms")
                        return response
                    
                    # If model not found or connection refused, try fallback logic immediately
                    if attempt < self.retries:
                        logger.warning(f"LLM Failed attempt {attempt+1}/{self.retries+1}: {response.error}")
                        # Optional: check fallback model
                        fallback = self.router.get_fallback_model(model)
                        if fallback and fallback != model:
                            logger.info(f"Switching to fallback model: {fallback}")
                            model = fallback
                        await asyncio.sleep(1) # Backoff
                        continue
                    
                    return response

                except Exception as e:
                    logger.error(f"LLM Critical Error: {e}")
                    if attempt == self.retries:
                        return LLMResponse(
                            ok=False,
                            provider="ollama",
                            model=model,
                            mode=mode,
                            content=None,
                            latency_ms=0,
                            error=LLMError(code="CRITICAL_FAILURE", message=str(e))
                        )

    def _log_attempt(self, request: LLMRequest, model: str, attempt: int):
        prompt_len = len(request.prompt) if request.prompt else 0
        if request.messages:
            prompt_len += sum(len(m.get("content", "")) for m in request.messages)
            
        prompt_hash = hashlib.md5(
            (request.prompt or str(request.messages)).encode()
        ).hexdigest()[:8]
        
        logger.info(
            f"LLM Request | Agent: {request.agent_id or 'System'} | "
            f"Model: {model} | Len: {prompt_len} chars | Hash: {prompt_hash} | "
            f"Attempt: {attempt+1}"
        )

    @classmethod
    async def health_check(cls) -> Dict[str, Any]:
        gateway = cls()
        ollama_ok = await gateway.provider.health_check()
        return {
            "ollama_reachable": ollama_ok,
            "base_url": gateway.ollama_url,
            "concurrency_limit": gateway._semaphore._value
        }
