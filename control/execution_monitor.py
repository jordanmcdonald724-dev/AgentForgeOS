"""Execution monitor for tracking pipeline steps."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ExecutionRecord:
    """Represents a single step execution record."""

    step: str
    status: str
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ExecutionMonitor:
    """Tracks start/end/error events for every pipeline step."""

    def __init__(self) -> None:
        self.records: List[ExecutionRecord] = []

    def start_step(self, step: str, context: Optional[Any] = None) -> None:
        self.records.append(ExecutionRecord(step=step, status="started"))

    def end_step(self, step: str, result: Dict[str, Any]) -> None:
        self.records.append(
            ExecutionRecord(step=step, status="completed", metadata={"result": result})
        )

    def record_error(self, step: str, error: str) -> None:
        self.records.append(ExecutionRecord(step=step, status="error", error=error))
