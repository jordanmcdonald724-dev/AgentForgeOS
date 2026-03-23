from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
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
    """V2 research ingestion service.

    Ingests external artifacts (GitHub repos, PDFs, docs, transcripts)
    and projects them into the V2 knowledge graph categories while
    extracting actionable patterns.
    """

    graph: KnowledgeGraph

    async def ingest(self, source: IngestedSource, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """Ingests a source and performs pattern extraction to 'learn' from it."""
        from .pattern_extractor import AdvancedPatternExtractor
        
        meta = dict(meta or {})
        meta.update({
            "kind": source.kind,
            "path": source.path,
            "categories": list(V2_KNOWLEDGE_CATEGORIES),
            "ingested_at": datetime.now(timezone.utc).isoformat()
        })
        
        node_id = f"source:{source.source_id}"
        
        # Perform real extraction if a local path is provided
        patterns = {}
        if source.path and Path(source.path).exists() and Path(source.path).is_dir():
            extractor = AdvancedPatternExtractor(knowledge_graph=self.graph)
            try:
                patterns = await extractor.extract_patterns_from_project(source.path)
                meta["pattern_summary"] = {k: len(v) for k, v in patterns.items()}
                meta["has_extracted_patterns"] = True
            except Exception as e:
                meta["extraction_error"] = str(e)
                meta["has_extracted_patterns"] = False
        
        self.graph.add_node(node_id, meta)
        
        return {
            "node_id": node_id, 
            "metadata": meta,
            "patterns_found": sum(len(v) for v in patterns.values()) if patterns else 0
        }

    def list_categories(self) -> List[str]:
        return list(V2_KNOWLEDGE_CATEGORIES)
