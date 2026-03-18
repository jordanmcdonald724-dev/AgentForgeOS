"""System Stabilizer agent — identifies and resolves instability and tech debt."""

from __future__ import annotations

from typing import Any, Dict, Optional

from agents.base_agent import BaseAgent


class SystemStabilizerAgent(BaseAgent):
    """Identifies instability, performance bottlenecks, and technical debt."""

    role = "System Stabilizer"
    system_prompt = (
        "You are a site reliability engineer and technical debt specialist. "
        "Review the provided system, code, or failure report for: "
        "performance bottlenecks, resource leaks, race conditions, "
        "unhandled error paths, missing retries, and tech debt. "
        "Prioritise findings by impact. "
        "For each issue: describe the problem, root cause, recommended fix, "
        "and estimated effort to resolve (S/M/L). "
        "If the system is stable, confirm that with a brief summary."
    )

    async def run(
        self, prompt: str, *, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return await self._run_with_service(prompt, context=context)
