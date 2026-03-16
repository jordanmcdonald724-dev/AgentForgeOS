"""Agent supervisor coordinating pipeline execution with guards."""

import logging
from typing import Iterable, List, Optional, Type

from services.agent_pipeline import AGENT_PIPELINE, PipelineContext
from control.ai_router import AIRouter
from control.file_guard import FileGuard
from services import AgentService

logger = logging.getLogger(__name__)


class AgentSupervisor:
    """Coordinates agent execution order and enforces guard checks.

    Agent classes are loaded from ``services.agent_registry.AGENT_REGISTRY``
    (falling back to ``agents.AGENT_CLASS_MAP`` for backward compatibility).
    The supervisor instantiates each agent in pipeline order and delegates
    execution to the typed agent.  If no class is registered for a role the
    generic ``AgentService.run_agent`` is used instead.

    Each agent execution is wrapped in a try/except so that a single agent
    failure never freezes the pipeline — the error is logged and the pipeline
    continues to the next stage.
    """

    def __init__(
        self,
        agent_service: AgentService,
        router: Optional[AIRouter] = None,
        guard: Optional[FileGuard] = None,
    ):
        self.agent_service = agent_service
        self.router = router or AIRouter()
        self.guard = guard or FileGuard()
        self._agent_classes = self._load_agent_classes()

    @staticmethod
    def _load_agent_classes() -> dict:
        """Load agent class map from the registry; fall back to AGENT_CLASS_MAP."""
        try:
            from services.agent_registry import AGENT_REGISTRY
            return dict(AGENT_REGISTRY)
        except Exception:
            pass
        try:
            from agents import AGENT_CLASS_MAP  # type: ignore
            return dict(AGENT_CLASS_MAP)
        except Exception:
            return {}

    def pipeline(self) -> List[str]:
        """Return the configured pipeline order."""
        return list(AGENT_PIPELINE)

    def can_modify(self, path: str, task_description: str) -> bool:
        """Check if a task may modify a given path."""
        category = self.router.classify(task_description)
        return self.guard.is_allowed(path, category)

    async def run_pipeline(
        self, user_request: str, context: Optional[dict] = None
    ) -> Iterable[dict]:
        """Execute the agent pipeline sequentially, passing context forward.

        A :class:`~services.agent_pipeline.PipelineContext` object is created
        (or wraps the supplied dict) and passed to every agent so outputs can
        be shared across stages.

        Each agent is called with whichever method it exposes — ``execute``
        takes priority over ``run``.  Any exception raised by an agent is
        caught, logged, and recorded as a failure response; the pipeline then
        continues to the next stage.
        """
        # Build a PipelineContext so agents can share data across stages.
        pipeline_ctx: PipelineContext
        if isinstance(context, PipelineContext):
            pipeline_ctx = context
        else:
            pipeline_ctx = PipelineContext()
            if isinstance(context, dict):
                for k, v in context.items():
                    pipeline_ctx.set(k, v)

        responses = []
        prompt = user_request

        for agent_name in self.pipeline():
            agent_cls: Optional[Type] = self._agent_classes.get(agent_name)
            try:
                if agent_cls is not None:
                    agent = agent_cls(agent_service=self.agent_service)
                    # Prefer execute(context) per spec; fall back to run(prompt).
                    if hasattr(agent, "execute"):
                        response = await agent.execute(pipeline_ctx)
                    else:
                        response = await agent.run(prompt, context=pipeline_ctx.data)
                else:
                    response = await self.agent_service.run_agent(
                        prompt, context=pipeline_ctx.data
                    )
            except Exception as exc:
                logger.error("Agent '%s' raised an exception", agent_name, exc_info=True)
                response = {
                    "success": False,
                    "data": None,
                    "error": f"{agent_name}: {exc}",
                }

            responses.append(response)

            if not response.get("success"):
                logger.warning(
                    "Agent '%s' reported failure; continuing pipeline.", agent_name
                )
                pipeline_ctx.set(f"{agent_name}:error", response.get("error"))
                continue

            # Advance the prompt to the agent's text output for the next stage.
            data = response.get("data")
            if isinstance(data, dict) and "text" in data:
                prompt = data["text"]
                pipeline_ctx.set(agent_name, data["text"])

        return responses
