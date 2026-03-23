from typing import Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel

from control.module_registry import module_registry

router = APIRouter()

class ModuleToggleRequest(BaseModel):
    module_id: str


@router.get("/modules", tags=["modules"])
async def list_modules():
    """Expose active modules for the Studio UI."""
    manifests = module_registry.list_manifests()
    modules = []
    for module_id, manifest in manifests.items():
        if not module_registry.is_enabled(module_id):
            continue
        modules.append(
            {
                "id": module_id,
                "name": manifest.get("name", module_id),
                "version": manifest.get("version"),
                "description": manifest.get("description"),
            }
        )
    return {"success": True, "data": modules, "error": None}


@router.post("/modules/load", tags=["modules"])
async def load_module(body: ModuleToggleRequest) -> Dict[str, Any]:
    module_id = (body.module_id or "").strip()
    if not module_id:
        return {"success": False, "data": None, "error": "module_id is required"}
    ok = module_registry.enable_module(module_id)
    if not ok:
        return {"success": False, "data": None, "error": "module not found"}
    return {"success": True, "data": {"module_id": module_id, "enabled": True}, "error": None}


@router.post("/modules/unload", tags=["modules"])
async def unload_module(body: ModuleToggleRequest) -> Dict[str, Any]:
    module_id = (body.module_id or "").strip()
    if not module_id:
        return {"success": False, "data": None, "error": "module_id is required"}
    ok = module_registry.disable_module(module_id)
    if not ok:
        return {"success": False, "data": None, "error": "module not found"}
    return {"success": True, "data": {"module_id": module_id, "enabled": False}, "error": None}
