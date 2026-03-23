"""OpenAIProvider — cloud LLM inference via the OpenAI Chat Completions API."""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

try:
    import httpx
except Exception:
    httpx = None

from providers.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

_DEFAULT_BASE_URL = "https://api.openai.com/v1"
_DEFAULT_MODEL = "gpt-4o-mini"
_REQUEST_TIMEOUT = 60.0


class OpenAIProvider(LLMProvider):
    """Sends chat requests to the OpenAI Chat Completions API.

    Requires ``OPENAI_API_KEY`` to be set in the environment (or
    passed directly as *api_key*).
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        *,
        timeout: float = _REQUEST_TIMEOUT,
        system_prompt: Optional[str] = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.base_url = os.environ.get("OPENAI_BASE_URL", _DEFAULT_BASE_URL).rstrip("/")
        self.endpoint = f"{self.base_url}/chat/completions"
        self.model = model or os.environ.get("OPENAI_MODEL", _DEFAULT_MODEL)
        self.timeout = timeout
        self.system_prompt = system_prompt

    async def chat(
        self, prompt: str, *, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if httpx is None:
            return {
                "success": False,
                "data": None,
                "error": "OpenAIProvider unavailable: missing optional dependency 'httpx'.",
            }
        if not self.api_key:
            return {
                "success": False,
                "data": None,
                "error": (
                    "OpenAI API key not set. "
                    "Configure OPENAI_API_KEY in config/.env"
                ),
            }

        messages: List[Dict[str, str]] = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        if context and isinstance(context.get("history"), list):
            messages.extend(context["history"])
        messages.append({"role": "user", "content": prompt})

        payload = {"model": self.model, "messages": messages}
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.endpoint, json=payload, headers=headers
                )
                response.raise_for_status()
                data = response.json()
                text = data["choices"][0]["message"]["content"]
                return {"success": True, "data": {"text": text}, "error": None}
        except Exception as exc:
            if httpx is not None and isinstance(exc, httpx.HTTPStatusError):
                logger.warning("OpenAIProvider HTTP error: %s", exc)
                return {
                    "success": False,
                    "data": None,
                    "error": f"HTTP {exc.response.status_code}: {exc.response.text}",
                }
            logger.warning("OpenAIProvider error: %s", exc)
            return {"success": False, "data": None, "error": str(exc)}
