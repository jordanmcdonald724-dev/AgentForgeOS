"""Sandbox module backend API routes.

Provides endpoints for the isolated agent experimentation environment:
- experiment execution (stub)
- experiment history listing
"""

from __future__ import annotations

import datetime
import uuid
from typing import Any, Dict, List

from fastapi import APIRouter

router = APIRouter(prefix="/sandbox", tags=["sandbox"])

# In-memory experiment log — replaced by persistence when MongoDB is available.
_experiments: List[Dict[str, Any]] = []


@router.get("/status")
async def sandbox_status():
    """Return the Sandbox module's current operational status."""
    return {
        "success": True,
        "data": {
            "module": "sandbox",
            "status": "ready",
            "description": "Isolated agent experimentation sandbox",
            "total_experiments": len(_experiments),
        },
        "error": None,
    }


@router.get("/experiments")
async def list_experiments():
    """Return all recorded sandbox experiments."""
    return {"success": True, "data": list(_experiments), "error": None}


@router.post("/run")
async def run_experiment(body: Dict[str, Any] = {}):
    """Record and enqueue a sandbox experiment (stub)."""
    entry: Dict[str, Any] = {
        "id": str(uuid.uuid4())[:8],
        "prompt": body.get("prompt", ""),
        "provider": body.get("provider", "ollama"),
        "status": "queued",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    _experiments.append(entry)
    return {"success": True, "data": entry, "error": None}


@router.delete("/experiments/{experiment_id}")
async def delete_experiment(experiment_id: str):
    """Remove a sandbox experiment by id."""
    global _experiments
    before = len(_experiments)
    _experiments = [e for e in _experiments if e.get("id") != experiment_id]
    removed = before - len(_experiments)
    return {"success": True, "data": {"removed": removed}, "error": None}
