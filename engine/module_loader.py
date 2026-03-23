from __future__ import annotations

import importlib.util
import json
import logging
from pathlib import Path
from types import ModuleType
from typing import Any

from control.module_registry import ModuleRegistry, module_registry

logger = logging.getLogger(__name__)


def _sanitize_identifier(value: str) -> str | None:
    """
    Convert a string to a safe Python identifier fragment.

    - Keeps alphanumeric characters and underscores only.
    - Prefixes an underscore if the cleaned value would start with a digit.
    - Returns None when no valid characters remain.
    """
    cleaned = "".join(ch for ch in value if ch.isalnum() or ch == "_")
    if not cleaned:
        return None
    if cleaned[0].isdigit():
        cleaned = f"_{cleaned}"
    if not cleaned.isidentifier():
        return None
    return cleaned


def _load_manifest(manifest_path: Path) -> dict[str, Any] | None:
    try:
        with manifest_path.open() as fp:
            data: Any = json.load(fp)
            if isinstance(data, dict):
                return data
            logger.warning("manifest is not a JSON object: %s", manifest_path)
            return None
    except Exception as exc:  # pragma: no cover - defensive log path
        logger.warning("Failed to read manifest %s: %s", manifest_path, exc)
        return None


def _load_module_config(module_config_path: Path) -> dict[str, Any] | None:
    try:
        with module_config_path.open() as fp:
            data: Any = json.load(fp)
            if isinstance(data, dict):
                return data
            logger.warning("module config is not a JSON object: %s", module_config_path)
            return None
    except Exception as exc:  # pragma: no cover - defensive log path
        logger.warning("Failed to read module config %s: %s", module_config_path, exc)
        return None


def _coerce_module_config_to_manifest(module_config: dict[str, Any], module_dir: Path) -> dict[str, Any] | None:
    module_id = module_config.get("id") or module_config.get("name")
    if not isinstance(module_id, str) or not module_id.strip():
        return None
    version = module_config.get("version") if isinstance(module_config.get("version"), str) else "1.0"
    display_name = module_config.get("display_name") if isinstance(module_config.get("display_name"), str) else module_id
    entry = module_config.get("entry") if isinstance(module_config.get("entry"), str) else "module.py"
    cls = module_config.get("class") if isinstance(module_config.get("class"), str) else None
    if cls is None:
        candidate = _sanitize_identifier(module_id)
        cls = f"{candidate}Module" if candidate else "Module"
    manifest: dict[str, Any] = {
        "id": module_id,
        "name": display_name,
        "version": version,
        "entry": entry,
        "class": cls,
        **module_config,
    }
    return manifest


def _validate_manifest(manifest: dict[str, Any], module_dir: Path) -> bool:
    """
    Validate that a module manifest contains required non-empty string fields.

    Required fields: id, name, version, entry, class.
    Returns True when valid; otherwise logs a warning and returns False.
    """
    required = {"id": str, "name": str, "version": str, "entry": str, "class": str}
    missing: list[str] = []
    for field, expected_type in required.items():
        value = manifest.get(field)
        if not isinstance(value, expected_type):
            missing.append(field)
            continue
        if not value.strip():
            missing.append(field)
    if missing:
        logger.warning(
            "Skipping %s: manifest missing or invalid required fields: %s",
            module_dir.name,
            ", ".join(missing),
        )
        return False
    return True


