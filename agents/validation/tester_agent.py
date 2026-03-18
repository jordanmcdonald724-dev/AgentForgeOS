"""Integration Tester agent — designs and writes integration test suites."""

from __future__ import annotations

from typing import Any, Dict, Optional

from agents.base_agent import BaseAgent


class IntegrationTesterAgent(BaseAgent):
    """Writes integration tests that verify components work together end-to-end."""

    role = "Integration Tester"
    system_prompt = (
        "You are a senior QA engineer specialising in integration testing. "
        "Given a component or API specification, write Python unittest or pytest test cases that: "
        "cover the happy path, edge cases, and error scenarios; "
        "mock external dependencies (databases, HTTP calls) appropriately; "
        "are runnable with `python -m unittest discover -s tests`. "
        "Follow the existing test conventions in the repository. "
        "Output only the test code."
    )

    async def run(
        self, prompt: str, *, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return await self._run_with_service(prompt, context=context)
