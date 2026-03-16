from typing import Any, Dict, List, Optional, Sequence, Tuple


class VectorStore:
    """Minimal placeholder vector store for Phase 4 scaffolding."""

    def __init__(self):
        self._documents: List[Tuple[str, Dict[str, Any]]] = []

    def add_document(self, doc_id: str, content: Dict[str, Any]) -> None:
        """Store a document with its metadata."""
        self._documents.append((doc_id, content))

    def query(self, query_vector: Sequence[float], *, top_k: int = 5) -> List[Dict[str, Any]]:
        """Return stored documents; similarity is not computed in the placeholder implementation."""
        _ = query_vector  # placeholder to satisfy interface
        return [meta for _, meta in self._documents[:top_k]]

    def count(self) -> int:
        """Return number of stored documents."""
        return len(self._documents)
