"""Frontend Engineer agent — implements UI components and studio interactions."""

from __future__ import annotations

from typing import Any, Dict, Optional

from agents.base_agent import BaseAgent


class FrontendEngineerAgent(BaseAgent):
    """Implements UI components for the AgentForgeOS Studio."""

    role = "Frontend Engineer"
    system_prompt = (
        "You are a senior frontend engineer specialising in the AgentForgeOS Studio UI. "
        "Implement the requested UI component using HTML, CSS, and vanilla JavaScript. "
        "Follow the existing five-region layout: nav, sidebar, workspace, bottom panels. "
        "Keep styles consistent with the existing dark-theme CSS (background #0f172a, accent #2563eb). "
        "Ensure accessibility attributes are present. "
        "Output only the relevant HTML/CSS/JS for the requested component."
    )

    async def run(
        self, prompt: str, *, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return await self._run_with_service(prompt, context=context)
