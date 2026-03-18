from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Dict, List, Optional, Set
import uuid

from agents.base_agent import AgentResult
from control.agent_supervisor import AgentSupervisor
from control.execution_monitor import ExecutionMonitor, execution_monitor
from control.scoring_engine import ScoringEngine, ScoreResult
from control.recovery_engine import RecoveryEngine
from control.learning_controller import LearningController
from control.dynamic_pipeline_builder import DynamicPipelineBuilder
from control.agent_factory import AgentFactory
from services.execution_history import ExecutionHistory


@dataclass
class PipelineStepResult:
    step_index: int
    agent_name: str
    status: str
    input_data: Dict[str, object]
    output_data: Dict[str, object]
    error: Optional[str]
    duration_ms: float
    retry_attempts: int = 0


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
    Controlled multi-agent execution pipeline for Gate 4.
    Executes agents in sequence via AgentSupervisor, with monitoring, scoring, and history capture.
    """

    def __init__(
        self,
        supervisor: AgentSupervisor,
        monitor: Optional[ExecutionMonitor] = None,
        scoring_engine: Optional[ScoringEngine] = None,
        history: Optional[ExecutionHistory] = None,
        recovery_engine: Optional[RecoveryEngine] = None,
        learning_controller: Optional[LearningController] = None,
        dynamic_pipeline_builder: Optional[DynamicPipelineBuilder] = None,
        agent_factory: Optional[AgentFactory] = None,
        max_steps: int = 20,
    ) -> None:
        if not isinstance(supervisor, AgentSupervisor):
            raise TypeError("AgentPipeline requires an AgentSupervisor instance.")
        self.supervisor = supervisor
        self.monitor = monitor or execution_monitor
        self.scoring_engine = scoring_engine or ScoringEngine()
        self.history = history or ExecutionHistory()
        self.recovery_engine = recovery_engine or RecoveryEngine()
        self.learning_controller = learning_controller
        self.dynamic_pipeline_builder = dynamic_pipeline_builder or DynamicPipelineBuilder()
        self.agent_factory = agent_factory or AgentFactory()
        self.max_steps = max(1, int(max_steps))

    def run_pipeline(
        self,
        agent_names: List[str],
        initial_input: Dict[str, object],
        route_context: Optional[Dict[str, object]] = None,
    ) -> PipelineResult:
        pipeline_id = str(uuid.uuid4())
        agent_sequence: List[str] = list(agent_names) if isinstance(agent_names, list) else []
        total_steps = len(agent_sequence)

        step_scores: List[ScoreResult] = []
        steps: List[PipelineStepResult] = []
        current_input: Dict[str, object] = dict(initial_input) if isinstance(initial_input, dict) else {}
        output_data: Dict[str, object] = {}
        adaptive_changes: List[Dict[str, object]] = []
        created_agents: List[Dict[str, object]] = []
        request_text = ""
        if isinstance(initial_input, dict):
            request_value = initial_input.get("request")
            if isinstance(request_value, str):
                request_text = request_value
        context_insights = self._get_context_insights(request_text)
        similar_runs_count = len(context_insights.get("similar_runs", [])) if isinstance(context_insights, dict) else 0
        recommended_agents = context_insights.get("recommended_agents") if isinstance(context_insights, dict) else []
        recommended_agents_used = bool(recommended_agents and isinstance(recommended_agents, list) and recommended_agents == agent_names)
        extra_metadata = {
            "similar_runs_count": similar_runs_count,
            "recommended_agents_used": recommended_agents_used,
            "adaptive_changes": adaptive_changes,
            "created_agents": created_agents,
            "final_pipeline": agent_sequence,
        }

        self._safe_monitor("start_pipeline", pipeline_id, {"route_context": route_context or {}, "total_steps": total_steps})

        if not isinstance(agent_names, list) or not agent_names:
            pipeline_score = self._safe_score_pipeline(step_scores)
            result = self._build_pipeline_failure(
                pipeline_id=pipeline_id,
                steps=steps,
                failed_step_index=0,
                error="agent_names must be a non-empty list.",
                total_steps=total_steps,
                completed_steps=0,
                step_scores=step_scores,
                pipeline_score=pipeline_score,
                extra_metadata=extra_metadata,
            )
            self._store_learning(request_text, agent_names, False, pipeline_score.score, result.metadata)
            self._finalize_pipeline(result, step_scores)
            return result

        if not isinstance(initial_input, dict):
            pipeline_score = self._safe_score_pipeline(step_scores)
            result = self._build_pipeline_failure(
                pipeline_id=pipeline_id,
                steps=steps,
                failed_step_index=0,
                error="initial_input must be a dictionary.",
                total_steps=len(agent_names),
                completed_steps=0,
                step_scores=step_scores,
                pipeline_score=pipeline_score,
                extra_metadata=extra_metadata,
            )
            self._store_learning(request_text, agent_names, False, pipeline_score.score, result.metadata)
            self._finalize_pipeline(result, step_scores)
            return result

        index = 0
        processed_steps = 0
        replaced_steps = set()
        while index < len(agent_sequence) and processed_steps < self.max_steps:
            agent_name = agent_sequence[index]
            retries = 0
            while True:
                step_started = datetime.now(UTC)
                self._safe_monitor("step_start", pipeline_id, index, agent_name, current_input)
                try:
                    result = self.supervisor.run_registered_agent(
                        agent_name=agent_name,
                        input_data=current_input,
                        route_context=route_context,
                    )
                except Exception as exc:  # pylint: disable=broad-except
                    duration_ms = (datetime.now(UTC) - step_started).total_seconds() * 1000.0
                    error_message = f"{type(exc).__name__}: {exc}"
                    self._safe_monitor("step_failed", pipeline_id, index, agent_name, error_message)
                    decision = self.recovery_engine.handle_failure(pipeline_id, index, agent_name, error_message)
                    if decision.action == "retry":
                        retries = decision.retry_count
                        self._safe_monitor("step_retry", pipeline_id, index, agent_name, retries)
                        continue

                    if self._try_replace_agent(
                        pipeline_id, index, agent_name, agent_sequence, replaced_steps, adaptive_changes, created_agents
                    ):
                        agent_name = agent_sequence[index]
                        retries = 0
                        continue

                    steps.append(
                        self._build_step_result(
                            step_index=index,
                            agent_name=agent_name,
                            status="failed",
                            input_data=current_input,
                            output_data={},
                            error=error_message,
                            duration_ms=duration_ms,
                            retry_attempts=retries,
                        )
                    )
                    step_scores.append(self._failure_score(agent_name, index, error_message))
                    pipeline_score = self._safe_score_pipeline(step_scores)
                    result_pipeline = self._build_pipeline_failure(
                        pipeline_id=pipeline_id,
                        steps=steps,
                        failed_step_index=index,
                        error=error_message,
                        total_steps=len(agent_sequence),
                        completed_steps=index,
                        step_scores=step_scores,
                        pipeline_score=pipeline_score,
                        extra_metadata={
                            **extra_metadata,
                            "adaptive_changes": adaptive_changes,
                            "created_agents": created_agents,
                            "final_pipeline": agent_sequence,
                        },
                    )
                    self._store_learning(request_text, agent_sequence, False, pipeline_score.score, result_pipeline.metadata)
                    self._finalize_pipeline(result_pipeline, step_scores)
                    return result_pipeline

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

                if status != "success" or not isinstance(output_data, dict):
                    failure_reason = error_text or "invalid_output"
                    self._safe_monitor("step_failed", pipeline_id, index, agent_name, failure_reason)
                    decision = self.recovery_engine.handle_failure(pipeline_id, index, agent_name, failure_reason)
                    if decision.action == "retry":
                        retries = decision.retry_count
                        self._safe_monitor("step_retry", pipeline_id, index, agent_name, retries)
                        continue

                    if self._try_replace_agent(
                        pipeline_id, index, agent_name, agent_sequence, replaced_steps, adaptive_changes, created_agents
                    ):
                        agent_name = agent_sequence[index]
                        retries = 0
                        continue

                    steps.append(
                        self._build_step_result(
                            step_index=index,
                            agent_name=agent_name,
                            status="failed",
                            input_data=current_input,
                            output_data={},
                            error=failure_reason,
                            duration_ms=float(duration_ms),
                            retry_attempts=retries,
                        )
                    )
                    step_scores.append(self._failure_score(agent_name, index, failure_reason))
                    pipeline_score = self._safe_score_pipeline(step_scores)
                    result_pipeline = self._build_pipeline_failure(
                        pipeline_id=pipeline_id,
                        steps=steps,
                        failed_step_index=index,
                        error=failure_reason,
                        total_steps=len(agent_sequence),
                        completed_steps=index,
                        step_scores=step_scores,
                        pipeline_score=pipeline_score,
                        extra_metadata={
                            **extra_metadata,
                            "adaptive_changes": adaptive_changes,
                            "created_agents": created_agents,
                            "final_pipeline": agent_sequence,
                        },
                    )
                    self._store_learning(request_text, agent_sequence, False, pipeline_score.score, result_pipeline.metadata)
                    self._finalize_pipeline(result_pipeline, step_scores)
                    return result_pipeline

                self._safe_monitor("step_complete", pipeline_id, index, agent_name, output_data, float(duration_ms))

                step_scores.append(self._safe_score_step(output_data))
                current_score = step_scores[-1]

                step_result = self._build_step_result(
                    step_index=index,
                    agent_name=agent_name,
                    status=status,
                    input_data=current_input,
                    output_data=output_data,
                    error=error_text,
                    duration_ms=float(duration_ms),
                    retry_attempts=retries,
                )
                steps.append(step_result)

                merged_input = dict(current_input)
                merged_input.update(output_data)
                current_input = merged_input
                processed_steps += 1

                if (
                    current_score.score < 0.5
                    and len(agent_sequence) < self.max_steps
                    and self.dynamic_pipeline_builder.validate_pipeline(agent_sequence)
                ):
                    updated = self.dynamic_pipeline_builder.insert_step(agent_sequence, index + 1, "planner_agent")
                    if len(updated) > len(agent_sequence):
                        agent_sequence = updated
                        adaptive_changes.append(
                            {"type": "insert", "agent": "planner_agent", "after_index": index, "reason": "low_score"}
                        )
                        self._safe_monitor(
                            "pipeline_modified",
                            pipeline_id,
                            "insert",
                            {"agent": "planner_agent", "after_index": index, "reason": "low_score"},
                        )

                index += 1
                break

        extra_metadata.update({"adaptive_changes": adaptive_changes, "created_agents": created_agents, "final_pipeline": agent_sequence})
        pipeline_score = self._safe_score_pipeline(step_scores)
        result_pipeline = self._build_pipeline_success(
            pipeline_id=pipeline_id,
            steps=steps,
            final_output=output_data if steps else {},
            total_steps=len(agent_sequence),
            step_scores=step_scores,
            pipeline_score=pipeline_score,
            extra_metadata=extra_metadata,
        )
        self._store_learning(request_text, agent_sequence, True, pipeline_score.score, result_pipeline.metadata)
        self._finalize_pipeline(result_pipeline, step_scores)
        return result_pipeline

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _get_context_insights(self, request_text: str) -> Dict[str, object]:
        try:
            if self.learning_controller and isinstance(request_text, str) and request_text.strip():
                return self.learning_controller.query_context(request_text) or {}
            return {}
        except Exception:
            return {}

    def _store_learning(
        self,
        request_text: str,
        agent_names: List[str],
        success: bool,
        pipeline_score: float,
        metadata: Dict[str, object],
    ) -> None:
        try:
            if not self.learning_controller:
                return
            self.learning_controller.store_execution(
                request=request_text or "",
                agent_sequence=list(agent_names) if isinstance(agent_names, list) else [],
                success=bool(success),
                score=float(pipeline_score) if pipeline_score is not None else 0.0,
                metadata=metadata if isinstance(metadata, dict) else {},
            )
        except Exception:
            return

    def _build_step_result(
        self,
        step_index: int,
        agent_name: str,
        status: str,
        input_data: Dict[str, object],
        output_data: Dict[str, object],
        error: Optional[str],
        duration_ms: float,
        retry_attempts: int = 0,
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
            retry_attempts=max(0, int(retry_attempts)),
        )

    def _build_pipeline_success(
        self,
        pipeline_id: str,
        steps: List[PipelineStepResult],
        final_output: Dict[str, object],
        total_steps: int,
        step_scores: List[ScoreResult],
        pipeline_score: ScoreResult,
        extra_metadata: Optional[Dict[str, object]] = None,
    ) -> PipelineResult:
        extra = extra_metadata if isinstance(extra_metadata, dict) else {}
        return PipelineResult(
            pipeline_id=pipeline_id,
            status="success",
            steps=steps,
            final_output=final_output if isinstance(final_output, dict) else {},
            failed_step_index=None,
            metadata={
                "total_steps": total_steps,
                "completed_steps": len(steps),
                "step_scores": [self._score_to_dict(score) for score in step_scores],
                "pipeline_score": self._score_to_dict(pipeline_score),
                **extra,
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
        step_scores: List[ScoreResult],
        pipeline_score: ScoreResult,
        extra_metadata: Optional[Dict[str, object]] = None,
    ) -> PipelineResult:
        extra = extra_metadata if isinstance(extra_metadata, dict) else {}
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
                "step_scores": [self._score_to_dict(score) for score in step_scores],
                "pipeline_score": self._score_to_dict(pipeline_score),
                **extra,
            },
        )

    # ------------------------------------------------------------------ #
    # Monitoring, scoring, persistence helpers
    # ------------------------------------------------------------------ #
    def _safe_monitor(self, method: str, *args) -> None:
        try:
            monitor_method = getattr(self.monitor, method, None)
            if callable(monitor_method):
                monitor_method(*args)
        except Exception:
            return

    def _safe_score_step(self, output: Dict[str, object]) -> ScoreResult:
        try:
            return self.scoring_engine.score_step(output)
        except Exception as exc:  # pylint: disable=broad-except
            return ScoreResult(score=0.0, confidence=0.0, issues=[f"scoring_error:{exc}"], metadata={})

    def _safe_score_pipeline(self, step_scores: List[ScoreResult]) -> ScoreResult:
        try:
            return self.scoring_engine.score_pipeline(step_scores)
        except Exception as exc:  # pylint: disable=broad-except
            return ScoreResult(score=0.0, confidence=0.0, issues=[f"scoring_error:{exc}"], metadata={})

    def _failure_score(self, agent_name: str, step_index: int, error: str) -> ScoreResult:
        return ScoreResult(
            score=0.0,
            confidence=0.0,
            issues=["failed_step", error],
            metadata={"agent_name": agent_name, "step_index": step_index},
        )

    @staticmethod
    def _score_to_dict(score: ScoreResult) -> Dict[str, object]:
        return {
            "score": float(score.score),
            "confidence": float(score.confidence),
            "issues": list(score.issues or []),
            "metadata": dict(score.metadata or {}),
        }

    def _finalize_pipeline(self, result: PipelineResult, step_scores: List[ScoreResult]) -> None:
        self._safe_monitor("end_pipeline", result.pipeline_id, result.status)
        try:
            pipeline_score = result.metadata.get("pipeline_score", {}) if isinstance(result.metadata, dict) else {}
            record = ExecutionHistory.build_record(
                pipeline_id=result.pipeline_id,
                status=result.status,
                steps=[step.__dict__ for step in result.steps],
                final_output=result.final_output,
                score=pipeline_score.get("score", 0.0) if isinstance(pipeline_score, dict) else 0.0,
                metadata=result.metadata,
            )
            self.history.store(record)
        except Exception:
            return

    def _try_replace_agent(
        self,
        pipeline_id: str,
        index: int,
        agent_name: str,
        agent_sequence: List[str],
        replaced_steps: Set[int],
        adaptive_changes: List[Dict[str, object]],
        created_agents: List[Dict[str, object]],
    ) -> bool:
        try:
            if not self.agent_factory or not self.dynamic_pipeline_builder:
                return False
            if index in replaced_steps or len(agent_sequence) >= self.max_steps:
                return False
            new_agent = self.agent_factory.create_agent(agent_name)
            self.supervisor.register_agent(new_agent)
            updated_sequence = self.dynamic_pipeline_builder.replace_step(agent_sequence, index, new_agent.name)
            if updated_sequence == agent_sequence:
                return False
            agent_sequence[:] = updated_sequence
            replaced_steps.add(index)
            created_agents.append({"role": agent_name, "created_name": new_agent.name})
            adaptive_changes.append({"type": "replace", "original_agent": agent_name, "new_agent": new_agent.name, "index": index})
            self._safe_monitor("agent_created", pipeline_id, new_agent.name, agent_name)
            self._safe_monitor(
                "pipeline_modified",
                pipeline_id,
                "replace",
                {"original_agent": agent_name, "new_agent": new_agent.name, "index": index, "reason": "max_retries_exceeded"},
            )
            return True
        except Exception:
            return False
