"""Agent supervisor coordinating pipeline execution with guards."""

from typing import Iterable, List, Optional, Type

from services.agent_pipeline import AGENT_PIPELINE
from control.ai_router import AIRouter
from control.file_guard import FileGuard
from services import AgentService


class AgentSupervisor:
    """Coordinates agent execution order and enforces guard checks.

    When individual agent classes are available (registered in
    ``agents.AGENT_CLASS_MAP``) the supervisor instantiates them and
    delegates ``run()`` to the typed agent.  Falls back to the generic
    ``AgentService.run_agent`` for any role not yet mapped.
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
    def _load_agent_classes():
        """Attempt to import the agent class map; return empty dict on failure."""
        try:
            from agents import AGENT_CLASS_MAP  # type: ignore
            return AGENT_CLASS_MAP
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
        """Execute the agent pipeline, using typed agent classes where available."""
        responses = []
        prompt = user_request
        for agent_name in self.pipeline():
            agent_cls: Optional[Type] = self._agent_classes.get(agent_name)
            if agent_cls is not None:
                agent = agent_cls(agent_service=self.agent_service)
                response = await agent.run(prompt, context=context)
            else:
                response = await self.agent_service.run_agent(prompt, context=context)
            responses.append(response)
            if not response.get("success"):
                break
            data = response.get("data")
            if isinstance(data, dict) and "text" in data:
                prompt = data["text"]
        return responses
