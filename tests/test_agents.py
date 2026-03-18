"""Tests for individual agent classes and the AGENT_CLASS_MAP registry."""

import asyncio
import unittest

from services.agent_pipeline import AGENT_PIPELINE


class AgentBaseClassTests(unittest.TestCase):
    """BaseAgent interface tests."""

    def test_base_agent_is_abstract(self):
        from agents.base_agent import BaseAgent
        import inspect

        self.assertTrue(inspect.isabstract(BaseAgent))

    def test_base_agent_describe(self):
        from agents.base_agent import BaseAgent
        from providers.noop_provider import NoOpLLMProvider
        from services.agent_service import AgentService

        class ConcreteAgent(BaseAgent):
            role = "Test Role"
            async def run(self, prompt, *, context=None):
                return {"success": True, "data": None, "error": None}

        agent = ConcreteAgent(agent_service=AgentService(NoOpLLMProvider()))
        desc = agent.describe()
        self.assertEqual(desc["role"], "Test Role")
        self.assertEqual(desc["class"], "ConcreteAgent")

    def test_build_prompt_prepends_system_prompt(self):
        from agents.base_agent import BaseAgent

        class ConcreteAgent(BaseAgent):
            role = "Tester"
            system_prompt = "Be thorough."
            async def run(self, prompt, *, context=None):
                return {"success": True, "data": None, "error": None}

        agent = ConcreteAgent()
        result = agent._build_prompt("do something")
        self.assertIn("Be thorough.", result)
        self.assertIn("do something", result)


class AgentClassMapTests(unittest.TestCase):
    """AGENT_CLASS_MAP must cover every AGENT_PIPELINE role."""

    def test_all_pipeline_roles_have_class(self):
        from agents import AGENT_CLASS_MAP

        for role in AGENT_PIPELINE:
            self.assertIn(
                role,
                AGENT_CLASS_MAP,
                f"No agent class registered for pipeline role '{role}'",
            )

    def test_all_classes_are_instantiable(self):
        from agents import AGENT_CLASS_MAP

        for role, cls in AGENT_CLASS_MAP.items():
            instance = cls()
            self.assertIsNotNone(instance, f"Could not instantiate {cls.__name__}")

    def test_all_classes_have_correct_role_attr(self):
        from agents import AGENT_CLASS_MAP

        for expected_role, cls in AGENT_CLASS_MAP.items():
            self.assertEqual(
                cls.role,
                expected_role,
                f"{cls.__name__}.role is '{cls.role}', expected '{expected_role}'",
            )


class ConcreteAgentRunTests(unittest.TestCase):
    """Each agent class delegates to AgentService via _run_with_service."""

    def _make_service(self, response_text="reply"):
        from providers.llm_provider import LLMProvider
        from services.agent_service import AgentService

        class StubLLM(LLMProvider):
            async def chat(self, prompt, *, context=None):
                return {
                    "success": True,
                    "data": {"text": response_text},
                    "error": None,
                }

        return AgentService(StubLLM())

    def test_planner_agent_run(self):
        from agents.strategic.planner_agent import PlannerAgent

        agent = PlannerAgent(agent_service=self._make_service("plan"))
        result = asyncio.run(agent.run("build a todo app"))
        self.assertTrue(result["success"])

    def test_auditor_agent_run(self):
        from agents.validation.auditor_agent import SecurityAuditorAgent

        agent = SecurityAuditorAgent(agent_service=self._make_service("audit ok"))
        result = asyncio.run(agent.run("review this code"))
        self.assertTrue(result["success"])

    def test_agent_without_service_returns_error(self):
        from agents.strategic.planner_agent import PlannerAgent

        agent = PlannerAgent()  # no service
        result = asyncio.run(agent.run("do something"))
        self.assertFalse(result["success"])
        self.assertIsNotNone(result["error"])


class AgentSubpackageExportTests(unittest.TestCase):
    """Sub-package __init__ files export the right names."""

    def test_strategic_exports(self):
        from agents.strategic import PlannerAgent, ArchitectAgent, RouterAgent

        self.assertIsNotNone(PlannerAgent)
        self.assertIsNotNone(ArchitectAgent)
        self.assertIsNotNone(RouterAgent)

    def test_architecture_exports(self):
        from agents.architecture import BuilderAgent, APIArchitectAgent, DataArchitectAgent

        self.assertIsNotNone(BuilderAgent)
        self.assertIsNotNone(APIArchitectAgent)
        self.assertIsNotNone(DataArchitectAgent)

    def test_production_exports(self):
        from agents.production import (
            BackendEngineerAgent,
            FrontendEngineerAgent,
            AIIntegrationEngineerAgent,
        )

        self.assertIsNotNone(BackendEngineerAgent)
        self.assertIsNotNone(FrontendEngineerAgent)
        self.assertIsNotNone(AIIntegrationEngineerAgent)

    def test_validation_exports(self):
        from agents.validation import (
            IntegrationTesterAgent,
            SecurityAuditorAgent,
            SystemStabilizerAgent,
        )

        self.assertIsNotNone(IntegrationTesterAgent)
        self.assertIsNotNone(SecurityAuditorAgent)
        self.assertIsNotNone(SystemStabilizerAgent)


class AgentServiceOptionalProviderTests(unittest.TestCase):
    """AgentService must work without an explicit LLM provider."""

    def test_no_args_uses_noop_provider(self):
        from services.agent_service import AgentService
        from providers.noop_provider import NoOpLLMProvider

        svc = AgentService()
        self.assertIsInstance(svc.llm_provider, NoOpLLMProvider)

    def test_run_agent_with_noop_returns_failure(self):
        from services.agent_service import AgentService

        svc = AgentService()
        result = asyncio.run(svc.run_agent("hello"))
        self.assertFalse(result["success"])


class AgentSupervisorWithClassesTests(unittest.TestCase):
    """AgentSupervisor dispatches to typed agent classes when available."""

    def _make_supervisor(self, response_text="reply"):
        from providers.llm_provider import LLMProvider
        from services.agent_service import AgentService
        from control.agent_supervisor import AgentSupervisor

        class StubLLM(LLMProvider):
            async def chat(self, prompt, *, context=None):
                return {
                    "success": True,
                    "data": {"text": response_text},
                    "error": None,
                }

        svc = AgentService(StubLLM())
        return AgentSupervisor(agent_service=svc)

    def test_agent_class_map_loaded(self):
        sup = self._make_supervisor()
        self.assertIsInstance(sup._agent_classes, dict)
        self.assertGreater(len(sup._agent_classes), 0)

    def test_run_pipeline_returns_responses(self):
        sup = self._make_supervisor("ok")
        responses = asyncio.run(sup.run_pipeline("build something"))
        self.assertIsInstance(responses, list)
        self.assertGreater(len(responses), 0)


if __name__ == "__main__":
    unittest.main()
