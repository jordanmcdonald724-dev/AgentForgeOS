"""TF-IDF embedding service — Phase 7 Knowledge System.

Uses a corpus-level inverse-document-frequency (IDF) vocabulary built from all
texts seen via ``fit()`` / ``add_text()``.  Embeddings are sparse TF-IDF
vectors encoded as dense lists so they slot into the existing ``KnowledgeVectorStore``
interface without new dependencies.

No external packages are required — everything uses Python's standard library.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import Dict, List, Sequence, Tuple


def _tokenize(text: str) -> List[str]:
    """Lower-case and split on non-alphanumeric characters."""
    return re.findall(r"[a-z0-9]+", text.lower())


def _cosine(a: Sequence[float], b: Sequence[float]) -> float:
    """Return cosine similarity between two equal-length vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(y * y for y in b))
    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0
    return dot / (mag_a * mag_b)


class EmbeddingService:
    """TF-IDF embedding service with cosine-similarity search.

    The vocabulary is built dynamically as documents are added via
    ``add_text()``.  Existing embeddings are **not** re-computed when new
    terms enter the vocabulary; call ``rebuild()`` after bulk inserts if
    you need fully consistent IDF weights.
    """

    def __init__(self) -> None:
        # term → number of documents that contain it (for IDF)
        self._doc_freq: Counter[str] = Counter()
        # total documents seen
        self._doc_count: int = 0
        # ordered vocabulary list (position = dimension index)
        self._vocab: List[str] = []
        self._vocab_index: Dict[str, int] = {}
        # stored documents: {doc_id: (embedding, metadata, raw_text)}
        self._store: Dict[str, Tuple[List[float], dict, str]] = {}

    # ------------------------------------------------------------------
    # Vocabulary helpers
    # ------------------------------------------------------------------

    def _update_vocab(self, tokens: List[str]) -> None:
        """Extend the vocabulary with any previously unseen tokens."""
        for tok in tokens:
            if tok not in self._vocab_index:
                self._vocab_index[tok] = len(self._vocab)
                self._vocab.append(tok)

    def _tfidf_vector(self, tokens: List[str]) -> List[float]:
        """Compute a TF-IDF vector for a tokenised document."""
        if not self._vocab:
            return []
        tf: Counter[str] = Counter(tokens)
        total = max(len(tokens), 1)
        vec = [0.0] * len(self._vocab)
        for term, count in tf.items():
            idx = self._vocab_index.get(term)
            if idx is None:
                continue
            tf_score = count / total
            df = self._doc_freq.get(term, 0)
            idf = math.log((self._doc_count + 1) / (df + 1)) + 1.0
            vec[idx] = tf_score * idf
        return vec

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def embed(self, text: str) -> List[float]:
        """Return a TF-IDF vector for *text* against the current corpus vocabulary.

        If the vocabulary is empty (no documents have been indexed yet) a
        length-8 deterministic stub vector is returned so the service is always
        usable even before any texts have been indexed.
        """
        tokens = _tokenize(text)
        if not self._vocab:
            # Graceful fallback when corpus is empty
            seed = sum(ord(c) for c in text)
            return [(seed % 100) / 100.0] * 8
        return self._tfidf_vector(tokens)

    def add_text(
        self,
        doc_id: str,
        text: str,
        *,
        metadata: dict | None = None,
    ) -> None:
        """Index *text* under *doc_id* and persist its TF-IDF embedding.

        Calling this multiple times with the same *doc_id* overwrites the
        previous entry.
        """
        tokens = _tokenize(text)
        unique_tokens = set(tokens)
        # Update IDF counts (only count once per document per term)
        if doc_id not in self._store:
            self._doc_count += 1
        else:
            # Remove old IDF contribution for re-indexed document
            _old_tokens = set(_tokenize(self._store[doc_id][2]))
            for tok in _old_tokens:
                self._doc_freq[tok] = max(0, self._doc_freq[tok] - 1)
        for tok in unique_tokens:
            self._doc_freq[tok] += 1
        self._update_vocab(tokens)
        embedding = self._tfidf_vector(tokens)
        self._store[doc_id] = (embedding, metadata or {}, text)

    def search(self, query: str, *, top_k: int = 5) -> List[dict]:
        """Return up to *top_k* documents ranked by cosine similarity to *query*.

        Each result dict contains ``doc_id``, ``score``, ``text``, and
        ``metadata`` fields.
        """
        if not self._store:
            return []
        q_tokens = _tokenize(query)
        self._update_vocab(q_tokens)
        q_vec = self._tfidf_vector(q_tokens)
        # Pad stored embeddings that pre-date vocabulary extensions
        scored: List[Tuple[float, str]] = []
        for doc_id, (emb, meta, raw) in self._store.items():
            # Extend old embedding with zeros if vocab grew
            padded = emb + [0.0] * (len(q_vec) - len(emb))
            score = _cosine(q_vec, padded)
            scored.append((score, doc_id))
        scored.sort(reverse=True)
        results = []
        for score, doc_id in scored[:top_k]:
            emb, meta, raw = self._store[doc_id]
            results.append(
                {"doc_id": doc_id, "score": score, "text": raw, "metadata": meta}
            )
        return results

    def document_count(self) -> int:
        """Return the number of indexed documents."""
        return len(self._store)
