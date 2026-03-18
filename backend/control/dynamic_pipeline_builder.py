from __future__ import annotations

from typing import List


class DynamicPipelineBuilder:
    """
    Deterministic helper for controlled, in-memory pipeline modifications.
    """

    def insert_step(self, agent_list: List[str], index: int, new_agent: str) -> List[str]:
        if not isinstance(agent_list, list):
            return []
        if not isinstance(new_agent, str) or not new_agent:
            return list(agent_list)
        try:
            safe_list = list(agent_list)
            if index < 0 or index > len(safe_list):
                return safe_list
            safe_list.insert(index, new_agent)
            return safe_list
        except Exception:
            return list(agent_list)

    def replace_step(self, agent_list: List[str], index: int, new_agent: str) -> List[str]:
        if not isinstance(agent_list, list):
            return []
        if not isinstance(new_agent, str) or not new_agent:
            return list(agent_list)
        try:
            safe_list = list(agent_list)
            if index < 0 or index >= len(safe_list):
                return safe_list
            safe_list[index] = new_agent
            return safe_list
        except Exception:
            return list(agent_list)

    @staticmethod
    def validate_pipeline(agent_list: List[str]) -> bool:
        return isinstance(agent_list, list) and all(isinstance(a, str) and a for a in agent_list)
