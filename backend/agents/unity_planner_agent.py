from __future__ import annotations

from typing import Any, Dict, List

from agents.base_agent import BaseAgent


class UnityPlannerAgent(BaseAgent):
    name = "unity_planner_agent"
    description = "Creates an initial Unity-focused execution plan for game systems and features"
    capabilities = ["unity_planning", "game_system_breakdown", "ui_logic_split"]

    def __init__(self) -> None:
        super().__init__(self.name, self.description, self.capabilities)  # type: ignore[arg-type]

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        request = str(input_data.get("request", "")).strip()
        if not request:
            raise ValueError("UnityPlannerAgent requires a non-empty 'request' field.")

        modules = self._detect_modules(request)
        suggested_steps = [
            "define_scenes_and_flow",
            "design_ui_wireframes",
            "implement_core_logic",
            "wire_input_and_events",
            "persist_and_sync_state",
        ]

        return {
            "engine": "unity",
            "summary": f"Unity plan for: {request}",
            "modules": modules,
            "suggested_steps": suggested_steps,
            "assumptions": ["Unity 2021+ project", "C# scripting"],
        }

    def self_evaluate(self, output: Dict[str, Any]) -> Dict[str, Any]:
        issues: List[str] = []
        if output.get("engine") != "unity":
            issues.append("engine_mismatch")
        if not output.get("modules"):
            issues.append("missing_modules")
        if not output.get("suggested_steps"):
            issues.append("missing_steps")

        confidence = 0.9 if not issues else 0.65 if len(issues) == 1 else 0.4
        return {
            "confidence": confidence,
            "issues": issues,
            "suggested_fix": "add modules/steps or correct engine" if issues else None,
        }

    def repair(self, output: Dict[str, Any], feedback: Dict[str, Any]) -> Dict[str, Any]:
        repaired = dict(output)
        modules = repaired.get("modules") or []
        required = {"UI", "Logic", "Data", "Input"}
        normalized = {str(m) for m in modules}

        if not required.intersection(normalized):
            modules.extend(["UI", "Logic"])

        repaired["modules"] = list(
            dict.fromkeys(modules)
        )  # dedupe while preserving order (Python 3.7+)

        if not repaired.get("suggested_steps"):
            repaired["suggested_steps"] = [
                "define_scenes_and_flow",
                "design_ui_wireframes",
                "implement_core_logic",
                "wire_input_and_events",
                "persist_and_sync_state",
            ]

        if repaired.get("engine") != "unity":
            repaired["engine"] = "unity"

        return repaired

    def _detect_modules(self, request: str) -> List[str]:
        lowered = request.lower()
        modules: List[str] = []
        if any(word in lowered for word in ["ui", "hud", "menu"]):
            modules.append("UI")
        if any(word in lowered for word in ["inventory", "combat", "logic", "quest"]):
            modules.append("Logic")
        if any(word in lowered for word in ["data", "save", "persist", "database"]):
            modules.append("Data")
        if any(word in lowered for word in ["input", "controller", "controls"]):
            modules.append("Input")
        if not modules:
            modules = ["UI", "Logic", "Data"]
        return modules
