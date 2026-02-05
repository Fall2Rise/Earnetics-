import os
import json
import time
import logging
import httpx
from typing import Dict, Any, Optional

from backend.llm.schemas import LLMRequest, LLMResponse, LLMError, LLMProvider, LLMMode

logger = logging.getLogger(__name__)

class OllamaProvider:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        
    async def chat(self, model: str, request: LLMRequest) -> LLMResponse:
        """
        Send a chat request to Ollama.
        Fallback to generate if chat fails with 404 (handled by gateway logic usually, 
        but we implement the raw call here).
        """
        start_time = time.time()
        url = f"{self.base_url}/api/chat"
        
        # Prepare messages
        messages = request.messages or []
        if request.prompt and not messages:
            if request.system_prompt:
                messages.append({"role": "system", "content": request.system_prompt})
            messages.append({"role": "user", "content": request.prompt})
        elif request.system_prompt and messages and messages[0]["role"] != "system":
             messages.insert(0, {"role": "system", "content": request.system_prompt})

        payload = {
            "model": model,
            "messages": messages,
            "stream": request.stream,
            "options": {
                "temperature": float(request.temperature),
            }
        }
        
        if request.max_tokens:
            payload["options"]["num_predict"] = int(request.max_tokens)
        if request.stop:
            payload["options"]["stop"] = request.stop

        try:
            timeout_val = float(os.getenv("LLM_TIMEOUT_SECONDS", 120))
            async with httpx.AsyncClient(timeout=timeout_val) as client:
                response = await client.post(url, json=payload)
                
                # Check for 404 (endpoint not found)
                if response.status_code == 404:
                    return await self.generate(model, request)
                
                response.raise_for_status()
                data = response.json()
                
                content = data.get("message", {}).get("content", "")
                latency = (time.time() - start_time) * 1000
                
                return LLMResponse(
                    ok=True,
                    provider=LLMProvider.OLLAMA,
                    model=model,
                    mode=LLMMode.CHAT,
                    content=content,
                    latency_ms=latency,
                    raw=data
                )

        except Exception as e:
            latency = (time.time() - start_time) * 1000
            return LLMResponse(
                ok=False,
                provider=LLMProvider.OLLAMA,
                model=model,
                mode=LLMMode.CHAT,
                content=None,
                latency_ms=latency,
                error=LLMError(
                    code="OLLAMA_CHAT_ERROR",
                    message=str(e),
                    details={"url": url}
                )
            )

    async def generate(self, model: str, request: LLMRequest) -> LLMResponse:
        """
        Fallback generate request (raw completion).
        """
        start_time = time.time()
        url = f"{self.base_url}/api/generate"
        
        # Combine messages into single prompt if needed
        full_prompt = request.prompt or ""
        if request.messages:
            full_prompt = "\n".join([f"{m['role']}: {m['content']}" for m in request.messages])
            
        payload = {
            "model": model,
            "prompt": full_prompt,
            "system": request.system_prompt,
            "stream": request.stream,
            "options": {
                "temperature": float(request.temperature),
            }
        }
        
        if request.max_tokens:
            payload["options"]["num_predict"] = int(request.max_tokens)

        try:
            timeout_val = float(os.getenv("LLM_TIMEOUT_SECONDS", 120))
            async with httpx.AsyncClient(timeout=timeout_val) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                
                content = data.get("response", "")
                latency = (time.time() - start_time) * 1000
                
                return LLMResponse(
                    ok=True,
                    provider=LLMProvider.OLLAMA,
                    model=model,
                    mode=LLMMode.GENERATE,
                    content=content,
                    latency_ms=latency,
                    raw=data
                )

        except Exception as e:
            latency = (time.time() - start_time) * 1000
            return LLMResponse(
                ok=False,
                provider=LLMProvider.OLLAMA,
                model=model,
                mode=LLMMode.GENERATE,
                content=None,
                latency_ms=latency,
                error=LLMError(
                    code="OLLAMA_GENERATE_ERROR",
                    message=str(e),
                    details={"url": url}
                )
            )

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False
