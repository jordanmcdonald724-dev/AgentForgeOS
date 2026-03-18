"""Tests for the pipeline wiring repair: agent registry, pipeline context,
and supervisor fault-tolerance."""

import asyncio
import unittest

from services.agent_pipeline import AGENT_PIPELINE


class AgentRegistryTests(unittest.TestCase):
    """AGENT_REGISTRY in services/agent_registry.py must cover all pipeline roles."""

    def test_registry_is_importable(self):
        from services.agent_registry import AGENT_REGISTRY

        self.assertIsInstance(AGENT_REGISTRY, dict)

    def test_registry_covers_all_pipeline_roles(self):
        from services.agent_registry import AGENT_REGISTRY

        for role in AGENT_PIPELINE:
            self.assertIn(
                role,
                AGENT_REGISTRY,
                f"AGENT_REGISTRY missing entry for pipeline role '{role}'",
            )

    def test_registry_classes_are_instantiable(self):
        from services.agent_registry import AGENT_REGISTRY

        for role, cls in AGENT_REGISTRY.items():
            instance = cls()
            self.assertIsNotNone(instance, f"Could not instantiate {cls.__name__}")

    def test_registry_exported_from_services_package(self):
        from services import AGENT_REGISTRY

        self.assertIsInstance(AGENT_REGISTRY, dict)
        self.assertGreater(len(AGENT_REGISTRY), 0)

    def test_registry_role_attributes_match(self):
        from services.agent_registry import AGENT_REGISTRY

        for expected_role, cls in AGENT_REGISTRY.items():
            self.assertEqual(
                cls.role,
                expected_role,
                f"{cls.__name__}.role is '{cls.role}', expected '{expected_role}'",
            )


class PipelineContextTests(unittest.TestCase):
    """PipelineContext passes data between pipeline stages."""

    def test_set_and_get(self):
        from services.agent_pipeline import PipelineContext

        ctx = PipelineContext()
        ctx.set("plan", "step 1, step 2")
        self.assertEqual(ctx.get("plan"), "step 1, step 2")

    def test_get_missing_key_returns_none(self):
        from services.agent_pipeline import PipelineContext

        ctx = PipelineContext()
        self.assertIsNone(ctx.get("nonexistent"))

    def test_get_missing_key_with_default(self):
        from services.agent_pipeline import PipelineContext

        ctx = PipelineContext()
        self.assertEqual(ctx.get("missing", "fallback"), "fallback")

    def test_data_dict_accessible(self):
        from services.agent_pipeline import PipelineContext

        ctx = PipelineContext()
        ctx.set("x", 42)
        self.assertIn("x", ctx.data)
        self.assertEqual(ctx.data["x"], 42)

    def test_multiple_values_stored_independently(self):
        from services.agent_pipeline import PipelineContext

        ctx = PipelineContext()
        ctx.set("a", 1)
        ctx.set("b", 2)
        self.assertEqual(ctx.get("a"), 1)
        self.assertEqual(ctx.get("b"), 2)

    def test_exported_from_services_package(self):
        from services import PipelineContext

        ctx = PipelineContext()
        ctx.set("k", "v")
        self.assertEqual(ctx.get("k"), "v")


class SupervisorRegistryWiringTests(unittest.TestCase):
    """AgentSupervisor loads classes from AGENT_REGISTRY."""

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

    def test_agent_classes_loaded_from_registry(self):
        from services.agent_registry import AGENT_REGISTRY

        sup = self._make_supervisor()
        # Every key in AGENT_REGISTRY must appear in the supervisor's class map.
        for role in AGENT_REGISTRY:
            self.assertIn(role, sup._agent_classes, f"Missing role '{role}' in supervisor")

    def test_run_pipeline_completes_all_stages(self):
        sup = self._make_supervisor("ok")
        responses = asyncio.run(sup.run_pipeline("build something"))
        self.assertEqual(len(responses), len(AGENT_PIPELINE))

    def test_context_dict_passed_to_pipeline(self):
        sup = self._make_supervisor("ok")
        responses = asyncio.run(
            sup.run_pipeline("build something", context={"seed": "initial"})
        )
        self.assertIsInstance(responses, list)
        self.assertGreater(len(responses), 0)

    def test_pipeline_context_object_accepted(self):
        from services.agent_pipeline import PipelineContext

        sup = self._make_supervisor("ok")
        ctx = PipelineContext()
        ctx.set("seed", "value")
        responses = asyncio.run(sup.run_pipeline("build something", context=ctx))
        self.assertIsInstance(responses, list)
        self.assertGreater(len(responses), 0)


class SupervisorFaultToleranceTests(unittest.TestCase):
    """Pipeline continues after an agent raises an exception."""

    def _make_supervisor_with_failing_agent(self, fail_role="Project Planner"):
        """Create a supervisor where one agent class raises on run()."""
        from providers.llm_provider import LLMProvider
        from services.agent_service import AgentService
        from control.agent_supervisor import AgentSupervisor
        from agents.base_agent import BaseAgent

        class BombAgent(BaseAgent):
            role = fail_role

            async def run(self, prompt, *, context=None):
                raise RuntimeError("intentional test failure")

        class StubLLM(LLMProvider):
            async def chat(self, prompt, *, context=None):
                return {"success": True, "data": {"text": "ok"}, "error": None}

        svc = AgentService(StubLLM())
        sup = AgentSupervisor(agent_service=svc)
        # Inject the failing class for the target role only.
        sup._agent_classes[fail_role] = BombAgent
        return sup

    def test_pipeline_continues_after_exception(self):
        """All 12 responses are returned even when one agent raises."""
        sup = self._make_supervisor_with_failing_agent("Project Planner")
        responses = asyncio.run(sup.run_pipeline("test request"))
        # Pipeline must not freeze — all stages should produce a response.
        self.assertEqual(len(responses), len(AGENT_PIPELINE))

    def test_failed_agent_response_has_error(self):
        sup = self._make_supervisor_with_failing_agent("Task Router")
        responses = asyncio.run(sup.run_pipeline("test request"))
        router_idx = AGENT_PIPELINE.index("Task Router")
        failed = responses[router_idx]
        self.assertFalse(failed["success"])
        self.assertIsNotNone(failed["error"])

    def test_subsequent_agents_still_run(self):
        """Agents after the failing one must still execute successfully."""
        sup = self._make_supervisor_with_failing_agent("Project Planner")
        responses = asyncio.run(sup.run_pipeline("test request"))
        # System Architect runs after Project Planner and should succeed.
        arch_idx = AGENT_PIPELINE.index("System Architect")
        self.assertTrue(responses[arch_idx]["success"])


if __name__ == "__main__":
    unittest.main()
