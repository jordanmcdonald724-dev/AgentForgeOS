"""Assets module backend API routes.

Provides endpoints for the Assets manager:
- listing generated assets (images, audio, files)
- retrieving asset metadata
"""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter

router = APIRouter(prefix="/assets", tags=["assets"])

_asset_registry: List[Dict[str, Any]] = []


@router.get("/status")
async def assets_status():
    """Return the Assets module's current operational status."""
    return {
        "success": True,
        "data": {
            "module": "assets",
            "status": "ready",
            "description": "Generated asset manager",
            "asset_count": len(_asset_registry),
        },
        "error": None,
    }


@router.get("/list")
async def list_assets():
    """Return all registered assets."""
    return {"success": True, "data": _asset_registry, "error": None}


@router.post("/register")
async def register_asset(body: Dict[str, Any] = {}):
    """Register a newly generated asset (image, audio, etc.)."""
    import datetime

    asset: Dict[str, Any] = {
        "id": len(_asset_registry) + 1,
        "type": body.get("type", "unknown"),
        "path": body.get("path", ""),
        "source": body.get("source", ""),
        "metadata": body.get("metadata", {}),
        "registered_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    _asset_registry.append(asset)
    return {"success": True, "data": asset, "error": None}


@router.post("/generate")
async def generate_asset(body: Dict[str, Any] = {}):
    import datetime
    import uuid

    asset_type_value = body.get("type", "image")
    asset_type = asset_type_value if isinstance(asset_type_value, str) and asset_type_value else "image"
    ext = "png" if asset_type == "image" else "txt"
    asset_id = f"asset_{uuid.uuid4().hex[:12]}"
    path_value = body.get("path")
    asset_path = (
        path_value
        if isinstance(path_value, str) and path_value.strip()
        else f"generated/{asset_id}.{ext}"
    )
    asset: Dict[str, Any] = {
        "id": asset_id,
        "type": asset_type,
        "path": asset_path,
        "source": body.get("source", "generated"),
        "metadata": body.get("metadata", {}),
        "prompt": body.get("prompt", ""),
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    _asset_registry.append(asset)
    return {"success": True, "data": asset, "error": None}
