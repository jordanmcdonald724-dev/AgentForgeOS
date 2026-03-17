"""Persistent vector store for the Phase 7 Knowledge System.

Documents (with their embeddings and metadata) are kept in memory for fast
access and optionally flushed to a JSON file on disk so the index survives
engine restarts.  No external database or library is required.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


def _cosine(a: Sequence[float], b: Sequence[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(y * y for y in b))
    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0
    return dot / (mag_a * mag_b)


class KnowledgeVectorStore:
    """Vector store that pairs embeddings with metadata.

    When *persist_path* is supplied the store is loaded from disk on
    construction and saved after every :py:meth:`add` call.
    """

    def __init__(self, persist_path: Optional[Path] = None) -> None:
        # doc_id → (metadata, embedding)
        self._documents: Dict[str, Tuple[Dict[str, Any], List[float]]] = {}
        self._persist_path: Optional[Path] = (
            Path(persist_path) if persist_path else None
        )
        if self._persist_path and self._persist_path.exists():
            self._load()

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def _load(self) -> None:
        """Populate the in-memory store from the JSON file on disk."""
        try:
            raw = json.loads(self._persist_path.read_text(encoding="utf-8"))
            for doc_id, entry in raw.items():
                self._documents[doc_id] = (entry["metadata"], entry["embedding"])
        except Exception:
            pass  # Corrupt or empty file — start fresh

    def _save(self) -> None:
        """Flush the current store to disk as JSON."""
        if not self._persist_path:
            return
        self._persist_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            doc_id: {"metadata": meta, "embedding": emb}
            for doc_id, (meta, emb) in self._documents.items()
        }
        self._persist_path.write_text(
            json.dumps(payload, indent=2), encoding="utf-8"
        )

    # ------------------------------------------------------------------
    # Public API (maintains original interface)
    # ------------------------------------------------------------------

    def add(
        self,
        doc_id: str,
        metadata: Dict[str, Any],
        embedding: Sequence[float],
    ) -> None:
        """Store a document with associated embedding and persist to disk."""
        self._documents[doc_id] = (dict(metadata), list(embedding))
        self._save()

    def query(
        self,
        query_vector: Sequence[float],
        *,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Return up to *top_k* documents ranked by cosine similarity."""
        if not self._documents:
            return []
        scored: List[Tuple[float, str]] = []
        for doc_id, (meta, emb) in self._documents.items():
            # Handle dimension mismatch from incremental vocab growth
            min_len = min(len(query_vector), len(emb))
            score = _cosine(query_vector[:min_len], emb[:min_len])
            scored.append((score, doc_id))
        scored.sort(reverse=True)
        return [self._documents[doc_id][0] for _, doc_id in scored[:top_k]]

    def count(self) -> int:
        """Return number of stored documents."""
        return len(self._documents)
