from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from typing import Any, Dict

from orchestration.task_model import Task
from .base import AgentResult
from infrastructure.model_router import ModelRouter, RouteKind


@dataclass
class AIEngineerAgent:
    """SYNAPSE (AI Engineer) agent.

    Implements the role defined in V2_AGENT_ROLES:
    - selects correct model routes
    - manages embeddings and inference logs
    Outputs model_routes.json and inference_logs.json under the
    project root for downstream agents to consume.
    """

    name: str = "Synapse"
    router: ModelRouter | None = None

    def _resolve_project_root(self, task: Task) -> Path:
        raw = task.inputs.get("project_root")
        base = Path(raw) if raw else Path("projects") / "session_default"
        base.mkdir(parents=True, exist_ok=True)
        return base

    def handle_task(self, task: Task) -> AgentResult:
        project_root = self._resolve_project_root(task)
        use_case = task.inputs.get("use_case", "code")
        kind = RouteKind.CODE if use_case == "code" else RouteKind.GENERIC
        route = (self.router or ModelRouter()).select_route(kind)

        routes = {"use_case": use_case, "route": route}
        logs = [
            {
                "message": f"Synapse selected route {route} for use_case={use_case}",
            }
        ]

        routes_path = project_root / "model_routes.json"
        logs_path = project_root / "inference_logs.json"

        routes_path.write_text(json.dumps(routes, indent=2), encoding="utf-8")
        logs_path.write_text(json.dumps(logs, indent=2), encoding="utf-8")

        return AgentResult(
            outputs={
                "model_routes_path": str(routes_path),
                "inference_logs_path": str(logs_path),
            },
            logs=[f"Synapse wrote model routing artifacts under {project_root}"],
        )
