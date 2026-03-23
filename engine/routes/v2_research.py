from __future__ import annotations

import hashlib
from pathlib import Path
from uuid import uuid4
from typing import Any, Dict, List

from fastapi import APIRouter, File, Request, UploadFile
from pydantic import BaseModel

from knowledge.knowledge_graph import KnowledgeGraph
from knowledge import V2_KNOWLEDGE_CATEGORIES
from research.ingestion import IngestedSource, ResearchIngestionService


router = APIRouter()

_graph: KnowledgeGraph | None = None
_ingestion: ResearchIngestionService | None = None

def _get_ingestion(request: Request) -> ResearchIngestionService:
    global _graph, _ingestion
    if _ingestion is not None and _graph is not None:
        return _ingestion
    workspace = getattr(request.app.state, "workspace_path", "")
    persist_path = None
    if isinstance(workspace, str) and workspace:
        persist_path = (Path(workspace) / "knowledge" / "v2_knowledge_graph.json")
    _graph = KnowledgeGraph(persist_path=persist_path)
    _ingestion = ResearchIngestionService(graph=_graph)
    return _ingestion


def _get_graph(request: Request) -> KnowledgeGraph:
    _get_ingestion(request)
    assert _graph is not None
    return _graph


class IngestRequest(BaseModel):
    id: str
    kind: str
    path: str | None = None
    label: str | None = None


class IngestUrlRequest(BaseModel):
    url: str
    label: str | None = None
    kind: str | None = None


@router.get("/v2/research/categories", tags=["v2-research"])
async def list_categories() -> Dict[str, Any]:
    return {"success": True, "data": {"categories": list(V2_KNOWLEDGE_CATEGORIES)}, "error": None}


@router.post("/v2/research/ingest", tags=["v2-research"])
async def ingest_source(body: IngestRequest, request: Request) -> Dict[str, Any]:
    ingestion = _get_ingestion(request)
    src = IngestedSource(source_id=body.id, kind=body.kind, path=body.path)
    info = await ingestion.ingest(src, meta={"label": body.label})
    return {"success": True, "data": info, "error": None}


def _workspace_temp_dir(request: Request) -> Path:
    raw = getattr(request.app.state, "workspace_path", "")
    ws = Path(raw) if isinstance(raw, str) and raw else (Path.home() / "Documents" / "AgentForgeOS")
    out = ws / "temp" / "research"
    out.mkdir(parents=True, exist_ok=True)
    return out


@router.post("/v2/research/ingest_url", tags=["v2-research"])
async def ingest_url(body: IngestUrlRequest, request: Request) -> Dict[str, Any]:
    url = str(body.url or "").strip()
    if not url:
        return {"success": False, "data": None, "error": "url is required"}

    url_l = url.lower()
    is_http = url_l.startswith("http://") or url_l.startswith("https://")
    if not is_http:
        return {"success": False, "data": None, "error": "url must start with http:// or https://"}

    label = str(body.label or "").strip() or url
    kind = str(body.kind or "").strip().lower()

    ingestion = _get_ingestion(request)
    graph = _get_graph(request)

    try:
        if kind == "video" or "youtube.com" in url_l or "youtu.be" in url_l:
            try:
                from research.video_processor import process_video
            except Exception as exc:
                return {"success": False, "data": None, "error": f"video ingestion unavailable: {exc}"}

            tmp = _workspace_temp_dir(request)
            transcription = process_video(url, str(tmp))
            source_id = hashlib.md5(url.encode("utf-8")).hexdigest()
            node_id = f"video:{source_id}"
            graph.add_node(
                node_id,
                {
                    "type": "video_transcription",
                    "source": url,
                    "label": label,
                    "content": transcription,
                    "category": "research_insights",
                },
            )
            return {"success": True, "data": {"node_id": node_id, "label": label, "kind": "video"}, "error": None}

        from research.internet_scanner import fetch_webpage_content

        content = fetch_webpage_content(url)
        if not isinstance(content, str):
            content = str(content)
        content = content.strip()
        if len(content) > 20000:
            content = content[:20000]
        source_id = hashlib.md5(url.encode("utf-8")).hexdigest()
        node_id = f"web:{source_id}"
        graph.add_node(
            node_id,
            {
                "type": "web_content",
                "source": url,
                "label": label,
                "content": content,
                "category": "research_insights",
            },
        )
        return {"success": True, "data": {"node_id": node_id, "label": label, "kind": "web"}, "error": None}
    except Exception as exc:
        return {"success": False, "data": None, "error": str(exc)}


@router.post("/v2/research/upload", tags=["v2-research"])
async def upload_and_ingest_file(request: Request, file: UploadFile = File(...)) -> Dict[str, Any]:
    temp_dir = _workspace_temp_dir(request)
    filename = str(file.filename or "upload.bin")
    safe_name = filename.replace("\\", "_").replace("/", "_").strip() or "upload.bin"
    dest = temp_dir / f"{uuid4().hex}_{safe_name}"

    content = await file.read()
    try:
        dest.write_bytes(content)
    except Exception as exc:
        return {"success": False, "data": None, "error": str(exc)}

    ingestion = _get_ingestion(request)
    source_id = f"file:{uuid4().hex}"
    src = IngestedSource(source_id=source_id, kind="file", path=str(dest))
    info = await ingestion.ingest(src, meta={"label": filename, "bytes": len(content)})
    return {"success": True, "data": info, "error": None}


@router.get("/v2/research/nodes", tags=["v2-research"])
async def list_nodes(request: Request) -> Dict[str, Any]:
    # Expose a thin view over the knowledge graph nodes.
    graph = _get_graph(request)
    nodes: List[Dict[str, Any]] = []
    for node_id, payload in graph._nodes.items():  # type: ignore[attr-defined]
        nodes.append({"id": node_id, **payload})
    return {"success": True, "data": {"nodes": nodes}, "error": None}
