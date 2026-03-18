from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict
import json

from orchestration.task_model import Task
from .base import AgentResult
from build_system.simulation_engine import SimulationEngine


@dataclass
class ProbeAgent:
    """Testing, probing, and QA agent.

    In the V2 architecture this also fronts the simulation
    engine for feasibility checks before builds are allowed
    to proceed.
    """

    name: str = "Analyst"
    simulation_engine: SimulationEngine = SimulationEngine()

    def _resolve_project_root(self, task: Task) -> Path:
        raw = task.inputs.get("project_root")
        base = Path(raw) if raw else Path("projects") / "session_default"
        base.mkdir(parents=True, exist_ok=True)
        return base

    def handle_task(self, task: Task) -> AgentResult:
        project_root = self._resolve_project_root(task)
        tests_dir = project_root / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)

        brief: Dict[str, Any] = task.inputs.get("brief") or {}
        sim_report = self.simulation_engine.run(brief)
        sim_result = self.simulation_engine.to_task_result(sim_report)

        # Persist the high-level simulation/test results so Guardian/Launcher
        # and the UI can inspect them.
        test_results = {
            "summary": "Simulation run complete.",
            "feasible": bool(getattr(sim_report, "feasible", True)),
        }
        performance_metrics = {
            "complexity": getattr(sim_report, "complexity", "unknown"),
            "duration_estimate": getattr(sim_report, "duration_estimate", "unknown"),
            "project_size": getattr(sim_report, "project_size", "unknown"),
        }
        failure_report = []

        test_results_path = tests_dir / "test_results.json"
        performance_path = tests_dir / "performance_metrics.json"
        failure_path = tests_dir / "failure_report.json"

        test_results_path.write_text(json.dumps(test_results, indent=2), encoding="utf-8")
        performance_path.write_text(json.dumps(performance_metrics, indent=2), encoding="utf-8")
        failure_path.write_text(json.dumps(failure_report, indent=2), encoding="utf-8")

        # Merge file paths into the existing AgentResult from the simulation engine.
        outputs = dict(sim_result.outputs)
        outputs.update(
            {
                "test_results_path": str(test_results_path),
                "performance_metrics_path": str(performance_path),
                "failure_report_path": str(failure_path),
            }
        )

        logs = list(sim_result.logs) + [
            f"Analyst wrote test and performance artifacts under {tests_dir}",
        ]

        return AgentResult(outputs=outputs, logs=logs)
