"""Backend Engineer agent — implements server-side logic and API handlers."""

from __future__ import annotations

from typing import Any, Dict, Optional

from agents.base_agent import BaseAgent


class BackendEngineerAgent(BaseAgent):
    """Implements server-side Python code for the designed APIs and services."""

    role = "Backend Engineer"
    system_prompt = (
        "You are a senior backend software engineer. "
        "Implement the server-side code based on the provided specifications. "
        "Write clean, well-structured Python (FastAPI preferred) with type hints. "
        "Include docstrings, error handling, and logging. "
        "Follow existing codebase conventions. "
        "Output only the code for the requested component."
    )

    async def run(
        self, prompt: str, *, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return await self._run_with_service(prompt, context=context)
