"""Research module backend API routes.

Provides endpoints for the Research workspace:
- knowledge search (via the knowledge/embedding layer)
- storing and retrieving research notes
"""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os

router = APIRouter(prefix="/research", tags=["research"])

_notes: List[Dict[str, Any]] = []


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
async def add_note(body: Dict[str, Any] = {}):
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

    # Index in embedding service if available.
    try:
        from services.embedding_service import EmbeddingService

        _embedding_service = EmbeddingService()
        _embedding_service.add_text(
            f"note-{note['id']}",
            note["content"],
            metadata={"title": note["title"], "tags": note["tags"]},
        )
    except Exception:
        pass

    return {"success": True, "data": note, "error": None}


@router.post("/search")
async def search_knowledge(body: Dict[str, Any] = {}):
    """Search indexed knowledge using the embedding service."""
    query = body.get("query", "")
    if not query:
        return {"success": False, "data": None, "error": "query is required"}
    try:
        from services.embedding_service import EmbeddingService

        svc = EmbeddingService()
        results = svc.search(query, top_k=int(body.get("top_k", 5)))
        return {"success": True, "data": results, "error": None}
    except Exception as exc:
        return {"success": False, "data": None, "error": str(exc)}


class VideoIngestRequest(BaseModel):
    video_source: str


class InternetScanRequest(BaseModel):
    query: str
    num_results: int = 10


# Add a route for video ingestion
from research.video_processor import process_video

@router.post("/video")
def ingest_video(payload: VideoIngestRequest):
    """Ingest a video file or YouTube URL."""
    output_dir = "./temp"
    os.makedirs(output_dir, exist_ok=True)

    try:
        transcription = process_video(payload.video_source, output_dir)
        return {"success": True, "transcription": transcription}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Add route for internet scanning
from research.internet_scanner import perform_web_search, fetch_webpage_content

@router.post("/scan")
def scan_internet(payload: InternetScanRequest):
    """Scan the internet for information based on a query."""
    try:
        results = perform_web_search(payload.query, payload.num_results)
        return {"success": True, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
