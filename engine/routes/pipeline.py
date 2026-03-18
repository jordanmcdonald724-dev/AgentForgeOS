"""Engine route for triggering the multi-agent pipeline."""

from __future__ import annotations

import logging

from fastapi import APIRouter
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class PipelineRunRequest(BaseModel):
    """Request body for a pipeline run."""

    prompt: str


@router.post("/pipeline/run", tags=["pipeline"])
async def run_pipeline(body: PipelineRunRequest):
    """
    Execute the full multi-agent pipeline for the given prompt.

    Delegates to :func:`agents.pipeline.run` and returns the collected
    stage results.
    """
    try:
        from agents.pipeline import run as pipeline_run

        results = await pipeline_run(body.prompt)
        return {"success": True, "steps": list(results)}
    except Exception as exc:
        logger.exception("Pipeline run failed")
        return {"success": False, "error": str(exc)}
