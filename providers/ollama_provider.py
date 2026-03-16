"""OllamaProvider — local LLM inference via the Ollama HTTP API."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import httpx

from providers.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

_DEFAULT_BASE_URL = "http://localhost:11434"
_DEFAULT_MODEL = "llama3"
_REQUEST_TIMEOUT = 120.0


class OllamaProvider(LLMProvider):
    """Sends chat requests to a locally running Ollama instance.

    Ollama must be installed and running (``ollama serve``).
    The model referenced by *model* must already be pulled
    (e.g. ``ollama pull llama3``).
    """

    def __init__(
        self,
        base_url: str = _DEFAULT_BASE_URL,
        model: str = _DEFAULT_MODEL,
        *,
        timeout: float = _REQUEST_TIMEOUT,
        system_prompt: Optional[str] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.system_prompt = system_prompt

    async def chat(
        self, prompt: str, *, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        messages: List[Dict[str, str]] = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        if context and isinstance(context.get("history"), list):
            messages.extend(context["history"])
        messages.append({"role": "user", "content": prompt})

        payload = {"model": self.model, "messages": messages, "stream": False}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat", json=payload
                )
                response.raise_for_status()
                data = response.json()
                text = data.get("message", {}).get("content", "")
                return {"success": True, "data": {"text": text}, "error": None}
        except httpx.HTTPStatusError as exc:
            logger.warning("OllamaProvider HTTP error: %s", exc)
            return {
                "success": False,
                "data": None,
                "error": f"HTTP {exc.response.status_code}: {exc.response.text}",
            }
        except Exception as exc:
            logger.warning("OllamaProvider error: %s", exc)
            return {"success": False, "data": None, "error": str(exc)}
