from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple
import json

from .task_model import Task, TaskStatus


RECURSIVE_STAGES: Tuple[str, ...] = (
    "plan",
    "build",
    "test",
    "review",
    "refine",
    "rebuild",
)

# Default project root used by the initial command graph. Individual
# agents can override this via an explicit ``project_root`` input,
# but when none is provided, the V2 agents all default to this path.
DEFAULT_PROJECT_ROOT = Path("projects") / "session_default"


def get_default_declared_outputs(agent: str, project_root: Path) -> List[str]:
    """Return the default declared_outputs for a given agent.

    This encodes, in one place, which concrete artifacts each V2
    role is responsible for producing under a project root. Tasks
    can use this helper to populate ``declared_outputs`` so that
    verify_outputs enforces the contracts.
    """

    root = project_root

    if agent == "Origin":
        return [
            str(root / "intent.json"),
            str(root / "task_graph.json"),
            str(root / "build_plan.json"),
        ]
    if agent == "Architect":
        return [
            str(root / "architecture.json"),
            str(root / "modules.json"),
            str(root / "interfaces.json"),
            str(root / "data_models.json"),
        ]
    if agent == "Analyst":
        return [
            str(root / "tests" / "test_results.json"),
            str(root / "tests" / "performance_metrics.json"),
            str(root / "tests" / "failure_report.json"),
        ]
    if agent == "Builder":
        return [
            str(root / "backend" / "app.py"),
            str(root / "backend" / "routes.py"),
            str(root / "backend"),
            str(root / "gameplay"),
            str(root / "systems"),
            str(root / "scripts"),
        ]
    if agent == "Surface":
        return [
            str(root / "frontend" / "src" / "pages" / "CommandCenter.tsx"),
            str(root / "frontend" / "src" / "pages" / "ProjectWorkspace.tsx"),
            str(root / "frontend" / "src" / "pages" / "ResearchLab.tsx"),
            str(root / "frontend" / "src" / "components" / "AppShell.tsx"),
        ]
    if agent == "Core":
        return [
            str(root / "backend" / "api" / "routes.py"),
            str(root / "backend" / "services" / "project_service.py"),
            str(root / "backend" / "models" / "project.py"),
        ]
    if agent == "Simulator":
        return [
            str(root / "unity" / "AgentForgeBootstrap.cs"),
            str(root / "unreal" / "AgentForgeBootstrap.cpp"),
            str(root / "engine_scripts" / "engine_bridge.md"),
        ]
    if agent == "Synapse":
        return [
            str(root / "model_routes.json"),
            str(root / "inference_logs.json"),
        ]
    if agent == "Fabricator":
        return [
            str(root / "assets" / "asset_manifest.json"),
            str(root / "assets" / "ui" / "core_ui_manifest.md"),
            str(root / "assets" / "audio" / "core_audio_manifest.md"),
        ]
    if agent == "Guardian":
        return [
            str(root / "reports" / "validation_report.json"),
            str(root / "reports" / "security_report.json"),
            str(root / "reports" / "issues.json"),
        ]
    if agent == "Launcher":
        return [
            str(root / "deploy" / "deployment_plan.json"),
            str(root / "deploy" / "logs" / "build.log"),
            str(root / "deploy" / "env" / "environment.json"),
        ]
    if agent == "Archivist":
        return [
            str(root / "research" / "research_insights.json"),
            str(root / "research" / "patterns.json"),
            str(root / "research" / "extracted_systems.json"),
        ]

    return []


