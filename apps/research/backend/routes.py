"""Research module backend API routes.

Provides endpoints for the Research workspace:
- knowledge search (via the knowledge/embedding layer)
- storing and retrieving research notes
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel
import os
import importlib
import hashlib

from knowledge import EmbeddingService, KnowledgeGraph, KnowledgeVectorStore
from research.ingestion import IngestedSource, ResearchIngestionService

router = APIRouter(prefix="/research", tags=["research"])

_notes: List[Dict[str, Any]] = []

_kb_graph: KnowledgeGraph | None = None
_kb_vectors: KnowledgeVectorStore | None = None
_kb_embeddings: EmbeddingService | None = None
_ingestion: ResearchIngestionService | None = None


def _workspace_path(request: Request) -> Path:
    raw = getattr(request.app.state, "workspace_path", "") or (Path.home() / "Documents" / "AgentForgeOS")
    return Path(raw)


def _ensure_kb(request: Request) -> tuple[KnowledgeGraph, KnowledgeVectorStore, EmbeddingService, ResearchIngestionService]:
    global _kb_graph, _kb_vectors, _kb_embeddings, _ingestion
    if _kb_graph is not None and _kb_vectors is not None and _kb_embeddings is not None and _ingestion is not None:
        return _kb_graph, _kb_vectors, _kb_embeddings, _ingestion

    workspace = _workspace_path(request)
    knowledge_dir = workspace / "knowledge"
    embeddings_dir = workspace / "embeddings"
    knowledge_dir.mkdir(parents=True, exist_ok=True)
    embeddings_dir.mkdir(parents=True, exist_ok=True)

    _kb_graph = KnowledgeGraph(persist_path=knowledge_dir / "knowledge_graph.json")
    _kb_vectors = KnowledgeVectorStore(persist_path=embeddings_dir / "knowledge_vectors.json")
    _kb_embeddings = EmbeddingService()
    _ingestion = ResearchIngestionService(graph=_kb_graph)
    return _kb_graph, _kb_vectors, _kb_embeddings, _ingestion


@router.get("/status")
async def research_status():
    """Return the Research module's current operational status."""
    return {
        "success": True,
        "data": {
            "module": "research",
            "status": "ready",
            "description": "Knowledge research workspace",
            "notes_count": len(_notes),
        },
        "error": None,
    }


@router.get("/notes")
async def list_notes():
    """Return all stored research notes."""
    return {"success": True, "data": _notes, "error": None}


