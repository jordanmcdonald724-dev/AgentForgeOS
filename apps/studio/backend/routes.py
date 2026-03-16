"""Studio module backend API routes.

Provides endpoints for the AI development Studio workspace:
- project status and metadata
- workspace file listing (via the bridge layer)
- triggering agent pipeline runs
"""

from __future__ import annotations

from fastapi import APIRouter, Query

router = APIRouter(prefix="/studio", tags=["studio"])


@router.get("/status")
async def studio_status():
    """Return the Studio module's current operational status."""
    return {
        "success": True,
        "data": {
            "module": "studio",
            "status": "ready",
            "description": "AI development environment — ready for agent tasks",
        },
        "error": None,
    }


@router.get("/workspace")
async def list_workspace(
    path: str = Query(".", description="Relative path within the workspace to list"),
):
    """List entries in a workspace directory via the bridge.

    Accepts an optional ``path`` query parameter (defaults to ``"."`` for the
    workspace root) so the frontend file browser can navigate into
    subdirectories without a separate endpoint.
    """
    try:
        from bridge.bridge_server import BridgeServer

        server = BridgeServer()
        result = server.list_directory(path)
        return {"success": True, "data": result, "error": None}
    except Exception as exc:
        return {"success": False, "data": None, "error": str(exc)}
