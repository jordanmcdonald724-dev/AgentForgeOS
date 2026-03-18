"""Module Builder agent — designs the module structure and interfaces."""

from __future__ import annotations

from typing import Any, Dict, Optional

from agents.base_agent import BaseAgent


class BuilderAgent(BaseAgent):
    """Defines module boundaries, interfaces, and dependency graphs."""

    role = "Module Builder"
    system_prompt = (
        "You are a module design specialist. "
        "Given an architecture plan, define each software module: "
        "its responsibilities, public interface (classes and functions), "
        "dependencies on other modules, and test surface. "
        "Produce a module specification document. "
        "Do not write implementation code — interfaces and contracts only."
    )

    async def run(
        self, prompt: str, *, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return await self._run_with_service(prompt, context=context)
