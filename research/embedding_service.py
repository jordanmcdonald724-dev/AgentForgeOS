"""
Embedding Service for Vector Search and Pattern Recognition

Provides text embedding generation and vector similarity search
capabilities for the AgentForgeOS research and knowledge systems.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    np = None
    HAS_NUMPY = False
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Embedding service for text vectorization and similarity search.
    
    Provides:
    - Text embedding generation
    - Vector similarity calculations
    - Batch processing capabilities
    - Multiple provider support
    - Caching for performance
    """
    
    def __init__(self, provider: str = "local", cache_enabled: bool = True):
        self.provider = provider
        self.cache_enabled = cache_enabled
        self.embedding_cache: Dict[str, np.ndarray] = {}
        
        # Initialize provider-specific settings
        if provider == "openai":
            self._init_openai()
        elif provider == "local":
            self._init_local()
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        logger.info(f"EmbeddingService initialized with provider: {provider}")
    
    def _init_openai(self) -> None:
        """Initialize OpenAI embedding provider."""
        try:
            import openai
            self.openai_client = openai
            self.model_name = "text-embedding-3-small"
            self.embedding_dim = 1536
        except ImportError:
            logger.warning("OpenAI not available, falling back to local provider")
            self._init_local()
    
    def _init_local(self) -> None:
        """Initialize local embedding provider."""
        self.embedding_dim = 384  # Standard for small local models
        self.model_name = "local-sentence-transformer"
        
        # Simple word embedding simulation for demo
        # In production, use actual sentence transformers
        self.word_vectors = self._load_simple_word_vectors()
    
    def _load_simple_word_vectors(self) -> Dict[str, np.ndarray]:
        """Load simple word vectors for local embedding."""
        # This is a simplified implementation
        # In production, load pre-trained word embeddings
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
            vector = np.array([
                ((hash_val >> i) & 0xFF) / 255.0 - 0.5
                for i in range(self.embedding_dim)
            ], dtype=np.float32)
            vectors[term] = vector / np.linalg.norm(vector)
        
        return vectors
    
    def get_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for text.
        
        Args:
            text: Text to embed
            
        Returns:
            Numpy array representing the text embedding
        """
        # Check cache first
        if self.cache_enabled:
            cache_key = self._get_cache_key(text)
            if cache_key in self.embedding_cache:
                return self.embedding_cache[cache_key]
        
        # Generate embedding based on provider
        if self.provider == "openai":
            embedding = self._get_openai_embedding(text)
        else:
            embedding = self._get_local_embedding(text)
        
        # Cache the result
        if self.cache_enabled:
            cache_key = self._get_cache_key(text)
            self.embedding_cache[cache_key] = embedding
        
        return embedding
    
    def _get_openai_embedding(self, text: str) -> np.ndarray:
        """Get embedding from OpenAI."""
        try:
            response = self.openai_client.embeddings.create(
                model=self.model_name,
                input=text
            )
            return np.array(response.data[0].embedding, dtype=np.float32)
        except Exception as e:
            logger.error(f"OpenAI embedding failed: {e}")
            # Fallback to local provider
            return self._get_local_embedding(text)
    
    def _get_local_embedding(self, text: str) -> np.ndarray:
        """Get embedding from local provider."""
        # Simple word-based embedding
        words = text.lower().split()
        word_vectors = []
        
        for word in words:
            # Remove punctuation and get clean word
            clean_word = ''.join(c for c in word if c.isalnum())
            
            if clean_word in self.word_vectors:
                word_vectors.append(self.word_vectors[clean_word])
            else:
                # Create random vector for unknown words
                hash_val = int(hashlib.md5(clean_word.encode()).hexdigest(), 16)
                vector = np.array([
                    ((hash_val >> i) & 0xFF) / 255.0 - 0.5
                    for i in range(self.embedding_dim)
                ], dtype=np.float32)
                vector = vector / np.linalg.norm(vector)
                word_vectors.append(vector)
        
        if word_vectors:
            # Average the word vectors
            embedding = np.mean(word_vectors, axis=0)
            return embedding / np.linalg.norm(embedding)
        else:
            # Return zero vector for empty input
            return np.zeros(self.embedding_dim, dtype=np.float32)
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        return hashlib.md5(text.encode()).hexdigest()
    
    def get_embeddings_batch(self, texts: List[str]) -> List[np.ndarray]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of numpy arrays representing embeddings
        """
        embeddings = []
        
        if self.provider == "openai":
            # Process in batches for OpenAI
            batch_size = 100
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_embeddings = self._get_openai_embeddings_batch(batch)
                embeddings.extend(batch_embeddings)
        else:
            # Process individually for local provider
            for text in texts:
                embedding = self.get_embedding(text)
                embeddings.append(embedding)
        
        return embeddings
    
    def _get_openai_embeddings_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Get batch embeddings from OpenAI."""
        try:
            response = self.openai_client.embeddings.create(
                model=self.model_name,
                input=texts
            )
            return [
                np.array(item.embedding, dtype=np.float32)
                for item in response.data
            ]
        except Exception as e:
            logger.error(f"OpenAI batch embedding failed: {e}")
            # Fallback to individual processing
            return [self.get_embedding(text) for text in texts]
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Cosine similarity score (0-1)
        """
        embedding1 = self.get_embedding(text1)
        embedding2 = self.get_embedding(text2)
        
        return self._cosine_similarity(embedding1, embedding2)
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def find_similar_texts(
        self, 
        query: str, 
        candidates: List[str], 
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Find most similar texts to query from candidates.
        
        Args:
            query: Query text
            candidates: List of candidate texts
            top_k: Number of top results to return
            
        Returns:
            List of (text, similarity_score) tuples
        """
        query_embedding = self.get_embedding(query)
        
        similarities = []
        for candidate in candidates:
            candidate_embedding = self.get_embedding(candidate)
            similarity = self._cosine_similarity(query_embedding, candidate_embedding)
            similarities.append((candidate, similarity))
        
        # Sort by similarity (descending) and return top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def cluster_texts(
        self, 
        texts: List[str], 
        num_clusters: int = 5,
        max_iterations: int = 100
    ) -> List[List[str]]:
        """
        Cluster texts using k-means on embeddings.
        
        Args:
            texts: List of texts to cluster
            num_clusters: Number of clusters to create
            max_iterations: Maximum iterations for k-means
            
        Returns:
            List of clusters, each containing text indices
        """
        if len(texts) < num_clusters:
            # Not enough texts for clustering
            return [[i] for i in range(len(texts))]
        
        # Get all embeddings
        embeddings = np.array(self.get_embeddings_batch(texts))
        
        # Simple k-means clustering
        clusters = self._kmeans_clustering(embeddings, num_clusters, max_iterations)
        
        # Convert cluster indices to text groups
        text_clusters = [[] for _ in range(num_clusters)]
        for text_idx, cluster_idx in enumerate(clusters):
            text_clusters[cluster_idx].append(text_idx)
        
        return text_clusters
    
    def _kmeans_clustering(
        self, 
        embeddings: np.ndarray, 
        num_clusters: int, 
        max_iterations: int
    ) -> List[int]:
        """Simple k-means clustering implementation."""
        n_samples = embeddings.shape[0]
        
        # Initialize random centroids
        np.random.seed(42)
        centroid_indices = np.random.choice(n_samples, num_clusters, replace=False)
        centroids = embeddings[centroid_indices]
        
        for iteration in range(max_iterations):
            # Assign each sample to nearest centroid
            distances = np.zeros((n_samples, num_clusters))
            for i in range(num_clusters):
                distances[:, i] = np.linalg.norm(embeddings - centroids[i], axis=1)
            
            cluster_assignments = np.argmin(distances, axis=1)
            
            # Update centroids
            new_centroids = np.zeros((num_clusters, embeddings.shape[1]))
            for i in range(num_clusters):
                cluster_points = embeddings[cluster_assignments == i]
                if len(cluster_points) > 0:
                    new_centroids[i] = np.mean(cluster_points, axis=0)
                else:
                    new_centroids[i] = centroids[i]
            
            # Check for convergence
            if np.allclose(centroids, new_centroids):
                break
            
            centroids = new_centroids
        
        return cluster_assignments.tolist()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get embedding cache statistics."""
        return {
            'cache_enabled': self.cache_enabled,
            'cache_size': len(self.embedding_cache),
            'provider': self.provider,
            'model_name': self.model_name,
            'embedding_dim': self.embedding_dim
        }
    
    def clear_cache(self) -> None:
        """Clear the embedding cache."""
        self.embedding_cache.clear()
        logger.info("Embedding cache cleared")
    
    def save_cache(self, file_path: str) -> None:
        """Save embedding cache to file."""
        if not self.cache_enabled:
            logger.warning("Cache is disabled, cannot save")
            return
        
        cache_data = {
            'provider': self.provider,
            'model_name': self.model_name,
            'embedding_dim': self.embedding_dim,
            'cache': {
                key: vector.tolist() for key, vector in self.embedding_cache.items()
            }
        }
        
        with open(file_path, 'w') as f:
            json.dump(cache_data, f)
        
        logger.info(f"Cache saved to {file_path}")
    
    def load_cache(self, file_path: str) -> None:
        """Load embedding cache from file."""
        if not self.cache_enabled:
            logger.warning("Cache is disabled, cannot load")
            return
        
        try:
            with open(file_path, 'r') as f:
                cache_data = json.load(f)
            
            # Validate cache data
            if cache_data.get('provider') != self.provider:
                logger.warning("Cache provider mismatch, cannot load")
                return
            
            if cache_data.get('embedding_dim') != self.embedding_dim:
                logger.warning("Cache embedding dimension mismatch, cannot load")
                return
            
            # Load cache
            self.embedding_cache = {
                key: np.array(vector, dtype=np.float32)
                for key, vector in cache_data['cache'].items()
            }
            
            logger.info(f"Cache loaded from {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to load cache: {e}")


# Global embedding service instance
if HAS_NUMPY:
    embedding_service = EmbeddingService()
else:
    from knowledge.embedding_service import EmbeddingService as _FallbackEmbeddingService

    EmbeddingService = _FallbackEmbeddingService
    embedding_service = EmbeddingService()
