from __future__ import annotations

from typing import Dict, List, Optional

from control.ai_router import AIRouter
from control.agent_pipeline import AgentPipeline
from control.dynamic_pipeline_builder import DynamicPipelineBuilder
from control.agent_factory import AgentFactory
from control.learning_controller import LearningController


class EmergentOrchestrator:
    """
    Gate 10 orchestrator that prepares and adapts autonomous execution loops.
    """

    def __init__(
        self,
        router: AIRouter,
        pipeline: AgentPipeline,
        learning_controller: LearningController,
        dynamic_builder: DynamicPipelineBuilder,
        agent_factory: AgentFactory,
    ) -> None:
        self.router = router
        self.pipeline = pipeline
        self.learning_controller = learning_controller
        self.dynamic_builder = dynamic_builder
        self.agent_factory = agent_factory

    def initialize_task(self, request: str) -> Dict[str, object]:
        decision = self.router.route_request(request, page_hint="sandbox")
        agent_sequence = list(decision.agents) if isinstance(decision.agents, list) else []

        if not agent_sequence:
            agent_sequence = ["planner_agent"]
        if "planner_agent" not in agent_sequence:
            agent_sequence.append("planner_agent")

        context_insights: Dict[str, object] = {}
        if self.learning_controller:
            context_insights = self.learning_controller.query_context(request) or {}

        return {
            "agent_sequence": agent_sequence,
            "context": {
                "route": {
                    "page": decision.page,
                    "pipeline_type": decision.pipeline_type,
                    "build_type": decision.build_type,
                    "metadata": decision.metadata,
                },
                "context_insights": context_insights,
            },
        }

    def adapt_pipeline(self, agent_sequence: List[str], last_score: float, failure: bool) -> List[str]:
        safe_sequence = list(agent_sequence) if isinstance(agent_sequence, list) else ["planner_agent"]
        if not safe_sequence:
            safe_sequence = ["planner_agent"]

        if failure:
            replace_index = len(safe_sequence) - 1
            return self.dynamic_builder.replace_step(safe_sequence, replace_index, "planner_agent")

        if last_score is not None and last_score < 0.6 and "planner_agent" not in safe_sequence:
            return self.dynamic_builder.insert_step(safe_sequence, max(1, len(safe_sequence)), "planner_agent")

        return safe_sequence
