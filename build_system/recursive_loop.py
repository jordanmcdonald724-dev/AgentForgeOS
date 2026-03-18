from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal

from orchestration.engine import RECURSIVE_STAGES, OrchestrationEngine
from orchestration.task_model import Task, TaskStatus


StageName = Literal["plan", "build", "test", "review", "refine", "rebuild"]


@dataclass
class LoopIteration:
    """Represents a single pass through the recursive build loop.

    This is a structural model only; actual task behavior is
    delegated to the orchestration engine and agents.
    """

    index: int
    stage: StageName
    tasks: List[str] = field(default_factory=list)


@dataclass
class RecursiveBuilder:
    """Recursive builder engine scaffold.

    Coordinates the Plan→Build→Test→Review→Refine→Rebuild loop around an
    existing task graph managed by the ``OrchestrationEngine``.
    """

    engine: OrchestrationEngine
    history: List[LoopIteration] = field(default_factory=list)

    def _collect_stage_tasks(self, stage: StageName) -> List[Task]:
        suffix = f".{stage}"
        return [t for t in self.engine.tasks.values() if t.task_id.endswith(suffix)]

    def describe(self) -> Dict[str, List[str]]:
        """Return a simple description of loop stages for UI use."""

        return {"stages": list(RECURSIVE_STAGES)}

    def record_iteration(self, index: int, stage: StageName) -> LoopIteration:
        tasks = [t.task_id for t in self._collect_stage_tasks(stage)]
        iteration = LoopIteration(index=index, stage=stage, tasks=tasks)
        self.history.append(iteration)
        return iteration

    def is_complete(self) -> bool:
        """Return True when all tasks in the engine are either completed or failed.

        This is a coarse completion check used by higher-level controllers.
        """

        if not self.engine.tasks:
            return False
        return all(t.status in {TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.BLOCKED} for t in self.engine.tasks.values())
