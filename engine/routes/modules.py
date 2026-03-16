from fastapi import APIRouter

from control.module_registry import module_registry

router = APIRouter()


@router.get("/modules", tags=["modules"])
async def list_modules():
    """Expose active modules for the Studio UI."""
    manifests = module_registry.list_manifests()
    modules = []
    for module_id, manifest in manifests.items():
        modules.append(
            {
                "id": module_id,
                "name": manifest.get("name", module_id),
                "version": manifest.get("version"),
                "description": manifest.get("description"),
            }
        )
    return {"success": True, "data": modules, "error": None}
