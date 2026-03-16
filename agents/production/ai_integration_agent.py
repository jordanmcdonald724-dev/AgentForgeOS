"""AI Integration Engineer agent — wires LLM/image/TTS providers into the pipeline."""

from __future__ import annotations

from typing import Any, Dict, Optional

from agents.base_agent import BaseAgent


class AIIntegrationEngineerAgent(BaseAgent):
    """Connects AI provider adapters and coordinates multi-modal pipelines."""

    role = "AI Integration Engineer"
    system_prompt = (
        "You are an AI integration specialist. "
        "Your job is to wire AI provider adapters (LLM, image, TTS) into the AgentForgeOS pipeline. "
        "Given a specification, write the integration code that: "
        "selects the correct provider based on config, "
        "handles provider-specific request/response formats, "
        "implements retry logic and graceful fallback, "
        "and exposes a clean interface to the rest of the system. "
        "Use the existing provider ABC interfaces (LLMProvider, ImageProvider, TTSProvider). "
        "Output only the integration code."
    )

    async def run(
        self, prompt: str, *, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return await self._run_with_service(prompt, context=context)
