from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class TTSProvider(ABC):
    """Standard interface for text-to-speech providers."""

    @abstractmethod
    async def speak(
        self, text: str, *, voice: Optional[str] = None, options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Convert text to speech using the provider.

        Implementations must return the standardized response structure:
        {
            "success": bool,
            "data": <provider-specific payload>,
            "error": Optional[str] | None
        }
        """
        raise NotImplementedError
