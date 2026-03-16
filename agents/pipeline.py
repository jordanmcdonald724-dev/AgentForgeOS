"""
Pipeline entry-point for the AgentForgeOS agent system.

This module wires the ordered agent list from services.agent_pipeline to the
AgentSupervisor, providing a single public function that external callers use
to run the full multi-agent pipeline.

Individual agent classes (planner, architect, etc.) are defined under this
package as they are implemented.  This entry-point is intentionally kept thin
so it remains stable while the agent implementations evolve.
"""

from typing import Iterable, Optional

from control.agent_supervisor import AgentSupervisor
from services import AgentService
from services.agent_pipeline import AGENT_PIPELINE


def get_pipeline_stages() -> list:
    """Return the ordered list of agent role names for the current pipeline."""
    return list(AGENT_PIPELINE)


async def run(user_request: str, context: Optional[dict] = None) -> Iterable[dict]:
    """
    Execute the full agent pipeline for *user_request*.

    Creates a default AgentService and AgentSupervisor, then delegates
    execution to the supervisor's run_pipeline method.

    Args:
        user_request: The natural-language task description.
        context:      Optional dict of additional context passed to each agent.

    Returns:
        An iterable of response dicts, one per pipeline stage.
    """
    agent_service = AgentService()
    supervisor = AgentSupervisor(agent_service=agent_service)
    return await supervisor.run_pipeline(user_request, context=context)
