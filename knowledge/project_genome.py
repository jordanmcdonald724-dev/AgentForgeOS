from typing import Any, Dict, List


class ProjectGenome:
    """Tracks project traits and lessons learned."""

    def __init__(self) -> None:
        self._traits: List[Dict[str, Any]] = []

    def add_trait(self, trait: Dict[str, Any]) -> None:
        """Record a trait or finding from a project run."""
        self._traits.append(trait)

    def summarize(self) -> Dict[str, Any]:
        """Return a basic summary of stored traits."""
        return {"count": len(self._traits), "traits": list(self._traits)}
