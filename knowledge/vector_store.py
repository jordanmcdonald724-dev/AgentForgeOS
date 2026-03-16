from typing import Any, Dict, List, Sequence, Tuple


class KnowledgeVectorStore:
    """Minimal placeholder vector store for Phase 7 knowledge layer."""

    def __init__(self) -> None:
        self._documents: List[Tuple[str, Dict[str, Any], Sequence[float]]] = []

    def add(self, doc_id: str, metadata: Dict[str, Any], embedding: Sequence[float]) -> None:
        """Store a document with associated embedding."""
        self._documents.append((doc_id, metadata, embedding))

    def query(self, query_vector: Sequence[float], *, top_k: int = 5) -> List[Dict[str, Any]]:
        """Return stored documents; similarity is not computed in this scaffold."""
        _ = query_vector  # placeholder to match interface
        return [meta for _, meta, _ in self._documents[:top_k]]

    def count(self) -> int:
        """Return number of stored documents."""
        return len(self._documents)
