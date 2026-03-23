from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class EngineConfigPaths:
    exe_base: Path
    resources_dir: Path
    config_dir: Path
    engine_config_path: Path
    engine_config_user_path: Path
    logs_dir: Path
    engine_logs_path: Path


def _get_exe_base_path() -> Path:
    if getattr(sys, "frozen", False):
        try:
            return Path(sys.executable).resolve().parent
        except Exception:
            return Path.cwd().resolve()
    return Path(__file__).resolve().parent.parent.parent


def _resources_root(exe_base: Path) -> Path:
    root = exe_base / "resources"
    nested = exe_base / "resources" / "resources"
    if (nested / "config.json").is_file() or (nested / "providers.json").is_file():
        return nested
    if (root / "config.json").is_file() or (root / "providers.json").is_file():
        return root
    return root


def get_paths(exe_base: Optional[Path] = None) -> EngineConfigPaths:
    base = exe_base or _get_exe_base_path()
    resources_dir = _resources_root(base)
    config_dir = resources_dir / "config"
    logs_dir = resources_dir / "logs"
    engine_config_path = config_dir / "engine_config.json"
    engine_config_user_path = config_dir / "engine_config.user.json"
    engine_logs_path = logs_dir / "engine_logs.json"
    return EngineConfigPaths(
        exe_base=base,
        resources_dir=resources_dir,
        config_dir=config_dir,
        engine_config_path=engine_config_path,
        engine_config_user_path=engine_config_user_path,
        logs_dir=logs_dir,
        engine_logs_path=engine_logs_path,
    )


def ensure_engine_config_exists(exe_base: Optional[Path] = None) -> EngineConfigPaths:
    paths = get_paths(exe_base)
    paths.config_dir.mkdir(parents=True, exist_ok=True)
    paths.logs_dir.mkdir(parents=True, exist_ok=True)
    if not paths.engine_config_path.is_file():
        default_src = Path(__file__).resolve().parent.parent.parent / "resources" / "config" / "engine_config.json"
        if default_src.is_file():
            paths.engine_config_path.write_text(default_src.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            paths.engine_config_path.write_text("{}", encoding="utf-8")
    if not paths.engine_logs_path.is_file():
        paths.engine_logs_path.write_text("[]", encoding="utf-8")
    return paths


def _deep_merge(base: Any, override: Any) -> Any:
    if isinstance(base, dict) and isinstance(override, dict):
        out = dict(base)
        for k, v in override.items():
            if k in out:
                out[k] = _deep_merge(out[k], v)
            else:
                out[k] = v
        return out
    if isinstance(override, list):
        return list(override)
    if override is None:
        return base
    return override


def load_engine_config(exe_base: Optional[Path] = None) -> Dict[str, Any]:
    paths = ensure_engine_config_exists(exe_base)
    base_cfg: Dict[str, Any] = {}
    user_cfg: Dict[str, Any] = {}
    try:
        raw = json.loads(paths.engine_config_path.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            base_cfg = raw
    except Exception:
        base_cfg = {}
    try:
        if paths.engine_config_user_path.is_file():
            raw_u = json.loads(paths.engine_config_user_path.read_text(encoding="utf-8"))
            if isinstance(raw_u, dict):
                user_cfg = raw_u
    except Exception:
        user_cfg = {}
    merged = _deep_merge(base_cfg, user_cfg)
    return merged if isinstance(merged, dict) else {}


def load_engine_config_user_override(exe_base: Optional[Path] = None) -> Dict[str, Any]:
    paths = ensure_engine_config_exists(exe_base)
    try:
        if not paths.engine_config_user_path.is_file():
            return {}
        raw = json.loads(paths.engine_config_user_path.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else {}
    except Exception:
        return {}


def save_engine_config_user_override(override: Dict[str, Any], exe_base: Optional[Path] = None) -> None:
    paths = ensure_engine_config_exists(exe_base)
    paths.config_dir.mkdir(parents=True, exist_ok=True)
    paths.engine_config_user_path.write_text(json.dumps(override, indent=2), encoding="utf-8")


def get_env_override(key: str) -> str:
    return os.getenv(key, "")

