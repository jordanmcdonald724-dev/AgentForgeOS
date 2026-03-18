"""Deployment module backend API routes.

Provides endpoints for the Deployment manager:
- listing deployments
- triggering a deployment action
- checking deployment status
- launching engine targets (web, Unity, Unreal)
"""

from __future__ import annotations

import datetime
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/deployment", tags=["deployment"])

_deployments: List[Dict[str, Any]] = []


class LaunchRequest(BaseModel):
    engine: str  # "web" | "unity" | "unreal"
    project: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None


@router.get("/status")
async def deployment_status():
    """Return the Deployment module's current operational status."""
    return {
        "success": True,
        "data": {
            "module": "deployment",
            "status": "ready",
            "description": "Project deployment manager",
            "total_deployments": len(_deployments),
        },
        "error": None,
    }


@router.get("/list")
async def list_deployments():
    """Return all recorded deployments."""
    return {"success": True, "data": _deployments, "error": None}


@router.post("/deploy")
async def trigger_deployment(body: Dict[str, Any] = {}):
    """Record a new deployment action (stub — real execution integration coming)."""
    deployment: Dict[str, Any] = {
        "id": str(uuid.uuid4())[:8],
        "target": body.get("target", "local"),
        "project": body.get("project", "unknown"),
        "version": body.get("version", "0.0.1"),
        "status": "pending",
        "initiated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    _deployments.append(deployment)
    return {"success": True, "data": deployment, "error": None}


@router.post("/launch")
async def launch_engine(body: LaunchRequest):
    """Queue a build launch for the specified engine target.

    Supported engines:
    - ``"web"``    — triggers a standard web build via the builds module
    - ``"unity"``  — stub (engine bridge not yet implemented)
    - ``"unreal"`` — stub (engine bridge not yet implemented)

    Returns a launch record with a ``status`` field of ``"queued"`` for
    real engines and ``"not_configured"`` for unimplemented targets.
    """
    engine = (body.engine or "").lower()

    _SUPPORTED = {"web"}
    _COMING_SOON = {"unity", "unreal"}

    if engine in _COMING_SOON:
        return {
            "success": True,
            "data": {
                "engine": engine,
                "status": "not_configured",
                "message": (
                    f"{engine.title()} engine bridge is not yet implemented. "
                    "Set the engine path in Settings once the bridge is ready."
                ),
                "project": body.project,
            },
            "error": None,
        }

    if engine not in _SUPPORTED:
        return {
            "success": False,
            "data": None,
            "error": f"Unknown engine '{engine}'. Supported values: web, unity, unreal.",
        }

    # "web" launch — record a deployment with target="web"
    deployment: Dict[str, Any] = {
        "id": str(uuid.uuid4())[:8],
        "target": "web",
        "project": body.project or "session_default",
        "version": "latest",
        "status": "queued",
        "initiated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    _deployments.append(deployment)

    return {
        "success": True,
        "data": {
            "engine": engine,
            "status": "queued",
            "deployment": deployment,
        },
        "error": None,
    }
