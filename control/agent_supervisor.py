"""Agent supervisor coordinating pipeline execution with guards."""

import logging
from typing import Iterable, List, Optional, Type, Dict

from services.agent_pipeline import AGENT_PIPELINE, PipelineContext
from control.ai_router import AIRouter
from control.file_guard import FileGuard
from control.execution_monitor import ExecutionMonitor
from control.scoring_engine import ScoringEngine
from control.recovery_engine import RecoveryEngine
from control.learning_controller import LearningController
from control.dynamic_pipeline_builder import DynamicPipelineBuilder
from control.agent_factory import AgentFactory
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
        monitor: Optional[ExecutionMonitor] = None,
        scorer: Optional[ScoringEngine] = None,
        recovery: Optional[RecoveryEngine] = None,
        learning: Optional[LearningController] = None,
        pipeline_builder: Optional[DynamicPipelineBuilder] = None,
        agent_factory: Optional[AgentFactory] = None,
    ):
        self.agent_service = agent_service
        self.router = router or AIRouter()
        self.guard = guard or FileGuard()
        self.monitor = monitor or ExecutionMonitor()
        self.scorer = scorer or ScoringEngine()
        self.recovery = recovery or RecoveryEngine()
        self.learning = learning or LearningController()
        self.pipeline_builder = pipeline_builder or DynamicPipelineBuilder()
        self.agent_factory = agent_factory or AgentFactory()
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

        # Pre-execution learning/context injection.
        self.learning.before_execution(pipeline_ctx)

        responses = []
        scores: Dict[str, Dict[str, float]] = {}
        prompt = user_request

        # Allow dynamic pipeline shaping before execution.
        pipeline_order = self.pipeline_builder.build(self.pipeline(), pipeline_ctx)

        for agent_name in pipeline_order:
            agent_cls: Optional[Type] = self._agent_classes.get(agent_name)
            self.monitor.start_step(agent_name, pipeline_ctx)
            try:
                if agent_cls is not None:
                    # Each role appears once per pipeline run; instantiate per-step for isolation.
                    agent = self.agent_factory.create(agent_cls, self.agent_service)
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

            if not response.get("success"):
                self.monitor.record_error(agent_name, str(response.get("error")))
                # Attempt recovery once.
                response = self.recovery.recover(
                    agent_name, response, pipeline_ctx, attempt=1
                )

            self.monitor.end_step(agent_name, response)
            scores[agent_name] = self.scorer.score(agent_name, response, pipeline_ctx)
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

        # Post-execution learning hook.
        self.learning.after_execution(responses, scores, pipeline_ctx)

        return responses
