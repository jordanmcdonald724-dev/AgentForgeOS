"""Tests for the control layer scaffolding (monitoring, scoring, recovery, learning)."""

import asyncio
import unittest

from services.agent_pipeline import AGENT_PIPELINE, PipelineContext


class _RecordingMonitor:
    def __init__(self):
        self.started = []
        self.ended = []
        self.errors = []

    def start_step(self, step, context=None):
        self.started.append(step)

    def end_step(self, step, result):
        self.ended.append(step)

    def record_error(self, step, error):
        self.errors.append((step, error))


class _RecoverySpy:
    def __init__(self):
        self.called = False

    def recover(self, step, response, context, *, attempt=1):
        self.called = True
        # ``attempt`` represents the recovery retry count (mirrors production signature).
        recovered = dict(response)
        recovered.setdefault("metadata", {})["recovery_attempted"] = True
        return recovered


class _ScoringSpy:
    def __init__(self):
        self.scored = []

    def score(self, step, result, context=None):
        self.scored.append(step)
        return {"quality": 1.0, "correctness": 1.0, "speed": 1.0, "stability": 1.0}


class ControlLayerTests(unittest.TestCase):
    def _make_supervisor(self, monitor=None, recovery=None, scorer=None):
        from providers.llm_provider import LLMProvider
        from services.agent_service import AgentService
        from control.agent_supervisor import AgentSupervisor

        class StubLLM(LLMProvider):
            async def chat(self, prompt, *, context=None):
                return {"success": True, "data": {"text": "ok"}, "error": None}

        svc = AgentService(StubLLM())
        return AgentSupervisor(
            agent_service=svc,
            monitor=monitor,
            recovery=recovery,
            scorer=scorer,
        )

    def test_monitor_tracks_all_steps(self):
        monitor = _RecordingMonitor()
        sup = self._make_supervisor(monitor=monitor)
        responses = asyncio.run(sup.run_pipeline("test request"))
        self.assertEqual(len(responses), len(AGENT_PIPELINE))
        self.assertEqual(len(monitor.started), len(AGENT_PIPELINE))
        self.assertEqual(len(monitor.ended), len(AGENT_PIPELINE))

    def test_recovery_invoked_on_failure(self):
        recovery = _RecoverySpy()
        sup = self._make_supervisor(recovery=recovery)

        from agents.base_agent import BaseAgent

        class FailingAgent(BaseAgent):
            role = "Project Planner"

            async def run(self, prompt, *, context=None):
                raise RuntimeError("boom")

        sup._agent_classes["Project Planner"] = FailingAgent

        responses = asyncio.run(sup.run_pipeline("test request"))
        self.assertTrue(recovery.called)
        self.assertEqual(len(responses), len(AGENT_PIPELINE))
        self.assertTrue(
            responses[0].get("metadata", {}).get("recovery_attempted", False)
        )

    def test_learning_hooks_store_scores(self):
        scorer = _ScoringSpy()
        sup = self._make_supervisor(scorer=scorer)
        ctx = PipelineContext()
        asyncio.run(sup.run_pipeline("test request", context=ctx))
        self.assertEqual(len(scorer.scored), len(AGENT_PIPELINE))
        self.assertIn("last_scores", ctx.data)
        self.assertIsInstance(ctx.get("last_scores"), dict)


if __name__ == "__main__":
    unittest.main()
