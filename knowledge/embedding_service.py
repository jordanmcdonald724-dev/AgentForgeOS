"""Unified Embedding Service — Phase 7 Knowledge System.

Provides text embedding generation, vector similarity search, and batch processing.
Supports both a zero-dependency TF-IDF fallback and advanced numpy/OpenAI providers.
"""

from __future__ import annotations

import math
import re
import hashlib
import json
import logging
from collections import Counter
from typing import Dict, List, Any, Optional, Tuple, Sequence
from datetime import datetime, timezone

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

logger = logging.getLogger(__name__)


def _tokenize(text: str) -> List[str]:
    """Lower-case and split on non-alphanumeric characters."""
    return re.findall(r"[a-z0-9]+", text.lower())


def _cosine_sim(a: Sequence[float], b: Sequence[float]) -> float:
    """Return cosine similarity between two equal-length vectors."""
    if not a or not b or len(a) != len(b):
        return 0.0
    
    if HAS_NUMPY:
        v1, v2 = np.array(a), np.array(b)
        dot = np.dot(v1, v2)
        norm1, norm2 = np.linalg.norm(v1), np.linalg.norm(v2)
        return float(dot / (norm1 * norm2)) if norm1 > 0 and norm2 > 0 else 0.0
    
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(y * y for y in b))
    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0
    return dot / (mag_a * mag_b)


