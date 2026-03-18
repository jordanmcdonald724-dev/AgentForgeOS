"""Base class for all AgentForgeOS pipeline agents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from services.agent_service import AgentService


class BaseAgent(ABC):
    """Common interface for every agent in the pipeline.

    Concrete agents inherit this class and set:
    - ``role``         – the pipeline role name (must match AGENT_PIPELINE)
    - ``system_prompt`` – instructions prepended to every user prompt

    The ``run()`` method is called by AgentSupervisor for each stage.
    """

    role: str = ""
    system_prompt: str = ""

    def __init__(self, agent_service: Optional["AgentService"] = None) -> None:
        self.agent_service = agent_service

    @abstractmethod
    async def run(
        self, prompt: str, *, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute this agent's role for the given prompt.

        Returns the standardised response dict:
        ``{"success": bool, "data": ..., "error": Optional[str]}``
        """
        raise NotImplementedError

    def describe(self) -> Dict[str, str]:
        """Return a brief description of this agent."""
        return {"role": self.role, "class": type(self).__name__}

    def _build_prompt(self, user_prompt: str) -> str:
        """Prefix the user prompt with the agent's system instructions."""
        if self.system_prompt:
            return f"[{self.role}]\n{self.system_prompt}\n\nTask: {user_prompt}"
        return user_prompt

    async def _run_with_service(
        self, prompt: str, *, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Convenience helper — prepend system prompt and call agent_service."""
        if self.agent_service is None:
            return {
                "success": False,
                "data": None,
                "error": f"{self.role}: no AgentService configured",
            }
        return await self.agent_service.run_agent(
            self._build_prompt(prompt), context=context
        )
