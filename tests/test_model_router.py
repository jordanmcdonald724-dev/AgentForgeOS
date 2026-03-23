import unittest
from unittest.mock import AsyncMock, patch
from typing import Any, cast


class ModelRouterTests(unittest.IsolatedAsyncioTestCase):
    async def test_agent_service_uses_router_when_configured(self):
        from services.agent_service import AgentService
        from providers.noop_provider import NoOpLLMProvider

        svc = AgentService(llm_provider=NoOpLLMProvider())
        svc.llm_provider.chat = AsyncMock(return_value={"success": True, "data": {"text": "noop"}, "error": None})

        class FakeRouter:
            async def generate(self, task_type, prompt, **kwargs):
                return f"{task_type}:{prompt}"

        svc.model_router = cast(Any, FakeRouter())
        out = await svc.run_agent("hello", task_type="coding")
        self.assertTrue(out["success"])
        self.assertEqual(out["data"]["text"], "coding:hello")
        svc.llm_provider.chat.assert_not_called()

    async def test_model_router_falls_back_on_failure(self):
        from engine.router.model_router import ModelRouter
        from engine.router import config_loader

        router = ModelRouter()

        fake_cfg = {
            "enabled_engines": ["fal", "local"],
            "api_keys": {"fal": "x"},
            "cost_controls": {"max_log_entries": 10},
            "engines": {
                "fal": {"base_url": "https://fal.run", "timeout_sec": 1, "retries": 0, "api_key": "x"},
                "local": {"provider": "ollama", "base_url": "http://localhost:11434", "timeout_sec": 1, "retries": 0},
            },
            "task_routing": {
                "coding": {
                    "engine": "fal",
                    "model": "m1",
                    "fallback": [{"engine": "local", "model": "m2"}],
                }
            },
        }

        async def fal_fail(model, prompt, engine_cfg=None):
            raise RuntimeError("fal down")

        async def local_ok(model, prompt, engine_cfg=None):
            return "ok"

        with patch.object(config_loader, "load_engine_config", return_value=fake_cfg):
            with patch("engine.engines.fal_engine.generate", new=fal_fail):
                with patch("engine.engines.local_engine.generate", new=local_ok):
                    text = await router.generate("coding", "hi")
                    self.assertEqual(text, "ok")


if __name__ == "__main__":
    unittest.main()
