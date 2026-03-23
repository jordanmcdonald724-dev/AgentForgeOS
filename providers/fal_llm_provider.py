from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

try:
    import httpx
except Exception:
    httpx = None

from providers.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

_FAL_API_BASE = "https://fal.run"
_DEFAULT_MODEL = "fal-ai/llama3.1-8b-instruct"
_REQUEST_TIMEOUT = 120.0


class FalLLMProvider(LLMProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        *,
        timeout: float = _REQUEST_TIMEOUT,
    ) -> None:
        self.api_key = api_key or os.environ.get("FAL_API_KEY", "")
        self.model = model or os.environ.get("FAL_LLM_MODEL", _DEFAULT_MODEL)
        self.timeout = timeout

    async def chat(
        self, prompt: str, *, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if httpx is None:
            return {
                "success": False,
                "data": None,
                "error": "FalLLMProvider unavailable: missing optional dependency 'httpx'.",
            }
        if not self.api_key:
            return {
                "success": False,
                "data": None,
                "error": "Fal API key not set. Configure FAL_API_KEY in config/.env",
            }

        payload: Dict[str, Any] = {"prompt": prompt}
        if context and isinstance(context.get("history"), list):
            payload["history"] = context["history"]

        headers = {
            "Authorization": f"Key {self.api_key}",
            "Content-Type": "application/json",
        }
        url = f"{_FAL_API_BASE}/{self.model}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                raw = response.json()
                text = None
                if isinstance(raw, dict):
                    for k in ("text", "output", "response", "result", "content"):
                        v = raw.get(k)
                        if isinstance(v, str) and v.strip():
                            text = v
                            break
                    if text is None:
                        m = raw.get("message")
                        if isinstance(m, dict):
                            c = m.get("content")
                            if isinstance(c, str) and c.strip():
                                text = c
                if text is None and isinstance(raw, str):
                    text = raw
                if text is None:
                    text = str(raw)
                return {"success": True, "data": {"text": text}, "error": None}
        except Exception as exc:
            if httpx is not None and isinstance(exc, httpx.HTTPStatusError):
                logger.warning("FalLLMProvider HTTP error: %s", exc)
                return {
                    "success": False,
                    "data": None,
                    "error": f"HTTP {exc.response.status_code}: {exc.response.text}",
                }
            logger.warning("FalLLMProvider error: %s", exc)
            return {"success": False, "data": None, "error": str(exc)}
