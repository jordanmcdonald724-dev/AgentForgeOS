from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel

from infrastructure.local_bridge import LocalBridge, LocalBridgeSettings
from infrastructure.model_router import ModelRouter, RouteKind
from models.settings import SystemSettings


router = APIRouter()


class SettingsPayload(BaseModel):
    unity_path: str | None = None
    unreal_path: str | None = None
    local_project_root: str | None = None
    local_bridge_port: int | None = None
    auto_launch_editor: bool | None = None
    enable_simulation_mode: bool | None = None


# In-memory settings instance for now; can be replaced by a persistent
# provider later without changing the API surface.
_settings = SystemSettings()


@router.get("/v2/settings", tags=["v2-infrastructure"])
async def get_settings() -> Dict[str, Any]:
    return {
        "success": True,
        "data": {
            "unity_path": str(_settings.unity_path) if _settings.unity_path else None,
            "unreal_path": str(_settings.unreal_path) if _settings.unreal_path else None,
            "local_project_root": str(_settings.local_project_root),
            "local_bridge_port": _settings.local_bridge_port,
            "auto_launch_editor": _settings.auto_launch_editor,
            "enable_simulation_mode": _settings.enable_simulation_mode,
        },
        "error": None,
    }


@router.post("/v2/settings", tags=["v2-infrastructure"])
async def update_settings(body: SettingsPayload) -> Dict[str, Any]:
    global _settings

    if body.unity_path is not None:
        _settings.unity_path = Path(body.unity_path)
    if body.unreal_path is not None:
        _settings.unreal_path = Path(body.unreal_path)
    if body.local_project_root is not None:
        _settings.local_project_root = Path(body.local_project_root)
    if body.local_bridge_port is not None:
        _settings.local_bridge_port = body.local_bridge_port
    if body.auto_launch_editor is not None:
        _settings.auto_launch_editor = body.auto_launch_editor
    if body.enable_simulation_mode is not None:
        _settings.enable_simulation_mode = body.enable_simulation_mode

    return await get_settings()


@router.get("/v2/local_bridge/projects", tags=["v2-infrastructure"])
async def list_local_projects() -> Dict[str, Any]:
    bridge = LocalBridge(settings=LocalBridgeSettings(root=_settings.local_project_root))
    projects: List[str] = [str(p) for p in bridge.list_projects()]
    return {"success": True, "data": {"projects": projects}, "error": None}


@router.get("/v2/model_routing/routes", tags=["v2-infrastructure"])
async def list_model_routes() -> Dict[str, Any]:
    router_impl = ModelRouter()
    routes = {
        "code": router_impl.select_route(RouteKind.CODE),
        "image": router_impl.select_route(RouteKind.IMAGE),
        "audio": router_impl.select_route(RouteKind.AUDIO),
        "three_d": router_impl.select_route(RouteKind.THREE_D),
        "generic": router_impl.select_route(RouteKind.GENERIC),
    }
    return {"success": True, "data": {"routes": routes}, "error": None}
