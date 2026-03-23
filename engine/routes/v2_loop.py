from __future__ import annotations

import asyncio
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Request
from pydantic import BaseModel

from control.execution_monitor import execution_monitor
from engine.router.config_loader import get_paths
from engine.security.preflight import require_preflight_ok


router = APIRouter(prefix="/v2/loop", tags=["v2-loop"])


STAGES: list[str] = ["plan", "build", "test", "review", "refine", "rebuild"]


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _loops_dir() -> Path:
    paths = get_paths()
    out = paths.resources_dir / "database" / "loops"
    out.mkdir(parents=True, exist_ok=True)
    return out


def _loop_path(loop_id: str) -> Path:
    return _loops_dir() / f"{loop_id}.json"


def _write_loop_state(loop_id: str, payload: Dict[str, Any]) -> None:
    try:
        _loop_path(loop_id).write_text(__import__("json").dumps(payload, indent=2), encoding="utf-8")
    except Exception:
        return


def _read_loop_state(loop_id: str) -> Dict[str, Any]:
    try:
        path = _loop_path(loop_id)
        if not path.is_file():
            return {}
        raw = __import__("json").loads(path.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else {}
    except Exception:
        return {}


def _default_provider(request: Request) -> str:
    provider = ""
    cfg_raw = getattr(request.app.state, "config", {}) or {}
    cfg = dict(cfg_raw) if isinstance(cfg_raw, dict) else {}
    raw_selected = cfg.get("providers")
    selected: dict[str, Any] = raw_selected if isinstance(raw_selected, dict) else {}
    provider = str(selected.get("llm") or "").strip().lower()
    if not provider:
        import os

        provider = os.environ.get("PROVIDER_LLM", "").strip().lower()
    return provider or "noop"


class LoopStartRequest(BaseModel):
    prompt: str
    project: str | None = None
    provider: str | None = None
    model: str | None = None
    max_iterations: int = 1


class LoopControlRequest(BaseModel):
    loop_id: str


@dataclass
class LoopHistoryEntry:
    iteration: int
    stage: str
    status: str
    started_at: str
    finished_at: str | None = None
    error: str | None = None


@dataclass
class LoopState:
    loop_id: str
    prompt: str
    project: str
    provider: str
    model: str | None
    max_iterations: int
    status: str = "running"
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)
    current_iteration: int = 0
    current_stage: str = ""
    history: list[LoopHistoryEntry] = field(default_factory=list)
    paused: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "loop_id": self.loop_id,
            "prompt": self.prompt,
            "project": self.project,
            "provider": self.provider,
            "model": self.model,
            "max_iterations": self.max_iterations,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "current_iteration": self.current_iteration,
            "current_stage": self.current_stage,
            "paused": self.paused,
            "history": [asdict(h) for h in self.history],
        }


