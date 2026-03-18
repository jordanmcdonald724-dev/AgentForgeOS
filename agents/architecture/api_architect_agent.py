"""API Architect agent — designs RESTful/WebSocket API contracts."""

from __future__ import annotations

from typing import Any, Dict, Optional

from agents.base_agent import BaseAgent


class APIArchitectAgent(BaseAgent):
    """Designs API contracts: endpoints, request/response schemas, auth."""

    role = "API Architect"
    system_prompt = (
        "You are an API design specialist. "
        "Given a module specification, design the REST API surface: "
        "define each endpoint with HTTP method, path, path/query parameters, "
        "request body schema, response schema, error codes, and auth requirements. "
        "Use OpenAPI 3 conventions in your descriptions. "
        "Do not write implementation — contracts only."
    )

    async def run(
        self, prompt: str, *, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return await self._run_with_service(prompt, context=context)
