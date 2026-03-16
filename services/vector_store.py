"""Service-layer vector store with cosine-similarity search.

Stores documents paired with their pre-computed embeddings and ranks
results by cosine distance so queries return semantically relevant entries
rather than insertion-order results.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Sequence, Tuple


def _cosine(a: Sequence[float], b: Sequence[float]) -> float:
    """Return cosine similarity between two equal-length vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(y * y for y in b))
    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0
    return dot / (mag_a * mag_b)


class VectorStore:
    """In-memory vector store with cosine-similarity ranking."""

    def __init__(self) -> None:
        # ordered list so deterministic tie-breaking is preserved
        self._docs: List[Tuple[str, Dict[str, Any]]] = []
        self._index: Dict[str, int] = {}  # doc_id → position in _docs

    def add_document(self, doc_id: str, content: Dict[str, Any]) -> None:
        """Store or replace a document and its associated metadata / embedding."""
        if doc_id in self._index:
            self._docs[self._index[doc_id]] = (doc_id, content)
        else:
            self._index[doc_id] = len(self._docs)
            self._docs.append((doc_id, content))

    def query(
        self, query_vector: Sequence[float], *, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Return up to *top_k* documents ranked by cosine similarity.

        Documents whose ``content`` dict does not contain an ``embedding``
        key (or whose embedding is empty) receive a score of 0.0 and are
        ranked last.
        """
        if not self._docs:
            return []
        scored: List[Tuple[float, int]] = []
        for i, (_, content) in enumerate(self._docs):
            emb: List[float] = content.get("embedding") or []
            if emb and query_vector:
                min_len = min(len(query_vector), len(emb))
                score = _cosine(list(query_vector)[:min_len], emb[:min_len])
            else:
                score = 0.0
            scored.append((score, i))
        scored.sort(reverse=True)
        return [self._docs[i][1] for _, i in scored[:top_k]]

    def count(self) -> int:
        """Return number of stored documents."""
        return len(self._docs)