@router.post("/notes")
async def add_note(request: Request, body: Dict[str, Any] = {}):
    """Add a research note and index it in the embedding service."""
    import datetime

    note: Dict[str, Any] = {
        "id": len(_notes) + 1,
        "title": body.get("title", "Untitled"),
        "content": body.get("content", ""),
        "tags": body.get("tags", []),
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    _notes.append(note)

    try:
        graph, vectors, embed, _ = _ensure_kb(request)
        node_id = f"note:{note['id']}"
        payload = {"type": "note", **note}
        graph.add_node(node_id, payload)
        vectors.add(node_id, {"id": node_id, "content": note["content"], "title": note["title"], "tags": note["tags"]}, embed.get_embedding(note["content"]))
    except Exception:
        return {"success": False, "data": None, "error": "note indexing failed"}

    return {"success": True, "data": note, "error": None}


@router.post("/search")
async def search_knowledge(request: Request, body: Dict[str, Any] = {}):
    """Search indexed knowledge using the embedding service."""
    query = body.get("query", "")
    if not query:
        return {"success": False, "data": None, "error": "query is required"}
    try:
        _, vectors, embed, _ = _ensure_kb(request)
        top_k = body.get("top_k", 5)
        try:
            k = max(1, min(int(top_k), 25))
        except Exception:
            k = 5
        results = vectors.query(embed.get_embedding(str(query)), top_k=k)
        return {"success": True, "data": results, "error": None}
    except Exception as exc:
        return {"success": False, "data": None, "error": str(exc)}

@router.get("/search")
async def search_knowledge_get(request: Request, query: str = Query("", min_length=1), top_k: int = Query(5, ge=1, le=25)):
    try:
        _, vectors, embed, _ = _ensure_kb(request)
        results = vectors.query(embed.get_embedding(query), top_k=top_k)
        return {"success": True, "data": results, "error": None}
    except Exception as exc:
        return {"success": False, "data": None, "error": str(exc)}


class IngestRequest(BaseModel):
    id: str
    kind: str
    path: str | None = None
    label: str | None = None


@router.post("/ingest")
async def ingest_source(request: Request, body: IngestRequest):
    graph, vectors, embed, ingestion = _ensure_kb(request)
    src = IngestedSource(source_id=body.id, kind=body.kind, path=body.path)
    info = await ingestion.ingest(src, meta={"label": body.label} if body.label else None)
    try:
        node_id = str(info.get("node_id") or f"source:{body.id}")
        meta = dict(info.get("metadata") or {})
        content = "\n".join([str(body.label or ""), str(body.kind or ""), str(body.path or ""), str(meta.get("pattern_summary") or "")]).strip()
        if content:
            vectors.add(node_id, {"id": node_id, "content": content, **meta}, embed.get_embedding(content))
    except Exception:
        pass
    return {"success": True, "data": info, "error": None}


class VideoIngestRequest(BaseModel):
    video_source: str


class InternetScanRequest(BaseModel):
    query: str
    num_results: int = 10


@router.post("/video")
async def ingest_video(request: Request, payload: VideoIngestRequest):
    """Ingest a video file or YouTube URL, transcribe it, and store in Knowledge Graph."""
    output_dir = "./temp"
    os.makedirs(output_dir, exist_ok=True)

    try:
        try:
            video_mod = importlib.import_module("research.video_processor")
            process_video = getattr(video_mod, "process_video")
        except Exception as exc:
            raise HTTPException(
                status_code=501,
                detail=f"Video ingestion is not available in this build: {exc}",
            )

        transcription = process_video(payload.video_source, output_dir)
        
        # Create a unique ID for the video source
        source_id = hashlib.md5(payload.video_source.encode()).hexdigest()
        node_id = f"video:{source_id}"
        
        # Save to Knowledge Graph
        graph, vectors, embed, _ = _ensure_kb(request)
        metadata = {
            "type": "video_transcription",
            "source": payload.video_source,
            "content": transcription,
            "category": "research_insights"
        }
        graph.add_node(node_id, metadata)
        
        vectors.add(node_id, {"id": node_id, **metadata}, embed.get_embedding(transcription))
        
        return {"success": True, "transcription": transcription, "node_id": node_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Add route for internet scanning
@router.post("/scan")
async def scan_internet(request: Request, payload: InternetScanRequest):
    """Scan the internet, fetch content from results, and store in Knowledge Graph."""
    try:
        from research.internet_scanner import perform_web_search, fetch_webpage_content

        results = perform_web_search(payload.query, payload.num_results)
        
        enriched_results = []
        graph, vectors, embed, _ = _ensure_kb(request)
        for res in results[:3]: # Fetch content for top 3 results to avoid timeout
            try:
                content = fetch_webpage_content(res['link'])
                res['content'] = content[:2000] # Limit content size
                
                # Create a unique ID for the webpage
                page_id = hashlib.md5(res['link'].encode()).hexdigest()
                node_id = f"web:{page_id}"
                
                # Save to Knowledge Graph
                metadata = {
                    "type": "web_content",
                    "title": res['title'],
                    "source": res['link'],
                    "content": res['content'],
                    "query": payload.query,
                    "category": "research_insights"
                }
                graph.add_node(node_id, metadata)
                
                vectors.add(node_id, {"id": node_id, **metadata}, embed.get_embedding(res["content"]))
                enriched_results.append(res)
            except Exception:
                continue
                
        return {"success": True, "results": results, "enriched_count": len(enriched_results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
