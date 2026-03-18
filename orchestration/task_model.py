from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class TaskStatus(str, Enum):
    PENDING = "pending"
    SIMULATING = "simulating"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class Task:
    """Core task model for the V2 orchestration engine.

    All work in the system should be expressed as Tasks that flow
    through the orchestration engine. Agents never talk directly;
    they receive Tasks and return structured outputs.
    """

    task_id: str
    assigned_agent: str
    # Optional execution metadata from V2_EXECUTION_MODEL
    # e.g. phase="planning" | "building" | "testing" and a human name.
    phase: Optional[str] = None
    name: Optional[str] = None
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    # Declared output file paths that should exist on disk after
    # successful execution. These are used by the engine's
    # verification step to enforce artifact creation.
    declared_outputs: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    description: Optional[str] = None

    def is_ready(self, completed_task_ids: List[str]) -> bool:
        if self.status not in {TaskStatus.PENDING, TaskStatus.READY}:
            return False
        return all(dep in completed_task_ids for dep in self.dependencies)
