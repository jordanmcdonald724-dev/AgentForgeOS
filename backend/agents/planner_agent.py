from __future__ import annotations

from typing import Any, Dict, List

from agents.base_agent import BaseAgent


class PlannerAgent(BaseAgent):
    name = "planner_agent"
    description = "Creates an initial execution plan for general software build requests"
    capabilities = ["planning", "task_breakdown", "initial_analysis"]

    def __init__(self) -> None:
        super().__init__(self.name, self.description, self.capabilities)  # type: ignore[arg-type]

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        request = str(input_data.get("request", "")).strip()
        if not request:
            raise ValueError("PlannerAgent requires a non-empty 'request' field.")

        detected_type = self._detect_type(request)
        suggested_steps = [
            "clarify_requirements",
            "outline_architecture",
            "identify_risks",
            "plan_implementation_phases",
        ]

        return {
            "summary": f"Initial plan for: {request}",
            "detected_type": detected_type,
            "suggested_steps": suggested_steps,
            "assumptions": ["requirements are stable", "basic auth needed"] if "auth" in request.lower() else [],
        }

    def self_evaluate(self, output: Dict[str, Any]) -> Dict[str, Any]:
        issues: List[str] = []
        if not output.get("summary"):
            issues.append("missing_summary")
        if not output.get("suggested_steps"):
            issues.append("missing_steps")
        if not output.get("assumptions"):
            issues.append("missing_assumptions")

        confidence = 0.9 if not issues else 0.65 if len(issues) == 1 else 0.4
        return {
            "confidence": confidence,
            "issues": issues,
            "suggested_fix": "populate missing fields" if issues else None,
        }

    def repair(self, output: Dict[str, Any], feedback: Dict[str, Any]) -> Dict[str, Any]:
        repaired = dict(output)

        if not repaired.get("suggested_steps"):
            repaired["suggested_steps"] = [
                "clarify_requirements",
                "outline_architecture",
                "identify_risks",
                "plan_implementation_phases",
            ]

        if not repaired.get("assumptions"):
            repaired["assumptions"] = ["assume default non-functional requirements"]

        if not repaired.get("summary"):
            repaired["summary"] = output.get("summary") or "Generated initial plan"

        return repaired

    def _detect_type(self, request: str) -> str:
        lowered = request.lower()
        if any(keyword in lowered for keyword in ["api", "backend", "service"]):
            return "backend_system"
        if any(keyword in lowered for keyword in ["mobile", "android", "ios"]):
            return "mobile_app"
        if any(keyword in lowered for keyword in ["web", "frontend", "ui"]):
            return "web_app"
        return "general_application"
