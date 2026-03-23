from __future__ import annotations

import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Request
from pydantic import BaseModel


router = APIRouter(tags=["tasks"])


MAX_FILES_PER_TASK = 5
MAX_LOC_PER_TASK = 500
MAX_PARALLEL_TASKS = 3
MAX_RETRIES = 1


@dataclass
class Task:
    task_id: str
    type: str
    description: str
    status: str = "pending"
    assigned_agent: Optional[str] = None
    depends_on: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    retry_count: int = 0
    last_error: Optional[str] = None
    planned_files: Optional[int] = None
    planned_loc: Optional[int] = None
    actual_files: Optional[int] = None
    actual_loc: Optional[int] = None
    validation: Dict[str, Any] = field(default_factory=dict)
    escalated: bool = False
    escalation_reason: Optional[str] = None
    escalation_at: Optional[str] = None


_tasks: Dict[str, Task] = {}
_loaded = False


def _resources_root(exe_base: Path) -> Path:
    if exe_base.name.lower() == "resources":
        return exe_base
    return exe_base / "resources"


def _tasks_file(request: Request) -> Path:
    exe_base_raw = getattr(request.app.state, "base_path", "")
    exe_base = Path(exe_base_raw) if isinstance(exe_base_raw, str) and exe_base_raw else Path(__file__).resolve().parent.parent.parent
    resources_dir = _resources_root(exe_base)
    db_dir = resources_dir / "database"
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir / "tasks.json"


def _load_from_disk(request: Request) -> None:
    global _loaded, _tasks
    if _loaded:
        return
    path = _tasks_file(request)
    try:
        if path.is_file():
            raw = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(raw, list):
                for entry in raw:
                    if not isinstance(entry, dict):
                        continue
                    task_id = entry.get("task_id")
                    if not isinstance(task_id, str) or not task_id.strip():
                        continue
                    fields = set(Task.__dataclass_fields__.keys())
                    payload = {k: v for k, v in entry.items() if k in fields}
                    _tasks[task_id] = Task(**payload)
    except Exception:
        _tasks = {}
    _loaded = True


def _save_to_disk(request: Request) -> None:
    path = _tasks_file(request)
    payload = [asdict(t) for t in _tasks.values()]
    try:
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except Exception:
        return


def create_task_internal(
    request: Request,
    *,
    type: str,
    description: str,
    assigned_agent: Optional[str] = None,
    depends_on: Optional[List[str]] = None,
    planned_files: Optional[int] = None,
    planned_loc: Optional[int] = None,
) -> Task:
    _load_from_disk(request)
    task_id = f"task_{uuid4().hex[:8]}"
    t = Task(
        task_id=task_id,
        type=type.strip(),
        description=description.strip(),
        assigned_agent=assigned_agent,
        depends_on=list(depends_on or []),
        planned_files=planned_files,
        planned_loc=planned_loc,
    )
    _tasks[task_id] = t
    _save_to_disk(request)
    return t


def set_task_status_internal(request: Request, task_id: str, status: str, error: Optional[str] = None) -> Optional[Task]:
    _load_from_disk(request)
    t = _tasks.get(task_id)
    if not t:
        return None
    t.status = status
    t.updated_at = _now()
    if error:
        t.last_error = error
    _save_to_disk(request)
    return t


def complete_task_internal(request: Request, task_id: str, *, actual_files: int = 0, actual_loc: int = 0) -> Optional[Task]:
    _load_from_disk(request)
    t = _tasks.get(task_id)
    if not t:
        return None
    t.status = "completed"
    t.actual_files = int(actual_files)
    t.actual_loc = int(actual_loc)
    t.last_error = None
    t.updated_at = _now()
    _save_to_disk(request)
    return t


def fail_task_internal(request: Request, task_id: str, error: str) -> Optional[Task]:
    _load_from_disk(request)
    t = _tasks.get(task_id)
    if not t:
        return None
    t.retry_count += 1
    t.last_error = error
    t.updated_at = _now()
    if t.retry_count <= MAX_RETRIES:
        t.status = "retry"
    else:
        t.status = "failed"
        t.escalated = True
        t.escalation_reason = error
        t.escalation_at = _now()
    _save_to_disk(request)
    return t


def _block_dependents(request: Request, failed_task_id: str) -> None:
    for t in _tasks.values():
        if failed_task_id in (t.depends_on or []) and t.status not in {"completed", "failed", "blocked"}:
            t.status = "blocked"
            t.last_error = f"Blocked: dependency {failed_task_id} failed"
            t.updated_at = _now()
    _save_to_disk(request)


class TaskCreateRequest(BaseModel):
    type: str
    description: str
    assigned_agent: Optional[str] = None
    depends_on: List[str] = []
    planned_files: Optional[int] = None
    planned_loc: Optional[int] = None


class TaskRunRequest(BaseModel):
    task_id: str


class TaskCompleteRequest(BaseModel):
    task_id: str
    actual_files: int
    actual_loc: int
    validation_passed: bool
    error: Optional[str] = None