class LoopRunner:
    def __init__(self, state: LoopState) -> None:
        self.state = state
        self._pause_gate = asyncio.Event()
        self._pause_gate.set()
        self._stop_requested = False

    def pause(self) -> None:
        self.state.paused = True
        self.state.updated_at = _now_iso()
        self._pause_gate.clear()

    def resume(self) -> None:
        self.state.paused = False
        self.state.updated_at = _now_iso()
        self._pause_gate.set()

    def stop(self) -> None:
        self._stop_requested = True
        self._pause_gate.set()

    async def run(self, request: Request) -> None:
        try:
            execution_monitor.start_pipeline(
                self.state.loop_id,
                metadata={
                    "type": "recursive_loop",
                    "project": self.state.project,
                    "provider": self.state.provider,
                    "model": self.state.model,
                    "max_iterations": self.state.max_iterations,
                },
            )
            _write_loop_state(self.state.loop_id, self.state.to_dict())

            from agents.pipeline import run as pipeline_run
            from engine.router.model_router import ModelRouter
            from providers.noop_provider import NoOpLLMProvider

            model_router = ModelRouter()
            for iteration in range(1, max(1, int(self.state.max_iterations)) + 1):
                if self._stop_requested:
                    self.state.status = "cancelled"
                    self.state.updated_at = _now_iso()
                    break
                self.state.current_iteration = iteration
                execution_monitor.loop_iteration(
                    self.state.loop_id,
                    iteration,
                    metadata={"project": self.state.project, "prompt": self.state.prompt},
                )
                _write_loop_state(self.state.loop_id, self.state.to_dict())

                for idx, stage in enumerate(STAGES):
                    await self._pause_gate.wait()
                    if self._stop_requested:
                        self.state.status = "cancelled"
                        self.state.updated_at = _now_iso()
                        break
                    self.state.current_stage = stage
                    self.state.updated_at = _now_iso()
                    h = LoopHistoryEntry(iteration=iteration, stage=stage, status="running", started_at=_now_iso())
                    self.state.history.append(h)
                    _write_loop_state(self.state.loop_id, self.state.to_dict())

                    stage_prompt = f"[loop_iteration:{iteration}][stage:{stage}][project:{self.state.project}]\n{self.state.prompt}"
                    execution_monitor.step_start(
                        self.state.loop_id,
                        step_index=idx,
                        agent_name=f"Loop:{stage}",
                        input_data={"prompt": stage_prompt, "project": self.state.project, "iteration": iteration, "stage": stage},
                    )
                    started = time.time()
                    try:
                        await pipeline_run(
                            stage_prompt,
                            context={
                                "pipeline_id": self.state.loop_id,
                                "stage": stage,
                                "iteration": iteration,
                                "project": self.state.project,
                                "workspace_path": getattr(request.app.state, "workspace_path", "") or "",
                            },
                            llm_provider=NoOpLLMProvider(),
                            model_router=model_router,
                        )
                        elapsed_ms = (time.time() - started) * 1000.0
                        h.status = "success"
                        h.finished_at = _now_iso()
                        execution_monitor.step_complete(
                            self.state.loop_id,
                            step_index=idx,
                            agent_name=f"Loop:{stage}",
                            output_data={"status": "success", "stage": stage, "iteration": iteration},
                            duration_ms=elapsed_ms,
                        )
                    except Exception as exc:
                        elapsed_ms = (time.time() - started) * 1000.0
                        h.status = "error"
                        h.error = str(exc)
                        h.finished_at = _now_iso()
                        execution_monitor.step_failed(self.state.loop_id, step_index=idx, agent_name=f"Loop:{stage}", error=str(exc))
                        self.state.status = "error"
                        self.state.updated_at = _now_iso()
                        _write_loop_state(self.state.loop_id, self.state.to_dict())
                        execution_monitor.end_pipeline(self.state.loop_id, status="error")
                        return
                    finally:
                        self.state.updated_at = _now_iso()
                        _write_loop_state(self.state.loop_id, self.state.to_dict())
                if self.state.status in {"cancelled", "error"}:
                    break

            if self.state.status not in {"cancelled", "error"}:
                self.state.status = "completed"
                self.state.updated_at = _now_iso()
            _write_loop_state(self.state.loop_id, self.state.to_dict())
            execution_monitor.end_pipeline(self.state.loop_id, status=self.state.status)
        except asyncio.CancelledError:
            self.state.status = "cancelled"
            self.state.updated_at = _now_iso()
            _write_loop_state(self.state.loop_id, self.state.to_dict())
            execution_monitor.end_pipeline(self.state.loop_id, status="cancelled")
            raise
        except Exception as exc:
            self.state.status = "error"
            self.state.updated_at = _now_iso()
            _write_loop_state(self.state.loop_id, self.state.to_dict())
            execution_monitor.end_pipeline(self.state.loop_id, status="error")
            raise exc


_running_loops: dict[str, asyncio.Task] = {}
_loop_runners: dict[str, LoopRunner] = {}


@router.get("/stages")
async def list_stages() -> Dict[str, Any]:
    return {"success": True, "data": {"stages": list(STAGES)}, "error": None}


@router.post("/run")
async def run_loop(body: LoopStartRequest, request: Request) -> Dict[str, Any]:
    ok, preflight = await require_preflight_ok(request, scope="loop.run")
    if not ok:
        return {"success": False, "data": {"preflight": preflight}, "error": "Preflight failed"}

    max_prompt_chars = int(os.getenv("AGENTFORGE_MAX_PROMPT_CHARS", "50000") or "50000")
    if not isinstance(body.prompt, str) or not body.prompt.strip():
        return {"success": False, "data": None, "error": "prompt is required"}
    if len(body.prompt) > max_prompt_chars:
        return {"success": False, "data": None, "error": f"prompt exceeds max length ({max_prompt_chars} chars)"}

    max_allowed_iters = int(os.getenv("AGENTFORGE_LOOP_MAX_ITERATIONS", "10") or "10")
    requested_iters = int(body.max_iterations) if isinstance(body.max_iterations, int) else 1
    safe_iters = max(1, min(requested_iters, max_allowed_iters))

    loop_id = f"loop_{uuid4().hex[:12]}"
    provider = (body.provider or "").strip().lower() or _default_provider(request)
    project = str(body.project or "projects/session_default").strip() or "projects/session_default"
    state = LoopState(loop_id=loop_id, prompt=body.prompt, project=project, provider=provider, model=body.model, max_iterations=safe_iters)
    runner = LoopRunner(state)
    _loop_runners[loop_id] = runner
    await runner.run(request)
    return {"success": True, "data": {"loop_id": loop_id, "status": runner.state.status, "state": runner.state.to_dict()}, "error": None}


