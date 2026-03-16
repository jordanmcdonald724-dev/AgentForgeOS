"""Service-layer knowledge graph with optional JSON file persistence.

Entities and relations are stored in memory and optionally persisted to a
JSON file on disk so the graph survives engine restarts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class KnowledgeGraph:
    """Knowledge graph with optional JSON file persistence."""

    def __init__(self, persist_path: Optional[Path] = None) -> None:
        self._entities: Dict[str, Dict[str, Any]] = {}
        self._relations: List[Tuple[str, str, str, Dict[str, Any]]] = []
        self._persist_path: Optional[Path] = (
            Path(persist_path) if persist_path else None
        )
        if self._persist_path and self._persist_path.exists():
            self._load()

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def _load(self) -> None:
        """Populate the graph from the JSON file on disk."""
        try:
            raw = json.loads(self._persist_path.read_text(encoding="utf-8"))
            self._entities = raw.get("entities", {})
            self._relations = [tuple(r) for r in raw.get("relations", [])]
        except Exception:
            pass  # Corrupt or missing file — start fresh

    def _save(self) -> None:
        """Flush the current graph to the JSON file on disk."""
        if not self._persist_path:
            return
        self._persist_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "entities": self._entities,
            "relations": [list(r) for r in self._relations],
        }
        self._persist_path.write_text(
            json.dumps(payload, indent=2), encoding="utf-8"
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_entity(self, entity_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Store or update an entity with optional metadata."""
        self._entities[entity_id] = metadata or {}
        self._save()

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
        self._save()

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
