"""Persistent knowledge graph — Phase 7 Knowledge System.

All nodes and edges are kept in memory and optionally persisted to a JSON
file on disk so the graph survives engine restarts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


class KnowledgeGraph:
    """Lightweight knowledge graph with optional JSON file persistence.

    When *persist_path* is supplied the graph is loaded from disk on
    construction and saved after every mutating call.
    """

    def __init__(self, persist_path: Optional[Path] = None) -> None:
        self._nodes: Dict[str, Dict[str, Any]] = {}
        self._edges: Set[Tuple[str, str]] = set()
        self._persist_path: Optional[Path] = (
            Path(persist_path) if persist_path else None
        )
        if self._persist_path and self._persist_path.exists():
            self._load()

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def _load(self) -> None:
        """Populate the in-memory graph from the JSON file on disk."""
        try:
            raw = json.loads(self._persist_path.read_text(encoding="utf-8"))
            self._nodes = raw.get("nodes", {})
            self._edges = {tuple(e) for e in raw.get("edges", [])}
        except Exception:
            pass  # Corrupt or empty file — start fresh

    def _save(self) -> None:
        """Flush the current graph to disk as JSON."""
        if not self._persist_path:
            return
        self._persist_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "nodes": self._nodes,
            "edges": [list(e) for e in self._edges],
        }
        self._persist_path.write_text(
            json.dumps(payload, indent=2), encoding="utf-8"
        )

    # ------------------------------------------------------------------
    # Public API (maintains original interface)
    # ------------------------------------------------------------------

    def add_node(self, node_id: str, payload: Dict[str, Any]) -> None:
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

    def get_node(self, node_id: str) -> Dict[str, Any]:
        """Return node metadata if it exists, or an empty dict if missing."""
        return self._nodes.get(node_id, {})

    def neighbors(self, node_id: str) -> List[str]:
        """Return adjacent nodes from the given source."""
        return [t for s, t in self._edges if s == node_id]

    def node_count(self) -> int:
        """Return the number of nodes stored."""
        return len(self._nodes)

    def edge_count(self) -> int:
        """Return the number of edges stored."""
        return len(self._edges)