class TaskFailRequest(BaseModel):
    task_id: str
    error: str


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _in_progress_count() -> int:
    return sum(1 for t in _tasks.values() if t.status == "in_progress")


def _dependencies_satisfied(task: Task) -> bool:
    for dep_id in task.depends_on:
        dep = _tasks.get(dep_id)
        if not dep or dep.status != "completed":
            return False
    return True


@router.get("/tasks")
async def list_tasks(request: Request):
    _load_from_disk(request)
    return {"success": True, "data": {"tasks": [asdict(t) for t in _tasks.values()]}, "error": None}


@router.post("/tasks/create")
async def create_task(request: Request, body: TaskCreateRequest):
    _load_from_disk(request)
    if not body.type.strip() or not body.description.strip():
        return {"success": False, "data": None, "error": "type and description are required"}

    if body.planned_files is not None and int(body.planned_files) > MAX_FILES_PER_TASK:
        return {"success": False, "data": None, "error": "planned_files exceeds limit"}
    if body.planned_loc is not None and int(body.planned_loc) > MAX_LOC_PER_TASK:
        return {"success": False, "data": None, "error": "planned_loc exceeds limit"}

    task_id = f"task_{uuid4().hex[:8]}"
    t = Task(
        task_id=task_id,
        type=body.type.strip(),
        description=body.description.strip(),
        assigned_agent=body.assigned_agent,
        depends_on=list(body.depends_on or []),
        planned_files=body.planned_files,
        planned_loc=body.planned_loc,
    )
    _tasks[task_id] = t
    _save_to_disk(request)
    return {"success": True, "data": {"task": asdict(t)}, "error": None}


@router.get("/tasks/status")
async def task_status(request: Request, task_id: str):
    _load_from_disk(request)
    t = _tasks.get(task_id)
    if not t:
        return {"success": False, "data": None, "error": "task not found"}
    return {"success": True, "data": {"task": asdict(t)}, "error": None}


@router.post("/tasks/run")
async def run_task(request: Request, body: TaskRunRequest):
    _load_from_disk(request)
    t = _tasks.get(body.task_id)
    if not t:
        return {"success": False, "data": None, "error": "task not found"}

    if t.status in {"completed"}:
        return {"success": False, "data": None, "error": "task already completed"}
    if t.status in {"failed", "blocked"}:
        return {"success": False, "data": None, "error": "task cannot be run"}

    if not _dependencies_satisfied(t):
        return {"success": False, "data": None, "error": "dependencies not satisfied"}

    if _in_progress_count() >= MAX_PARALLEL_TASKS:
        return {"success": False, "data": None, "error": "parallel task limit reached"}

    t.status = "in_progress"
    t.updated_at = _now()
    _save_to_disk(request)
    return {"success": True, "data": {"task": asdict(t)}, "error": None}


@router.post("/tasks/complete")
async def complete_task(request: Request, body: TaskCompleteRequest):
    _load_from_disk(request)
    t = _tasks.get(body.task_id)
    if not t:
        return {"success": False, "data": None, "error": "task not found"}

    if int(body.actual_files) > MAX_FILES_PER_TASK:
        return {"success": False, "data": None, "error": "actual_files exceeds limit"}
    if int(body.actual_loc) > MAX_LOC_PER_TASK:
        return {"success": False, "data": None, "error": "actual_loc exceeds limit"}
    if t.planned_files is not None and int(body.actual_files) > int(t.planned_files):
        return {"success": False, "data": None, "error": "actual_files exceeds plan"}
    if t.planned_loc is not None and int(body.actual_loc) > int(t.planned_loc):
        return {"success": False, "data": None, "error": "actual_loc exceeds plan"}
    if not body.validation_passed:
        return {"success": False, "data": None, "error": "validation failed"}

    t.status = "completed"
    t.actual_files = int(body.actual_files)
    t.actual_loc = int(body.actual_loc)
    t.last_error = None
    t.validation = {"passed": True, "method": "client_asserted", "validated_at": _now()}
    t.updated_at = _now()
    _save_to_disk(request)
    return {"success": True, "data": {"task": asdict(t)}, "error": None}


@router.post("/tasks/fail")
async def fail_task(request: Request, body: TaskFailRequest):
    _load_from_disk(request)
    t = _tasks.get(body.task_id)
    if not t:
        return {"success": False, "data": None, "error": "task not found"}

    t.retry_count += 1
    t.last_error = body.error
    t.updated_at = _now()
    if t.retry_count <= MAX_RETRIES:
        t.status = "retry"
        _save_to_disk(request)
        return {"success": True, "data": {"task": asdict(t), "action": "retry"}, "error": None}

    t.status = "failed"
    t.escalated = True
    t.escalation_reason = body.error
    t.escalation_at = _now()
    _block_dependents(request, t.task_id)
    _save_to_disk(request)
    return {"success": True, "data": {"task": asdict(t), "action": "escalate"}, "error": None}
