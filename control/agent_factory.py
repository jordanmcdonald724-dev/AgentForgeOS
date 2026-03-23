"""Factory for creating agent instances."""

from __future__ import annotations

from typing import Any, Optional, Type

from services.agent_service import AgentService
from services.agent_behavior import load_agent_system_prompt


class AgentFactory:
    """Constructs agent instances with shared dependencies."""

    def create(self, agent_cls: Type[Any], agent_service: AgentService) -> Any:
        agent = agent_cls(agent_service=agent_service)
        role = getattr(agent, "role", "") or ""
        if isinstance(role, str) and role.strip():
            prompt = load_agent_system_prompt(role.strip())
            if prompt:
                setattr(agent, "system_prompt", prompt)
        return agent
