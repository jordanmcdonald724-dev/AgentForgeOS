"""Engine route for triggering the multi-agent pipeline."""

from __future__ import annotations

import asyncio
import logging
import os

from dataclasses import asdict

from fastapi import APIRouter, Request
from pydantic import BaseModel
from uuid import uuid4
from typing import Any

from control.execution_monitor import execution_monitor
from engine.security.preflight import require_preflight_ok

logger = logging.getLogger(__name__)

router = APIRouter()

_running: dict[str, asyncio.Task] = {}


class PipelineRunRequest(BaseModel):
    """Request body for a pipeline run."""

    prompt: str
    provider: str | None = None
    model: str | None = None


def _default_provider() -> str:
    provider = os.environ.get("PROVIDER_LLM", "").strip().lower()
    return provider or "noop"


@router.post("/pipeline/run", tags=["pipeline"])
async def run_pipeline(body: PipelineRunRequest, request: Request):
    ok, preflight = await require_preflight_ok(request, scope="pipeline.run")
    if not ok:
        return {"success": False, "error": "Preflight failed", "data": {"preflight": preflight}}
    """
    Execute the full multi-agent pipeline for the given prompt.

    Delegates to :func:`agents.pipeline.run` and returns the collected
    stage results.
    """
    pipeline_id = str(uuid4())
    provider_name = (body.provider or "").strip().lower()
    if not provider_name:
        cfg_raw = getattr(request.app.state, "config", {}) or {}
        cfg = dict(cfg_raw) if isinstance(cfg_raw, dict) else {}
        raw_selected = cfg.get("providers")
        selected: dict[str, Any] = raw_selected if isinstance(raw_selected, dict) else {}
        provider_name = str(selected.get("llm") or "").strip().lower()
    if not provider_name:
        provider_name = _default_provider()
    execution_monitor.start_pipeline(
        pipeline_id,
        metadata={"prompt": body.prompt, "provider": provider_name, "model": body.model},
    )
    try:
        from agents.pipeline import run as pipeline_run
        from engine.router.model_router import ModelRouter
        from providers.noop_provider import NoOpLLMProvider

        results = await pipeline_run(
            body.prompt,
            context={"pipeline_id": pipeline_id, "workspace_path": getattr(request.app.state, "workspace_path", "") or ""},
            llm_provider=NoOpLLMProvider(),
            model_router=ModelRouter(),
        )
        execution_monitor.end_pipeline(pipeline_id, status="success")
        return {"success": True, "pipeline_id": pipeline_id, "steps": list(results)}
    except Exception as exc:
        logger.exception("Pipeline run failed")
        execution_monitor.end_pipeline(pipeline_id, status="error")
        return {"success": False, "error": str(exc)}


@router.post("/pipeline/start", tags=["pipeline"])
async def start_pipeline(body: PipelineRunRequest, request: Request):
    ok, preflight = await require_preflight_ok(request, scope="pipeline.start")
    if not ok:
        return {"success": False, "data": {"preflight": preflight}, "error": "Preflight failed"}
    pipeline_id = str(uuid4())
    provider_name = (body.provider or "").strip().lower()
    if not provider_name:
        cfg_raw = getattr(request.app.state, "config", {}) or {}
        cfg = dict(cfg_raw) if isinstance(cfg_raw, dict) else {}
        raw_selected = cfg.get("providers")
        selected: dict[str, Any] = raw_selected if isinstance(raw_selected, dict) else {}
        provider_name = str(selected.get("llm") or "").strip().lower()
    if not provider_name:
        provider_name = _default_provider()

    execution_monitor.start_pipeline(
        pipeline_id,
        metadata={"prompt": body.prompt, "provider": provider_name, "model": body.model, "mode": "async"},
    )

    async def _runner() -> None:
        try:
            from agents.pipeline import run as pipeline_run
            from engine.router.model_router import ModelRouter
            from providers.noop_provider import NoOpLLMProvider

            await pipeline_run(
                body.prompt,
                context={"pipeline_id": pipeline_id, "workspace_path": getattr(request.app.state, "workspace_path", "") or ""},
                llm_provider=NoOpLLMProvider(),
                model_router=ModelRouter(),
            )
            execution_monitor.end_pipeline(pipeline_id, status="success")
        except asyncio.CancelledError:
            execution_monitor.end_pipeline(pipeline_id, status="cancelled")
            raise
        except Exception:
            logger.exception("Pipeline run failed")
            execution_monitor.end_pipeline(pipeline_id, status="error")
        finally:
            _running.pop(pipeline_id, None)

    task = asyncio.create_task(_runner())
    _running[pipeline_id] = task
    return {"success": True, "pipeline_id": pipeline_id, "started": True}


@router.post("/pipeline/stop", tags=["pipeline"])
async def stop_pipeline(pipeline_id: str | None = None):
    pid = (pipeline_id or "").strip()
    if not pid:
        return {"success": False, "data": None, "error": "pipeline_id is required"}
    task = _running.get(pid)
    if not task:
        return {"success": True, "data": {"stopped": False, "pipeline_id": pid, "supported": True, "reason": "not_running"}, "error": None}
    try:
        task.cancel()
        return {"success": True, "data": {"stopped": True, "pipeline_id": pid, "supported": True}, "error": None}
    except Exception as exc:
        return {"success": False, "data": {"stopped": False, "pipeline_id": pid, "supported": True}, "error": str(exc)}


@router.get("/pipeline/status", tags=["pipeline"])
async def pipeline_status(pipeline_id: str | None = None):
    events = execution_monitor.get_events(pipeline_id=pipeline_id)
    last = events[-1] if events else None
    return {
        "success": True,
        "data": {
            "pipeline_id": pipeline_id,
            "event_count": len(events),
            "last_event": asdict(last) if last else None,
            "running": bool(pipeline_id and pipeline_id in _running),
        },
        "error": None,
    }


@router.get("/pipeline/logs", tags=["pipeline"])
async def pipeline_logs(cursor: int = 0, pipeline_id: str | None = None):
    return await get_pipeline_events(cursor=cursor, pipeline_id=pipeline_id)


@router.get("/pipeline/events", tags=["pipeline"])
async def get_pipeline_events(cursor: int = 0, pipeline_id: str | None = None):
    """Return ExecutionMonitor events since the provided cursor."""

    events = execution_monitor.get_events_since(cursor, pipeline_id)
    serialized = [asdict(event) for event in events]
    next_cursor = cursor + len(events)
    return {
        "success": True,
        "data": {
            "events": serialized,
            "next_cursor": next_cursor,
        },
        "error": None,
    }
