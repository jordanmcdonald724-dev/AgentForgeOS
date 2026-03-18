"""System Architect agent — designs the high-level system structure."""

from __future__ import annotations

from typing import Any, Dict, Optional

from agents.base_agent import BaseAgent


class ArchitectAgent(BaseAgent):
    """Designs the system architecture based on the project plan."""

    role = "System Architect"
    system_prompt = (
        "You are a senior system architect. "
        "Given a project plan, design the high-level architecture: "
        "identify services, modules, data flows, and integration points. "
        "Specify technology choices with justification. "
        "Produce an architecture document with component diagram (text form) and key design decisions. "
        "Do not write code — architecture only."
    )

    async def run(
        self, prompt: str, *, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return await self._run_with_service(prompt, context=context)
