from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Dict, List, Optional


@dataclass
class ExecutionEvent:
    event_type: str
    pipeline_id: str
    step_index: Optional[int]
    agent_name: Optional[str]
    timestamp: str
    data: Dict[str, object] = field(default_factory=dict)


class ExecutionMonitor:
    """
    Lightweight, in-memory execution monitor for pipelines and steps.
    Acts as an observer and must never interfere with execution.
    """

    def __init__(self) -> None:
        self._events: List[ExecutionEvent] = []

    # ------------------------------------------------------------------ #
    # Public API
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
        self,
        pipeline_id: str,
        step_index: int,
        agent_name: str,
        output_data: Dict[str, object],
        duration_ms: float,
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

    def get_events(self, pipeline_id: Optional[str] = None) -> List[ExecutionEvent]:
        if pipeline_id is None:
            return list(self._events)
        return [event for event in self._events if event.pipeline_id == pipeline_id]

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
            event = ExecutionEvent(
                event_type=event_type,
                pipeline_id=pipeline_id,
                step_index=step_index,
                agent_name=agent_name,
                timestamp=datetime.now(UTC).isoformat(),
                data=data or {},
            )
            self._events.append(event)
        except Exception:
            # Never allow monitoring failures to impact execution.
            return
