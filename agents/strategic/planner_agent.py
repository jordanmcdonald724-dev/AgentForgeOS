"""Project Planner agent — decomposes user requests into an ordered task list."""

from __future__ import annotations

from typing import Any, Dict, Optional

from agents.base_agent import BaseAgent


class PlannerAgent(BaseAgent):
    """Analyses the user's request and produces a structured project plan."""

    role = "Project Planner"
    system_prompt = (
        "You are a senior project planner. "
        "Break the given task into a clear, ordered list of sub-tasks. "
        "Each task should have a name, a brief description, and a priority level (high/medium/low). "
        "Output the plan as a numbered list. "
        "Do not start implementation — planning only."
    )

    async def run(
        self, prompt: str, *, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return await self._run_with_service(prompt, context=context)
