from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class LLMProvider(ABC):
    """Standard interface for large language model providers."""

    @abstractmethod
    async def chat(
        self, prompt: str, *, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate a response for the provided prompt.

        Implementations must return the standardized response structure:
        {
            "success": bool,
            "data": <provider-specific payload>,
            "error": Optional[str]
        }
        The "error" field is None when successful and should contain a descriptive
        message when success is False.
        """
        raise NotImplementedError
