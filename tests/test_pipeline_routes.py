"""Tests for the pipeline API route.

Validates that ``POST /api/pipeline/run`` correctly invokes the agent pipeline
and returns structured JSON responses for both success and error cases.
"""

import unittest
from unittest.mock import AsyncMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from engine.routes.pipeline import router as pipeline_router


def _build_test_app():
    """Return a minimal FastAPI app with only the pipeline route."""
    app = FastAPI()
    app.include_router(pipeline_router, prefix="/api")
    return app


class PipelineRunSuccessTests(unittest.TestCase):
    """POST /api/pipeline/run returns pipeline results on success."""

    def setUp(self):
        self.client = TestClient(_build_test_app())

    @patch("agents.pipeline.run", new_callable=AsyncMock)
    def test_run_returns_success_with_steps(self, mock_run):
        mock_run.return_value = [{"stage": "planner", "output": "plan"}]
        resp = self.client.post("/api/pipeline/run", json={"prompt": "Build a chat app"})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body["success"])
        self.assertIsInstance(body["steps"], list)
        self.assertEqual(body["steps"][0]["stage"], "planner")

    @patch("agents.pipeline.run", new_callable=AsyncMock)
    def test_run_passes_prompt_to_pipeline(self, mock_run):
        mock_run.return_value = []
        self.client.post("/api/pipeline/run", json={"prompt": "hello world"})
        mock_run.assert_awaited_once_with("hello world")


class PipelineRunValidationTests(unittest.TestCase):
    """Request validation rejects payloads missing the required prompt field."""

    def setUp(self):
        self.client = TestClient(_build_test_app())

    def test_missing_prompt_returns_422(self):
        resp = self.client.post("/api/pipeline/run", json={})
        self.assertEqual(resp.status_code, 422)

    def test_empty_body_returns_422(self):
        resp = self.client.post("/api/pipeline/run", content=b"")
        self.assertEqual(resp.status_code, 422)


class PipelineRunErrorTests(unittest.TestCase):
    """POST /api/pipeline/run returns error JSON when the pipeline fails."""

    def setUp(self):
        self.client = TestClient(_build_test_app())

    @patch("agents.pipeline.run", new_callable=AsyncMock)
    def test_exception_returns_error_json(self, mock_run):
        mock_run.side_effect = RuntimeError("provider down")
        resp = self.client.post("/api/pipeline/run", json={"prompt": "test"})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertFalse(body["success"])
        self.assertIn("provider down", body["error"])


if __name__ == "__main__":
    unittest.main()
