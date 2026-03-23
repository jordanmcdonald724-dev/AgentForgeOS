"""Service-layer embedding wrapper — delegates to the Phase 7 knowledge engine.

Uses TF-IDF vectorisation and cosine-similarity search implemented in
``knowledge.EmbeddingService``.  No external packages are required.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from knowledge.embedding_service import EmbeddingService as _KnowledgeEmbeddingService


class EmbeddingService:
    """Thin wrapper around the knowledge-layer TF-IDF embedding engine."""

    def __init__(self) -> None:
        self._engine = _KnowledgeEmbeddingService()

    def get_embedding(self, text: str) -> List[float]:
        """Returns a dense vector representation of the text."""
        return self._engine.get_embedding(text)

    def add_text(
        self, doc_id: str, text: str, *, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Index *text* under *doc_id* and persist its TF-IDF embedding."""
        self._engine.add_text(doc_id, text, metadata=metadata)

    def search(self, query: str, *, top_k: int = 5) -> List[Dict[str, Any]]:
        """Return up to *top_k* documents ranked by cosine similarity to *query*.

        Each result dict contains ``doc_id``, ``score``, ``text``, and
        ``metadata`` keys.
        """
        return self._engine.search(query, top_k=top_k)
