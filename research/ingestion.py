from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List

from knowledge import KnowledgeGraph, V2_KNOWLEDGE_CATEGORIES


@dataclass
class IngestedSource:
    source_id: str
    kind: str  # e.g. "github", "pdf", "docs", "transcript"
    path: str | None = None


@dataclass
class ResearchIngestionService:
    """V2 research ingestion scaffold.

    This service defines the contract for ingesting external
    artifacts (GitHub repos, PDFs, docs, transcripts) and
    projecting them into the V2 knowledge graph categories.
    """

    graph: KnowledgeGraph

    def ingest(self, source: IngestedSource, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
        # This is intentionally a stub: it records a node per-source
        # and tags it with basic metadata plus categories. Real
        # extractors will later interpret and expand content.
        meta = dict(meta or {})
        meta.update({
            "kind": source.kind,
            "path": source.path,
            "categories": list(V2_KNOWLEDGE_CATEGORIES),
        })
        node_id = f"source:{source.source_id}"
        self.graph.add_node(node_id, meta)
        return {"node_id": node_id, "metadata": meta}

    def list_categories(self) -> List[str]:
        return list(V2_KNOWLEDGE_CATEGORIES)
