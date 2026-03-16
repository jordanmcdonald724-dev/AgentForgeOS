from __future__ import annotations

from typing import Any, Dict, Optional


class ModuleRegistry:
    """Runtime registry for active modules."""

    def __init__(self) -> None:
        self._modules: Dict[str, Dict[str, Any]] = {}

    def register_module(self, module_id: str, module_instance: Any, manifest: Dict[str, Any]) -> None:
        """Store a module instance and its manifest."""
        self._modules[module_id] = {"instance": module_instance, "manifest": manifest}

    def get_module(self, module_id: str) -> Optional[Dict[str, Any]]:
        return self._modules.get(module_id)

    def list_manifests(self) -> Dict[str, Dict[str, Any]]:
        """Expose manifest data for all registered modules."""
        return {module_id: data["manifest"] for module_id, data in self._modules.items()}

    def instances(self) -> Dict[str, Any]:
        """Expose the live module instances."""
        return {module_id: data["instance"] for module_id, data in self._modules.items()}


module_registry = ModuleRegistry()
