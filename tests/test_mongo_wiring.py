"""Tests for MongoDB memory wiring into AgentService.

These tests exercise ``AgentService`` with a ``MongoMemoryManager`` but
without a real database connection.  ``MongoMemoryManager`` is designed to
fall back gracefully to its in-memory ``_local`` list when MongoDB is
unavailable, so all assertions below work without a running MongoDB server.
"""

import asyncio
import unittest

from services.agent_service import AgentService
from services.mongo_memory import MongoMemoryManager
from services.memory_manager import MemoryManager
from providers.llm_provider import LLMProvider


class _EchoLLMProvider(LLMProvider):
    """Synchronous echo stub — returns the prompt as the response text."""

    async def chat(self, prompt: str, *, context=None):
        return {"success": True, "data": {"text": f"echo:{prompt}"}, "error": None}


class AgentServiceWithMongoMemoryTests(unittest.TestCase):
    """AgentService works correctly when given a MongoMemoryManager."""

    def _make_service(self, session_id: str = "test-session") -> AgentService:
        memory = MongoMemoryManager(db=None, session_id=session_id)
        return AgentService(llm_provider=_EchoLLMProvider(), memory_manager=memory)

    def test_accepts_mongo_memory_manager(self):
        service = self._make_service()
        self.assertIsInstance(service.memory, MongoMemoryManager)

    def test_run_agent_records_turns_in_local_cache(self):
        service = self._make_service()
        asyncio.run(service.run_agent("hello"))

        history = service.history()
        self.assertGreaterEqual(len(history), 2)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[0]["content"], "hello")
        self.assertEqual(history[1]["role"], "assistant")
        self.assertIn("echo:hello", history[1]["content"])

    def test_history_limit_respected(self):
        service = self._make_service()
        asyncio.run(service.run_agent("first"))
        asyncio.run(service.run_agent("second"))

        # 4 entries total (2 user + 2 assistant); limit=2 returns last 2
        limited = service.history(limit=2)
        self.assertEqual(len(limited), 2)

    def test_history_does_not_leak_session_id_field(self):
        service = self._make_service()
        asyncio.run(service.run_agent("leak check"))

        for entry in service.history():
            self.assertNotIn("session_id", entry, "session_id must not appear in history")

    def test_history_is_session_scoped(self):
        """Histories from different sessions must not bleed into each other."""
        svc_a = self._make_service(session_id="session-A")
        svc_b = self._make_service(session_id="session-B")

        asyncio.run(svc_a.run_agent("ping-A"))
        asyncio.run(svc_b.run_agent("ping-B"))

        hist_a = svc_a.history()
        hist_b = svc_b.history()
        # Each session should see its own turns only
        contents_a = [e["content"] for e in hist_a]
        contents_b = [e["content"] for e in hist_b]
        self.assertTrue(any("ping-A" in c for c in contents_a))
        self.assertTrue(any("ping-B" in c for c in contents_b))
        self.assertFalse(any("ping-B" in c for c in contents_a))
        self.assertFalse(any("ping-A" in c for c in contents_b))

    def test_failed_llm_response_not_added_to_history(self):
        class FailingLLM(LLMProvider):
            async def chat(self, prompt, *, context=None):
                return {"success": False, "data": None, "error": "timeout"}

        memory = MongoMemoryManager(db=None, session_id="fail-session")
        service = AgentService(llm_provider=FailingLLM(), memory_manager=memory)
        asyncio.run(service.run_agent("will fail"))

        history = service.history()
        # User turn must be recorded, but no assistant turn
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["role"], "user")


class AgentServiceBackwardCompatibilityTests(unittest.TestCase):
    """AgentService still works with the original in-memory MemoryManager."""

    def test_default_memory_is_memory_manager(self):
        service = AgentService()
        self.assertIsInstance(service.memory, MemoryManager)

    def test_history_with_memory_manager(self):
        service = AgentService(llm_provider=_EchoLLMProvider())
        asyncio.run(service.run_agent("hello"))
        history = service.history()
        self.assertGreaterEqual(len(history), 2)
        self.assertEqual(history[0]["role"], "user")

    def test_history_limit_with_memory_manager(self):
        service = AgentService(llm_provider=_EchoLLMProvider())
        asyncio.run(service.run_agent("one"))
        asyncio.run(service.run_agent("two"))
        self.assertEqual(len(service.history(limit=1)), 1)


class MongoMemoryManagerNoDbTests(unittest.TestCase):
    """MongoMemoryManager falls back gracefully when no DB is provided."""

    def test_save_and_load_without_db(self):
        mgr = MongoMemoryManager(db=None, session_id="s1")
        asyncio.run(mgr.save_memory({"role": "user", "content": "hi"}))
        entries = asyncio.run(mgr.load_memories())
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["content"], "hi")

    def test_clear_without_db(self):
        mgr = MongoMemoryManager(db=None, session_id="s2")
        asyncio.run(mgr.save_memory({"role": "user", "content": "data"}))
        asyncio.run(mgr.clear())
        self.assertEqual(asyncio.run(mgr.load_memories()), [])

    def test_load_limit_respected(self):
        mgr = MongoMemoryManager(db=None, session_id="s3")
        for i in range(5):
            asyncio.run(mgr.save_memory({"role": "user", "content": str(i)}))
        entries = asyncio.run(mgr.load_memories(limit=3))
        self.assertEqual(len(entries), 3)


class AgentRouteMemoryWiringTests(unittest.TestCase):
    """_build_memory_manager in engine/routes/agent.py returns a MongoMemoryManager."""

    def test_build_memory_manager_returns_mongo_instance(self):
        from engine.routes.agent import _build_memory_manager

        mgr = _build_memory_manager("my-session")
        self.assertIsInstance(mgr, MongoMemoryManager)
        self.assertEqual(mgr.session_id, "my-session")

    def test_agent_run_request_accepts_session_id(self):
        from engine.routes.agent import AgentRunRequest

        req = AgentRunRequest(prompt="hello", session_id="abc-123")
        self.assertEqual(req.session_id, "abc-123")

    def test_agent_run_request_session_id_defaults_none(self):
        from engine.routes.agent import AgentRunRequest

        req = AgentRunRequest(prompt="hello")
        self.assertIsNone(req.session_id)


if __name__ == "__main__":
    unittest.main()
