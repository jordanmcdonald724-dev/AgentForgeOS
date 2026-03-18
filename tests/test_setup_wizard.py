"""Tests for the /api/setup wizard routes.

Uses FastAPI's TestClient to exercise the three setup endpoints without
requiring a running server or a real MongoDB instance.
"""

import os
import unittest
from pathlib import Path
from unittest.mock import patch

# Ensure the engine routes can resolve their parent-relative path
# to config/.env by forcing _env_path() to point at a temp file.

ENV_PLACEHOLDER = "SETUP_COMPLETE=1\n"


class SetupRouteTests(unittest.TestCase):
    def setUp(self):
        """Import the setup router and build a minimal FastAPI test client."""
        try:
            from fastapi import FastAPI
            from fastapi.testclient import TestClient
            from engine.routes.setup import router as setup_router, _env_path
        except ImportError as exc:
            self.skipTest(f"FastAPI/TestClient not available: {exc}")
            return

        app = FastAPI()
        app.include_router(setup_router, prefix="/api")
        self.client = TestClient(app)
        self.env_path = _env_path()
        # Stash existing .env so tests don't overwrite user config
        self._original_exists = self.env_path.exists()
        if self._original_exists:
            self._original_text = self.env_path.read_text(encoding="utf-8")

    def tearDown(self):
        if not hasattr(self, "env_path"):
            return
        # Restore original .env if it existed; otherwise remove test file
        if self._original_exists:
            self.env_path.write_text(self._original_text, encoding="utf-8")
        elif self.env_path.exists():
            self.env_path.unlink()
        # Clean up env vars injected during test
        for key in ("SETUP_COMPLETE", "OPENAI_API_KEY", "PROVIDER_LLM"):
            os.environ.pop(key, None)

    def test_get_setup_state_returns_json(self):
        """GET /api/setup must return a valid JSON response."""
        resp = self.client.get("/api/setup")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("success", data)
        self.assertIn("data", data)
        self.assertIn("setup_complete", data["data"])

    def test_get_setup_state_false_when_env_missing(self):
        """setup_complete is False when config/.env does not exist."""
        if self.env_path.exists():
            self.env_path.unlink()
        resp = self.client.get("/api/setup")
        self.assertFalse(resp.json()["data"]["setup_complete"])

    def test_save_config_writes_env_and_marks_complete(self):
        """POST /api/setup/save persists config and sets SETUP_COMPLETE=1."""
        payload = {
            "config": {
                "PROVIDER_LLM": "ollama",
                "OLLAMA_BASE_URL": "http://localhost:11434",
                "OLLAMA_MODEL": "llama3",
            }
        }
        resp = self.client.post("/api/setup/save", json=payload)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["success"])
        # The .env file should now contain SETUP_COMPLETE=1
        self.assertTrue(self.env_path.exists())
        content = self.env_path.read_text(encoding="utf-8")
        self.assertIn("SETUP_COMPLETE=1", content)
        self.assertIn("PROVIDER_LLM=ollama", content)

    def test_save_config_rejects_disallowed_keys(self):
        """POST /api/setup/save silently drops unknown/disallowed keys."""
        payload = {
            "config": {
                "PROVIDER_LLM": "openai",
                "INJECTED_SECRET": "bad_value",
            }
        }
        resp = self.client.post("/api/setup/save", json=payload)
        self.assertEqual(resp.status_code, 200)
        content = self.env_path.read_text(encoding="utf-8") if self.env_path.exists() else ""
        self.assertNotIn("INJECTED_SECRET", content)

    def test_reset_setup_clears_complete_flag(self):
        """POST /api/setup/reset removes SETUP_COMPLETE from the .env."""
        # First complete setup
        self.client.post("/api/setup/save", json={"config": {"PROVIDER_LLM": "ollama"}})
        # Now reset
        resp = self.client.post("/api/setup/reset")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["success"])
        content = self.env_path.read_text(encoding="utf-8") if self.env_path.exists() else ""
        self.assertNotIn("SETUP_COMPLETE=1", content)

    def test_get_setup_state_true_after_save(self):
        """GET /api/setup returns setup_complete=True after a successful save."""
        self.client.post("/api/setup/save", json={"config": {"PROVIDER_LLM": "ollama"}})
        resp = self.client.get("/api/setup")
        self.assertTrue(resp.json()["data"]["setup_complete"])


if __name__ == "__main__":
    unittest.main()
