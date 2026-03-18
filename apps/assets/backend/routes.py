"""Assets module backend API routes.

Provides endpoints for the Assets manager:
- listing generated assets (images, audio, files)
- retrieving asset metadata
- generating image assets via configured providers (fal.ai or ComfyUI)
"""

from __future__ import annotations

import datetime
import os
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/assets", tags=["assets"])

_asset_registry: List[Dict[str, Any]] = []


class GenerateAssetRequest(BaseModel):
    prompt: str
    provider: Optional[str] = None  # "fal" | "comfyui" | None → auto-detect from env
    options: Optional[Dict[str, Any]] = None


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
    asset: Dict[str, Any] = {
        "id": str(uuid.uuid4())[:8],
        "type": body.get("type", "unknown"),
        "path": body.get("path", ""),
        "source": body.get("source", ""),
        "metadata": body.get("metadata", {}),
        "registered_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    _asset_registry.append(asset)
    return {"success": True, "data": asset, "error": None}


@router.post("/generate")
async def generate_asset(body: GenerateAssetRequest):
    """Generate an image asset via the configured provider.

    Provider selection order:
    1. ``body.provider`` if explicitly supplied (``"fal"`` or ``"comfyui"``)
    2. ``PROVIDER_IMAGE`` environment variable
    3. Falls back to a safe stub response when no real provider is available.

    The generated asset is automatically registered in the asset registry and
    the full asset record is returned.
    """
    provider_name = (
        body.provider
        or os.environ.get("PROVIDER_IMAGE", "")
    ).lower()

    result: Dict[str, Any] = {}
    error_msg: Optional[str] = None

    try:
        # Providers are imported lazily here because they carry optional
        # heavyweight dependencies (httpx is fine, but fal/comfyui may pull in
        # extra packages).  This keeps the asset module importable even when
        # those providers are not installed.
        if provider_name == "fal":
            from providers.fal_provider import FalImageProvider
            provider = FalImageProvider()
            result = await provider.generate(body.prompt, options=body.options)

        elif provider_name == "comfyui":
            from providers.comfyui_provider import ComfyUIImageProvider
            provider = ComfyUIImageProvider()
            result = await provider.generate(body.prompt, options=body.options)

        else:
            # No provider configured — return a descriptive stub so the UI
            # still receives a success=True response and can display guidance.
            result = {
                "stub": True,
                "message": (
                    "No image provider configured. "
                    "Set PROVIDER_IMAGE=fal or PROVIDER_IMAGE=comfyui in config/.env "
                    "and supply the corresponding API key / base URL."
                ),
                "prompt": body.prompt,
            }

    except Exception as exc:
        error_msg = str(exc)
        result = {"error_detail": error_msg, "prompt": body.prompt}

    if error_msg:
        return {"success": False, "data": result, "error": error_msg}

    # Auto-register the asset so it appears in /api/modules/assets/list.
    asset: Dict[str, Any] = {
        "id": str(uuid.uuid4())[:8],
        "type": "image",
        "path": result.get("url") or result.get("image_url") or "",
        "source": provider_name or "stub",
        "metadata": {
            "prompt": body.prompt,
            "provider": provider_name or "stub",
            "result": result,
        },
        "registered_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    _asset_registry.append(asset)
    return {"success": True, "data": asset, "error": None}
