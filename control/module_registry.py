from __future__ import annotations

import threading
from types import MappingProxyType
from typing import Any, Dict, Mapping, Optional


class ModuleRegistry:
    """Runtime registry for active modules (singleton)."""

    _instance: Optional["ModuleRegistry"] = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return
        self._modules: Dict[str, Dict[str, Any]] = {}
        self._initialized = True

    def register_module(self, module_id: str, module_instance: Any, manifest: Dict[str, Any]) -> None:
        """Store a module instance and its manifest."""
        with self._lock:
            self._modules[module_id] = {"instance": module_instance, "manifest": manifest}

    def get_module(self, module_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._modules.get(module_id)

    def get_all_modules(self) -> Mapping[str, Dict[str, Any]]:
        """Expose all registered module entries as a read-only view."""
        with self._lock:
            return MappingProxyType(dict(self._modules))

    def clear(self) -> None:
        """Reset registry contents (primarily for testing)."""
        with self._lock:
            self._modules.clear()

    # Backwards-compatible helpers
    def get_instance(self, module_id: str) -> Optional[Any]:
        entry = self.get_module(module_id)
        return entry["instance"] if entry else None

    def get_manifest(self, module_id: str) -> Optional[Dict[str, Any]]:
        entry = self.get_module(module_id)
        return entry["manifest"] if entry else None

    def list_manifests(self) -> Dict[str, Dict[str, Any]]:
        """Expose manifest data for all registered modules."""
        modules = self.get_all_modules()
        return {module_id: data["manifest"] for module_id, data in modules.items()}

    def instances(self) -> Dict[str, Any]:
        """Expose the live module instances."""
        modules = self.get_all_modules()
        return {module_id: data["instance"] for module_id, data in modules.items()}


module_registry = ModuleRegistry()
