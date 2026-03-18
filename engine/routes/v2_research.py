from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel

from knowledge.knowledge_graph import KnowledgeGraph
from knowledge import V2_KNOWLEDGE_CATEGORIES
from research.ingestion import IngestedSource, ResearchIngestionService


router = APIRouter()


_graph = KnowledgeGraph()
_ingestion = ResearchIngestionService(graph=_graph)


class IngestRequest(BaseModel):
    id: str
    kind: str
    path: str | None = None
    label: str | None = None


@router.get("/v2/research/categories", tags=["v2-research"])
async def list_categories() -> Dict[str, Any]:
    return {"success": True, "data": {"categories": list(V2_KNOWLEDGE_CATEGORIES)}, "error": None}


@router.post("/v2/research/ingest", tags=["v2-research"])
async def ingest_source(body: IngestRequest) -> Dict[str, Any]:
    src = IngestedSource(source_id=body.id, kind=body.kind, path=body.path)
    info = _ingestion.ingest(src, meta={"label": body.label})
    return {"success": True, "data": info, "error": None}


@router.get("/v2/research/nodes", tags=["v2-research"])
async def list_nodes() -> Dict[str, Any]:
    # Expose a thin view over the knowledge graph nodes.
    nodes: List[Dict[str, Any]] = []
    for node_id, payload in _graph._nodes.items():  # type: ignore[attr-defined]
        nodes.append({"id": node_id, **payload})
    return {"success": True, "data": {"nodes": nodes}, "error": None}