@dataclass
class OrchestrationEngine:
    """V2 orchestration controller.

    - Parses high-level commands into tasks
    - Builds and manages task graphs
    - Enforces simulation-before-build gating
    - Coordinates the recursive Plan→Build→Test→Review→Refine→Rebuild loop
    """

    tasks: Dict[str, Task] = field(default_factory=dict)
    simulation_required: bool = True

    def add_task(self, task: Task) -> None:
        self.tasks[task.task_id] = task

    def get_task(self, task_id: str) -> Task:
        return self.tasks[task_id]

    def list_tasks(self) -> List[Task]:
        return list(self.tasks.values())

    def create_command_task_graph(self, command: str) -> List[Task]:
        """Create a minimal task graph for a new command.

        This is intentionally generic scaffolding; Commander/Probe/Forge/etc.
        will specialize it when the full V2 chain is wired.
        """

        default_root = DEFAULT_PROJECT_ROOT

        # All tasks share the same default project root by default so
        # agents can resolve artifacts deterministically.
        project_root_str = str(default_root)

        root = Task(
            task_id="cmd:root",
            assigned_agent="Origin",
            inputs={"command": command, "project_root": project_root_str},
            description="Entry task for user command",
            declared_outputs=get_default_declared_outputs("Origin", default_root),
        )
        self.add_task(root)

        simulation = Task(
            task_id="cmd:simulate",
            assigned_agent="Analyst",
            inputs={"project_root": project_root_str},
            dependencies=[root.task_id],
            description="Simulate build before execution",
            declared_outputs=get_default_declared_outputs("Analyst", default_root),
        )
        self.add_task(simulation)

        plan = Task(
            task_id="cmd:plan",
            assigned_agent="Architect",
            inputs={"project_root": project_root_str},
            dependencies=[simulation.task_id],
            description="Architecture plan after simulation approval",
            declared_outputs=get_default_declared_outputs("Architect", default_root),
        )
        self.add_task(plan)

        build = Task(
            task_id="cmd:build",
            assigned_agent="Builder",
            inputs={"project_root": project_root_str},
            dependencies=[plan.task_id],
            description="Primary build task (gated by simulation)",
            declared_outputs=get_default_declared_outputs("Builder", default_root),
        )
        self.add_task(build)

        # Validation and launch stages. These make Guardian and Launcher
        # concrete participants in the default command flow so that their
        # artifact contracts are enforced as well.
        guard = Task(
            task_id="cmd:guard",
            assigned_agent="Guardian",
            inputs={"project_root": project_root_str},
            dependencies=[build.task_id],
            description="Run safety and validation checks after build",
            declared_outputs=get_default_declared_outputs("Guardian", default_root),
        )
        self.add_task(guard)

        launch = Task(
            task_id="cmd:launch",
            assigned_agent="Launcher",
            inputs={"project_root": project_root_str},
            dependencies=[guard.task_id],
            description="Prepare deployment artifacts after validation",
            declared_outputs=get_default_declared_outputs("Launcher", default_root),
        )
        self.add_task(launch)

        return [root, simulation, plan, build, guard, launch]

    def create_tasks_from_origin_graph(self, project_root: Path | str) -> List[Task]:
        """Instantiate tasks from Origin's task_graph.json specification.

        This uses the AAA-style graph that Origin writes to define
        additional tasks and attaches declared_outputs contracts for
        each agent via get_default_declared_outputs.
        """

        root_path = Path(project_root)
        spec_path = root_path / "task_graph.json"
        if not spec_path.is_file():
            return []

        data = json.loads(spec_path.read_text(encoding="utf-8"))
        created: List[Task] = []
        for node in data:
            task_id = node.get("task_id")
            agent = node.get("agent")
            if not task_id or not agent:
                continue

            deps = list(node.get("dependencies") or [])
            name = node.get("name")

            task = Task(
                task_id=task_id,
                assigned_agent=agent,
                name=name,
                description=name,
                dependencies=deps,
                inputs={"project_root": str(root_path)},
                declared_outputs=get_default_declared_outputs(agent, root_path),
            )
            # Do not overwrite any existing tasks with the same id.
            if task_id not in self.tasks:
                self.add_task(task)
                created.append(task)

        return created

    def mark_simulation_result(self, task_id: str, approved: bool, details: dict | None = None) -> None:
        """Record the outcome of the simulation and enforce gating.

        When ``approved`` is False, all build-oriented tasks (currently
        represented by the Forge and DevOps Engineer agents) are marked as
        BLOCKED so they cannot be executed. This encodes the Build Bible
        rule that no builds may start without simulation approval.
        """

        task = self.get_task(task_id)
        task.outputs["simulation"] = {"approved": approved, "details": details or {}}
        task.status = TaskStatus.COMPLETED if approved else TaskStatus.FAILED

        # If simulation failed, block all build tasks. We intentionally do
        # not try to be clever about graph topology here: the Build Bible
        # requires that *no* build work proceed when feasibility is not
        # approved, so any Builder / Launcher tasks are blocked globally.
        if not approved:
            for t in self.tasks.values():
                if t.assigned_agent in {"Builder", "Launcher"}:
                    t.status = TaskStatus.BLOCKED

    def next_ready_tasks(self) -> List[Task]:
        completed = [t.task_id for t in self.tasks.values() if t.status == TaskStatus.COMPLETED]
        ready: List[Task] = []
        for task in self.tasks.values():
            if task.is_ready(completed_task_ids=completed):
                if task.status != TaskStatus.READY:
                    task.status = TaskStatus.READY
                ready.append(task)
        return ready

    def start_task(self, task_id: str) -> None:
        task = self.get_task(task_id)
        if task.status == TaskStatus.READY:
            task.status = TaskStatus.RUNNING

    def complete_task(self, task_id: str, outputs: dict | None = None) -> None:
        task = self.get_task(task_id)
        task.outputs.update(outputs or {})
        task.status = TaskStatus.COMPLETED

    def fail_task(self, task_id: str, error: str) -> None:
        task = self.get_task(task_id)
        task.outputs.setdefault("errors", []).append(error)
        task.status = TaskStatus.FAILED

    def verify_outputs(self, task_id: str) -> None:
        """Verify declared output artifacts exist on disk.

        This is a non-breaking scaffold for the V2 execution model's
        artifact enforcement rules. If a task declares expected output
        paths in ``declared_outputs`` and any are missing, the task is
        marked FAILED and the missing paths are recorded. When no
        outputs are declared, this method is a no-op.
        """

        task = self.get_task(task_id)
        declared = getattr(task, "declared_outputs", None) or []
        if not declared:
            return

        missing: list[str] = []
        for raw in declared:
            path = Path(raw)
            if not path.exists():
                missing.append(str(path))

        if missing:
            task.status = TaskStatus.FAILED
            task.outputs.setdefault("missing_outputs", []).extend(missing)

    def describe_recursive_loop(self) -> Dict[str, str]:
        """Return a static description of the recursive loop stages.

        This is used by the UI / API to render the Plan→Build→Test→Review→Refine→Rebuild
        stages even before the full execution plumbing is wired.
        """

        return {
            "stages": ",".join(RECURSIVE_STAGES),
        }
