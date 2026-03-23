"""Sandbox module backend API routes.

Provides endpoints for the isolated agent experimentation environment:
- experiment execution (stub)
- experiment history listing
"""

from __future__ import annotations

import asyncio
import datetime
import uuid
from typing import Any, Dict, List

from fastapi import APIRouter

from control.execution_monitor import execution_monitor

router = APIRouter(prefix="/sandbox", tags=["sandbox"])

# In-memory experiment log — replaced by persistence when MongoDB is available.
_experiments: List[Dict[str, Any]] = []


@router.get("/status")
async def sandbox_status():
    """Return the Sandbox module's current operational status."""
    return {
        "success": True,
        "data": {
            "module": "sandbox",
            "status": "ready",
            "description": "Isolated agent experimentation sandbox",
            "total_experiments": len(_experiments),
        },
        "error": None,
    }


@router.get("/experiments")
async def list_experiments():
    """Return all recorded sandbox experiments."""
    return {"success": True, "data": list(_experiments), "error": None}


@router.post("/run")
async def run_experiment(body: Dict[str, Any] = {}):
    prompt = body.get("prompt", "")
    if not isinstance(prompt, str) or not prompt.strip():
        return {"success": False, "data": None, "error": "prompt is required"}
    provider = body.get("provider", "ollama")
    model = body.get("model")
    experiment_id = f"sandbox_{uuid.uuid4().hex[:10]}"
    entry: Dict[str, Any] = {
        "id": experiment_id,
        "prompt": prompt,
        "provider": provider,
        "model": model,
        "status": "queued",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "steps": [],
        "error": None,
    }
    _experiments.append(entry)

    async def _run() -> None:
        try:
            entry["status"] = "running"
            execution_monitor.start_pipeline(experiment_id, metadata={"prompt": prompt, "provider": provider, "model": model, "kind": "sandbox"})
            from engine.routes.pipeline import _build_provider  # type: ignore
            from agents.pipeline import run as pipeline_run

            llm_provider = _build_provider(str(provider or "noop").strip().lower(), model=str(model) if isinstance(model, str) and model.strip() else None)
            results = await pipeline_run(prompt, context={"pipeline_id": experiment_id}, llm_provider=llm_provider)
            steps = list(results)
            entry["steps"] = steps
            entry["status"] = "completed"
            entry["completed_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            execution_monitor.end_pipeline(experiment_id, status="success")
        except Exception as exc:
            entry["status"] = "error"
            entry["error"] = str(exc)
            entry["completed_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            execution_monitor.end_pipeline(experiment_id, status="error")

    asyncio.create_task(_run())
    return {"success": True, "data": entry, "error": None}


@router.delete("/experiments/{experiment_id}")
async def delete_experiment(experiment_id: str):
    """Remove a sandbox experiment by id."""
    global _experiments
    before = len(_experiments)
    _experiments = [e for e in _experiments if e.get("id") != experiment_id]
    removed = before - len(_experiments)
    return {"success": True, "data": {"removed": removed}, "error": None}
