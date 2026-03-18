"""Game Dev module backend API routes.

Provides endpoints for the game development assistant:
- project listing
- game design document generation (stub)
- scene scaffolding (stub)
"""

from __future__ import annotations

import datetime
import uuid
from typing import Any, Dict, List

from fastapi import APIRouter

router = APIRouter(prefix="/game_dev", tags=["game_dev"])

# In-memory project store — replaced by persistence when MongoDB is available.
_projects: List[Dict[str, Any]] = []


@router.get("/status")
async def game_dev_status():
    """Return the Game Dev module's current operational status."""
    return {
        "success": True,
        "data": {
            "module": "game_dev",
            "status": "ready",
            "description": "Game development assistant and asset pipeline",
            "total_projects": len(_projects),
        },
        "error": None,
    }


@router.get("/projects")
async def list_projects():
    """Return all recorded game projects."""
    return {"success": True, "data": list(_projects), "error": None}


@router.post("/design")
async def generate_design(body: Dict[str, Any] = {}):
    """Create a new game design document stub and register the project."""
    project: Dict[str, Any] = {
        "id": str(uuid.uuid4())[:8],
        "title": body.get("title", "Untitled Game"),
        "genre": body.get("genre", "unknown"),
        "platform": body.get("platform", "cross-platform"),
        "description": body.get("description", ""),
        "status": "design",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    _projects.append(project)
    return {"success": True, "data": project, "error": None}


@router.post("/scene")
async def scaffold_scene(body: Dict[str, Any] = {}):
    """Return a scene scaffolding stub for the given project."""
    scene: Dict[str, Any] = {
        "project_id": body.get("project_id", ""),
        "scene_name": body.get("scene_name", "MainScene"),
        "entities": [],
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    return {"success": True, "data": scene, "error": None}
