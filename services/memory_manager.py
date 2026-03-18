from collections import deque
from typing import Any, Deque, Dict, List, Optional


class MemoryManager:
    """In-memory store for agent conversations."""

    def __init__(self, max_items: int = 100):
        self._memories: Deque[Dict[str, Any]] = deque(maxlen=max_items)

    def add_memory(self, entry: Dict[str, Any]) -> None:
        """Add a memory entry to the buffer."""
        self._memories.append(entry)

    def get_recent(self, *, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Return the most recent memory entries."""
        data = list(self._memories)
        if limit is None:
            return data
        return data[-limit:]
