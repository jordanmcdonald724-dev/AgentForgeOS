"""Defines the Phase 5 agent pipeline."""

from typing import List

strategic_agents: List[str] = ["Project Planner", "System Architect", "Task Router"]
architecture_agents: List[str] = ["Module Builder", "API Architect", "Data Architect"]
production_agents: List[str] = ["Backend Engineer", "Frontend Engineer", "AI Integration Engineer"]
validation_agents: List[str] = ["Integration Tester", "Security Auditor", "System Stabilizer"]

# Full execution order derived from docs
AGENT_PIPELINE: List[str] = [
    *strategic_agents,
    *architecture_agents,
    *production_agents,
    *validation_agents,
]
