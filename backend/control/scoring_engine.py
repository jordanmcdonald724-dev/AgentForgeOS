from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ScoreResult:
    score: float
    confidence: float
    issues: List[str] = field(default_factory=list)
    metadata: Dict[str, object] = field(default_factory=dict)


class ScoringEngine:
    """
    Deterministic, lightweight scoring engine for pipeline steps and pipelines.
    """

    def score_step(self, output: Dict[str, object]) -> ScoreResult:
        try:
            issues: List[str] = []
            if not isinstance(output, dict) or not output:
                return ScoreResult(score=0.0, confidence=0.0, issues=["empty_or_invalid_output"], metadata={})

            expected_keys = {"summary", "assumptions", "suggested_steps", "engine"}
            present_keys = set(k for k in output.keys() if isinstance(k, str))
            missing = expected_keys - present_keys

            completeness = min(len(output) / max(len(expected_keys), 1), 1.0)
            structure_score = 1.0 - (len(missing) / max(len(expected_keys), 1))
            base_score = 0.6 * completeness + 0.4 * max(structure_score, 0.0)
            base_score = self._clamp(base_score)

            if missing:
                issues.append(f"missing_keys:{','.join(sorted(missing))}")

            confidence = self._clamp(0.5 + 0.5 * base_score)

            return ScoreResult(
                score=base_score,
                confidence=confidence,
                issues=issues,
                metadata={"present_keys": sorted(present_keys), "missing_keys": sorted(missing)},
            )
        except Exception as exc:  # pylint: disable=broad-except
            return ScoreResult(score=0.0, confidence=0.0, issues=[f"scoring_error:{exc}"], metadata={})

    def score_pipeline(self, step_scores: List[ScoreResult]) -> ScoreResult:
        try:
            if not step_scores:
                return ScoreResult(score=0.0, confidence=0.0, issues=["no_steps_scored"], metadata={})

            avg_score = sum(s.score for s in step_scores) / len(step_scores)
            avg_confidence = sum(s.confidence for s in step_scores) / len(step_scores)

            failed = [s for s in step_scores if s.score <= 0.0]
            issues: List[str] = []
            if failed:
                issues.append(f"failed_steps:{len(failed)}")

            pipeline_score = self._clamp(avg_score - 0.05 * len(failed))
            pipeline_confidence = self._clamp(avg_confidence - 0.05 * len(failed))

            return ScoreResult(
                score=pipeline_score,
                confidence=pipeline_confidence,
                issues=issues,
                metadata={"step_count": len(step_scores)},
            )
        except Exception as exc:  # pylint: disable=broad-except
            return ScoreResult(score=0.0, confidence=0.0, issues=[f"scoring_error:{exc}"], metadata={})

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))
