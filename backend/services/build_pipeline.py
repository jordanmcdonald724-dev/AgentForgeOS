from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Dict, List

from control.ai_router import AIRouter
from control.agent_pipeline import AgentPipeline, PipelineResult, PipelineStepResult
from control.learning_controller import LearningController
from services.architecture_engine import ArchitectureEngine
from services.build_templates import BUILD_TEMPLATES
from services.system_designer import SystemDesigner


class BuildPipeline:
    """
    Gate 8 orchestration entry for the Builds page.
    """

    def __init__(
        self,
        router: AIRouter,
        agent_pipeline: AgentPipeline,
        system_designer: SystemDesigner,
        architecture_engine: ArchitectureEngine,
        learning_controller: LearningController,
    ) -> None:
        self.router = router
        self.agent_pipeline = agent_pipeline
        self.system_designer = system_designer
        self.architecture_engine = architecture_engine
        self.learning_controller = learning_controller

    def run_build(self, request: str) -> Dict[str, Any]:
        design = self.system_designer.design_system(request)
        architecture = self.architecture_engine.build_architecture(design)
        route = self.router.route_request(request, page_hint="builds")

        agent_sequence = self._select_agents(design, architecture, route.agents)

        pipeline_result = self.agent_pipeline.run_pipeline(
            agent_names=agent_sequence,
            initial_input={
                "request": request,
                "design": design,
                "architecture": architecture,
                "route": asdict(route),
            },
            route_context=route.metadata,
        )

        return {
            "design": design,
            "architecture": architecture,
            "agent_sequence": agent_sequence,
            "pipeline_result": self._pipeline_result_to_dict(pipeline_result),
        }

    def _select_agents(self, design: Dict[str, Any], architecture: Dict[str, Any], route_agents: List[str]) -> List[str]:
        template_key = self._resolve_template_key(design)
        if template_key in BUILD_TEMPLATES:
            return list(BUILD_TEMPLATES[template_key])

        arch_agents = architecture.get("pipeline_agents") if isinstance(architecture, dict) else []
        if isinstance(arch_agents, list) and arch_agents:
            return list(arch_agents)

        return list(route_agents or [])

    def _resolve_template_key(self, design: Dict[str, Any]) -> str:
        platform = str(design.get("platform", "")).lower() if isinstance(design, dict) else ""
        system_type = str(design.get("type", "")).lower() if isinstance(design, dict) else ""

        if platform == "unity":
            return "unity_system"
        if platform == "unreal":
            return "unreal_system"
        if platform == "web":
            return "web_app"
        if system_type == "backend":
            return "backend"
        return ""

    def _pipeline_result_to_dict(self, result: PipelineResult) -> Dict[str, Any]:
        if not isinstance(result, PipelineResult):
            return {}

        return {
            "pipeline_id": result.pipeline_id,
            "status": result.status,
            "steps": [self._step_to_dict(step) for step in result.steps],
            "final_output": result.final_output,
            "failed_step_index": result.failed_step_index,
            "metadata": result.metadata,
        }

    @staticmethod
    def _step_to_dict(step: PipelineStepResult) -> Dict[str, Any]:
        if is_dataclass(step):
            return asdict(step)
        return {}
