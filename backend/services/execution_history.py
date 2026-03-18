from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Dict, List, Optional


@dataclass
class ExecutionRecord:
    pipeline_id: str
    status: str
    steps: List[Dict[str, object]]
    final_output: Dict[str, object]
    score: float
    created_at: str
    metadata: Dict[str, object] = field(default_factory=dict)


class ExecutionHistory:
    """
    In-memory execution history for pipeline runs.
    Provides a clear interface for future persistence layers.
    """

    def __init__(self) -> None:
        self._records: Dict[str, ExecutionRecord] = {}

    def store(self, record: ExecutionRecord) -> None:
        try:
            if not isinstance(record, ExecutionRecord):
                return
            self._records[record.pipeline_id] = record
        except Exception:
            return

    def get(self, pipeline_id: str) -> Optional[ExecutionRecord]:
        return self._records.get(pipeline_id)

    def list_all(self) -> List[ExecutionRecord]:
        return list(self._records.values())

    @staticmethod
    def build_record(
        pipeline_id: str,
        status: str,
        steps: List[Dict[str, object]],
        final_output: Dict[str, object],
        score: float,
        metadata: Dict[str, object],
    ) -> ExecutionRecord:
        created_at = datetime.now(UTC).isoformat()
        safe_steps = steps if isinstance(steps, list) else []
        safe_output = final_output if isinstance(final_output, dict) else {}
        safe_metadata = metadata if isinstance(metadata, dict) else {}
        return ExecutionRecord(
            pipeline_id=pipeline_id,
            status=status,
            steps=safe_steps,
            final_output=safe_output,
            score=float(score),
            created_at=created_at,
            metadata=safe_metadata,
        )
