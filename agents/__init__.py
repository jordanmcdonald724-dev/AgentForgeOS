"""AgentForgeOS agent package — base class and all 12 pipeline agent classes."""

from .base_agent import BaseAgent

from .strategic import PlannerAgent, ArchitectAgent, RouterAgent
from .architecture import BuilderAgent, APIArchitectAgent, DataArchitectAgent
from .production import BackendEngineerAgent, FrontendEngineerAgent, AIIntegrationEngineerAgent
from .validation import IntegrationTesterAgent, SecurityAuditorAgent, SystemStabilizerAgent

# Mapping from AGENT_PIPELINE role name → concrete agent class.
AGENT_CLASS_MAP = {
    "Project Planner": PlannerAgent,
    "System Architect": ArchitectAgent,
    "Task Router": RouterAgent,
    "Module Builder": BuilderAgent,
    "API Architect": APIArchitectAgent,
    "Data Architect": DataArchitectAgent,
    "Backend Engineer": BackendEngineerAgent,
    "Frontend Engineer": FrontendEngineerAgent,
    "AI Integration Engineer": AIIntegrationEngineerAgent,
    "Integration Tester": IntegrationTesterAgent,
    "Security Auditor": SecurityAuditorAgent,
    "System Stabilizer": SystemStabilizerAgent,
}

__all__ = [
    "BaseAgent",
    "AGENT_CLASS_MAP",
    "PlannerAgent",
    "ArchitectAgent",
    "RouterAgent",
    "BuilderAgent",
    "APIArchitectAgent",
    "DataArchitectAgent",
    "BackendEngineerAgent",
    "FrontendEngineerAgent",
    "AIIntegrationEngineerAgent",
    "IntegrationTesterAgent",
    "SecurityAuditorAgent",
    "SystemStabilizerAgent",
]
