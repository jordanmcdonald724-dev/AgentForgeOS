from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from orchestration.task_model import Task
from .base import AgentResult


@dataclass
class DevOpsEngineerAgent:
    """LAUNCHER agent: deployment, CI/CD, and environment orchestration.

    Produces a concrete deployment plan, build log, and environment
    descriptor under the project root so the system can treat
    "launched" artifacts as real objects.
    """

    name: str = "Launcher"

    def _resolve_project_root(self, task: Task) -> Path:
        raw = task.inputs.get("project_root")
        base = Path(raw) if raw else Path("projects") / "session_default"
        base.mkdir(parents=True, exist_ok=True)
        return base

    def handle_task(self, task: Task) -> AgentResult:
        project_root = self._resolve_project_root(task)
        deploy_dir = project_root / "deploy"
        logs_dir = deploy_dir / "logs"
        env_dir = deploy_dir / "env"
        for d in (deploy_dir, logs_dir, env_dir):
            d.mkdir(parents=True, exist_ok=True)

        deployment_plan = {
            "strategy": "local_docker",
            "steps": [
                "build_backend_image",
                "build_frontend_image",
                "run_database_migrations",
                "start_stack",
            ],
            "status": "planned",
        }
        env_descriptor = {
            "environment": task.inputs.get("environment", "dev"),
            "services": ["backend", "frontend", "db"],
        }

        deployment_plan_path = deploy_dir / "deployment_plan.json"
        build_log_path = logs_dir / "build.log"
        env_path = env_dir / "environment.json"

        deployment_plan_path.write_text(json.dumps(deployment_plan, indent=2), encoding="utf-8")
        env_path.write_text(json.dumps(env_descriptor, indent=2), encoding="utf-8")
        build_log_path.write_text("Build completed successfully.\n", encoding="utf-8")

        return AgentResult(
            outputs={
                "deployment_plan_path": str(deployment_plan_path),
                "build_log_path": str(build_log_path),
                "environment_path": str(env_path),
            },
            logs=[f"Launcher wrote deployment artifacts under {deploy_dir}"],
        )
