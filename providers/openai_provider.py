"""OpenAIProvider — cloud LLM inference via the OpenAI Chat Completions API."""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

import httpx

from providers.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

_CHAT_COMPLETIONS_URL = "https://api.openai.com/v1/chat/completions"
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
        model: str = _DEFAULT_MODEL,
        *,
        timeout: float = _REQUEST_TIMEOUT,
        system_prompt: Optional[str] = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.model = model
        self.timeout = timeout
        self.system_prompt = system_prompt

    async def chat(
        self, prompt: str, *, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
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
                    _CHAT_COMPLETIONS_URL, json=payload, headers=headers
                )
                response.raise_for_status()
                data = response.json()
                text = data["choices"][0]["message"]["content"]
                return {"success": True, "data": {"text": text}, "error": None}
        except httpx.HTTPStatusError as exc:
            logger.warning("OpenAIProvider HTTP error: %s", exc)
            return {
                "success": False,
                "data": None,
                "error": f"HTTP {exc.response.status_code}: {exc.response.text}",
            }
        except Exception as exc:
            logger.warning("OpenAIProvider error: %s", exc)
            return {"success": False, "data": None, "error": str(exc)}
