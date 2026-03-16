"""Agent registry — maps pipeline role names to their concrete agent classes.

This registry is the authoritative source used by AgentSupervisor to
instantiate the correct agent class for each pipeline step.  It is kept
in ``services/`` so that the control layer can import it without creating
a circular dependency on the ``agents`` package's top-level ``__init__``.
"""

from typing import Dict, Type

from agents.strategic.planner_agent import PlannerAgent
from agents.strategic.architect_agent import ArchitectAgent
from agents.strategic.router_agent import RouterAgent

from agents.architecture.builder_agent import BuilderAgent
from agents.architecture.api_architect_agent import APIArchitectAgent
from agents.architecture.data_architect_agent import DataArchitectAgent

from agents.production.backend_agent import BackendEngineerAgent
from agents.production.frontend_agent import FrontendEngineerAgent
from agents.production.ai_integration_agent import AIIntegrationEngineerAgent

from agents.validation.tester_agent import IntegrationTesterAgent
from agents.validation.auditor_agent import SecurityAuditorAgent
from agents.validation.stabilizer_agent import SystemStabilizerAgent
from agents.base_agent import BaseAgent

AGENT_REGISTRY: Dict[str, Type[BaseAgent]] = {
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

__all__ = ["AGENT_REGISTRY"]
