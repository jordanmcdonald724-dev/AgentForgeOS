from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Dict, List, Optional
import uuid

from agents.base_agent import AgentResult
from control.agent_supervisor import AgentSupervisor


@dataclass
class PipelineStepResult:
    step_index: int
    agent_name: str
    status: str
    input_data: Dict[str, object]
    output_data: Dict[str, object]
    error: Optional[str]
    duration_ms: float


@dataclass
class PipelineResult:
    pipeline_id: str
    status: str
    steps: List[PipelineStepResult] = field(default_factory=list)
    final_output: Dict[str, object] = field(default_factory=dict)
    failed_step_index: Optional[int] = None
    metadata: Dict[str, object] = field(default_factory=dict)


class AgentPipeline:
    """
    Controlled multi-agent execution pipeline for Gate 3.
    Executes agents in sequence via AgentSupervisor, passing outputs forward.
    """

    def __init__(self, supervisor: AgentSupervisor) -> None:
        if not isinstance(supervisor, AgentSupervisor):
            raise TypeError("AgentPipeline requires an AgentSupervisor instance.")
        self.supervisor = supervisor

    def run_pipeline(
        self,
        agent_names: List[str],
        initial_input: Dict[str, object],
        route_context: Optional[Dict[str, object]] = None,
    ) -> PipelineResult:
        pipeline_id = str(uuid.uuid4())

        if not isinstance(agent_names, list) or not agent_names:
            return self._build_pipeline_failure(
                pipeline_id=pipeline_id,
                steps=[],
                failed_step_index=0,
                error="agent_names must be a non-empty list.",
                total_steps=0,
                completed_steps=0,
            )

        if not isinstance(initial_input, dict):
            return self._build_pipeline_failure(
                pipeline_id=pipeline_id,
                steps=[],
                failed_step_index=0,
                error="initial_input must be a dictionary.",
                total_steps=len(agent_names),
                completed_steps=0,
            )

        steps: List[PipelineStepResult] = []
        current_input: Dict[str, object] = dict(initial_input)

        for index, agent_name in enumerate(agent_names):
            step_started = datetime.now(UTC)
            try:
                result = self.supervisor.run_registered_agent(
                    agent_name=agent_name,
                    input_data=current_input,
                    route_context=route_context,
                )
            except Exception as exc:  # pylint: disable=broad-except
                duration_ms = (datetime.now(UTC) - step_started).total_seconds() * 1000.0
                steps.append(
                    self._build_step_result(
                        step_index=index,
                        agent_name=agent_name,
                        status="failed",
                        input_data=current_input,
                        output_data={},
                        error=f"{type(exc).__name__}: {exc}",
                        duration_ms=duration_ms,
                    )
                )
                return self._build_pipeline_failure(
                    pipeline_id=pipeline_id,
                    steps=steps,
                    failed_step_index=index,
                    error=f"{type(exc).__name__}: {exc}",
                    total_steps=len(agent_names),
                    completed_steps=index,
                )

            output_data = result.output if isinstance(result.output, dict) else {}
            status = result.status
            duration_ms = (
                result.metadata.get("duration_ms")
                if isinstance(result.metadata, dict) and isinstance(result.metadata.get("duration_ms"), (int, float))
                else (datetime.now(UTC) - step_started).total_seconds() * 1000.0
            )

            error_text = None
            if status != "success":
                feedback_error = result.feedback.get("error") if isinstance(result.feedback, dict) else None
                error_text = feedback_error or "agent_execution_failed"

            step_result = self._build_step_result(
                step_index=index,
                agent_name=agent_name,
                status=status,
                input_data=current_input,
                output_data=output_data,
                error=error_text,
                duration_ms=float(duration_ms),
            )
            steps.append(step_result)

            if status != "success" or not isinstance(output_data, dict):
                return self._build_pipeline_failure(
                    pipeline_id=pipeline_id,
                    steps=steps,
                    failed_step_index=index,
                    error=error_text or "invalid_output",
                    total_steps=len(agent_names),
                    completed_steps=index,
                )

            merged_input = dict(current_input)
            merged_input.update(output_data)
            current_input = merged_input

        return self._build_pipeline_success(
            pipeline_id=pipeline_id,
            steps=steps,
            final_output=output_data if steps else {},
            total_steps=len(agent_names),
        )

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    def _build_step_result(
        self,
        step_index: int,
        agent_name: str,
        status: str,
        input_data: Dict[str, object],
        output_data: Dict[str, object],
        error: Optional[str],
        duration_ms: float,
    ) -> PipelineStepResult:
        safe_input = input_data if isinstance(input_data, dict) else {}
        safe_output = output_data if isinstance(output_data, dict) else {}
        return PipelineStepResult(
            step_index=step_index,
            agent_name=agent_name,
            status=status,
            input_data=safe_input,
            output_data=safe_output,
            error=error,
            duration_ms=float(duration_ms),
        )

    def _build_pipeline_success(
        self,
        pipeline_id: str,
        steps: List[PipelineStepResult],
        final_output: Dict[str, object],
        total_steps: int,
    ) -> PipelineResult:
        return PipelineResult(
            pipeline_id=pipeline_id,
            status="success",
            steps=steps,
            final_output=final_output if isinstance(final_output, dict) else {},
            failed_step_index=None,
            metadata={
                "total_steps": total_steps,
                "completed_steps": len(steps),
            },
        )

    def _build_pipeline_failure(
        self,
        pipeline_id: str,
        steps: List[PipelineStepResult],
        failed_step_index: int,
        error: Optional[str],
        total_steps: int,
        completed_steps: int,
    ) -> PipelineResult:
        return PipelineResult(
            pipeline_id=pipeline_id,
            status="failed",
            steps=steps,
            final_output={},
            failed_step_index=failed_step_index,
            metadata={
                "error": error,
                "total_steps": total_steps,
                "completed_steps": completed_steps,
            },
        )
