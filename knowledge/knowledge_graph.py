from typing import Any, Dict, List, Set, Tuple


class KnowledgeGraph:
    """Lightweight in-memory knowledge graph scaffold for Phase 7."""

    def __init__(self) -> None:
        self._nodes: Dict[str, Dict[str, Any]] = {}
        self._edges: Set[Tuple[str, str]] = set()

    def add_node(self, node_id: str, payload: Dict[str, Any]) -> None:
        """Store or update a node with metadata."""
        self._nodes[node_id] = payload

    def add_edge(self, source: str, target: str) -> None:
        """
        Create a directed edge between two nodes.

        Raises:
            ValueError: if either node is missing.
        """
        if source not in self._nodes or target not in self._nodes:
            raise ValueError("Both source and target nodes must exist before adding an edge.")
        self._edges.add((source, target))

    def get_node(self, node_id: str) -> Dict[str, Any]:
        """Return node metadata if it exists."""
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
