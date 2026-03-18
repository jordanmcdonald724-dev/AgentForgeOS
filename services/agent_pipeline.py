"""Defines the Phase 5 agent pipeline and shared pipeline context."""

from typing import Any, List, Optional

strategic_agents: List[str] = ["Project Planner", "System Architect", "Task Router"]
architecture_agents: List[str] = ["Module Builder", "API Architect", "Data Architect"]
production_agents: List[str] = ["Backend Engineer", "Frontend Engineer", "AI Integration Engineer"]
validation_agents: List[str] = ["Integration Tester", "Security Auditor", "System Stabilizer"]

# Full execution order derived from docs
AGENT_PIPELINE: List[str] = [
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
        self.data: dict = {}

    def set(self, key: str, value: Any) -> None:
        """Store *value* under *key* in the context."""
        self.data[key] = value

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Retrieve the value stored under *key*, or *default* if absent."""
        return self.data.get(key, default)