def _import_module(entry_path: Path, module_name: str) -> ModuleType | None:
    try:
        spec = importlib.util.spec_from_file_location(module_name, entry_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    except Exception as exc:  # pragma: no cover - defensive log path
        logger.warning("Failed to import module from %s: %s", entry_path, exc)
    return None


def _resolve_module_class(mod: ModuleType, manifest: dict[str, Any]) -> type | None:
    """
    Resolve the module class using manifest hints and naming conventions.

    Candidate order:
    1. Value of manifest["class"] (if provided)
    2. "{name}Module" derived from manifest["name"]
    3. "{id}Module" derived from manifest["id"]
    4. "Module"
    Returns the first matching type or None.
    """
    preferred = manifest.get("class")
    candidates: list[str] = []
    if isinstance(preferred, str) and preferred.strip():
        candidates.append(preferred)
    name_value = manifest.get("name")
    if isinstance(name_value, str):
        cleaned_name = _sanitize_identifier(name_value)
        if cleaned_name:
            candidates.append(f"{cleaned_name}Module")
    id_value = manifest.get("id")
    if isinstance(id_value, str):
        cleaned_id = _sanitize_identifier(id_value)
        if cleaned_id:
            candidates.append(f"{cleaned_id}Module")
    candidates.append("Module")

    for candidate in candidates:
        if hasattr(mod, candidate):
            attr = getattr(mod, candidate)
            if isinstance(attr, type):
                return attr
    return None


def _discover_module_router(module_dir: Path):
    """
    Look for a ``backend/routes.py`` file inside the module directory and
    import it.  Returns the ``router`` attribute if present, otherwise None.
    """
    routes_path = module_dir / "backend" / "routes.py"
    if not routes_path.exists():
        return None
    try:
        module_name = f"apps.{module_dir.name}.backend.routes"
        spec = importlib.util.spec_from_file_location(module_name, routes_path)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            router = getattr(mod, "router", None)
            if router is not None:
                logger.info("Discovered backend router for module %s", module_dir.name)
                return router
    except Exception as exc:  # pragma: no cover - defensive log path
        logger.warning(
            "Failed to import backend routes for %s: %s", module_dir.name, exc
        )
    return None


def load_modules(
    apps_path: Path | None = None, registry: ModuleRegistry | None = None
) -> dict[str, object]:
    """
    Scan the /apps directory, load module manifests, import module classes,
    and register active modules in the runtime registry.

    Args:
        apps_path: Optional path override for the apps directory. Defaults to ../apps.
        registry: Optional ModuleRegistry to populate. Defaults to the global module_registry.

    Returns:
        Dict mapping module IDs to instantiated module objects.
    """
    apps_dir = apps_path or Path(__file__).resolve().parent.parent / "apps"
    active_registry = registry or module_registry
    loaded: dict[str, object] = {}

    if not apps_dir.exists():
        logger.warning("Apps directory not found at %s", apps_dir)
        return loaded

    for module_dir in apps_dir.iterdir():
        if not module_dir.is_dir():
            continue

        module_config_path = module_dir / "module_config.json"
        manifest_path = module_dir / "manifest.json"
        manifest: dict[str, Any] | None = None

        if module_config_path.exists():
            module_config = _load_module_config(module_config_path)
            manifest = _coerce_module_config_to_manifest(module_config or {}, module_dir)
        elif manifest_path.exists():
            manifest = _load_manifest(manifest_path)

        if not manifest:
            logger.info("Skipping %s: no module_config.json or manifest.json found", module_dir.name)
            continue

        if not _validate_manifest(manifest, module_dir):
            continue

        module_id = manifest["id"]
        entry_name = manifest["entry"]
        entry_path = module_dir / entry_name
        if not entry_path.exists():
            logger.warning("Entry file %s missing for module %s", entry_path, module_id)
            continue

        module_name = f"apps.{module_dir.name}.{entry_path.stem}"
        imported = _import_module(entry_path, module_name)
        if not imported:
            continue

        cls = _resolve_module_class(imported, manifest)
        if not cls:
            logger.warning("No module class found for %s", module_id)
            continue

        try:
            instance = cls()
            initializer = getattr(instance, "initialize", None)
            if callable(initializer):
                try:
                    initializer()
                except Exception as exc:  # pragma: no cover - defensive log path
                    logger.warning("Module %s initialize() failed: %s", module_id, exc)
                    continue

            # Attach backend router if present.
            router = _discover_module_router(module_dir)
            active_registry.register_module(module_id, instance, manifest)
            if router is not None:
                active_registry.register_module(
                    module_id,
                    instance,
                    {**manifest, "_router": router},
                )
            loaded[module_id] = instance
            logger.info("Loaded module %s", module_id)
        except Exception as exc:  # pragma: no cover - defensive log path
            logger.warning("Failed to instantiate module %s: %s", module_id, exc)

    return loaded


def collect_module_routers(
    apps_path: Path | None = None,
) -> list[object]:
    """
    Return a list of FastAPI routers discovered from all app module
    ``backend/routes.py`` files.  Used by the engine server to mount
    module-specific API routes under ``/api/modules``.
    """
    apps_dir = apps_path or Path(__file__).resolve().parent.parent / "apps"
    routers: list[object] = []
    if not apps_dir.exists():
        return routers
    for module_dir in sorted(apps_dir.iterdir()):
        if not module_dir.is_dir():
            continue
        router = _discover_module_router(module_dir)
        if router is not None:
            routers.append(router)
    return routers
