from typing import List


class EmbeddingService:
    """Placeholder embedding generator for Phase 7."""

    def embed(self, text: str) -> List[float]:
        """Return a deterministic stub embedding."""
        seed = sum(ord(char) for char in text)
        return [(seed % 100) / 100.0] * 8
