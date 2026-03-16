"""Engine route for executing the agent pipeline."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class AgentRunRequest(BaseModel):
    """Request body for a single-agent or full-pipeline run."""

    prompt: str
    provider: str = "ollama"
    model: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    pipeline: bool = False


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
    """
    llm_provider = _build_provider(body.provider, model=body.model)
    if body.pipeline:
        return await _run_pipeline(body.prompt, llm_provider, body.context)
    return await _run_single(body.prompt, llm_provider, body.context)


def _build_provider(provider_name: str, model: Optional[str] = None):
    """Instantiate the requested LLM provider."""
    if provider_name == "openai":
        from providers.openai_provider import OpenAIProvider

        return OpenAIProvider(model=model) if model else OpenAIProvider()
    # Default — Ollama
    from providers.ollama_provider import OllamaProvider

    return OllamaProvider(model=model) if model else OllamaProvider()


async def _run_single(
    prompt: str, llm_provider, context: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    from services.agent_service import AgentService

    service = AgentService(llm_provider=llm_provider)
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
