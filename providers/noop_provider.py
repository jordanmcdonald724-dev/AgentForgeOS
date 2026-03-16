"""No-operation LLM provider used as a safe fallback when no provider is configured."""

from typing import Any, Dict, Optional

from providers.llm_provider import LLMProvider


class NoOpLLMProvider(LLMProvider):
    """Returns a not-configured error for every chat request.

    Used as a placeholder when no real LLM provider has been selected or
    configured.  This lets the rest of the system boot successfully while
    making the misconfiguration obvious at request time.
    """

    async def chat(
        self, prompt: str, *, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return {
            "success": False,
            "data": None,
            "error": (
                "No LLM provider configured. "
                "Set PROVIDER_LLM in config/.env and configure the chosen provider."
            ),
        }
