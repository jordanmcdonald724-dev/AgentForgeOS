from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Protocol
import traceback
import uuid


class AgentProtocol(Protocol):
    """
    Minimal runtime contract for agents in Gate 1.
    """

    name: str

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        ...


@dataclass
class AgentExecutionResult:
    """
    Structured result for a single agent execution.
    """

    execution_id: str
    agent_name: str
    status: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    started_at: str = ""
    completed_at: str = ""
    duration_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentSupervisor:
    """
    Gate 1 execution authority.

    Responsibilities:
    - Accept an agent instance
    - Run it safely
    - Return structured result
    - Prevent raw uncontrolled execution from leaking outward
    """

    def __init__(self) -> None:
        self._registered_agents: Dict[str, AgentProtocol] = {}

    def register_agent(self, agent: AgentProtocol) -> None:
        """
        Register a live agent instance by its name.
        """
        if not hasattr(agent, "name") or not isinstance(agent.name, str) or not agent.name.strip():
            raise ValueError("Agent must have a non-empty 'name' attribute.")

        if not hasattr(agent, "run") or not callable(agent.run):
            raise ValueError(f"Agent '{agent.name}' must implement a callable run(input_data) method.")

        self._registered_agents[agent.name] = agent

    def get_registered_agent(self, agent_name: str) -> AgentProtocol:
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
        agent: AgentProtocol,
        input_data: Dict[str, Any],
        route_context: Optional[Dict[str, Any]] = None,
    ) -> AgentExecutionResult:
        """
        Execute a single agent and return a structured result.

        Args:
            agent: Agent instance with .name and .run(...)
            input_data: Structured input payload
            route_context: Optional router/system context

        Returns:
            AgentExecutionResult
        """
        if not isinstance(input_data, dict):
            raise ValueError("run_agent requires input_data to be a dictionary.")

        execution_id = str(uuid.uuid4())
        started_dt = datetime.now(timezone.utc)

        result = AgentExecutionResult(
            execution_id=execution_id,
            agent_name=agent.name,
            status="running",
            input_data=input_data,
            started_at=started_dt.isoformat(),
            metadata={
                "route_context": route_context or {},
                "gate": 1,
            },
        )

        try:
            output = agent.run(input_data)

            if not isinstance(output, dict):
                raise TypeError(
                    f"Agent '{agent.name}' returned invalid output type "
                    f"'{type(output).__name__}'. Expected dict."
                )

            completed_dt = datetime.now(timezone.utc)
            result.status = "success"
            result.output_data = output
            result.completed_at = completed_dt.isoformat()
            result.duration_ms = (completed_dt - started_dt).total_seconds() * 1000.0
            return result

        except Exception as exc:  # pylint: disable=broad-except
            completed_dt = datetime.now(timezone.utc)
            result.status = "failed"
            result.error = f"{type(exc).__name__}: {exc}"
            result.completed_at = completed_dt.isoformat()
            result.duration_ms = (completed_dt - started_dt).total_seconds() * 1000.0
            result.metadata["traceback"] = traceback.format_exc()
            return result

    def run_registered_agent(
        self,
        agent_name: str,
        input_data: Dict[str, Any],
        route_context: Optional[Dict[str, Any]] = None,
    ) -> AgentExecutionResult:
        """
        Lookup a registered agent by name and execute it.
        """
        agent = self.get_registered_agent(agent_name)
        return self.run_agent(agent=agent, input_data=input_data, route_context=route_context)


# -------------------------------------------------------------------
# TEMP GATE 1 TEST AGENTS
# These let you verify the control spine immediately.
# You can delete them later once your real agents exist.
# -------------------------------------------------------------------


class PlannerAgent:
    name = "planner_agent"

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        request = input_data.get("request", "").strip()
        if not request:
            raise ValueError("PlannerAgent requires 'request' in input_data.")

        return {
            "summary": f"Planned request: {request}",
            "next_step": "architecture_phase",
            "confidence": 0.82,
        }


class UnityPlannerAgent:
    name = "unity_planner_agent"

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        request = input_data.get("request", "").strip()
        return {
            "engine": "unity",
            "plan": f"Prepared Unity-focused planning pass for: {request}",
            "modules": ["UI", "Logic", "Data"],
        }


class UnrealPlannerAgent:
    name = "unreal_planner_agent"

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        request = input_data.get("request", "").strip()
        return {
            "engine": "unreal",
            "plan": f"Prepared Unreal-focused planning pass for: {request}",
            "modules": ["Blueprints/C++", "UI", "Gameplay Data"],
        }


class AssetPlannerAgent:
    name = "asset_planner_agent"

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        request = input_data.get("request", "").strip()
        return {
            "asset_type": "general_asset",
            "plan": f"Prepared asset generation plan for: {request}",
            "stages": ["reference_analysis", "generation", "validation"],
        }


class TexturePlannerAgent:
    name = "texture_planner_agent"

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        request = input_data.get("request", "").strip()
        return {
            "asset_type": "texture_or_material",
            "plan": f"Prepared texture/material workflow for: {request}",
            "stages": ["style_analysis", "texture_generation", "validation"],
        }


class AdaptivePlannerAgent:
    name = "adaptive_planner_agent"

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        request = input_data.get("request", "").strip()
        return {
            "mode": "adaptive",
            "plan": f"Prepared autonomous adaptive workflow for: {request}",
            "features": ["dynamic_routing", "live_adjustment"],
        }


class ResearchIngestAgent:
    name = "research_ingest_agent"

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        request = input_data.get("request", "").strip()
        return {
            "mode": "knowledge_ingestion",
            "plan": f"Prepared research ingestion flow for: {request}",
            "stages": ["parse", "chunk", "index"],
        }


class GamePlannerAgent:
    name = "game_planner_agent"

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        request = input_data.get("request", "").strip()
        return {
            "mode": "game_dev",
            "plan": f"Prepared game development plan for: {request}",
            "stages": ["system_design", "implementation", "validation"],
        }


class DeploymentPlannerAgent:
    name = "deployment_planner_agent"

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        request = input_data.get("request", "").strip()
        return {
            "mode": "deployment",
            "plan": f"Prepared deployment pipeline for: {request}",
            "stages": ["package", "verify", "release"],
        }


if __name__ == "__main__":
    supervisor = AgentSupervisor()

    supervisor.register_agent(PlannerAgent())
    supervisor.register_agent(UnityPlannerAgent())
    supervisor.register_agent(UnrealPlannerAgent())
    supervisor.register_agent(AssetPlannerAgent())
    supervisor.register_agent(TexturePlannerAgent())
    supervisor.register_agent(AdaptivePlannerAgent())
    supervisor.register_agent(ResearchIngestAgent())
    supervisor.register_agent(GamePlannerAgent())
    supervisor.register_agent(DeploymentPlannerAgent())

    test_result = supervisor.run_registered_agent(
        agent_name="planner_agent",
        input_data={"request": "Build a desktop app with authentication"},
        route_context={"pipeline_type": "structured_execution"},
    )

    print("=== EXECUTION RESULT ===")
    print(f"execution_id: {test_result.execution_id}")
    print(f"agent_name: {test_result.agent_name}")
    print(f"status: {test_result.status}")
    print(f"output_data: {test_result.output_data}")
    print(f"error: {test_result.error}")
    print(f"duration_ms: {test_result.duration_ms:.2f}")
