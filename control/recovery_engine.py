"""Recovery engine to handle pipeline failures."""

from __future__ import annotations

from typing import Any, Dict, Optional

from services.agent_pipeline import PipelineContext


class RecoveryEngine:
    """Attempts lightweight recovery when a pipeline step fails."""

    def recover(
        self,
        step: str,
        response: Dict[str, Any],
        context: PipelineContext,
        *,
        attempt: int = 1,
    ) -> Dict[str, Any]:
        """Return a recovered response or the original if no recovery is possible."""
        if attempt > 1:
            return response

        # Placeholder recovery hook — simply annotate the response.
        recovered = dict(response)
        recovered.setdefault("metadata", {})
        recovered["metadata"]["recovery_attempted"] = True
        return recovered
