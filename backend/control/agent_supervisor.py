from __future__ import annotations

from typing import Dict, Optional
from datetime import UTC, datetime
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
        Always returns AgentResult; never raises.
        """
        execution_id = str(uuid.uuid4())
        started = datetime.now(UTC)

        if not isinstance(input_data, dict):
            duration_ms = (datetime.now(UTC) - started).total_seconds() * 1000.0
            return AgentResult(
                agent_name=getattr(agent, "name", "unknown"),
                status="failed",
                output={},
                confidence=0.0,
                feedback={"error": "input_data must be a dictionary."},
                metadata={
                    "execution_id": execution_id,
                    "route_context": route_context or {},
                    "gate": 2,
                    "duration_ms": duration_ms,
                },
            )

        try:
            result = agent.execute(input_data)
            if not isinstance(result, AgentResult):
                raise TypeError(
                    f"Agent '{agent.name}' execute() must return AgentResult, got {type(result).__name__}."
                )

            duration_ms = (datetime.now(UTC) - started).total_seconds() * 1000.0
            metadata = dict(result.metadata)
            metadata.update(
                {
                    "execution_id": execution_id,
                    "route_context": route_context or {},
                    "gate": 2,
                    "duration_ms": metadata.get("duration_ms", duration_ms),
                }
            )

            return AgentResult(
                agent_name=result.agent_name,
                status=result.status,
                output=result.output if isinstance(result.output, dict) else {},
                confidence=result.confidence,
                feedback=result.feedback,
                metadata=metadata,
            )

        except Exception as exc:  # pylint: disable=broad-except
            duration_ms = (datetime.now(UTC) - started).total_seconds() * 1000.0
            metadata = {
                "execution_id": execution_id,
                "route_context": route_context or {},
                "gate": 2,
                "duration_ms": duration_ms,
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
        try:
            agent = self.get_registered_agent(agent_name)
        except Exception as exc:  # pylint: disable=broad-except
            return AgentResult(
                agent_name=agent_name,
                status="failed",
                output={},
                confidence=0.0,
                feedback={"error": f"{type(exc).__name__}: {exc}"},
                metadata={
                    "execution_id": str(uuid.uuid4()),
                    "route_context": route_context or {},
                    "gate": 2,
                },
            )

        return self.run_agent(agent=agent, input_data=input_data, route_context=route_context)
