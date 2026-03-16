from typing import Any, Dict, List, Optional, Tuple


class KnowledgeGraph:
    """Handles knowledge graph relationships for system memory."""

    def __init__(self) -> None:
        self._entities: Dict[str, Dict[str, Any]] = {}
        self._relations: List[Tuple[str, str, str, Dict[str, Any]]] = []

    def add_entity(self, entity_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Store or update an entity with optional metadata."""
        self._entities[entity_id] = metadata or {}

    def add_relation(
        self,
        subject: str,
        predicate: str,
        obj: str,
        *,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Connect two entities with a labeled relationship."""
        self._relations.append((subject, predicate, obj, metadata or {}))

    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Return metadata for an entity if it exists."""
        return self._entities.get(entity_id)

    def relations_for(self, entity_id: str) -> List[Dict[str, Any]]:
        """Return all relations that involve the specified entity."""
        related: List[Dict[str, Any]] = []
        for subject, predicate, obj, metadata in self._relations:
            if subject == entity_id or obj == entity_id:
                related.append(
                    {
                        "subject": subject,
                        "predicate": predicate,
                        "object": obj,
                        "metadata": metadata,
                    }
                )
        return related

    def list_entities(self) -> List[str]:
        """Return all stored entity identifiers."""
        return list(self._entities.keys())
