from __future__ import annotations

from typing import Dict, List

from knowledge.context_index import ContextEntry, ContextIndex
from services.execution_history import ExecutionHistory


class LearningController:
    """
    Gate 6 learning controller.
    Bridges execution history and context index to inform future routing/pipelines.
    """

    def __init__(self, context_index: ContextIndex, execution_history: ExecutionHistory) -> None:
        self.context_index = context_index
        self.execution_history = execution_history

    def build_request_signature(self, request: str) -> str:
        try:
            if not isinstance(request, str):
                return ""
            signature = " ".join(request.strip().lower().split())
            return signature
        except Exception:
            return ""

    def store_execution(
        self,
        request: str,
        agent_sequence: List[str],
        success: bool,
        score: float,
        metadata: Dict[str, object],
    ) -> None:
        try:
            signature = self.build_request_signature(request)
            entry = ContextEntry(
                request_signature=signature,
                pipeline_agents=list(agent_sequence) if isinstance(agent_sequence, list) else [],
                success=bool(success),
                score=float(score) if score is not None else 0.0,
                metadata=metadata if isinstance(metadata, dict) else {},
            )
            self.context_index.add_entry(entry)
        except Exception:
            return

    def query_context(self, request: str) -> Dict[str, object]:
        try:
            signature = self.build_request_signature(request)
            similar_entries = self.context_index.query_similar(signature, top_k=3)

            similar_runs = [
                {
                    "request_signature": entry.request_signature,
                    "pipeline_agents": list(entry.pipeline_agents),
                    "success": bool(entry.success),
                    "score": float(entry.score),
                    "metadata": dict(entry.metadata or {}),
                }
                for entry in similar_entries
            ]

            successful = [entry for entry in similar_entries if entry.success]
            recommended_agents = list(successful[0].pipeline_agents) if successful else []

            warnings: List[str] = []
            if any(not entry.success for entry in similar_entries):
                warnings.append("similar_failures_detected")

            return {
                "similar_runs": similar_runs,
                "recommended_agents": recommended_agents,
                "warnings": warnings,
            }
        except Exception:
            return {"similar_runs": [], "recommended_agents": [], "warnings": ["learning_controller_error"]}
