"""Bridge API routes — expose the bridge layer over HTTP.

Provides REST endpoints so the frontend (and other consumers) can see and
interact with the project filesystem through the bridge.

Endpoints:
    GET  /bridge/health  — bridge status
    GET  /bridge/list    — list directory contents
    GET  /bridge/read    — read a single file
    POST /bridge/sync    — return a recursive snapshot of the project tree
"""

from __future__ import annotations

import logging
from typing import Dict, List

from fastapi import APIRouter, Query

from bridge.bridge_server import BridgeServer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bridge", tags=["bridge"])

_bridge: BridgeServer | None = None


def _get_bridge() -> BridgeServer:
    """Lazy-initialise a module-level BridgeServer singleton."""
    global _bridge
    if _bridge is None:
        _bridge = BridgeServer()
    return _bridge


# ------------------------------------------------------------------ #
# GET /bridge/health                                                   #
# ------------------------------------------------------------------ #

@router.get("/health")
async def bridge_health():
    """Return the bridge's operational status."""
    bridge = _get_bridge()
    root_exists = bridge.root.is_dir()
    return {
        "success": True,
        "data": {
            "status": "ok" if root_exists else "degraded",
            "root": str(bridge.root),
            "root_exists": root_exists,
        },
        "error": None,
    }


# ------------------------------------------------------------------ #
# GET /bridge/list?path=.                                              #
# ------------------------------------------------------------------ #

@router.get("/list")
async def bridge_list(
    path: str = Query(".", description="Relative path within the bridge root"),
):
    """List the contents of a directory inside the bridge root."""
    bridge = _get_bridge()
    result = bridge.list_directory(path)
    if result["success"]:
        return {"success": True, "data": result, "error": None}
    return {"success": False, "data": None, "error": result.get("error")}


# ------------------------------------------------------------------ #
# GET /bridge/read?path=<file>                                         #
# ------------------------------------------------------------------ #

@router.get("/read")
async def bridge_read(
    path: str = Query(..., description="Relative file path within the bridge root"),
):
    """Read a single file inside the bridge root."""
    bridge = _get_bridge()
    result = bridge.read_file(path)
    if result["success"]:
        return {"success": True, "data": result, "error": None}
    return {"success": False, "data": None, "error": result.get("error")}


# ------------------------------------------------------------------ #
# POST /bridge/sync                                                    #
# ------------------------------------------------------------------ #

def _walk_tree(bridge: BridgeServer, rel: str = ".") -> List[Dict]:
    """Recursively walk the bridge root and return a flat file list."""
    result = bridge.list_directory(rel)
    if not result["success"]:
        return []

    items: List[Dict] = []
    for entry in result.get("entries", []):
        child_path = entry["name"] if rel == "." else f"{rel}/{entry['name']}"
        items.append({"path": child_path, "type": entry["type"], "size": entry.get("size")})
        if entry["type"] == "directory":
            items.extend(_walk_tree(bridge, child_path))
    return items


@router.post("/sync")
async def bridge_sync():
    """Return a recursive snapshot of every file in the project tree.

    This is the ``/bridge/sync`` endpoint described in the system API
    contracts.  It walks the bridge root and returns all visible files
    and directories so that callers can build a complete project view.
    """
    bridge = _get_bridge()
    if not bridge.root.is_dir():
        return {
            "success": False,
            "data": None,
            "error": "Bridge root does not exist",
        }
    tree = _walk_tree(bridge)
    return {
        "success": True,
        "data": {"root": str(bridge.root), "entries": tree},
        "error": None,
    }
