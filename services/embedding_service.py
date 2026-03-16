from typing import Any, Dict, List, Optional

from .vector_store import VectorStore


class EmbeddingService:
    """Placeholder embedding service that stores vectors in the shared VectorStore."""

    def __init__(self, vector_store: Optional[VectorStore] = None) -> None:
        self.vector_store = vector_store or VectorStore()

    def embed_text(self, text: str) -> List[float]:
        """Generate a trivial embedding based on text length for scaffolding purposes."""
        return [float(len(text))]

    def add_text(self, doc_id: str, text: str, *, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Embed text and persist it to the vector store."""
        embedding = self.embed_text(text)
        payload = {"text": text, "metadata": metadata or {}, "embedding": embedding}
        self.vector_store.add_document(doc_id, payload)

    def search(self, query: str, *, top_k: int = 5) -> List[Dict[str, Any]]:
        """Return stored entries ordered by insertion (similarity is mocked)."""
        embedding = self.embed_text(query)
        return self.vector_store.query(embedding, top_k=top_k)
