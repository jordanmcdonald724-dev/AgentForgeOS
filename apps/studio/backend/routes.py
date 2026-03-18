"""Studio module backend API routes.

Provides endpoints for the AI development Studio workspace:
- module status and metadata
- workspace file listing (via the bridge layer)

These routes are mounted by the engine under ``/api/modules`` so the
final paths are:
- ``GET /api/modules/studio/status``
- ``GET /api/modules/studio/workspace``
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import APIRouter, Query

from bridge.bridge_server import BridgeServer

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/studio", tags=["studio"])


@router.get("/status")
async def studio_status() -> Dict[str, Any]:
    """Return basic status information for the Studio module.

    The response follows the standard API envelope used throughout the
    system API contracts: ``success``, ``data``, and ``error`` keys.
    """

    try:
        server = BridgeServer()
        return {
            "success": True,
            "data": {"module": "studio", "bridge_root": str(server.root)},
            "error": None,
        }
    except Exception as exc:  # pragma: no cover - defensive path
        logger.warning("Studio status check failed: %s", exc)
        return {"success": False, "data": None, "error": str(exc)}


@router.get("/workspace")
async def list_workspace(
    path: str = Query(".", description="Relative path within the workspace to list"),
) -> Dict[str, Any]:
    """List entries in a workspace directory via the bridge.

    The bridge root is resolved by :class:`BridgeServer` (typically from the
    ``BRIDGE_ROOT`` environment variable or ``./workspace``). The *path*
    argument is interpreted as a path relative to that root.
    """

    try:
        server = BridgeServer()
        result = server.list_directory(path)
        if result.get("success"):
            return {"success": True, "data": result, "error": None}
        # Propagate structured bridge error while keeping 200 response code
        return {"success": False, "data": None, "error": result.get("error")}
    except Exception as exc:  # pragma: no cover - defensive path
        logger.warning("Studio workspace listing failed for path '%s': %s", path, exc)
        return {"success": False, "data": None, "error": str(exc)}