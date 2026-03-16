from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class ImageProvider(ABC):
    """Standard interface for image generation providers."""

    @abstractmethod
    async def generate(
        self, prompt: str, *, options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate an image for the given prompt.

        Implementations must return the standardized response structure:
        {
            "success": bool,
            "data": <provider-specific payload>,
            "error": str | None
        }
        The "error" field is None when successful.
        """
        raise NotImplementedError
