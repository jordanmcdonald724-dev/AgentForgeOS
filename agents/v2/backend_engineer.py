from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from orchestration.task_model import Task
from .base import AgentResult


@dataclass
class BackendEngineerAgent:
    """CORE (Backend Engineer) agent.

    Implements the role defined in V2_AGENT_ROLES:
    - implements FastAPI routes
    - implements service layers and models
    Outputs live under backend/api, backend/services, backend/models
    for the project workspace, separate from the main engine/backend.
    """

    name: str = "Core"

    def _resolve_project_root(self, task: Task) -> Path:
        raw = task.inputs.get("project_root")
        base = Path(raw) if raw else Path("projects") / "session_default"
        base.mkdir(parents=True, exist_ok=True)
        return base

    def handle_task(self, task: Task) -> AgentResult:
        project_root = self._resolve_project_root(task)
        backend_root = project_root / "backend"
        api_root = backend_root / "api"
        services_root = backend_root / "services"
        models_root = backend_root / "models"

        for root in (api_root, services_root, models_root):
            root.mkdir(parents=True, exist_ok=True)

        # Minimal FastAPI route + service + model scaffolds.
        api_main = api_root / "routes.py"
        service_file = services_root / "project_service.py"
        model_file = models_root / "project.py"

        if not api_main.exists():
            api_main.write_text(
                """from fastapi import APIRouter


router = APIRouter()


@router.get("/projects")
async def list_projects() -> list[dict]:
  return []
""",
                encoding="utf-8",
            )

        if not service_file.exists():
            service_file.write_text(
                """class ProjectService:
  def list_projects(self) -> list[dict]:
    return []
""",
                encoding="utf-8",
            )

        if not model_file.exists():
            model_file.write_text(
                """from dataclasses import dataclass


@dataclass
class Project:
  id: str
  name: str
""",
                encoding="utf-8",
            )

        created = [str(api_main), str(service_file), str(model_file)]

        return AgentResult(
            outputs={"created_paths": created, "project_root": str(project_root)},
            logs=[f"Backend Engineer scaffolded API/services/models under {project_root}"],
        )
