"""Persistent knowledge graph — Phase 7 Knowledge System.

Enhanced with Neo4j-compatible interface and Qdrant vector integration.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import hashlib
from datetime import datetime, timezone
from typing import Any, cast


class KnowledgeGraph:
    """Enhanced knowledge graph with Neo4j-compatible interface and vector integration.
    
    Provides both local JSON persistence and interfaces for Neo4j/Qdrant integration.
    """

    def __init__(self, persist_path: Path | None = None) -> None:
        self._nodes: dict[str, dict[str, Any]] = {}
        self._edges: set[tuple[str, str]] = set()
        self._persist_path: Path | None = Path(persist_path) if persist_path else None
        self._neo4j_enabled = os.getenv('NEO4J_ENABLED', 'false').lower() == 'true'
        self._qdrant_enabled = os.getenv('QDRANT_ENABLED', 'false').lower() == 'true'
        
        # Initialize database connections if enabled
        self._neo4j_driver = None
        self._qdrant_client = None
        
        if self._neo4j_enabled:
            self._init_neo4j()
        if self._qdrant_enabled:
            self._init_qdrant()
            
        if self._persist_path and self._persist_path.exists():
            self._load()

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def _load(self) -> None:
        """Populate the in-memory graph from the JSON file on disk."""
        persist_path = self._persist_path
        if persist_path is None:
            return
        try:
            raw: Any = json.loads(persist_path.read_text(encoding="utf-8"))
            nodes = raw.get("nodes", {}) if isinstance(raw, dict) else {}
            self._nodes = nodes if isinstance(nodes, dict) else {}
            self._edges = {tuple(e) for e in raw.get("edges", [])}
        except Exception:
            pass  # Corrupt or empty file — start fresh

    def _save(self) -> None:
        """Flush the current graph to disk as JSON."""
        persist_path = self._persist_path
        if persist_path is None:
            return
        persist_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "nodes": self._nodes,
            "edges": [list(e) for e in self._edges],
        }
        persist_path.write_text(
            json.dumps(payload, indent=2), encoding="utf-8"
        )

    # ------------------------------------------------------------------
    # Database initialization
    # ------------------------------------------------------------------

    def _init_neo4j(self) -> None:
        """Initialize Neo4j connection if available."""
        try:
            neo4j_mod = __import__("neo4j")
            GraphDatabase: Any = getattr(neo4j_mod, "GraphDatabase")
            neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
            neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
            neo4j_password = os.getenv('NEO4J_PASSWORD', 'password')
            
            self._neo4j_driver = GraphDatabase.driver(
                neo4j_uri, 
                auth=(neo4j_user, neo4j_password)
            )
        except ImportError:
            print("Neo4j driver not installed, falling back to local storage")
            self._neo4j_enabled = False
        except Exception as e:
            print(f"Failed to connect to Neo4j: {e}")
            self._neo4j_enabled = False

    def _init_qdrant(self) -> None:
        """Initialize Qdrant connection if available."""
        try:
            qdrant_mod = __import__("qdrant_client")
            QdrantClient: Any = getattr(qdrant_mod, "QdrantClient")
            qdrant_host = os.getenv('QDRANT_HOST', 'localhost')
            qdrant_port = int(os.getenv('QDRANT_PORT', '6333'))
            
            self._qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port)
            
            # Create collection if it doesn't exist
            collection_name = "agentforge_knowledge"
            try:
                self._qdrant_client.get_collection(collection_name)
            except:
                models_mod = __import__("qdrant_client.models", fromlist=["Distance", "VectorParams"])
                Distance: Any = getattr(models_mod, "Distance")
                VectorParams: Any = getattr(models_mod, "VectorParams")
                self._qdrant_client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
                )
        except ImportError:
            print("Qdrant client not installed, falling back to local storage")
            self._qdrant_enabled = False
        except Exception as e:
            print(f"Failed to connect to Qdrant: {e}")
            self._qdrant_enabled = False

    # ------------------------------------------------------------------
    # Enhanced public API with database integration
    # ------------------------------------------------------------------

    def _add_node_with_integrations(self, node_id: str, payload: dict[str, Any]) -> None:
        """Store or update a node with metadata."""
        # Add timestamp and hash
        payload['created_at'] = datetime.now(timezone.utc).isoformat()
        payload['content_hash'] = hashlib.md5(
            json.dumps(payload, sort_keys=True).encode()
        ).hexdigest()
        
        self._nodes[node_id] = payload
        
        # Sync to Neo4j if enabled
        if self._neo4j_enabled and self._neo4j_driver:
            self._add_node_neo4j(node_id, payload)
        
        # Sync to Qdrant if enabled and node has text content
        if self._qdrant_enabled and self._qdrant_client and 'content' in payload:
            self._add_vector_qdrant(node_id, payload)
        
        self._save()

    def _add_edge_with_integrations(self, source: str, target: str) -> None:
        """Create a directed edge between two nodes."""
        if source not in self._nodes or target not in self._nodes:
            raise ValueError(
                "Both source and target nodes must exist before adding an edge."
            )
        self._edges.add((source, target))
        
        # Sync to Neo4j if enabled
        if self._neo4j_enabled and self._neo4j_driver:
            self._add_edge_neo4j(source, target)
        
        self._save()

    def find_similar_projects(self, command: str, features: list[str]) -> list[dict[str, Any]]:
        """Find similar projects based on command and features."""
        similar_projects: list[dict[str, Any]] = []
        
        # Search in local storage
        for node_id, node_data in self._nodes.items():
            if node_data.get('type') == 'project':
                project_features = node_data.get('features', [])
                project_command = node_data.get('command', '')
                
                # Simple similarity scoring
                feature_overlap = len(set(features) & set(project_features))
                command_similarity = self._text_similarity(command, project_command)
                
                if feature_overlap > 0 or command_similarity > 0.3:
                    similar_projects.append({
                        'project_id': node_id,
                        'similarity_score': (feature_overlap * 0.7 + command_similarity * 0.3),
                        'project_data': node_data
                    })
        
        # Search in Qdrant if enabled
        if self._qdrant_enabled and self._qdrant_client:
            try:
                from knowledge.embedding_service import EmbeddingService
                embedding_service = EmbeddingService()
                query_vector = embedding_service.get_embedding(command)
                
                search_results = self._qdrant_client.search(
                    collection_name="agentforge_knowledge",
                    query_vector=query_vector,
                    limit=5,
                    query_filter={"must": [{"key": "type", "match": {"value": "project"}}]}
                )
                
                for result in search_results:
                    similar_projects.append({
                        'project_id': result.id,
                        'similarity_score': result.score,
                        'project_data': result.payload
                    })
            except Exception as e:
                print(f"Qdrant search failed: {e}")
        
        # Sort by similarity and return top results
        def _similarity_key(item: dict[str, Any]) -> float:
            score = item.get("similarity_score", 0.0)
            return float(score) if isinstance(score, (int, float)) else 0.0

        similar_projects.sort(key=_similarity_key, reverse=True)
        return similar_projects[:5]

    def _text_similarity(self, text1: str, text2: str) -> float:
        """Simple text similarity using word overlap."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)

    def _add_node_neo4j(self, node_id: str, payload: dict[str, Any]) -> None:
        """Add node to Neo4j database."""
        driver = self._neo4j_driver
        if driver is None:
            return
        try:
            with driver.session() as session:
                query = """
                MERGE (n:Node {id: $id})
                SET n += $payload
                """
                session.run(query, id=node_id, payload=payload)
        except Exception as e:
            print(f"Failed to add node to Neo4j: {e}")

    def _add_edge_neo4j(self, source: str, target: str) -> None:
        """Add edge to Neo4j database."""
        driver = self._neo4j_driver
        if driver is None:
            return
        try:
            with driver.session() as session:
                query = """
                MATCH (a:Node {id: $source}), (b:Node {id: $target})
                MERGE (a)-[:RELATES_TO]->(b)
                """
                session.run(query, source=source, target=target)
        except Exception as e:
            print(f"Failed to add edge to Neo4j: {e}")

    def _add_vector_qdrant(self, node_id: str, payload: dict[str, Any]) -> None:
        """Add vector representation to Qdrant."""
        client = self._qdrant_client
        if client is None:
            return
        try:
            from knowledge.embedding_service import EmbeddingService
            embedding_service = EmbeddingService()
            
            content = payload.get('content', '')
            vector = embedding_service.get_embedding(content)
            
            client.upsert(
                collection_name="agentforge_knowledge",
                points=[
                    {
                        "id": node_id,
                        "vector": vector,
                        "payload": payload
                    }
                ]
            )
        except Exception as e:
            print(f"Failed to add vector to Qdrant: {e}")

    # ------------------------------------------------------------------
    # Original API methods (unchanged for compatibility)
    # ------------------------------------------------------------------

    def add_node(self, node_id: str, payload: dict[str, Any]) -> None:
        """Store or update a node with metadata."""
        self._nodes[node_id] = payload
        self._save()

    def add_edge(self, source: str, target: str) -> None:
        """Create a directed edge between two nodes.

        Raises:
            ValueError: if either node is missing.
        """
        if source not in self._nodes or target not in self._nodes:
            raise ValueError(
                "Both source and target nodes must exist before adding an edge."
            )
        self._edges.add((source, target))
        self._save()

    def get_node(self, node_id: str) -> dict[str, Any]:
        """Return node metadata if it exists, or an empty dict if missing."""
        return self._nodes.get(node_id, {})

    def neighbors(self, node_id: str) -> list[str]:
        """Return adjacent nodes from the given source."""
        return [t for s, t in self._edges if s == node_id]

    def node_count(self) -> int:
        """Return the number of nodes stored."""
        return len(self._nodes)

    def edge_count(self) -> int:
        """Return the number of edges stored."""
        return len(self._edges)

    def query(self, cypher_query: str) -> list[dict[str, Any]]:
        """Execute Cypher-like query on local graph (simplified)."""
        # Very basic query parsing - in production, use proper Cypher parser
        results: list[dict[str, Any]] = []
        
        if "MATCH (n)" in cypher_query and "RETURN" in cypher_query:
            # Simple return all nodes
            for node_id, node_data in self._nodes.items():
                results.append({'id': node_id, **node_data})
        
        return results

    def close_connections(self) -> None:
        """Close database connections."""
        if self._neo4j_driver:
            cast(Any, self._neo4j_driver).close()
        # Qdrant client doesn't need explicit closing
