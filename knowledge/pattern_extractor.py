from typing import Any, Dict, List


class PatternExtractor:
    """Simple pattern collector scaffold for Phase 7."""

    def __init__(self):
        self._patterns: List[Dict[str, Any]] = []

    def record(self, pattern: Dict[str, Any]) -> None:
        """Store a detected pattern."""
        self._patterns.append(pattern)

    def list_patterns(self) -> List[Dict[str, Any]]:
        """Return all recorded patterns."""
        return list(self._patterns)
