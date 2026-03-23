from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict

from infrastructure.local_bridge import LocalBridge, LocalBridgeSettings
from infrastructure.model_router import ModelRouter, RouteKind
from models.settings import SystemSettings


router = APIRouter()


class SettingsPayload(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    fal_api_key: str | None = None
    openai_api_key: str | None = None
    default_model_provider: str | None = None
    model_temperature: float | None = None
    max_tokens: int | None = None

    mongo_url: str | None = None
    db_name: str | None = None
    neo4j_uri: str | None = None
    neo4j_user: str | None = None
    neo4j_password: str | None = None
    qdrant_host: str | None = None
    qdrant_port: str | None = None

    unity_editor_path: str | None = None
    unreal_editor_path: str | None = None
    default_game_engine: str | None = None
    unity_path: str | None = None

    docker_enabled: bool | None = None
    sandbox_image: str | None = None
    memory_limit: str | None = None
    cpu_limit: str | None = None
    timeout: int | None = None

    log_level: str | None = None
    max_concurrent_tasks: int | None = None
    enable_realtime_updates: bool | None = None
    enable_telemetry: bool | None = None

    local_project_root: str | None = None
    local_bridge_port: int | None = None
    auto_launch_editor: bool | None = None
    enable_simulation_mode: bool | None = None


# In-memory settings instance for now; can be replaced by a persistent
# provider later without changing the API surface.
_settings = SystemSettings()

def _settings_to_dict() -> Dict[str, Any]:
    data = asdict(_settings)
    if "unity_editor_path" in data and "unity_path" not in data:
        data["unity_path"] = data["unity_editor_path"]
    if "unreal_editor_path" in data and "unreal_path" not in data:
        data["unreal_path"] = data["unreal_editor_path"]
    return data


@router.get("/v2/settings", tags=["v2-infrastructure"])
async def get_settings() -> Dict[str, Any]:
    return {"success": True, "data": _settings_to_dict(), "error": None}


@router.post("/v2/settings", tags=["v2-infrastructure"])
async def update_settings(body: SettingsPayload) -> Dict[str, Any]:
    global _settings

    payload = body.model_dump(exclude_none=True)
    if "unity_path" in payload and "unity_editor_path" not in payload:
        payload["unity_editor_path"] = payload["unity_path"]
    for field, value in payload.items():
        if field == "unity_path":
            continue
        setattr(_settings, field, value)

    return await get_settings()


@router.get("/v2/local_bridge/projects", tags=["v2-infrastructure"])
async def list_local_projects() -> Dict[str, Any]:
    if _settings.local_project_root:
        bridge = LocalBridge(settings=LocalBridgeSettings(root=Path(_settings.local_project_root)))
    else:
        bridge = LocalBridge(settings=LocalBridgeSettings())
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
