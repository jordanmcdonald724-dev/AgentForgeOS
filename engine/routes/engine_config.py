from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from engine.router.config_loader import (
    get_paths,
    load_engine_config,
    load_engine_config_user_override,
    save_engine_config_user_override,
)


router = APIRouter()


class EngineConfigUpdate(BaseModel):
    enabled_engines: Optional[list[str]] = None
    api_keys: Optional[dict[str, str]] = None
    cost_controls: Optional[dict[str, Any]] = None
    task_routing: Optional[dict[str, Any]] = None
    engines: Optional[dict[str, Any]] = None


def _merge(base: Dict[str, Any], patch: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(base)
    for k, v in patch.items():
        if v is None:
            continue
        if isinstance(out.get(k), dict) and isinstance(v, dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = v
    return out


@router.get("/engine_config", tags=["engine_config"])
async def get_engine_config() -> dict[str, Any]:
    cfg = load_engine_config()
    raw_api_keys = cfg.get("api_keys")
    api_keys: Dict[str, Any] = raw_api_keys if isinstance(raw_api_keys, dict) else {}
    api_keys_set = {k: bool(isinstance(v, str) and v.strip()) for k, v in api_keys.items()}
    safe_cfg = dict(cfg)
    safe_cfg["api_keys"] = {k: "" for k in api_keys.keys()}
    return {"success": True, "data": {"config": safe_cfg, "api_keys_set": api_keys_set}, "error": None}


@router.post("/engine_config", tags=["engine_config"])
async def update_engine_config(body: EngineConfigUpdate) -> dict[str, Any]:
    existing_override = load_engine_config_user_override()
    update: Dict[str, Any] = {}
    if body.enabled_engines is not None:
        update["enabled_engines"] = list(body.enabled_engines)
    if isinstance(body.api_keys, dict):
        keys: Dict[str, Any] = {}
        for k, v in body.api_keys.items():
            if not isinstance(k, str):
                continue
            if not isinstance(v, str):
                continue
            keys[k] = v
        update["api_keys"] = keys
    if body.cost_controls is not None:
        update["cost_controls"] = body.cost_controls
    if body.task_routing is not None:
        update["task_routing"] = body.task_routing
    if body.engines is not None:
        update["engines"] = body.engines

    new_override = _merge(existing_override, update)
    save_engine_config_user_override(new_override)

    try:
        raw_keys = update.get("api_keys")
        api_keys = raw_keys if isinstance(raw_keys, dict) else {}
        if isinstance(api_keys, dict):
            fal_key = api_keys.get("fal")
            if isinstance(fal_key, str) and fal_key.strip():
                os.environ["FAL_API_KEY"] = fal_key.strip()
            openai_key = api_keys.get("openai")
            if isinstance(openai_key, str) and openai_key.strip():
                os.environ["OPENAI_API_KEY"] = openai_key.strip()
            anthropic_key = api_keys.get("anthropic")
            if isinstance(anthropic_key, str) and anthropic_key.strip():
                os.environ["ANTHROPIC_API_KEY"] = anthropic_key.strip()

            paths = get_paths()
            providers_path = paths.resources_dir / "providers.json"
            current: Dict[str, Any] = {}
            if providers_path.is_file():
                loaded = json.loads(providers_path.read_text(encoding="utf-8"))
                current = loaded if isinstance(loaded, dict) else {}
            if isinstance(fal_key, str) and fal_key.strip():
                fal_section = current.get("fal")
                fal_section = dict(fal_section) if isinstance(fal_section, dict) else {}
                fal_section["api_key"] = fal_key.strip()
                current["fal"] = fal_section
            if isinstance(openai_key, str) and openai_key.strip():
                openai_section = current.get("openai")
                openai_section = dict(openai_section) if isinstance(openai_section, dict) else {}
                openai_section["api_key"] = openai_key.strip()
                current["openai"] = openai_section
            providers_path.parent.mkdir(parents=True, exist_ok=True)
            providers_path.write_text(json.dumps(current, indent=2), encoding="utf-8")
    except Exception:
        pass
    cfg = load_engine_config()
    raw_api_keys = cfg.get("api_keys")
    api_keys: Dict[str, Any] = raw_api_keys if isinstance(raw_api_keys, dict) else {}
    api_keys_set = {k: bool(isinstance(v, str) and v.strip()) for k, v in api_keys.items()}
    safe_cfg = dict(cfg)
    safe_cfg["api_keys"] = {k: "" for k in api_keys.keys()}
    return {"success": True, "data": {"config": safe_cfg, "api_keys_set": api_keys_set}, "error": None}


@router.get("/engine_logs", tags=["engine_config"])
async def get_engine_logs(
    cursor: int = 0,
    limit: int = 200,
    task_type: str | None = None,
    engine: str | None = None,
    success: bool | None = None,
) -> dict[str, Any]:
    paths = get_paths()
    log_path = paths.engine_logs_path
    try:
        if not log_path.is_file():
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text("[]", encoding="utf-8")
    except Exception:
        pass

    entries: list[dict[str, Any]] = []
    try:
        raw = json.loads(log_path.read_text(encoding="utf-8") or "[]")
        if isinstance(raw, list):
            entries = [e for e in raw if isinstance(e, dict)]
    except Exception:
        entries = []

    if task_type and isinstance(task_type, str) and task_type.strip():
        want = task_type.strip()
        entries = [e for e in entries if str(e.get("task_type") or "") == want]
    if engine and isinstance(engine, str) and engine.strip():
        want = engine.strip()
        entries = [e for e in entries if str(e.get("engine") or "") == want]
    if isinstance(success, bool):
        entries = [e for e in entries if bool(e.get("success")) is success]

    safe_limit = max(1, min(int(limit), 5000))
    start = max(0, int(cursor))
    sliced = entries[start : start + safe_limit]
    next_cursor = start + len(sliced)
    return {
        "success": True,
        "data": {"entries": sliced, "next_cursor": next_cursor, "total": len(entries)},
        "error": None,
    }
