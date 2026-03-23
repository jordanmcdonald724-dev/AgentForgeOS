from __future__ import annotations

from typing import Dict, List, Optional

from control.agent_pipeline import AgentPipeline
from control.emergent_orchestrator import EmergentOrchestrator


SUCCESS_SCORE_THRESHOLD = 0.7


class LiveExecutionLoop:
    """
    Gate 10 continuous execution loop with simple adaptation rules.
    """

    def __init__(self, orchestrator: EmergentOrchestrator, pipeline: AgentPipeline) -> None:
        self.orchestrator = orchestrator
        self.pipeline = pipeline

    def run(self, request: str, max_iterations: int = 10) -> Dict[str, object]:
        init = self.orchestrator.initialize_task(request)
        agent_sequence: List[str] = list(init.get("agent_sequence", []))

        iterations = 0
        last_result: Optional[object] = None
        last_score: float = 0.0

        for iteration in range(max(1, int(max_iterations))):
            iterations = iteration + 1
            self._safe_loop_event(iteration, agent_sequence)

            result = self.pipeline.run_pipeline(
                agent_names=agent_sequence,
                initial_input={"request": request},
                route_context=init.get("context"),
            )
            last_result = result

            success = getattr(result, "status", "") == "success"
            last_score = self._extract_pipeline_score(result)

            if success and last_score > SUCCESS_SCORE_THRESHOLD:
                break

            agent_sequence = self.orchestrator.adapt_pipeline(agent_sequence, last_score, not success)

        self._store_learning(request, agent_sequence, last_result, last_score, iterations)

        return {
            "final_result": self._result_to_dict(last_result),
            "iterations": iterations,
            "final_pipeline": agent_sequence,
        }

    def _extract_pipeline_score(self, result: object) -> float:
        try:
            metadata = getattr(result, "metadata", {}) if result else {}
            pipeline_score = metadata.get("pipeline_score") if isinstance(metadata, dict) else {}
            score = pipeline_score.get("score") if isinstance(pipeline_score, dict) else None
            return float(score) if score is not None else 0.0
        except Exception:
            return 0.0

    def _result_to_dict(self, result: object) -> Dict[str, object]:
        if not result:
            return {}
        try:
            return {
                "status": getattr(result, "status", None),
                "final_output": getattr(result, "final_output", {}),
                "metadata": getattr(result, "metadata", {}),
                "failed_step_index": getattr(result, "failed_step_index", None),
            }
        except Exception:
            return {}

    def _safe_loop_event(self, iteration: int, agent_sequence: List[str]) -> None:
        try:
            monitor = getattr(self.pipeline, "monitor", None)
            if hasattr(monitor, "loop_iteration"):
                monitor.loop_iteration(
                    pipeline_id="live_loop",
                    iteration=iteration,
                    metadata={"agents": list(agent_sequence)},
                )
        except Exception:
            return

    def _store_learning(
        self,
        request: str,
        agent_sequence: List[str],
        result: Optional[object],
        score: float,
        iteration_count: int,
    ) -> None:
        try:
            learning_controller = getattr(self.pipeline, "learning_controller", None)
            if not learning_controller:
                return
            success = getattr(result, "status", "") == "success" if result else False
            metadata = getattr(result, "metadata", {}) if result else {}
            metadata = metadata if isinstance(metadata, dict) else {}
            metadata.update(
                {
                    "iteration_count": iteration_count,
                    "final_agent_sequence": list(agent_sequence),
                }
            )
            learning_controller.store_execution(
                request=request,
                agent_sequence=list(agent_sequence),
                success=success,
                score=score,
                metadata=metadata,
            )
        except Exception:
            return
