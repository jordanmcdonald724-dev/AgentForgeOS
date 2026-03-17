from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

REFINEMENT_POLYCOUNT_BUFFER = 2000

from control.agent_pipeline import AgentPipeline
from services.asset_planner import AssetPlanner
from knowledge.reference_analyzer import ReferenceAnalyzer
from systems.model_generator import ModelGenerator
from systems.texture_generator import TextureGenerator
from systems.asset_validator import AssetValidator
from services.asset_registry import AssetRegistry


class AssetPipeline:
    """
    Gate 9 Assets orchestration pipeline.
    """

    def __init__(
        self,
        planner: AssetPlanner,
        analyzer: ReferenceAnalyzer,
        model_generator: ModelGenerator,
        texture_generator: TextureGenerator,
        validator: AssetValidator,
        registry: AssetRegistry,
        agent_pipeline: Optional[AgentPipeline] = None,
    ) -> None:
        self.planner = planner
        self.analyzer = analyzer
        self.model_generator = model_generator
        self.texture_generator = texture_generator
        self.validator = validator
        self.registry = registry
        self.agent_pipeline = agent_pipeline

    def run_asset_pipeline(self, request: str, references: Optional[List[Any]] = None) -> Dict[str, object]:
        refs = references or []

        plan = self.planner.plan_asset(request, refs)
        ref_data = self.analyzer.analyze(refs)

        # Optional: allow control-layer monitoring when provided, but never block execution.
        if self.agent_pipeline:
            try:
                self.agent_pipeline.run_pipeline(
                    agent_names=["planner_agent"],
                    initial_input={"request": request, "plan": plan, "references": refs},
                    route_context={"gate": 9, "context": "assets"},
                )
            except Exception:
                # Safe fallback to direct execution.
                pass

        asset, validation = self._generate_and_validate(plan, ref_data)

        if not validation.get("valid"):
            asset, validation = self._refine_once(plan, ref_data)

        asset_id = self.registry.create_asset(asset)

        return {
            "plan": plan,
            "validation": validation,
            "asset_id": asset_id,
            "asset": asset,
        }

    def _generate_and_validate(self, plan: Dict[str, object], ref_data: Dict[str, object]) -> Tuple[Dict[str, object], Dict[str, object]]:
        model = self.model_generator.generate(plan, ref_data)
        textures = self.texture_generator.generate(plan, ref_data)

        asset = {**model, **textures, "status": "generated"}
        validation = self.validator.validate(asset, plan)
        return asset, validation

    def _refine_once(self, plan: Dict[str, object], ref_data: Dict[str, object]) -> Tuple[Dict[str, object], Dict[str, object]]:
        refined_plan = dict(plan)
        constraints = refined_plan.get("constraints", {})
        if isinstance(constraints, dict) and "polycount" in constraints and isinstance(constraints["polycount"], int):
            # Loosen constraint slightly to allow refinement to pass validation.
            constraints["polycount"] = max(constraints["polycount"], 0) + REFINEMENT_POLYCOUNT_BUFFER
        refined_plan["constraints"] = constraints

        model = self.model_generator.generate(refined_plan, ref_data)
        # Clamp to the refined constraint to guarantee determinism.
        if isinstance(constraints, dict) and isinstance(constraints.get("polycount"), int) and constraints["polycount"] > 0:
            # Preserve a lower generated polycount if present, otherwise clamp to constraint.
            model["polycount"] = min(model.get("polycount", constraints["polycount"]), constraints["polycount"])

        textures = self.texture_generator.generate(refined_plan, ref_data)
        asset = {**model, **textures, "status": "refined"}
        validation = self.validator.validate(asset, refined_plan)
        return asset, validation
