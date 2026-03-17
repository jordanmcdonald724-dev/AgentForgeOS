from __future__ import annotations

from typing import Dict, Optional
import traceback
import uuid

from agents.base_agent import AgentResult, BaseAgent


class AgentSupervisor:
    """
    Gate 2 execution authority.

    Responsibilities:
    - Accept BaseAgent instances
    - Run them via execute()
    - Return structured AgentResult
    - Keep routing metadata isolated from agent internals
    """

    def __init__(self) -> None:
        self._registered_agents: Dict[str, BaseAgent] = {}

    def register_agent(self, agent: BaseAgent) -> None:
        """
        Register a live BaseAgent instance by its name.
        """
        if not isinstance(agent, BaseAgent):
            raise TypeError("AgentSupervisor only accepts BaseAgent instances.")

        if not isinstance(agent.name, str) or not agent.name.strip():
            raise ValueError("Agent must have a non-empty 'name' attribute.")

        self._registered_agents[agent.name] = agent

    def get_registered_agent(self, agent_name: str) -> BaseAgent:
        """
        Retrieve a previously registered agent instance.
        """
        if agent_name not in self._registered_agents:
            available = ", ".join(sorted(self._registered_agents.keys())) or "none"
            raise KeyError(
                f"Agent '{agent_name}' is not registered. Available registered agents: {available}"
            )
        return self._registered_agents[agent_name]

    def run_agent(
        self,
        agent: BaseAgent,
        input_data: Dict[str, object],
        route_context: Optional[Dict[str, object]] = None,
    ) -> AgentResult:
        """
        Execute a single agent through its controlled orchestration flow.
        """
        if not isinstance(input_data, dict):
            raise ValueError("run_agent requires input_data to be a dictionary.")

        execution_id = str(uuid.uuid4())

        try:
            result = agent.execute(input_data)
            if not isinstance(result, AgentResult):
                raise TypeError(
                    f"Agent '{agent.name}' execute() must return AgentResult, got {type(result).__name__}."
                )

            metadata = dict(result.metadata)
            metadata.update(
                {
                    "execution_id": execution_id,
                    "route_context": route_context or {},
                    "gate": 2,
                }
            )

            return AgentResult(
                agent_name=result.agent_name,
                status=result.status,
                output=result.output,
                confidence=result.confidence,
                feedback=result.feedback,
                metadata=metadata,
            )

        except Exception as exc:  # pylint: disable=broad-except
            metadata = {
                "execution_id": execution_id,
                "route_context": route_context or {},
                "gate": 2,
                "traceback": traceback.format_exc(),
            }
            return AgentResult(
                agent_name=getattr(agent, "name", "unknown"),
                status="failed",
                output={},
                confidence=0.0,
                feedback={"error": f"{type(exc).__name__}: {exc}"},
                metadata=metadata,
            )

    def run_registered_agent(
        self,
        agent_name: str,
        input_data: Dict[str, object],
        route_context: Optional[Dict[str, object]] = None,
    ) -> AgentResult:
        """
        Lookup a registered agent by name and execute it.
        """
        agent = self.get_registered_agent(agent_name)
        return self.run_agent(agent=agent, input_data=input_data, route_context=route_context)