@router.post("/start")
async def start_loop(body: LoopStartRequest, request: Request) -> Dict[str, Any]:
    ok, preflight = await require_preflight_ok(request, scope="loop.start")
    if not ok:
        return {"success": False, "data": {"preflight": preflight}, "error": "Preflight failed"}

    max_prompt_chars = int(os.getenv("AGENTFORGE_MAX_PROMPT_CHARS", "50000") or "50000")
    if not isinstance(body.prompt, str) or not body.prompt.strip():
        return {"success": False, "data": None, "error": "prompt is required"}
    if len(body.prompt) > max_prompt_chars:
        return {"success": False, "data": None, "error": f"prompt exceeds max length ({max_prompt_chars} chars)"}

    max_allowed_iters = int(os.getenv("AGENTFORGE_LOOP_MAX_ITERATIONS", "10") or "10")
    requested_iters = int(body.max_iterations) if isinstance(body.max_iterations, int) else 1
    safe_iters = max(1, min(requested_iters, max_allowed_iters))

    loop_id = f"loop_{uuid4().hex[:12]}"
    provider = (body.provider or "").strip().lower() or _default_provider(request)
    project = str(body.project or "projects/session_default").strip() or "projects/session_default"
    state = LoopState(loop_id=loop_id, prompt=body.prompt, project=project, provider=provider, model=body.model, max_iterations=safe_iters)
    runner = LoopRunner(state)
    _loop_runners[loop_id] = runner

    task = asyncio.create_task(runner.run(request))
    _running_loops[loop_id] = task

    def _cleanup(_t: asyncio.Task) -> None:
        _running_loops.pop(loop_id, None)

    task.add_done_callback(_cleanup)
    return {"success": True, "data": {"loop_id": loop_id, "status": "running"}, "error": None}


@router.post("/pause")
async def pause_loop(body: LoopControlRequest) -> Dict[str, Any]:
    runner = _loop_runners.get(body.loop_id)
    if not runner:
        return {"success": False, "data": None, "error": "loop not found"}
    runner.pause()
    _write_loop_state(body.loop_id, runner.state.to_dict())
    execution_monitor.pipeline_modified(body.loop_id, change_type="pause", details={})
    return {"success": True, "data": {"loop_id": body.loop_id, "paused": True}, "error": None}


@router.post("/resume")
async def resume_loop(body: LoopControlRequest) -> Dict[str, Any]:
    runner = _loop_runners.get(body.loop_id)
    if not runner:
        return {"success": False, "data": None, "error": "loop not found"}
    runner.resume()
    _write_loop_state(body.loop_id, runner.state.to_dict())
    execution_monitor.pipeline_modified(body.loop_id, change_type="resume", details={})
    return {"success": True, "data": {"loop_id": body.loop_id, "paused": False}, "error": None}


@router.post("/stop")
async def stop_loop(body: LoopControlRequest) -> Dict[str, Any]:
    runner = _loop_runners.get(body.loop_id)
    task = _running_loops.get(body.loop_id)
    if not runner and not task:
        return {"success": False, "data": None, "error": "loop not found"}
    if runner:
        runner.stop()
        _write_loop_state(body.loop_id, runner.state.to_dict())
    if task:
        task.cancel()
    execution_monitor.pipeline_modified(body.loop_id, change_type="stop", details={})
    return {"success": True, "data": {"loop_id": body.loop_id, "stopped": True}, "error": None}


@router.get("/status")
async def loop_status(loop_id: str) -> Dict[str, Any]:
    state = _read_loop_state(loop_id)
    if not state:
        runner = _loop_runners.get(loop_id)
        if runner:
            state = runner.state.to_dict()
    if not state:
        return {"success": False, "data": None, "error": "loop not found"}
    state["running"] = bool(loop_id in _running_loops)
    return {"success": True, "data": state, "error": None}


@router.get("/history")
async def loop_history(loop_id: str) -> Dict[str, Any]:
    state = _read_loop_state(loop_id)
    if not state:
        runner = _loop_runners.get(loop_id)
        if runner:
            state = runner.state.to_dict()
    if not state:
        return {"success": False, "data": None, "error": "loop not found"}
    return {"success": True, "data": {"loop_id": loop_id, "history": state.get("history", [])}, "error": None}
