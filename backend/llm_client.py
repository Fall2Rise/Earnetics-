"""Unified LLM client with local (Ollama) default support, no direct cloud-chat SDK dependency."""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx


class LLMClientError(Exception):
    """Base exception for LLM client errors."""


class LLMNotConfiguredError(LLMClientError):
    """Raised when no provider is configured."""


class LLMGenerationError(LLMClientError):
    """Raised when text generation fails."""


@dataclass
class LLMResponse:
    content: str
    raw: Dict[str, Any]


class LLMClient:
    """Provider-agnostic chat completion client."""

    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 60.0,
        temperature: float = 0.7,
    ) -> None:
        # Default to local/Ollama
        self.provider = (provider or os.getenv("LLM_PROVIDER", "ollama")).lower()
        self.timeout = timeout
        self.default_temperature = temperature

        self.model = model or os.getenv("LLM_MODEL")
        self.base_url = base_url or os.getenv("LLM_BASE_URL")
        self._client: Any = None          # For Anthropic / Google SDKs only
        self._api_key: Optional[str] = None
        self._init_error: Optional[str] = None

        self._configure_provider()

    def _configure_provider(self) -> None:
        # ----- LOCAL / OLLAMA -----
        if self.provider in {"ollama", "local"}:
            if not self.model:
                self.model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
            if not self.base_url:
                self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            return

        # ----- ROUTER (e.g. OpenRouter) VIA HTTP -----
        if self.provider in {"router", "openrouter"}:
            self._api_key = os.getenv("OPENROUTER_API_KEY")
            if not self._api_key:
                self._init_error = "OPENROUTER_API_KEY is not set"
                return

            if not self.base_url:
                self.base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

            if not self.model:
                self.model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct")


        # ----- GROK (X.AI) VIA HTTP -----
        if self.provider == "grok":
            self._api_key = os.getenv("GROK_API_KEY")
            if not self._api_key:
                self._init_error = "GROK_API_KEY is not set"
                return

            if not self.base_url:
                self.base_url = os.getenv("GROK_BASE_URL", "https://api.x.ai/v1")

            if not self.model:
                self.model = os.getenv("GROK_MODEL", "grok-beta")
            return

        # ----- ANTHROPIC (SDK) -----
        if self.provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                self._init_error = "ANTHROPIC_API_KEY is not set"
                return
            try:
                from anthropic import Anthropic  # type: ignore
            except ImportError:
                self._init_error = "anthropic package is not installed"
                return

            self._client = Anthropic(api_key=api_key)
            if not self.model:
                self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
            return

        # ----- GOOGLE / GEMINI (SDK) -----
        if self.provider == "google":
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                self._init_error = "GOOGLE_API_KEY is not set"
                return
            try:
                import google.generativeai as genai  # type: ignore
            except ImportError:
                self._init_error = "google-generativeai package is not installed"
                return

            genai.configure(api_key=api_key)
            self._client = genai
            if not self.model:
                self.model = os.getenv("GOOGLE_MODEL", "gemini-2.0-flash")
            return

        # ----- UNKNOWN PROVIDER -----
        self._init_error = f"Unsupported LLM provider '{self.provider}'"

    @property
    def configured(self) -> bool:
        return self._init_error is None

    @property
    def init_error(self) -> Optional[str]:
        return self._init_error

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        if not self.configured:
            raise LLMNotConfiguredError(self._init_error or "LLM provider not configured")

        messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        if self.provider in {"ollama", "local"}:
            return await self._generate_with_ollama(messages, temperature, max_tokens)
        if self.provider in {"router", "openrouter"}:
            return await self._generate_with_router_http(messages, temperature, max_tokens)
        if self.provider == "grok":
            return await self._generate_with_grok_http(messages, temperature, max_tokens)
        if self.provider == "anthropic":
            return await self._generate_with_anthropic(messages, temperature, max_tokens)
        if self.provider == "google":
            return await self._generate_with_google(messages, temperature, max_tokens)

        raise LLMNotConfiguredError(f"Unsupported provider '{self.provider}'")

    # -------------------------------------------------------------------------
    # OLLAMA / LOCAL
    # -------------------------------------------------------------------------
    async def _generate_with_ollama(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float],
        max_tokens: Optional[int],
    ) -> LLMResponse:
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature if temperature is not None else self.default_temperature,
            },
        }
        if max_tokens is not None:
            payload["options"]["num_predict"] = max_tokens

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(f"{self.base_url}/api/chat", json=payload)
                response.raise_for_status()
            except (httpx.HTTPError, httpx.TimeoutException) as exc:
                raise LLMGenerationError(f"Ollama request failed: {exc}") from exc

        data = response.json()
        message = data.get("message", {})
        content = message.get("content")
        if not content:
            raise LLMGenerationError("No content returned from Ollama")
        return LLMResponse(content=content, raw=data)

    # -------------------------------------------------------------------------
    # ROUTER (e.g. OpenRouter) VIA RAW HTTP
    # -------------------------------------------------------------------------
    async def _generate_with_router_http(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float],
        max_tokens: Optional[int],
    ) -> LLMResponse:
        if not self._api_key:
            raise LLMNotConfiguredError("OPENROUTER_API_KEY is not set")

        url = f"{self.base_url.rstrip('/')}/chat/completions"
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.default_temperature,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": os.getenv("OPENROUTER_REFERRER", "https://kodacorp-income.netlify.app"),
            "X-Title": os.getenv("OPENROUTER_TITLE", "Fallat_CrewAI"),
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
            except (httpx.HTTPError, httpx.TimeoutException) as exc:
                raise LLMGenerationError(f"Router HTTP request failed: {exc}") from exc

        data = resp.json()
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            raise LLMGenerationError(f"Unexpected router response: {data}")
        return LLMResponse(content=content, raw=data)

    # -------------------------------------------------------------------------
    # GROK (X.AI) VIA RAW HTTP
    # -------------------------------------------------------------------------
    async def _generate_with_grok_http(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float],
        max_tokens: Optional[int],
    ) -> LLMResponse:
        if not self._api_key:
            raise LLMNotConfiguredError("GROK_API_KEY is not set")

        url = f"{self.base_url.rstrip('/')}/chat/completions"
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.default_temperature,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
            except (httpx.HTTPError, httpx.TimeoutException) as exc:
                raise LLMGenerationError(f"Grok HTTP request failed: {exc}") from exc

        data = resp.json()
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            raise LLMGenerationError(f"Unexpected Grok response: {data}")
        return LLMResponse(content=content, raw=data)

    # -------------------------------------------------------------------------
    # ANTHROPIC (SDK)
    # -------------------------------------------------------------------------
    async def _generate_with_anthropic(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float],
        max_tokens: Optional[int],
    ) -> LLMResponse:
        loop = asyncio.get_event_loop()

        prompt = "\n\n".join([msg["content"] for msg in messages])

        def _call() -> Any:
            assert self._client is not None
            return self._client.messages.create(
                model=self.model,
                max_tokens=max_tokens or 1024,
                temperature=temperature if temperature is not None else self.default_temperature,
                messages=[{"role": "user", "content": prompt}],
            )

        try:
            response = await loop.run_in_executor(None, _call)
        except Exception as exc:  # pragma: no cover
            raise LLMGenerationError(f"Anthropic request failed: {exc}") from exc

        content_blocks = getattr(response, "content", [])
        text = "".join(getattr(block, "text", "") for block in content_blocks)
        if not text:
            raise LLMGenerationError("No content returned from Anthropic")
        return LLMResponse(content=text, raw=response.__dict__)

    # -------------------------------------------------------------------------
    # GOOGLE / GEMINI (SDK)
    # -------------------------------------------------------------------------
    async def _generate_with_google(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float],
        max_tokens: Optional[int],
    ) -> LLMResponse:
        if self._client is None:
            raise LLMNotConfiguredError("Google Gemini client not initialized")

        loop = asyncio.get_event_loop()

        full_prompt = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in messages])

        def _call() -> Any:
            model = self._client.GenerativeModel(self.model)
            config = self._client.types.GenerationConfig(
                temperature=temperature if temperature is not None else self.default_temperature,
                max_output_tokens=max_tokens,
            )
            return model.generate_content(full_prompt, generation_config=config)

        try:
            response = await loop.run_in_executor(None, _call)
        except Exception as exc:
            raise LLMGenerationError(f"Google request failed: {exc}") from exc

        if not getattr(response, "text", None):
            raise LLMGenerationError("No content returned from Google")

        return LLMResponse(content=response.text, raw={"text": response.text})


def get_llm_client(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
    timeout: float = 60.0,
    temperature: float = 0.7,
) -> Optional[LLMClient]:
    """Return a configured LLM client or None if unavailable."""
    client = LLMClient(
        provider=provider,
        model=model,
        base_url=base_url,
        timeout=timeout,
        temperature=temperature,
    )
    if client.configured:
        return client
    return None
