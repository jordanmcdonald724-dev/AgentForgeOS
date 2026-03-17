"""Execution monitor for tracking pipeline activity.

This module intentionally supports two layers:
- A simple record list used by the legacy supervisor flow (start_step/end_step/record_error)
- A richer event stream used by the AgentForge UI (step_start/step_complete/step_failed/etc.)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional


@dataclass
class ExecutionRecord:
    """Legacy per-step record (kept for backwards compatibility)."""

    step: str
    status: str
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionEvent:
    """UI-focused execution event."""

    event_type: str
    pipeline_id: str
    step_index: Optional[int]
    agent_name: Optional[str]
    timestamp: str
    data: Dict[str, object] = field(default_factory=dict)


class ExecutionMonitor:
    """Tracks execution state and emits events for UI streaming."""

    def __init__(self) -> None:
        self.records: List[ExecutionRecord] = []
        self._events: List[ExecutionEvent] = []

    # ------------------------------------------------------------------ #
    # Legacy API (used by control/agent_supervisor.py)
    # ------------------------------------------------------------------ #
    def start_step(self, step: str, context: Optional[Any] = None) -> None:
        self.records.append(ExecutionRecord(step=step, status="started"))
        self._record_event(
            event_type="step_start",
            pipeline_id=_pipeline_id_from_context(context),
            step_index=_step_index_from_context(context),
            agent_name=step,
            data={"input_data": _context_to_data(context)},
        )

    def end_step(self, step: str, result: Dict[str, Any]) -> None:
        self.records.append(ExecutionRecord(step=step, status="completed", metadata={"result": result}))
        self._record_event(
            event_type="step_complete",
            pipeline_id=_pipeline_id_from_context(result),
            step_index=_step_index_from_context(result),
            agent_name=step,
            data={"output_data": result or {}},
        )

    def record_error(self, step: str, error: str) -> None:
        self.records.append(ExecutionRecord(step=step, status="error", error=error))
        self._record_event(
            event_type="step_failed",
            pipeline_id="unknown",
            step_index=None,
            agent_name=step,
            data={"error": error},
        )

    # ------------------------------------------------------------------ #
    # Event-stream API (preferred for new systems)
    # ------------------------------------------------------------------ #
    def start_pipeline(self, pipeline_id: str, metadata: Dict[str, object]) -> None:
        self._record_event(
            event_type="pipeline_start",
            pipeline_id=pipeline_id,
            step_index=None,
            agent_name=None,
            data={"metadata": metadata or {}},
        )

    def end_pipeline(self, pipeline_id: str, status: str) -> None:
        self._record_event(
            event_type="pipeline_complete",
            pipeline_id=pipeline_id,
            step_index=None,
            agent_name=None,
            data={"status": status},
        )

    def step_start(self, pipeline_id: str, step_index: int, agent_name: str, input_data: Dict[str, object]) -> None:
        self._record_event(
            event_type="step_start",
            pipeline_id=pipeline_id,
            step_index=step_index,
            agent_name=agent_name,
            data={"input_data": input_data or {}},
        )

    def step_complete(
        self, pipeline_id: str, step_index: int, agent_name: str, output_data: Dict[str, object], duration_ms: float
    ) -> None:
        self._record_event(
            event_type="step_complete",
            pipeline_id=pipeline_id,
            step_index=step_index,
            agent_name=agent_name,
            data={"output_data": output_data or {}, "duration_ms": duration_ms},
        )

    def step_failed(self, pipeline_id: str, step_index: int, agent_name: str, error: str) -> None:
        self._record_event(
            event_type="step_failed",
            pipeline_id=pipeline_id,
            step_index=step_index,
            agent_name=agent_name,
            data={"error": error},
        )

    def step_retry(self, pipeline_id: str, step_index: int, agent_name: str, retry_attempt: int) -> None:
        self._record_event(
            event_type="step_retry",
            pipeline_id=pipeline_id,
            step_index=step_index,
            agent_name=agent_name,
            data={"retry_attempt": retry_attempt},
        )

    def pipeline_modified(self, pipeline_id: str, change_type: str, details: Dict[str, object]) -> None:
        self._record_event(
            event_type="pipeline_modified",
            pipeline_id=pipeline_id,
            step_index=None,
            agent_name=None,
            data={"change_type": change_type, "details": details or {}},
        )

    def agent_created(self, pipeline_id: str, agent_name: str, role: str) -> None:
        self._record_event(
            event_type="agent_created",
            pipeline_id=pipeline_id,
            step_index=None,
            agent_name=agent_name,
            data={"role": role},
        )

    def loop_iteration(self, pipeline_id: str, iteration: int, metadata: Optional[Dict[str, object]] = None) -> None:
        self._record_event(
            event_type="loop_iteration",
            pipeline_id=pipeline_id,
            step_index=None,
            agent_name=None,
            data={"iteration": int(iteration), "metadata": metadata or {}},
        )

    def get_events(self, pipeline_id: Optional[str] = None) -> List[ExecutionEvent]:
        if pipeline_id is None:
            return list(self._events)
        return [event for event in self._events if event.pipeline_id == pipeline_id]

    def get_events_since(self, cursor: int, pipeline_id: Optional[str] = None) -> List[ExecutionEvent]:
        events = self.get_events(pipeline_id=pipeline_id)
        if cursor <= 0:
            return events
        if cursor >= len(events):
            return []
        return events[cursor:]

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _record_event(
        self,
        event_type: str,
        pipeline_id: str,
        step_index: Optional[int],
        agent_name: Optional[str],
        data: Dict[str, object],
    ) -> None:
        try:
            self._events.append(
                ExecutionEvent(
                    event_type=event_type,
                    pipeline_id=pipeline_id,
                    step_index=step_index,
                    agent_name=agent_name,
                    timestamp=datetime.now(UTC).isoformat(),
                    data=data or {},
                )
            )
        except Exception:
            return


def _pipeline_id_from_context(ctx: Any) -> str:
    if isinstance(ctx, dict):
        v = ctx.get("pipeline_id")
        if isinstance(v, str) and v.strip():
            return v
    return "unknown"


def _step_index_from_context(ctx: Any) -> Optional[int]:
    if isinstance(ctx, dict):
        v = ctx.get("step_index")
        if isinstance(v, int):
            return v
    return None


def _context_to_data(ctx: Any) -> Dict[str, object]:
    if isinstance(ctx, dict):
        return dict(ctx)
    return {}


# Shared, process-wide execution monitor used for streaming (/ws) and for
# pipelines that do not supply a custom monitor.
execution_monitor = ExecutionMonitor()
