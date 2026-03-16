"""Agent supervisor coordinating pipeline execution with guards."""

from typing import Iterable, List, Optional

from agents import AGENT_PIPELINE
from control.ai_router import AIRouter
from control.file_guard import FileGuard
from services import AgentService


class AgentSupervisor:
    """Coordinates agent execution order and enforces guard checks."""

    def __init__(self, agent_service: AgentService, router: Optional[AIRouter] = None, guard: Optional[FileGuard] = None):
        self.agent_service = agent_service
        self.router = router or AIRouter()
        self.guard = guard or FileGuard()

    def pipeline(self) -> List[str]:
        """Return the configured pipeline order."""
        return list(AGENT_PIPELINE)

    def can_modify(self, path: str, task_description: str) -> bool:
        """Check if a task may modify a given path."""
        category = self.router.classify(task_description)
        return self.guard.is_allowed(path, category)

    async def run_pipeline(self, user_request: str, context: Optional[dict] = None) -> Iterable[dict]:
        """Execute the agent pipeline, streaming provider responses."""
        responses = []
        prompt = user_request
        for _agent_name in self.pipeline():
            response = await self.agent_service.run_agent(prompt, context=context)
            responses.append(response)
            if not response.get("success"):
                break
            data = response.get("data")
            if isinstance(data, dict) and "text" in data:
                prompt = data["text"]
        return responses
