from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from engine.router.config_loader import get_paths


def _safe_read_json(path: Path) -> Dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else {}
    except Exception:
        return {}


def _safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def _agents_dir(resources_dir: Path) -> Path:
    return resources_dir / "config" / "agents"


def normalize_pipeline_role(value: str) -> str:
    v = (value or "").strip()
    if not v:
        return ""
    aliases = {
        "planner": "Project Planner",
        "architect": "System Architect",
        "router": "Task Router",
        "builder": "Module Builder",
        "api": "API Architect",
        "data": "Data Architect",
        "backend": "Backend Engineer",
        "frontend": "Frontend Engineer",
        "ai": "AI Integration Engineer",
        "tester": "Integration Tester",
        "auditor": "Security Auditor",
        "stabilizer": "System Stabilizer",
    }
    key = v.lower()
    return aliases.get(key, v)


def load_agent_spec_by_role(role: str) -> Dict[str, Any]:
    paths = get_paths()
    agents_dir = _agents_dir(paths.resources_dir)
    if not agents_dir.is_dir():
        return {}
    normalized = normalize_pipeline_role(role)
    for p in agents_dir.glob("*.json"):
        spec = _safe_read_json(p)
        if spec.get("pipeline_role") == normalized:
            return spec
    return {}


def load_agent_system_prompt(role: str) -> str:
    paths = get_paths()
    spec = load_agent_spec_by_role(role)
    rel = spec.get("system_prompt_path")
    if not isinstance(rel, str) or not rel.strip():
        return ""
    prompt_path = paths.resources_dir / rel
    return _safe_read_text(prompt_path).strip()


def get_agent_identity(role: str) -> Tuple[str, str]:
    spec = load_agent_spec_by_role(role)
    agent_id = spec.get("agent_id")
    display = spec.get("display_name")
    return (
        agent_id if isinstance(agent_id, str) and agent_id.strip() else role,
        display if isinstance(display, str) and display.strip() else role,
    )
