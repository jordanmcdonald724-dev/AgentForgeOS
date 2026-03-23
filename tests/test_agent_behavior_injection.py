import unittest
from unittest.mock import patch


class AgentBehaviorInjectionTests(unittest.TestCase):
    def test_agent_factory_overrides_system_prompt_when_spec_exists(self):
        from control.agent_factory import AgentFactory
        from services.agent_service import AgentService
        from agents.strategic.planner_agent import PlannerAgent

        factory = AgentFactory()
        svc = AgentService()

        with patch("control.agent_factory.load_agent_system_prompt", return_value="OVERRIDE_PROMPT"):
            agent = factory.create(PlannerAgent, svc)
            self.assertEqual(agent.system_prompt, "OVERRIDE_PROMPT")

    def test_task_router_spec_is_loadable(self):
        from services.agent_behavior import load_agent_spec_by_role, load_agent_system_prompt

        spec = load_agent_spec_by_role("Task Router")
        self.assertEqual(spec.get("agent_id"), "task_router")
        prompt = load_agent_system_prompt("Task Router")
        self.assertIn("Task Router AI", prompt)

    def test_backend_engineer_spec_is_loadable(self):
        from services.agent_behavior import load_agent_spec_by_role, load_agent_system_prompt

        spec = load_agent_spec_by_role("Backend Engineer")
        self.assertEqual(spec.get("agent_id"), "backend_engineer")
        prompt = load_agent_system_prompt("Backend Engineer")
        self.assertIn("Backend Engineer", prompt)

    def test_game_engine_engineer_spec_is_loadable(self):
        from services.agent_behavior import load_agent_spec_by_role, load_agent_system_prompt

        spec = load_agent_spec_by_role("Game Engine Engineer")
        self.assertEqual(spec.get("agent_id"), "game_engine_engineer")
        prompt = load_agent_system_prompt("Game Engine Engineer")
        self.assertIn("Game Engine Engineer", prompt)

    def test_frontend_engineer_spec_is_loadable(self):
        from services.agent_behavior import load_agent_spec_by_role, load_agent_system_prompt

        spec = load_agent_spec_by_role("Frontend Engineer")
        self.assertEqual(spec.get("agent_id"), "frontend_engineer")
        prompt = load_agent_system_prompt("Frontend Engineer")
        self.assertIn("Frontend Engineer", prompt)

    def test_database_engineer_spec_is_loadable(self):
        from services.agent_behavior import load_agent_spec_by_role, load_agent_system_prompt

        spec = load_agent_spec_by_role("Data Architect")
        self.assertEqual(spec.get("agent_id"), "database_engineer")
        prompt = load_agent_system_prompt("Data Architect")
        self.assertIn("Database Engineer", prompt)

    def test_ai_engineer_spec_is_loadable(self):
        from services.agent_behavior import load_agent_spec_by_role, load_agent_system_prompt

        spec = load_agent_spec_by_role("AI Integration Engineer")
        self.assertEqual(spec.get("agent_id"), "ai_engineer")
        prompt = load_agent_system_prompt("AI Integration Engineer")
        self.assertIn("AI Engineer", prompt)

    def test_asset_generator_spec_is_loadable(self):
        from services.agent_behavior import load_agent_spec_by_role, load_agent_system_prompt

        spec = load_agent_spec_by_role("Asset Generator")
        self.assertEqual(spec.get("agent_id"), "asset_generator")
        prompt = load_agent_system_prompt("Asset Generator")
        self.assertIn("Asset Generator", prompt)

    def test_devops_engineer_spec_is_loadable(self):
        from services.agent_behavior import load_agent_spec_by_role, load_agent_system_prompt

        spec = load_agent_spec_by_role("DevOps Engineer")
        self.assertEqual(spec.get("agent_id"), "devops_engineer")
        prompt = load_agent_system_prompt("DevOps Engineer")
        self.assertIn("DevOps Engineer", prompt)

    def test_review_agent_spec_is_loadable(self):
        from services.agent_behavior import load_agent_spec_by_role, load_agent_system_prompt

        spec = load_agent_spec_by_role("Integration Tester")
        self.assertEqual(spec.get("agent_id"), "review_agent")
        prompt = load_agent_system_prompt("Integration Tester")
        self.assertIn("Review Agent", prompt)

    def test_refactor_agent_spec_is_loadable(self):
        from services.agent_behavior import load_agent_spec_by_role, load_agent_system_prompt

        spec = load_agent_spec_by_role("System Stabilizer")
        self.assertEqual(spec.get("agent_id"), "refactor_agent")
        prompt = load_agent_system_prompt("System Stabilizer")
        self.assertIn("Refactor Agent", prompt)

    def test_learning_agent_spec_is_loadable(self):
        from services.agent_behavior import load_agent_spec_by_role, load_agent_system_prompt

        spec = load_agent_spec_by_role("Learning Agent")
        self.assertEqual(spec.get("agent_id"), "learning_agent")
        prompt = load_agent_system_prompt("Learning Agent")
        self.assertIn("Learning Agent", prompt)


if __name__ == "__main__":
    unittest.main()
