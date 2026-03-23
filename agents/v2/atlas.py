from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from typing import Any, Dict

from orchestration.task_model import Task
from .base import Agent, AgentResult


@dataclass
class AtlasAgent:
    """ARCHITECT (Atlas) agent.

    Implements the role defined in V2_AGENT_ROLES:
    - defines system modules and gameplay/backend/UI layers
    - defines data models and interfaces
    - selects engines/frameworks
    - emits architecture.json, modules.json, interfaces.json, data_models.json
    """

    name: str = "Architect"

    def _resolve_project_root(self, task: Task) -> Path:
        raw = task.inputs.get("project_root")
        base = Path(raw) if raw else Path("projects") / "session_default"
        base.mkdir(parents=True, exist_ok=True)
        return base

    def _load_intent(self, project_root: Path) -> Dict[str, Any]:
        intent_path = project_root / "intent.json"
        if intent_path.is_file():
            try:
                return json.loads(intent_path.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    def handle_task(self, task: Task) -> AgentResult:
        project_root = self._resolve_project_root(task)
        intent = self._load_intent(project_root)
        product_type = intent.get("product_type", "hybrid")

        # Very lightweight derived structure from intent; this is
        # deterministic scaffolding, not a simulator.
        has_gameplay = bool(intent.get("scope", {}).get("has_gameplay", product_type == "game"))

        architecture: Dict[str, Any] = {
            "product_type": product_type,
            "layers": ["frontend", "backend", "orchestration"],
            "has_gameplay": has_gameplay,
        }

        modules: Dict[str, Any] = {
            "frontend": {
                "pages": ["command_center", "project_workspace", "research_lab"],
            },
            "backend": {
                "services": ["orchestration", "knowledge", "research", "infrastructure"],
            },
            "gameplay": {"systems": ["core_loop", "progression"]} if has_gameplay else {},
        }

        interfaces: Dict[str, Any] = {
            "frontend_backend": {
                "protocol": "http",
                "endpoints": ["/api/v2/command/preview", "/api/v2/research/ingest"],
            }
        }

        data_models: Dict[str, Any] = {
            "Project": {"fields": ["id", "name", "type", "created_at"]},
            "Task": {"fields": ["id", "agent", "status", "inputs", "outputs"]},
        }

        arch_path = project_root / "architecture.json"
        modules_path = project_root / "modules.json"
        interfaces_path = project_root / "interfaces.json"
        data_models_path = project_root / "data_models.json"

        arch_path.write_text(json.dumps(architecture, indent=2), encoding="utf-8")
        modules_path.write_text(json.dumps(modules, indent=2), encoding="utf-8")
        interfaces_path.write_text(json.dumps(interfaces, indent=2), encoding="utf-8")
        data_models_path.write_text(json.dumps(data_models, indent=2), encoding="utf-8")

        return AgentResult(
            outputs={
                "architecture_path": str(arch_path),
                "modules_path": str(modules_path),
                "interfaces_path": str(interfaces_path),
                "data_models_path": str(data_models_path),
            },
            logs=[
                f"Atlas generated architecture artifacts in {project_root}",
                f"product_type={product_type}",
            ],
        )
