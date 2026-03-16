"""Security Auditor agent — reviews code for vulnerabilities and policy violations."""

from __future__ import annotations

from typing import Any, Dict, Optional

from agents.base_agent import BaseAgent


class SecurityAuditorAgent(BaseAgent):
    """Audits code for security vulnerabilities, injection risks, and policy gaps."""

    role = "Security Auditor"
    system_prompt = (
        "You are a security engineer specialising in application security audits. "
        "Review the provided code or specification for: "
        "injection vulnerabilities (SQL, command, path traversal), "
        "insecure secrets handling, missing authentication/authorisation checks, "
        "unsafe deserialization, dependency vulnerabilities, and data exposure risks. "
        "For each finding, provide: severity (critical/high/medium/low), description, "
        "affected location, and recommended remediation. "
        "If no issues are found, explicitly state the code is clear."
    )

    async def run(
        self, prompt: str, *, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return await self._run_with_service(prompt, context=context)
