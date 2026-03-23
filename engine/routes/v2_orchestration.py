from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel

from orchestration.runtime import OrchestrationRuntime
from orchestration.task_model import Task, TaskStatus
from orchestration.engine import OrchestrationEngine, RECURSIVE_STAGES, get_default_declared_outputs
from knowledge.knowledge_graph import KnowledgeGraph
from research.ingestion import IngestedSource, ResearchIngestionService


router = APIRouter()


class CommandPreviewRequest(BaseModel):
    command: str
    brief: Dict[str, Any] | None = None
    research_sources: List[Dict[str, Any]] | None = None


def _task_to_dict(task: Task) -> Dict[str, Any]:
    return {
        "task_id": task.task_id,
        "assigned_agent": task.assigned_agent,
        "status": task.status.value,
        "dependencies": list(task.dependencies),
        "description": task.description,
        "outputs": task.outputs,
    }


def _build_artifact_index(project_root: Path) -> Dict[str, Any]:
    """Summarize key artifacts for a project.

    This mirrors the shape documented in V2_RUNTIME_RELIABILITY_AND_PREVIEW.md
    and is intentionally conservative: it only reports booleans based on
    concrete filesystem checks under the given project root.
    """

    def exists(rel: str) -> bool:
        return (project_root / rel).exists()

    return {
        "intent": exists("intent.json"),
        "architecture": exists("architecture.json"),
        "tests": {
            "results": exists("tests/test_results.json"),
            "performance": exists("tests/performance_metrics.json"),
            "failures": exists("tests/failure_report.json"),
        },
        "reports": {
            "validation": exists("reports/validation_report.json"),
            "security": exists("reports/security_report.json"),
        },
        "deploy": {
            "plan": exists("deploy/deployment_plan.json"),
            "build_log": exists("deploy/logs/build.log"),
        },
    }


@router.post("/v2/command/preview", tags=["v2-orchestration"])
async def preview_command(body: CommandPreviewRequest) -> Dict[str, Any]:
    """Simulate a command through the V2 orchestration stack.

    This endpoint:
    - builds a task graph for the command
    - runs the simulation phase via the Probe agent
    - executes the minimal Plan→Build chain defined in the engine
    - returns the resulting task graph and simulation report

    It does not perform any real builds yet; all agent behavior is
    stubbed and safe.
    """

    runtime = OrchestrationRuntime()
    runtime.submit_command(body.command, brief=body.brief)
    await runtime.run_all()

    tasks: List[Task] = list(runtime.list_tasks().values())
    task_data = [_task_to_dict(t) for t in tasks]

    simulation = next((t for t in tasks if t.task_id == "cmd:simulate"), None)
    simulation_report = simulation.outputs if simulation else {}

    build = next((t for t in tasks if t.task_id == "cmd:build"), None)
    build_status = build.status.value if build else TaskStatus.PENDING.value

    # Optionally ingest research sources into the V2 knowledge graph so that
    # downstream agents can consult them in future iterations.
    research_summary: Dict[str, Any] = {"ingested": []}
    if body.research_sources:
        graph = KnowledgeGraph()
        ingestion = ResearchIngestionService(graph=graph)
        for raw in body.research_sources:
            src = IngestedSource(
                source_id=str(raw.get("id", "anon")),
                kind=str(raw.get("kind", "unknown")),
                path=raw.get("path"),
            )
            info = await ingestion.ingest(src, meta={"label": raw.get("label")})
            research_summary["ingested"].append(info)

    return {
        "success": True,
        "data": {
            "tasks": task_data,
            "simulation": simulation_report,
            "build_status": build_status,
            "recursive_loop": {
                "stages": list(RECURSIVE_STAGES),
            },
            "research": research_summary,
        },
        "error": None,
    }


@router.get("/v2/projects/{project_id}/status", tags=["v2-orchestration"])
async def project_status(project_id: str) -> Dict[str, Any]:
    """Return a deterministic status view for a project.

    This endpoint inspects the filesystem under ``projects/{project_id}`` and
    constructs a task-style view based on the default command graph and any
    AAA tasks defined by Origin's ``task_graph.json``.

    Task statuses are derived from artifact contracts:
    - when all declared outputs exist → ``completed``
    - when some are missing → ``failed`` with ``missing_outputs`` populated
    - when no outputs are declared → ``pending``
    """

    project_root = Path("projects") / project_id

    engine = OrchestrationEngine()
    # Seed the default command graph so we always have the core cmd:* tasks.
    engine.create_command_task_graph(command=f"status:{project_id}")
    # Optionally extend with Origin's AAA graph if present.
    engine.create_tasks_from_origin_graph(project_root)

    tasks_view: List[Dict[str, Any]] = []
    for task in engine.list_tasks():
        declared = get_default_declared_outputs(task.assigned_agent, project_root)
        missing = [path for path in declared if not Path(path).exists()]

        if not declared:
            status = TaskStatus.PENDING.value
        elif missing:
            status = TaskStatus.FAILED.value
        else:
            status = TaskStatus.COMPLETED.value

        tasks_view.append(
            {
                "task_id": task.task_id,
                "agent": task.assigned_agent,
                "status": status,
                "dependencies": list(task.dependencies),
                "declared_outputs": declared,
                "missing_outputs": missing,
                "phase": task.phase,
                "name": task.name or task.description,
            }
        )

    artifact_index = _build_artifact_index(project_root)

    return {
        "success": True,
        "data": {
            "project_id": project_id,
            "tasks": tasks_view,
            "artifact_index": artifact_index,
        },
        "error": None,
    }
