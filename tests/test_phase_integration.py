import asyncio
import os
import unittest


class PhaseIntegrationTests(unittest.TestCase):
    """Lightweight integration checks to prove wiring across phases."""

    def test_engine_health_route(self):
        from fastapi.routing import APIRoute
        from engine.server import create_app

        app = create_app()
        routes = [r for r in app.router.routes if isinstance(r, APIRoute)]
        health_route = next((r for r in routes if r.path == "/api/health"), None)

        self.assertIsNotNone(health_route, "Health route missing on engine app")

        body = asyncio.run(health_route.endpoint())
        self.assertTrue(body.get("success"))
        self.assertEqual(body.get("data", {}).get("status"), "ok")

    def test_core_modules_import_and_run(self):
        from agents import pipeline
        from control import ai_router, agent_supervisor, file_guard
        from knowledge import (
            embedding_service,
            knowledge_graph,
            pattern_extractor,
            project_genome,
            vector_store,
        )
        from providers import llm_provider
        from services.agent_service import AgentService

        class DummyLLM(llm_provider.LLMProvider):
            async def chat(self, prompt: str, *, context=None):
                return {"success": True, "data": {"text": f"echo:{prompt}"}, "error": None}

        agent = AgentService(DummyLLM())
        result = asyncio.run(agent.run_agent("ping"))

        self.assertTrue(result.get("success"))
        self.assertIsInstance(pipeline.AGENT_PIPELINE, list)
        self.assertGreater(len(pipeline.AGENT_PIPELINE), 0)

        # Ensure control and knowledge modules are importable (wiring present)
        self.assertIsNotNone(ai_router)
        self.assertIsNotNone(agent_supervisor)
        self.assertIsNotNone(file_guard)
        self.assertIsNotNone(knowledge_graph)
        self.assertIsNotNone(vector_store)
        self.assertIsNotNone(embedding_service)
        self.assertIsNotNone(pattern_extractor)
        self.assertIsNotNone(project_genome)

    def test_desktop_frontend_artifacts_exist(self):
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        desktop_main = os.path.join(repo_root, "desktop", "src", "main.rs")
        frontend_index = os.path.join(repo_root, "frontend", "index.html")

        self.assertTrue(os.path.isfile(desktop_main), "Desktop runtime entrypoint missing")
        self.assertTrue(os.path.isfile(frontend_index), "Frontend studio scaffold missing")

    def test_agent_service_history_records_interactions(self):
        from providers import llm_provider
        from services.agent_service import AgentService

        class DummyLLM(llm_provider.LLMProvider):
            async def chat(self, prompt: str, *, context=None):
                return {"success": True, "data": {"text": f"echo:{prompt}"}, "error": None}

        agent = AgentService(DummyLLM())
        asyncio.run(agent.run_agent("hello"))
        history = agent.history()

        self.assertGreaterEqual(len(history), 2)
        self.assertEqual(history[0].get("role"), "user")
        self.assertEqual(history[0].get("content"), "hello")
        self.assertEqual(history[1].get("role"), "assistant")
        self.assertIn("echo:hello", history[1].get("content"))


if __name__ == "__main__":
    unittest.main()
