from __future__ import annotations

from typing import Any, Dict, List

from agents.base_agent import BaseAgent


class UnrealPlannerAgent(BaseAgent):
    name = "unreal_planner_agent"
    description = "Creates an initial Unreal-focused execution plan for gameplay systems and features"
    capabilities = ["unreal_planning", "gameplay_system_breakdown", "blueprint_cpp_split"]

    def __init__(self) -> None:
        super().__init__(self.name, self.description, self.capabilities)  # type: ignore[arg-type]

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        request = str(input_data.get("request", "")).strip()
        if not request:
            raise ValueError("UnrealPlannerAgent requires a non-empty 'request' field.")

        modules = self._detect_modules(request)
        suggested_steps = [
            "define_gameplay_loop",
            "prototype_blueprints",
            "establish_cpp_interfaces",
            "implement_ui_widgets",
            "hook_input_and_savegame",
        ]

        return {
            "engine": "unreal",
            "summary": f"Unreal plan for: {request}",
            "modules": modules,
            "suggested_steps": suggested_steps,
            "assumptions": ["UE5 project", "Blueprints with optional C++ extensions"],
        }

    def self_evaluate(self, output: Dict[str, Any]) -> Dict[str, Any]:
        issues: List[str] = []
        if output.get("engine") != "unreal":
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
        required = {"UI", "Gameplay Logic", "Data", "Input", "Blueprint/C++"}
        normalized = {str(m) for m in modules}

        if not required.intersection(normalized):
            modules.extend(["Gameplay Logic", "Blueprint/C++"])

        repaired["modules"] = list(dict.fromkeys(modules))  # dedupe while preserving order

        if not repaired.get("suggested_steps"):
            repaired["suggested_steps"] = [
                "define_gameplay_loop",
                "prototype_blueprints",
                "establish_cpp_interfaces",
                "implement_ui_widgets",
                "hook_input_and_savegame",
            ]

        if repaired.get("engine") != "unreal":
            repaired["engine"] = "unreal"

        return repaired

    def _detect_modules(self, request: str) -> List[str]:
        lowered = request.lower()
        modules: List[str] = []
        if any(word in lowered for word in ["ui", "hud", "menu"]):
            modules.append("UI")
        if any(word in lowered for word in ["combat", "inventory", "gameplay", "logic"]):
            modules.append("Gameplay Logic")
        if any(word in lowered for word in ["data", "save", "persistence", "database"]):
            modules.append("Data")
        if any(word in lowered for word in ["input", "controller", "controls"]):
            modules.append("Input")
        if any(word in lowered for word in ["blueprint", "c++", "cpp"]):
            modules.append("Blueprint/C++")
        if not modules:
            modules = ["Gameplay Logic", "Blueprint/C++", "UI"]
        return modules
