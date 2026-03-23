"""Defines the Phase 5 agent pipeline and shared pipeline context."""

from typing import Any

strategic_agents: list[str] = ["Project Planner", "System Architect", "Task Router"]
architecture_agents: list[str] = ["Module Builder", "API Architect", "Data Architect"]
production_agents: list[str] = ["Backend Engineer", "Frontend Engineer", "AI Integration Engineer"]
validation_agents: list[str] = ["Integration Tester", "Security Auditor", "System Stabilizer"]

# Full execution order derived from docs
AGENT_PIPELINE: list[str] = [
    *strategic_agents,
    *architecture_agents,
    *production_agents,
    *validation_agents,
]


class PipelineContext:
    """Shared context object passed through every pipeline step.

    Agents read prior outputs and write their own results via ``get`` /
    ``set`` so that data flows forward through the full pipeline.
    """

    def __init__(self) -> None:
        self.data: dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        """Store *value* under *key* in the context."""
        self.data[key] = value

    def get(self, key: str, default: Any | None = None) -> Any:
        """Retrieve the value stored under *key*, or *default* if absent."""
        return self.data.get(key, default)
