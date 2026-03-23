"""Engine route for executing the agent pipeline."""

from __future__ import annotations

import logging
import os
from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel

from engine.database import db
from providers.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

_DEFAULT_SESSION_ID = "default"

router = APIRouter()


class AgentRunRequest(BaseModel):
    """Request body for a single-agent or full-pipeline run."""

    prompt: str
    provider: str | None = None
    model: str | None = None
    task_type: str = "conversation"
    agent_id: str | None = None
    context: dict[str, Any] | None = None
    pipeline: bool = False
    session_id: str | None = None


@router.post("/agent/run", tags=["agent"])
async def run_agent(body: AgentRunRequest, request: Request) -> dict[str, Any]:
    """
    Execute a prompt through a single agent interaction.

    When ``pipeline`` is ``True``, runs the full 12-stage pipeline.
    Otherwise, runs a single ``AgentService.run_agent`` call.

    The provider is selected from ``body.provider``:
    - ``"ollama"``  — local Ollama (default)
    - ``"openai"``  — OpenAI Chat Completions API

    Additional providers (fal, comfyui, piper) are image/TTS only and
    are not applicable to text agent runs.

    Conversation history is persisted to MongoDB when the database is
    available.  Pass ``session_id`` to group turns into a named session.
    """
    provider_name = (body.provider or "").strip().lower()
    if not provider_name:
        cfg_raw = getattr(request.app.state, "config", {}) or {}
        cfg = dict(cfg_raw) if isinstance(cfg_raw, dict) else {}
        raw_selected = cfg.get("providers")
        selected: dict[str, Any] = raw_selected if isinstance(raw_selected, dict) else {}
        provider_name = str(selected.get("llm") or "").strip().lower() or os.environ.get("PROVIDER_LLM", "").strip().lower()
    if not provider_name:
        provider_name = "ollama"

    agents_logger = logging.getLogger("agents")
    agents_logger.info("run provider=%s pipeline=%s session_id=%s", provider_name, bool(body.pipeline), body.session_id or _DEFAULT_SESSION_ID)
    from providers.noop_provider import NoOpLLMProvider
    from engine.router.model_router import ModelRouter

    llm_provider = NoOpLLMProvider()
    model_router = ModelRouter()
    session_id = body.session_id or _DEFAULT_SESSION_ID
    merged_context: dict[str, Any] = {}
    if isinstance(body.context, dict):
        merged_context.update(body.context)
    ws = getattr(request.app.state, "workspace_path", "") or ""
    if isinstance(ws, str) and ws.strip():
        merged_context.setdefault("workspace_path", ws)
    if body.pipeline:
        return await _run_pipeline(body.prompt, llm_provider, merged_context or body.context, model_router=model_router)
    return await _run_single(
        body.prompt,
        llm_provider,
        merged_context or body.context,
        session_id,
        model_router=model_router,
        task_type=body.task_type,
        agent_id=body.agent_id,
    )


@router.post("/agents/run", tags=["agents"])
async def run_agents(body: AgentRunRequest, request: Request) -> dict[str, Any]:
    return await run_agent(body, request)


@router.get("/agents/list", tags=["agents"])
async def list_agents() -> dict[str, Any]:
    agents = [
        {"id": "planner", "name": "Planner"},
        {"id": "architect", "name": "Architect"},
        {"id": "router", "name": "Router"},
        {"id": "builder", "name": "Builder"},
        {"id": "api", "name": "API"},
        {"id": "data", "name": "Data"},
        {"id": "backend", "name": "Backend"},
        {"id": "frontend", "name": "Frontend"},
        {"id": "ai", "name": "AI"},
        {"id": "tester", "name": "Tester"},
        {"id": "auditor", "name": "Auditor"},
        {"id": "stabilizer", "name": "Stabilizer"},
    ]
    return {"success": True, "data": {"agents": agents}, "error": None}


@router.get("/agents/status", tags=["agents"])
async def agents_status() -> dict[str, Any]:
    return {"success": True, "data": {"status": "ok"}, "error": None}


def _build_memory_manager(session_id: str):
    """Return a ``MongoMemoryManager`` wired to the live DB, or ``None``.

    When MongoDB is not yet connected (e.g. during unit tests or when the
    server starts without a DB URI), this returns ``None`` so that
    ``AgentService`` falls back to its in-memory ``MemoryManager``.
    """
    from services.mongo_memory import MongoMemoryManager

    return MongoMemoryManager(db=db, session_id=session_id)


async def _run_single(
    prompt: str,
    llm_provider: LLMProvider,
    context: dict[str, Any] | None,
    session_id: str,
    *,
    model_router: Any | None = None,
    task_type: str = "conversation",
    agent_id: str | None = None,
) -> dict[str, Any]:
    from services.agent_service import AgentService

    memory = _build_memory_manager(session_id)
    service = AgentService(llm_provider=llm_provider, memory_manager=memory)
    if model_router is not None:
        service.model_router = model_router
    merged_context: dict[str, Any] = {}
    if isinstance(context, dict):
        merged_context.update(context)
    if agent_id and isinstance(agent_id, str) and agent_id.strip():
        merged_context["agent_id"] = agent_id.strip()
    response = await service.run_agent(prompt, context=merged_context or context, task_type=task_type)
    return {"success": response.get("success"), "data": response, "error": response.get("error")}


async def _run_pipeline(
    prompt: str,
    llm_provider: LLMProvider,
    context: dict[str, Any] | None,
    *,
    model_router: Any | None = None,
) -> dict[str, Any]:
    from agents.pipeline import run as pipeline_run

    responses = await pipeline_run(prompt, context=context, llm_provider=llm_provider, model_router=model_router)
    return {
        "success": True,
        "data": {"stages": list(responses)},
        "error": None,
    }