class EmbeddingService:
    """Unified embedding service for AgentForgeOS.
    
    Acts as the single authority for text-to-vector projections.
    - get_embedding: Project text to a dense vector (numpy or list)
    - add_text / search: TF-IDF indexing for rapid local search
    """

    def __init__(self, provider: str = "local", cache_enabled: bool = True) -> None:
        self.provider = provider
        self.cache_enabled = cache_enabled
        self.embedding_cache: Dict[str, Any] = {}
        
        # TF-IDF state
        self._doc_freq: Counter[str] = Counter()
        self._doc_count: int = 0
        self._vocab: List[str] = []
        self._vocab_index: Dict[str, int] = {}
        self._store: Dict[str, Tuple[List[float], dict, str]] = {}
        
        # Advanced provider state
        if provider == "openai":
            self._init_openai()
        else:
            self._init_local()

    def _init_openai(self) -> None:
        try:
            import openai
            self.openai_client = openai
            self.model_name = "text-embedding-3-small"
            self.embedding_dim = 1536
        except ImportError:
            logger.warning("OpenAI not available, falling back to local provider")
            self._init_local()

    def _init_local(self) -> None:
        self.embedding_dim = 384
        self.model_name = "local-sentence-transformer"
        
        # Simple word embedding simulation for demo
        # In production, use actual sentence transformers
        self.word_vectors = self._load_simple_word_vectors()

    def _load_simple_word_vectors(self) -> Dict[str, Any]:
        """Load simple word vectors for local embedding."""
        vectors = {}
        # Common technical terms with simple vectors
        terms = [
            'react', 'vue', 'angular', 'nodejs', 'python', 'java', 'javascript',
            'database', 'api', 'frontend', 'backend', 'docker', 'kubernetes',
            'microservices', 'monolith', 'mvc', 'rest', 'graphql', 'websocket',
            'authentication', 'authorization', 'security', 'performance', 'scalability'
        ]
        
        for term in terms:
            # Create deterministic but pseudo-random vectors
            hash_val = int(hashlib.md5(term.encode()).hexdigest(), 16)
            if HAS_NUMPY:
                vector = np.array([
                    ((hash_val >> i) & 0xFF) / 255.0 - 0.5
                    for i in range(self.embedding_dim)
                ], dtype=np.float32)
                vector = vector / np.linalg.norm(vector)
                vectors[term] = vector
            else:
                vector = [
                    ((hash_val >> i) & 0xFF) / 255.0 - 0.5
                    for i in range(8) # Fallback to small vector if no numpy
                ]
                vectors[term] = vector
        
        return vectors

    # ------------------------------------------------------------------
    # Public Unified API
    # ------------------------------------------------------------------

    def get_embedding(self, text: str) -> List[float]:
        """Returns a dense vector representation of the text."""
        # If cache is enabled, check it
        cache_key = hashlib.md5(text.encode()).hexdigest()
        if self.cache_enabled and cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]

        # Generate via provider
        if self.provider == "openai" and hasattr(self, "openai_client"):
            try:
                response = self.openai_client.embeddings.create(model=self.model_name, input=text)
                vector = [float(x) for x in response.data[0].embedding]
            except Exception:
                vector = self._get_local_dense_embedding(text)
        else:
            vector = self._get_local_dense_embedding(text)
            
        if self.cache_enabled:
            self.embedding_cache[cache_key] = vector
        return vector

    def _get_local_dense_embedding(self, text: str) -> List[float]:
        """Get dense embedding from local word vectors or fallback to TF-IDF."""
        if not HAS_NUMPY:
            return self.embed(text)
            
        words = text.lower().split()
        word_vectors = []
        
        for word in words:
            clean_word = ''.join(c for c in word if c.isalnum())
            if clean_word in self.word_vectors:
                word_vectors.append(self.word_vectors[clean_word])
            else:
                hash_val = int(hashlib.md5(clean_word.encode()).hexdigest(), 16)
                vector = np.array([
                    ((hash_val >> i) & 0xFF) / 255.0 - 0.5
                    for i in range(self.embedding_dim)
                ], dtype=np.float32)
                vector = vector / np.linalg.norm(vector)
                word_vectors.append(vector)
        
        if word_vectors:
            embedding = np.mean(word_vectors, axis=0)
            embedding = embedding / np.linalg.norm(embedding)
            return embedding.tolist()
        return [0.0] * self.embedding_dim

    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        return [self.get_embedding(t) for t in texts]

    def cluster_texts(self, texts: List[str], num_clusters: int = 5) -> List[List[int]]:
        """Cluster texts using k-means (requires numpy)."""
        if not HAS_NUMPY or len(texts) < num_clusters:
            return [[i] for i in range(len(texts))]
            
        embeddings = np.array(self.get_embeddings_batch(texts))
        n_samples = embeddings.shape[0]
        
        np.random.seed(42)
        centroids = embeddings[np.random.choice(n_samples, num_clusters, replace=False)]
        
        for _ in range(100):
            distances = np.linalg.norm(embeddings[:, np.newaxis] - centroids, axis=2)
            assignments = np.argmin(distances, axis=1)
            new_centroids = np.array([embeddings[assignments == i].mean(axis=0) if len(embeddings[assignments == i]) > 0 else centroids[i] for i in range(num_clusters)])
            if np.allclose(centroids, new_centroids): break
            centroids = new_centroids
            
        clusters = [[] for _ in range(num_clusters)]
        for idx, cluster_idx in enumerate(assignments):
            clusters[cluster_idx].append(idx)
        return clusters

    def save_cache(self, file_path: str) -> None:
        """Save embedding cache to disk."""
        if not self.cache_enabled: return
        data = {
            'provider': self.provider,
            'model_name': self.model_name,
            'cache': {k: (v.tolist() if HAS_NUMPY and isinstance(v, np.ndarray) else v) for k, v in self.embedding_cache.items()}
        }
        Path(file_path).write_text(json.dumps(data), encoding='utf-8')

    def load_cache(self, file_path: str) -> None:
        """Load embedding cache from disk."""
        if not self.cache_enabled: return
        try:
            data = json.loads(Path(file_path).read_text(encoding='utf-8'))
            if data.get('provider') == self.provider:
                self.embedding_cache = data.get('cache', {})
        except Exception: pass

    def embed(self, text: str) -> List[float]:
        """TF-IDF vector for *text* against the current corpus vocabulary."""
        tokens = _tokenize(text)
        if not self._vocab:
            # Deterministic stub vector for empty vocabulary
            seed = sum(ord(c) for c in text)
            return [(seed % 100) / 100.0] * 8
        return self._tfidf_vector(tokens)

    def add_text(self, doc_id: str, text: str, *, metadata: dict | None = None) -> None:
        """Index *text* for TF-IDF search."""
        tokens = _tokenize(text)
        if doc_id not in self._store:
            self._doc_count += 1
        else:
            _old_tokens = set(_tokenize(self._store[doc_id][2]))
            for tok in _old_tokens:
                self._doc_freq[tok] = max(0, self._doc_freq[tok] - 1)
        
        for tok in set(tokens):
            self._doc_freq[tok] += 1
        
        self._update_vocab(tokens)
        embedding = self._tfidf_vector(tokens)
        self._store[doc_id] = (embedding, metadata or {}, text)

    def document_count(self) -> int:
        return self._doc_count

    def search(self, query: str, *, top_k: int = 5) -> List[dict]:
        """Ranked cosine similarity search."""
        if not self._store: return []
        q_vec = self.embed(query)
        scored = []
        for doc_id, (emb, meta, raw) in self._store.items():
            # Pad if vocab grew
            padded = emb + [0.0] * (len(q_vec) - len(emb))
            score = _cosine_sim(q_vec, padded)
            scored.append((score, doc_id))
        scored.sort(reverse=True)
        return [{"doc_id": d, "score": s, "text": self._store[d][2], "metadata": self._store[d][1]} for s, d in scored[:top_k]]

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    def _update_vocab(self, tokens: List[str]) -> None:
        for tok in tokens:
            if tok not in self._vocab_index:
                self._vocab_index[tok] = len(self._vocab)
                self._vocab.append(tok)

    def _tfidf_vector(self, tokens: List[str]) -> List[float]:
        if not self._vocab: return []
        tf: Counter[str] = Counter(tokens)
        total = max(len(tokens), 1)
        vec = [0.0] * len(self._vocab)
        for term, count in tf.items():
            idx = self._vocab_index.get(term)
            if idx is None: continue
            tf_score = count / total
            df = self._doc_freq.get(term, 0)
            idf = math.log((self._doc_count + 1) / (df + 1)) + 1.0
            vec[idx] = tf_score * idf
        return vec
