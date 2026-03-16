from collections import deque
from typing import Deque, Dict, List, Optional


class MemoryManager:
    """In-memory store for agent conversations."""

    def __init__(self, max_items: int = 100):
        self._memories: Deque[Dict] = deque(maxlen=max_items)

    def add_memory(self, entry: Dict) -> None:
        """Add a memory entry to the buffer."""
        self._memories.append(entry)

    def get_recent(self, *, limit: Optional[int] = None) -> List[Dict]:
        """Return the most recent memory entries."""
        if limit is None:
            return list(self._memories)
        return list(self._memories)[-limit:]
