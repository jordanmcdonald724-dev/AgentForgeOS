"""FalImageProvider — image generation via the fal.ai inference API."""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

import httpx

from providers.image_provider import ImageProvider

logger = logging.getLogger(__name__)

_FAL_API_BASE = "https://fal.run"
_DEFAULT_MODEL = "fal-ai/flux/schnell"
_REQUEST_TIMEOUT = 120.0


class FalImageProvider(ImageProvider):
    """Generates images using the fal.ai inference API.

    Requires ``FAL_API_KEY`` to be set in the environment (or passed
    directly as *api_key*).  See https://fal.ai for API key setup.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = _DEFAULT_MODEL,
        *,
        timeout: float = _REQUEST_TIMEOUT,
    ) -> None:
        self.api_key = api_key or os.environ.get("FAL_API_KEY", "")
        self.model = model
        self.timeout = timeout

    async def generate(
        self, prompt: str, *, options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if not self.api_key:
            return {
                "success": False,
                "data": None,
                "error": (
                    "Fal API key not set. "
                    "Configure FAL_API_KEY in config/.env"
                ),
            }

        payload = {"prompt": prompt, **(options or {})}
        headers = {
            "Authorization": f"Key {self.api_key}",
            "Content-Type": "application/json",
        }
        url = f"{_FAL_API_BASE}/{self.model}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                return {"success": True, "data": data, "error": None}
        except httpx.HTTPStatusError as exc:
            logger.warning("FalImageProvider HTTP error: %s", exc)
            return {
                "success": False,
                "data": None,
                "error": f"HTTP {exc.response.status_code}: {exc.response.text}",
            }
        except Exception as exc:
            logger.warning("FalImageProvider error: %s", exc)
            return {"success": False, "data": None, "error": str(exc)}
