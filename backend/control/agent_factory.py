from __future__ import annotations

from typing import Any, Dict, List

from agents.base_agent import BaseAgent


class GeneratedAgent(BaseAgent):
    """
    Deterministic placeholder agent created dynamically by the AgentFactory.
    Produces structured output that can flow through the existing pipeline.
    """

    def __init__(self, name: str, description: str, capabilities: List[str]) -> None:
        super().__init__(name=name, description=description, capabilities=capabilities)

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        request = input_data.get("request") if isinstance(input_data, dict) else None
        return {
            "summary": f"Generated plan for role '{self.name}'",
            "assumptions": [f"Based on request: {request}"] if request else [],
            "suggested_steps": [
                "analyze current context",
                "draft detailed plan",
                "execute plan with available tools",
            ],
            "engine": "dynamic",
        }

    def self_evaluate(self, output: Dict[str, Any]) -> Dict[str, Any]:
        has_summary = bool(output.get("summary")) if isinstance(output, dict) else False
        confidence = 0.8 if has_summary else 0.5
        return {"confidence": confidence, "issues": [] if has_summary else ["missing_summary"], "suggested_fix": None}

    def repair(self, output: Dict[str, Any], feedback: Dict[str, Any]) -> Dict[str, Any]:
        repaired = dict(output or {})
        repaired.setdefault("summary", "Repaired output for generated agent.")
        repaired.setdefault("assumptions", [])
        repaired.setdefault("suggested_steps", ["fallback step"])
        repaired.setdefault("engine", "dynamic")
        repaired["repair_note"] = "Auto-repaired by generated agent."
        return repaired


class AgentFactory:
    """
    Creates deterministic placeholder agents for missing capabilities.
    """

    def create_agent(self, role: str) -> BaseAgent:
        try:
            safe_role = role.strip().replace(" ", "_") if isinstance(role, str) else "generated"
            name = f"{safe_role}_generated_agent" if safe_role else "generated_agent"
            description = f"Dynamically created agent for {role}"
            capabilities = [safe_role or "generated"]
            return GeneratedAgent(name=name, description=description, capabilities=capabilities)
        except Exception:
            return GeneratedAgent(
                name="generated_agent",
                description="Fallback dynamically created agent",
                capabilities=["generated"],
            )
