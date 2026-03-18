"""Engine route for executing the agent pipeline."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from engine.database import db

logger = logging.getLogger(__name__)

_DEFAULT_SESSION_ID = "default"

router = APIRouter()


class AgentRunRequest(BaseModel):
    """Request body for a single-agent or full-pipeline run."""

    prompt: str
    provider: str = "ollama"
    model: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    pipeline: bool = False
    session_id: Optional[str] = None


@router.post("/agent/run", tags=["agent"])
async def run_agent(body: AgentRunRequest):
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
    llm_provider = _build_provider(body.provider, model=body.model)
    session_id = body.session_id or _DEFAULT_SESSION_ID
    if body.pipeline:
        return await _run_pipeline(body.prompt, llm_provider, body.context)
    return await _run_single(body.prompt, llm_provider, body.context, session_id)


def _build_provider(provider_name: str, model: Optional[str] = None):
    """Instantiate the requested LLM provider."""
    if provider_name == "openai":
        from providers.openai_provider import OpenAIProvider

        return OpenAIProvider(model=model) if model else OpenAIProvider()
    # Default — Ollama
    from providers.ollama_provider import OllamaProvider

    return OllamaProvider(model=model) if model else OllamaProvider()


def _build_memory_manager(session_id: str):
    """Return a ``MongoMemoryManager`` wired to the live DB, or ``None``.

    When MongoDB is not yet connected (e.g. during unit tests or when the
    server starts without a DB URI), this returns ``None`` so that
    ``AgentService`` falls back to its in-memory ``MemoryManager``.
    """
    from services.mongo_memory import MongoMemoryManager

    return MongoMemoryManager(db=db, session_id=session_id)


async def _run_single(
    prompt: str, llm_provider, context: Optional[Dict[str, Any]], session_id: str
) -> Dict[str, Any]:
    from services.agent_service import AgentService

    memory = _build_memory_manager(session_id)
    service = AgentService(llm_provider=llm_provider, memory_manager=memory)
    response = await service.run_agent(prompt, context=context)
    return {"success": response.get("success"), "data": response, "error": response.get("error")}


async def _run_pipeline(
    prompt: str, llm_provider, context: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    from agents.pipeline import run as pipeline_run

    responses = await pipeline_run(prompt, context=context, llm_provider=llm_provider)
    return {
        "success": True,
        "data": {"stages": list(responses)},
        "error": None,
    }
