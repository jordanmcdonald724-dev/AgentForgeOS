import asyncio
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from engine.server import create_app


class V2LoopTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app()
        self.client = TestClient(self.app)
        self.tmpdir = Path(tempfile.mkdtemp())
        self.app.state.workspace_path = str(self.tmpdir)
        self.app.state.config = {"providers": {"llm": "noop"}}

    def tearDown(self) -> None:
        try:
            self.client.close()
        except Exception:
            pass

    def test_loop_run_completes_and_persists(self) -> None:
        with patch("agents.pipeline.run", new=AsyncMock(return_value=[])):
            resp = self.client.post("/api/v2/loop/run", json={"prompt": "build something", "max_iterations": 1})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body["success"])
        data = body["data"]
        loop_id = data["loop_id"]
        self.assertTrue(loop_id)
        self.assertEqual(data["status"], "completed")

        status = self.client.get(f"/api/v2/loop/status?loop_id={loop_id}").json()
        self.assertTrue(status["success"])
        self.assertEqual(status["data"]["status"], "completed")
        self.assertGreaterEqual(len(status["data"]["history"]), 1)

        events = self.client.get(f"/api/pipeline/events?pipeline_id={loop_id}").json()
        self.assertTrue(events["success"])
        self.assertGreaterEqual(len(events["data"]["events"]), 1)

    def test_loop_start_pause_resume_stop(self) -> None:
        gate = asyncio.Event()

        async def fake_run(*args, **kwargs):
            await gate.wait()
            return []

        with patch("agents.pipeline.run", new=fake_run):
            resp = self.client.post("/api/v2/loop/start", json={"prompt": "x", "max_iterations": 1})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body["success"])
        loop_id = body["data"]["loop_id"]

        pause = self.client.post("/api/v2/loop/pause", json={"loop_id": loop_id}).json()
        self.assertTrue(pause["success"])
        resume = self.client.post("/api/v2/loop/resume", json={"loop_id": loop_id}).json()
        self.assertTrue(resume["success"])

        stop = self.client.post("/api/v2/loop/stop", json={"loop_id": loop_id}).json()
        self.assertTrue(stop["success"])
        gate.set()


if __name__ == "__main__":
    unittest.main()

