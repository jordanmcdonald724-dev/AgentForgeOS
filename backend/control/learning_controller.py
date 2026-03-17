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
            meta = metadata if isinstance(metadata, dict) else {}
            entry = ContextEntry(
                request_signature=signature,
                pipeline_agents=list(agent_sequence) if isinstance(agent_sequence, list) else [],
                success=bool(success),
                score=float(score) if score is not None else 0.0,
                metadata=meta,
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

            adaptive_patterns: Dict[str, object] = {"modifications": {}, "created_agents": {}}
            for entry in similar_entries:
                meta = entry.metadata if isinstance(entry.metadata, dict) else {}
                changes = meta.get("adaptive_changes", []) if isinstance(meta, dict) else []
                created = meta.get("created_agents", []) if isinstance(meta, dict) else []
                outcome = "success" if entry.success else "failure"

                for change in changes if isinstance(changes, list) else []:
                    change_type = change.get("type", "unknown") if isinstance(change, dict) else "unknown"
                    key = f"{change_type}:{outcome}"
                    adaptive_patterns["modifications"][key] = adaptive_patterns["modifications"].get(key, 0) + 1

                for created_agent in created if isinstance(created, list) else []:
                    role = created_agent.get("role", "unknown") if isinstance(created_agent, dict) else "unknown"
                    key = f"{role}:{outcome}"
                    adaptive_patterns["created_agents"][key] = adaptive_patterns["created_agents"].get(key, 0) + 1

            return {
                "similar_runs": similar_runs,
                "recommended_agents": recommended_agents,
                "warnings": warnings,
                "adaptive_patterns": adaptive_patterns,
                "optimization_patterns": self._optimization_patterns(similar_entries),
            }
        except Exception:
            return {"similar_runs": [], "recommended_agents": [], "warnings": ["learning_controller_error"], "adaptive_patterns": {}}

    def _optimization_patterns(self, entries: List[ContextEntry]) -> Dict[str, object]:
        patterns: Dict[str, object] = {"iteration_counts": [], "final_agent_sequences": []}
        try:
            for entry in entries:
                meta = entry.metadata if isinstance(entry.metadata, dict) else {}
                iteration_count = meta.get("iteration_count")
                final_agents = meta.get("final_agent_sequence")
                if iteration_count is not None:
                    patterns["iteration_counts"].append(iteration_count)
                if isinstance(final_agents, list):
                    patterns["final_agent_sequences"].append(list(final_agents))
            return patterns
        except Exception:
            return patterns
