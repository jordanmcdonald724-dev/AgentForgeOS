"""Builds and adjusts the pipeline sequence at runtime."""

from __future__ import annotations

from typing import List

from services.agent_pipeline import PipelineContext


class DynamicPipelineBuilder:
    """Returns the pipeline order, allowing runtime adjustments."""

    def build(self, base_pipeline: List[str], context: PipelineContext) -> List[str]:
        """Return the pipeline for this run. Placeholder: no dynamic changes yet."""
        return list(base_pipeline)

    def modify_during_execution(
        self, current_pipeline: List[str], context: PipelineContext
    ) -> List[str]:
        """Placeholder for mid-execution adjustments; currently returns the pipeline unchanged."""
        return current_pipeline
