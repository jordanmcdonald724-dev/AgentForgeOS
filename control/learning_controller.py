"""Learning controller orchestrates context injection and result storage."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from services.agent_pipeline import PipelineContext
from services.autopsy_service import AutopsyService


class LearningController:
    """Coordinates memory usage before and after pipeline execution.
    """

    def before_execution(self, context: PipelineContext) -> None:
        """Hook to enrich context before the pipeline runs."""
        context.set("memory_initialized", True)
        ws_raw = context.get("workspace_path")
        if isinstance(ws_raw, str) and ws_raw.strip():
            persist_path = Path(ws_raw).expanduser().resolve() / "knowledge" / "autopsy_reports.json"
            svc = AutopsyService(persist_path=persist_path)
            context.set("autopsy_history", svc.history(limit=10))

    def after_execution(
        self,
        responses: List[Dict[str, Any]],
        scores: Dict[str, Dict[str, float]],
        context: PipelineContext,
    ) -> None:
        """Hook to persist outcomes and scores."""
        context.set("last_scores", scores)
        context.set("last_responses", responses)

        failures: List[str] = []
        for r in responses:
            if not isinstance(r, dict):
                continue
            if r.get("success"):
                continue
            err = r.get("error")
            if isinstance(err, str) and err.strip():
                failures.append(err.strip())

        if not failures:
            return

        ws_raw = context.get("workspace_path")
        persist_path = None
        if isinstance(ws_raw, str) and ws_raw.strip():
            persist_path = Path(ws_raw).expanduser().resolve() / "knowledge" / "autopsy_reports.json"

        project = context.get("project")
        project_name = project.strip() if isinstance(project, str) and project.strip() else "unknown"
        pipeline_id = context.get("pipeline_id")
        pipeline_tag = pipeline_id.strip() if isinstance(pipeline_id, str) and pipeline_id.strip() else "unknown"
        summary = f"[pipeline_id:{pipeline_tag}] " + " | ".join(failures[:8])
        root_cause = context.get("root_cause") if isinstance(context.get("root_cause"), str) else None
        remediation = context.get("remediation") if isinstance(context.get("remediation"), str) else None

        svc = AutopsyService(persist_path=persist_path)
        report = svc.record_failure(project_name, summary, root_cause=root_cause, remediation=remediation)
        context.set("last_autopsy_report", report)
