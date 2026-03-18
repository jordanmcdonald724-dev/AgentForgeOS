"""Builds module backend API routes.

Provides endpoints for the CI/CD pipeline manager:
- pipeline run listing and status
- triggering a new build
"""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter

router = APIRouter(prefix="/builds", tags=["builds"])

# In-memory build log — replaced by MongoDB persistence when available.
_build_log: List[Dict[str, Any]] = []


@router.get("/status")
async def builds_status():
    """Return the Builds module's current operational status."""
    return {
        "success": True,
        "data": {
            "module": "builds",
            "status": "ready",
            "description": "CI/CD pipeline manager",
            "total_runs": len(_build_log),
        },
        "error": None,
    }


@router.get("/runs")
async def list_runs():
    """Return all recorded build runs."""
    return {"success": True, "data": _build_log, "error": None}


@router.post("/trigger")
async def trigger_build(body: Dict[str, Any] = {}):
    """Record a new build run (stub — real pipeline integration coming)."""
    import datetime

    entry: Dict[str, Any] = {
        "id": len(_build_log) + 1,
        "project": body.get("project", "unknown"),
        "status": "queued",
        "triggered_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    _build_log.append(entry)
    return {"success": True, "data": entry, "error": None}
