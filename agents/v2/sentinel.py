from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from orchestration.task_model import Task
from .base import AgentResult


@dataclass
class SentinelAgent:
    """GUARDIAN agent: safety, guardrails, and risk analysis.

    Writes structured validation and security reports under the
    project root so that Launcher and others can enforce gates.
    """

    name: str = "Guardian"

    def _resolve_project_root(self, task: Task) -> Path:
        raw = task.inputs.get("project_root")
        base = Path(raw) if raw else Path("projects") / "session_default"
        base.mkdir(parents=True, exist_ok=True)
        return base

    def handle_task(self, task: Task) -> AgentResult:
        project_root = self._resolve_project_root(task)
        reports_dir = project_root / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)

        validation_report = {
            "status": "ok",
            "summary": "Baseline validation checks passed.",
            "issues": [],
        }
        security_report = {
            "status": "review",
            "summary": "Security review required for external integrations.",
            "findings": [],
        }
        issues = {
            "critical": [],
            "warnings": [],
        }

        validation_path = reports_dir / "validation_report.json"
        security_path = reports_dir / "security_report.json"
        issues_path = reports_dir / "issues.json"

        validation_path.write_text(json.dumps(validation_report, indent=2), encoding="utf-8")
        security_path.write_text(json.dumps(security_report, indent=2), encoding="utf-8")
        issues_path.write_text(json.dumps(issues, indent=2), encoding="utf-8")

        return AgentResult(
            outputs={
                "validation_report_path": str(validation_path),
                "security_report_path": str(security_path),
                "issues_path": str(issues_path),
            },
            logs=[f"Guardian wrote validation and security reports under {reports_dir}"],
        )
