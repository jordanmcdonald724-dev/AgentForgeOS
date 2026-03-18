from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any

from orchestration.task_model import Task
from agents.v2.base import AgentResult


@dataclass
class SimulationReport:
    complexity: str
    duration_estimate: str
    project_size: str
    architecture_preview: str
    feasible: bool


class SimulationEngine:
    """Stubbed simulation engine.

    Takes a project brief and returns a coarse feasibility
    report as described in BUILD_BIBLE_V2.
    """

    def run(self, brief: Dict[str, Any]) -> SimulationReport:
        # Placeholder heuristics only; real logic will use
        # knowledge graphs and agent collaboration.
        return SimulationReport(
            complexity="medium",
            duration_estimate="3-6 weeks",
            project_size="medium",
            architecture_preview="Placeholder architecture preview",
            feasible=True,
        )

    def to_task_result(self, report: SimulationReport) -> AgentResult:
        return AgentResult(
            outputs={
                "complexity": report.complexity,
                "duration_estimate": report.duration_estimate,
                "project_size": report.project_size,
                "architecture_preview": report.architecture_preview,
                "feasible": report.feasible,
            },
            logs=["SimulationEngine produced a placeholder feasibility report."],
        )
