"""Factory for creating agent instances."""

from __future__ import annotations

from typing import Any, Optional, Type

from services.agent_service import AgentService


class AgentFactory:
    """Constructs agent instances with shared dependencies."""

    def create(self, agent_cls: Type[Any], agent_service: AgentService) -> Any:
        return agent_cls(agent_service=agent_service)
