from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Protocol

from orchestration.task_model import Task


@dataclass
class AgentResult:
    outputs: Dict[str, Any]
    logs: list[str] | None = None


class Agent(Protocol):
    """Protocol for all V2 agents.

    Each concrete agent implements `handle_task` for its role-specific behavior.
    """

    name: str

    def handle_task(self, task: Task) -> AgentResult:  # pragma: no cover - behavior defined in concrete agents
        ...
