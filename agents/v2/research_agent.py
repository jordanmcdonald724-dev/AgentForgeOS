from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from orchestration.task_model import Task
from .base import AgentResult


@dataclass
class ResearchAgent:
    """ARCHIVIST agent: research ingestion and synthesis.

    Writes structured research artifacts under the project root that
    capture sources, insights, and extracted systems/patterns.
    """

    name: str = "Archivist"

    def _resolve_project_root(self, task: Task) -> Path:
        raw = task.inputs.get("project_root")
        base = Path(raw) if raw else Path("projects") / "session_default"
        base.mkdir(parents=True, exist_ok=True)
        return base

    def handle_task(self, task: Task) -> AgentResult:
        project_root = self._resolve_project_root(task)
        research_dir = project_root / "research"
        research_dir.mkdir(parents=True, exist_ok=True)

        brief = task.inputs.get("brief") or {}
        sources = brief.get("sources") or []

        research_insights = {
            "sources": sources,
            "high_level_summary": "Initial research synthesis placeholder.",
        }
        patterns = {
            "design_patterns": [],
            "architecture_patterns": [],
        }
        extracted_systems = {
            "systems": [],
        }

        insights_path = research_dir / "research_insights.json"
        patterns_path = research_dir / "patterns.json"
        systems_path = research_dir / "extracted_systems.json"

        insights_path.write_text(json.dumps(research_insights, indent=2), encoding="utf-8")
        patterns_path.write_text(json.dumps(patterns, indent=2), encoding="utf-8")
        systems_path.write_text(json.dumps(extracted_systems, indent=2), encoding="utf-8")

        return AgentResult(
            outputs={
                "research_insights_path": str(insights_path),
                "patterns_path": str(patterns_path),
                "extracted_systems_path": str(systems_path),
            },
            logs=[f"Archivist wrote research artifacts under {research_dir}"],
        )
