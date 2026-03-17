from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class RecoveryDecision:
    action: str  # "retry" or "abort"
    reason: str
    retry_count: int
    metadata: Dict[str, object] = field(default_factory=dict)


class RecoveryEngine:
    """
    Deterministic, bounded recovery engine for Gate 5.
    Supports controlled retries of the same agent without any dynamic pipeline changes.
    """

    def __init__(self, max_retries_per_step: int = 2) -> None:
        self.max_retries_per_step = max(0, int(max_retries_per_step))
        self._retries: Dict[str, Dict[int, int]] = {}

    def handle_failure(self, pipeline_id: str, step_index: int, agent_name: str, error: str) -> RecoveryDecision:
        try:
            retry_count = self._increment_retry(pipeline_id, step_index)
            if retry_count <= self.max_retries_per_step:
                return RecoveryDecision(
                    action="retry",
                    reason="retry_allowed",
                    retry_count=retry_count,
                    metadata={
                        "agent_name": agent_name,
                        "error": error,
                        "retry_attempt": retry_count,
                        "max_retries": self.max_retries_per_step,
                    },
                )

            return RecoveryDecision(
                action="abort",
                reason="max_retries_exceeded",
                retry_count=retry_count,
                metadata={
                    "agent_name": agent_name,
                    "error": error,
                    "retry_attempt": retry_count,
                    "max_retries": self.max_retries_per_step,
                },
            )
        except Exception as exc:  # pylint: disable=broad-except
            return RecoveryDecision(
                action="abort",
                reason=f"recovery_error:{exc}",
                retry_count=self._get_retry_count(pipeline_id, step_index),
                metadata={
                    "agent_name": agent_name,
                    "error": error,
                    "max_retries": self.max_retries_per_step,
                },
            )

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _get_retry_count(self, pipeline_id: str, step_index: int) -> int:
        pipeline_retries = self._retries.get(pipeline_id, {})
        return max(0, int(pipeline_retries.get(step_index, 0)))

    def _increment_retry(self, pipeline_id: str, step_index: int) -> int:
        pipeline_retries = self._retries.setdefault(pipeline_id, {})
        current = max(0, int(pipeline_retries.get(step_index, 0)))
        current += 1
        pipeline_retries[step_index] = current
        return current
