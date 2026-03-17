from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List
import traceback


@dataclass
class AgentResult:
    """
    Standardized agent execution result for Gate 2.
    """

    agent_name: str
    status: str
    output: Dict[str, Any]
    confidence: float
    feedback: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """
    Strict base class that controls agent orchestration.

    All subclasses must implement `run`. They may override `self_evaluate`
    and `repair`, but should rely on `execute` as the single entry point.
    """

    confidence_threshold: float = 0.75

    def __init__(self, name: str, description: str, capabilities: List[str]) -> None:
        self._validate_identity(name, description, capabilities)
        self.name = name
        self.description = description
        self.capabilities = capabilities

    @abstractmethod
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Core agent behavior. Must be implemented by subclasses.
        """

    def self_evaluate(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Default self-evaluation. Subclasses can override for domain logic.
        """
        has_content = bool(output)
        confidence = 0.6 if has_content else 0.3
        return {
            "confidence": confidence,
            "issues": [] if has_content else ["empty_output"],
            "suggested_fix": None if has_content else "Populate output with meaningful content.",
        }

    def repair(self, output: Dict[str, Any], feedback: Dict[str, Any]) -> Dict[str, Any]:
        """
        Default repair simply returns the original output. Subclasses can override.
        """
        return output

    def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Controlled orchestration entry point.
        """
        started_at = datetime.now(timezone.utc)

        try:
            self._validate_input(input_data)

            primary_output = self.run(input_data)
            self._ensure_dict("run", primary_output)

            evaluation = self.self_evaluate(primary_output)
            self._ensure_dict("self_evaluate", evaluation)
            confidence = self._clamp_confidence(evaluation.get("confidence", 0.0))
            feedback = evaluation
            final_output = primary_output

            if confidence < self.confidence_threshold:
                repaired_output = self.repair(primary_output, feedback)
                self._ensure_dict("repair", repaired_output)
                final_output = repaired_output

                reevaluation = self.self_evaluate(repaired_output)
                self._ensure_dict("self_evaluate", reevaluation)
                confidence = self._clamp_confidence(reevaluation.get("confidence", confidence))
                feedback = reevaluation

            completed_at = datetime.now(timezone.utc)
            metadata = {
                "started_at": started_at.isoformat(),
                "completed_at": completed_at.isoformat(),
                "duration_ms": (completed_at - started_at).total_seconds() * 1000.0,
            }
            return self._build_success_result(final_output, confidence, feedback, metadata)

        except Exception as exc:  # pylint: disable=broad-except
            completed_at = datetime.now(timezone.utc)
            metadata = {
                "started_at": started_at.isoformat(),
                "completed_at": completed_at.isoformat(),
                "duration_ms": (completed_at - started_at).total_seconds() * 1000.0,
                "traceback": traceback.format_exc(),
            }
            return self._build_failure_result(str(exc), metadata)

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    def _validate_identity(self, name: str, description: str, capabilities: List[str]) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Agent name must be a non-empty string.")
        if not isinstance(description, str) or not description.strip():
            raise ValueError("Agent description must be a non-empty string.")
        if not isinstance(capabilities, list) or not all(isinstance(c, str) and c.strip() for c in capabilities):
            raise ValueError("Agent capabilities must be a list of non-empty strings.")

    def _validate_input(self, input_data: Dict[str, Any]) -> None:
        if not isinstance(input_data, dict):
            raise ValueError("Input data must be a dictionary.")

    def _ensure_dict(self, stage: str, payload: Any) -> None:
        if not isinstance(payload, dict):
            raise TypeError(f"{stage}() must return a dict, got {type(payload).__name__}.")

    def _clamp_confidence(self, confidence: Any) -> float:
        try:
            value = float(confidence)
        except (TypeError, ValueError):
            value = 0.0
        return max(0.0, min(1.0, value))

    def _build_success_result(
        self,
        output: Dict[str, Any],
        confidence: float,
        feedback: Dict[str, Any],
        metadata: Dict[str, Any],
    ) -> AgentResult:
        return AgentResult(
            agent_name=self.name,
            status="success",
            output=output,
            confidence=confidence,
            feedback=feedback,
            metadata=metadata,
        )

    def _build_failure_result(self, error_message: str, metadata: Dict[str, Any]) -> AgentResult:
        return AgentResult(
            agent_name=self.name,
            status="failed",
            output={},
            confidence=0.0,
            feedback={"error": error_message},
            metadata=metadata,
        )
