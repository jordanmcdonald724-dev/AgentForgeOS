from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any

from agents.v2.base import Agent, AgentResult
from agents.v2.ai_engineer import AIEngineerAgent
from agents.v2.atlas import AtlasAgent
from agents.v2.backend_engineer import BackendEngineerAgent
from agents.v2.devops_engineer import DevOpsEngineerAgent
from agents.v2.forge import ForgeAgent
from agents.v2.frontend_engineer import FrontendEngineerAgent
from agents.v2.game_engine_engineer import GameEngineEngineerAgent
from agents.v2.prism import PrismAgent
from agents.v2.probe import ProbeAgent
from agents.v2.commander import CommanderAgent
from agents.v2.research_agent import ResearchAgent
from agents.v2.sentinel import SentinelAgent
from infrastructure.model_router import ModelRouter

from .engine import OrchestrationEngine
from .task_model import Task


@dataclass
class AgentRegistry:
    """Registry of all V2 agents by name.

    This keeps the orchestration engine decoupled from concrete
    agent implementations.
    """

    agents: Dict[str, Agent] = field(default_factory=dict)

    def get(self, name: str) -> Agent:
        return self.agents[name]


def default_agent_registry() -> AgentRegistry:
    router = ModelRouter()
    registry = AgentRegistry(
        agents={
            "Origin": CommanderAgent(),
            "Architect": AtlasAgent(),
            "Builder": ForgeAgent(),
            "Surface": FrontendEngineerAgent(),
            "Core": BackendEngineerAgent(),
            "Simulator": GameEngineEngineerAgent(),
            "Synapse": AIEngineerAgent(router=router),
            "Fabricator": PrismAgent(),
            "Guardian": SentinelAgent(),
            "Analyst": ProbeAgent(),
            "Launcher": DevOpsEngineerAgent(),
            "Archivist": ResearchAgent(),
        }
    )
    return registry


@dataclass
class OrchestrationRuntime:
    """Thin runtime wrapper around the orchestration engine.

    It owns an engine instance and an agent registry and is able
    to execute all ready tasks until the graph is exhausted.
    """

    engine: OrchestrationEngine = field(default_factory=OrchestrationEngine)
    registry: AgentRegistry = field(default_factory=default_agent_registry)

    def submit_command(self, command: str, brief: Dict[str, Any] | None = None) -> None:
        """Create a task graph for a new command.

        Optionally attaches a ``brief`` payload to the simulation task so
        the Probe agent can run the feasibility simulation as described in
        BUILD_BIBLE_V2.
        """

        self.engine.create_command_task_graph(command)
        if brief is not None and "cmd:simulate" in self.engine.tasks:
            self.engine.tasks["cmd:simulate"].inputs["brief"] = brief

    def step(self) -> bool:
        """Execute one wave of ready tasks.

        Returns True if any task was executed, otherwise False.
        """

        ready = self.engine.next_ready_tasks()
        if not ready:
            return False

        for task in ready:
            agent = self.registry.get(task.assigned_agent)
            self.engine.start_task(task.task_id)
            result: AgentResult = agent.handle_task(task)

            # Enforce simulation gating: once the Analyst completes, mark the
            # simulation result so downstream build tasks can be blocked when
            # feasibility is not approved.
            if task.assigned_agent == "Analyst":
                approved = bool(result.outputs.get("feasible", True))
                self.engine.mark_simulation_result(
                    task_id=task.task_id,
                    approved=approved,
                    details=result.outputs,
                )
                # Analyst also declares concrete test artifacts; enforce
                # that they exist on disk after the simulation run.
                self.engine.verify_outputs(task.task_id)
            else:
                self.engine.complete_task(task.task_id, outputs=result.outputs)
                # After a task reports completion, enforce the V2
                # execution rule that declared output artifacts must
                # exist physically on disk when they are specified.
                self.engine.verify_outputs(task.task_id)
        return True

    def run_all(self) -> None:
        while self.step():
            pass

    def list_tasks(self) -> Dict[str, Task]:
        return dict(self.engine.tasks)
