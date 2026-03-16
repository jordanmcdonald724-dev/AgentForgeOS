from __future__ import annotations

import importlib.util
import json
import logging
from pathlib import Path
from types import ModuleType
from typing import Dict, Optional

from control.module_registry import ModuleRegistry, module_registry

logger = logging.getLogger(__name__)


def _sanitize_identifier(value: str) -> Optional[str]:
    cleaned = "".join(ch for ch in value if ch.isalnum())
    if not cleaned:
        return None
    if cleaned[0].isdigit():
        cleaned = f"_{cleaned}"
    return cleaned


def _load_manifest(manifest_path: Path) -> Optional[Dict]:
    try:
        with manifest_path.open() as fp:
            return json.load(fp)
    except Exception as exc:  # pragma: no cover - defensive log path
        logger.warning("Failed to read manifest %s: %s", manifest_path, exc)
        return None


def _import_module(entry_path: Path, module_name: str) -> Optional[ModuleType]:
    try:
        spec = importlib.util.spec_from_file_location(module_name, entry_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    except Exception as exc:  # pragma: no cover - defensive log path
        logger.warning("Failed to import module from %s: %s", entry_path, exc)
    return None


def _resolve_module_class(mod: ModuleType, manifest: Dict) -> Optional[type]:
    """Resolve the module class using manifest hint or common naming conventions."""
    preferred = manifest.get("class")
    candidates = []
    if preferred:
        candidates.append(preferred)
    if "name" in manifest:
        cleaned_name = _sanitize_identifier(manifest["name"])
        if cleaned_name:
            candidates.append(f"{cleaned_name}Module")
    if "id" in manifest:
        cleaned_id = _sanitize_identifier(manifest["id"])
        if cleaned_id:
            candidates.append(f"{cleaned_id}Module")
    candidates.append("Module")

    for candidate in candidates:
        if hasattr(mod, candidate):
            attr = getattr(mod, candidate)
            if isinstance(attr, type):
                return attr
    return None


def load_modules(
    apps_path: Optional[Path] = None, registry: Optional[ModuleRegistry] = None
) -> Dict[str, object]:
    """
    Scan the /apps directory, load module manifests, import module classes,
    and register active modules in the runtime registry.
    """
    apps_dir = apps_path or Path(__file__).resolve().parent.parent / "apps"
    active_registry = registry or module_registry
    loaded: Dict[str, object] = {}

    if not apps_dir.exists():
        logger.warning("Apps directory not found at %s", apps_dir)
        return loaded

    for module_dir in apps_dir.iterdir():
        if not module_dir.is_dir():
            continue

        manifest_path = module_dir / "manifest.json"
        if not manifest_path.exists():
            logger.info("Skipping %s: no manifest.json found", module_dir.name)
            continue

        manifest = _load_manifest(manifest_path)
        if not manifest:
            continue

        module_id = manifest.get("id") or module_dir.name
        entry_name = manifest.get("entry", "module.py")
        entry_path = module_dir / entry_name
        if not entry_path.exists():
            logger.warning("Entry file %s missing for module %s", entry_path, module_id)
            continue

        module_name = f"apps.{module_dir.name}.{entry_name.replace('.py', '')}"
        imported = _import_module(entry_path, module_name)
        if not imported:
            continue

        cls = _resolve_module_class(imported, manifest)
        if not cls:
            logger.warning("No module class found for %s", module_id)
            continue

        try:
            instance = cls()
            if hasattr(instance, "initialize") and callable(getattr(instance, "initialize")):
                try:
                    instance.initialize()
                except Exception as exc:  # pragma: no cover - defensive log path
                    logger.warning("Module %s initialize() failed: %s", module_id, exc)
            active_registry.register_module(module_id, instance, manifest)
            loaded[module_id] = instance
            logger.info("Loaded module %s", module_id)
        except Exception as exc:  # pragma: no cover - defensive log path
            logger.warning("Failed to instantiate module %s: %s", module_id, exc)

    return loaded
