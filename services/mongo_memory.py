"""MongoMemoryManager — optional MongoDB-backed conversation memory.

This class provides the same interface as the in-memory ``MemoryManager``
but persists memories to a MongoDB collection when a database handle is
available.  Falls back to pure in-memory operation when the database is
not configured.

Usage::

    from engine.database import db
    from services.mongo_memory import MongoMemoryManager

    memory = MongoMemoryManager(db=db, session_id="user-123")
    await memory.save_memory({"role": "user", "content": "hello"})
    history = await memory.load_memories()
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_COLLECTION_NAME = "memories"


class MongoMemoryManager:
    """Async memory manager that persists conversation history to MongoDB.

    When the database handle has no live connection (e.g. motor is not
    installed, or the MongoDB server is unreachable) all operations fall
    back to the in-memory list, so the rest of the system keeps working.
    """

    def __init__(self, db=None, session_id: str = "default") -> None:
        self._db = db
        self.session_id = session_id
        self._local: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _collection(self):
        """Return the MongoDB collection, or None if unavailable."""
        if self._db is None:
            return None
        database = getattr(self._db, "database", None)
        if database is None:
            return None
        try:
            return database[_COLLECTION_NAME]
        except Exception:
            return None

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    async def save_memory(self, entry: Dict[str, Any]) -> None:
        """Persist a single memory entry for this session."""
        record = {"session_id": self.session_id, **entry}
        self._local.append(record)

        collection = self._collection()
        if collection is None:
            return
        try:
            await collection.insert_one(record)
        except Exception as exc:
            logger.warning("MongoMemoryManager.save_memory failed: %s", exc)

    async def load_memories(
        self, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Return conversation history for this session (newest last).

        Tries MongoDB first; falls back to the local in-memory list.
        """
        collection = self._collection()
        if collection is not None:
            try:
                cursor = collection.find(
                    {"session_id": self.session_id},
                    {"_id": 0},
                )
                if limit:
                    cursor = cursor.limit(limit)
                results = await cursor.to_list(length=limit or 1000)
                return results
            except Exception as exc:
                logger.warning("MongoMemoryManager.load_memories failed: %s", exc)

        # Fallback to in-memory
        entries = [
            {k: v for k, v in e.items() if k != "session_id"}
            for e in self._local
            if e.get("session_id") == self.session_id
        ]
        if limit:
            return entries[-limit:]
        return entries

    async def clear(self) -> None:
        """Remove all memories for this session."""
        self._local = [
            e for e in self._local if e.get("session_id") != self.session_id
        ]
        collection = self._collection()
        if collection is None:
            return
        try:
            await collection.delete_many({"session_id": self.session_id})
        except Exception as exc:
            logger.warning("MongoMemoryManager.clear failed: %s", exc)

    def get_local_cache(self) -> List[Dict[str, Any]]:
        """Return a session-filtered view of the in-memory cache without the
        internal ``session_id`` field.

        This provides a synchronous, encapsulation-safe way for consumers such
        as ``AgentService.history()`` to read the local cache without reaching
        into private attributes.
        """
        return [
            {k: v for k, v in entry.items() if k != "session_id"}
            for entry in self._local
            if entry.get("session_id") == self.session_id
        ]
