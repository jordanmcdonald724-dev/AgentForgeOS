from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from typing import Dict, Any

from orchestration.task_model import Task
from .base import Agent, AgentResult


@dataclass
class CommanderAgent:
    """ORIGIN (Commander) agent.

    Implements the role defined in V2_AGENT_ROLES:
    - parses the raw command
    - classifies product type
    - defines basic scope
    - produces intent/task graph/build plan artifacts
    """

    name: str = "Origin"

    def _classify_product_type(self, command: str) -> str:
        cmd = command.lower()
        if "game" in cmd:
            return "game"
        if "web" in cmd or "site" in cmd:
            return "web"
        if "app" in cmd:
            return "app"
        return "hybrid"

    def _resolve_project_root(self, task: Task) -> Path:
        raw = task.inputs.get("project_root")
        base = Path(raw) if raw else Path("projects") / "session_default"
        base.mkdir(parents=True, exist_ok=True)
        return base

    def handle_task(self, task: Task) -> AgentResult:
        raw_command = str(task.inputs.get("command", "")).strip()
        command_text = raw_command or "(empty command)"

        product_type = self._classify_product_type(command_text)

        intent: Dict[str, Any] = {
            "command": command_text,
            "product_type": product_type,
            "scope": {
                "has_gameplay": product_type == "game",
                "has_backend": True,
                "has_ui": True,
            },
        }

        # Minimal connected graph following the AAA flow example in V2_EXECUTION_MODEL.
        task_graph = [
            {"task_id": "t0", "agent": "Origin", "name": "interpret command"},
            {"task_id": "t1", "agent": "Architect", "name": "design architecture", "dependencies": ["t0"]},
            {"task_id": "t2", "agent": "Builder", "name": "generate backend code", "dependencies": ["t1"]},
            {"task_id": "t3", "agent": "Surface", "name": "implement UI", "dependencies": ["t1"]},
            {"task_id": "t4", "agent": "Analyst", "name": "run tests", "dependencies": ["t2", "t3"]},
            {"task_id": "t5", "agent": "Guardian", "name": "validate system", "dependencies": ["t4"]},
            {"task_id": "t6", "agent": "Launcher", "name": "build and launch", "dependencies": ["t5"]},
        ]

        build_plan: Dict[str, Any] = {
            "entry_task": "t0",
            "tasks": task_graph,
        }

        project_root = self._resolve_project_root(task)
        intent_path = project_root / "intent.json"
        task_graph_path = project_root / "task_graph.json"
        build_plan_path = project_root / "build_plan.json"

        intent_path.write_text(json.dumps(intent, indent=2), encoding="utf-8")
        task_graph_path.write_text(json.dumps(task_graph, indent=2), encoding="utf-8")
        build_plan_path.write_text(json.dumps(build_plan, indent=2), encoding="utf-8")

        return AgentResult(
            outputs={
                "intent_path": str(intent_path),
                "task_graph_path": str(task_graph_path),
                "build_plan_path": str(build_plan_path),
            },
            logs=[
                f"Commander interpreted command: {command_text}",
                f"product_type={product_type}",
                f"artifacts written to {project_root}",
            ],
        )
