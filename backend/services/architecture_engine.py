from __future__ import annotations

from typing import Dict, List


class ArchitectureEngine:
    """
    Deterministic architecture planner for Gate 8.
    Converts a system design into modules, components, and an initial agent plan.
    """

    def build_architecture(self, spec: Dict[str, object]) -> Dict[str, object]:
        safe_spec = spec or {}
        system_type = str(safe_spec.get("type", "app"))
        platform = str(safe_spec.get("platform", "unknown"))

        modules = self._map_modules(system_type)
        components = self._map_components(platform)
        pipeline_agents = self._map_agents(system_type, platform)

        return {
            "modules": modules,
            "components": components,
            "pipeline_agents": pipeline_agents,
        }

    def _map_modules(self, system_type: str) -> List[str]:
        mapping = {
            "game_system": ["UI", "Logic", "Data"],
            "backend": ["API", "Auth", "Persistence"],
            "os": ["Kernel", "Drivers", "Userland"],
            "app": ["UI", "Logic", "Data"],
        }
        return mapping.get(system_type, ["UI", "Logic", "Data"])

    def _map_components(self, platform: str) -> List[str]:
        platform_map = {
            "unity": ["UnityEngine", "CSharpScripts", "Scenes"],
            "unreal": ["Blueprints", "C++Modules", "Levels"],
            "web": ["Frontend", "Backend", "API Gateway"],
            "desktop": ["UI Layer", "Service Layer", "Storage"],
        }
        return platform_map.get(platform, ["Core", "IO", "Services"])

    def _map_agents(self, system_type: str, platform: str) -> List[str]:
        agents: List[str] = ["planner_agent"]

        if platform == "unity":
            agents.append("unity_planner_agent")
        elif platform == "unreal":
            agents.append("unreal_planner_agent")

        if system_type == "backend":
            agents.append("planner_agent")

        # Deduplicate while preserving order
        seen = set()
        ordered = []
        for agent in agents:
            if agent not in seen:
                seen.add(agent)
                ordered.append(agent)
        return ordered
