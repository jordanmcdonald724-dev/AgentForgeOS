"""Learning controller orchestrates context injection and result storage."""

from __future__ import annotations

from typing import Any, Dict, List

from services.agent_pipeline import PipelineContext


class LearningController:
    """Coordinates memory usage before and after pipeline execution.

    TODO: fetch contextual embeddings/graph facts before execution and persist
    step outputs, scores, and patterns back to the memory layer afterward.
    """

    def before_execution(self, context: PipelineContext) -> None:
        """Hook to enrich context before the pipeline runs."""
        # Placeholder: in future, pull from vector store / knowledge graph.
        context.set("memory_initialized", True)

    def after_execution(
        self,
        responses: List[Dict[str, Any]],
        scores: Dict[str, Dict[str, float]],
        context: PipelineContext,
    ) -> None:
        """Hook to persist outcomes and scores."""
        context.set("last_scores", scores)
        context.set("last_responses", responses)
