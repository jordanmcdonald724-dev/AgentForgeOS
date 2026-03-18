"""Task Router agent — classifies and routes tasks to the correct pipeline."""

from __future__ import annotations

from typing import Any, Dict, Optional

from agents.base_agent import BaseAgent


class RouterAgent(BaseAgent):
    """Classifies each sub-task and routes it to the right specialist agent."""

    role = "Task Router"
    system_prompt = (
        "You are a task routing specialist. "
        "Given a list of sub-tasks from the project plan, classify each one as: "
        "backend, frontend, data, infrastructure, security, or research. "
        "Assign each task to the appropriate specialist role. "
        "Return a routing table with: task name, category, assigned role, and estimated effort (S/M/L)."
    )

    async def run(
        self, prompt: str, *, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return await self._run_with_service(prompt, context=context)
