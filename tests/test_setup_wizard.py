"""Tests for the /api/setup wizard routes.

Uses FastAPI's TestClient to exercise the three setup endpoints without
requiring a running server or a real MongoDB instance.
"""

import os
import json
import tempfile
import unittest
import sys
from pathlib import Path
from typing import Any, cast
from unittest.mock import AsyncMock, patch

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
        if hasattr(self, "client"):
            try:
                self.client.close()
            except Exception:
                pass
        # Restore original .env if it existed; otherwise remove test file
        if self._original_exists:
            self.env_path.write_text(self._original_text, encoding="utf-8")
        elif self.env_path.exists():
            self.env_path.unlink()
        # Clean up env vars injected during test
        for key in ("SETUP_COMPLETE", "OPENAI_API_KEY", "PROVIDER_LLM", "FAL_API_KEY", "FAL_LLM_MODEL"):
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

    def test_save_config_sets_session_cookie_when_token_present(self):
        os.environ["AGENTFORGE_BRIDGE_TOKEN"] = "testtoken"
        resp = self.client.post("/api/setup/save", json={"config": {"PROVIDER_LLM": "ollama"}})
        self.assertEqual(resp.status_code, 200)
        set_cookie = resp.headers.get("set-cookie", "")
        self.assertIn("agentforge_session=", set_cookie)

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

    def test_wizard_e2e_save_sets_cookie_and_enables_bridge(self):
        try:
            from fastapi.testclient import TestClient
            from engine.server import create_app
        except Exception as exc:
            self.skipTest(str(exc))
            return

        os.environ["AGENTFORGE_BRIDGE_TOKEN"] = "testtoken"
        tmpdir = tempfile.mkdtemp()
        os.environ["BRIDGE_ROOT"] = tmpdir

        app = create_app()
        with TestClient(app) as client:
            app_state = cast(Any, client.app).state
            base_path = Path(getattr(app_state, "base_path", ""))
            resources_dir = base_path / "resources"
            config_path = resources_dir / "config.json"
            providers_path = resources_dir / "providers.json"

            config_backup = config_path.read_text(encoding="utf-8") if config_path.exists() else None
            providers_backup = providers_path.read_text(encoding="utf-8") if providers_path.exists() else None
            try:
                resp = client.get("/wizard.html")
                self.assertEqual(resp.status_code, 200)
                self.assertTrue("/setup/save" in resp.text or "setup/save" in resp.text)

                client.post("/api/setup/reset")
                resp = client.get("/api/setup")
                self.assertEqual(resp.status_code, 200)
                self.assertFalse(resp.json()["data"]["setup_complete"])

                resp = client.post("/api/bridge/create_file", json={"path": "hello.txt", "content": "hi"})
                self.assertEqual(resp.status_code, 200)
                self.assertFalse(resp.json()["success"])

                ws_path = str(Path(tmpdir) / "workspace")
                payload = {
                    "config": {
                        "WORKSPACE_PATH": ws_path,
                        "PROVIDER_LLM": "noop",
                        "OPENAI_API_KEY": "wizard_secret",
                        "OPENAI_MODEL": "gpt-4.1",
                    }
                }
                resp = client.post("/api/setup/save", json=payload)
                self.assertEqual(resp.status_code, 200)
                self.assertTrue(resp.json()["success"])
                set_cookie = resp.headers.get("set-cookie", "")
                self.assertIn("agentforge_session=", set_cookie)

                resp = client.post("/api/bridge/create_file", json={"path": "hello.txt", "content": "hi"})
                self.assertEqual(resp.status_code, 200)
                self.assertTrue(resp.json()["success"])
                self.assertTrue((Path(tmpdir) / "hello.txt").is_file())

                resp = client.get("/api/setup")
                self.assertEqual(resp.status_code, 200)
                self.assertTrue(resp.json()["data"]["setup_complete"])

                self.assertTrue(config_path.is_file())
                config = json.loads(config_path.read_text(encoding="utf-8"))
                self.assertEqual(config.get("workspace_path"), ws_path)
                self.assertEqual(config.get("providers", {}).get("llm"), "noop")

                self.assertTrue(providers_path.is_file())
                providers = json.loads(providers_path.read_text(encoding="utf-8"))
                self.assertEqual(providers.get("openai", {}).get("api_key"), "wizard_secret")
                self.assertEqual(providers.get("openai", {}).get("model"), "gpt-4.1")
            finally:
                if config_backup is not None:
                    config_path.write_text(config_backup, encoding="utf-8")
                elif config_path.exists():
                    config_path.unlink()
                if providers_backup is not None:
                    providers_path.write_text(providers_backup, encoding="utf-8")
                elif providers_path.exists():
                    providers_path.unlink()
                os.environ.pop("BRIDGE_ROOT", None)

    def test_save_config_overwrites_env_and_updates_providers_test(self):
        try:
            from fastapi.testclient import TestClient
            from engine.server import create_app
        except Exception as exc:
            self.skipTest(str(exc))
            return

        os.environ["FAL_API_KEY"] = "old_key"
        app = create_app()
        with TestClient(app) as client:
            app_state = cast(Any, client.app).state
            base_path = Path(getattr(app_state, "base_path", ""))
            resources_dir = base_path / "resources"
            config_path = resources_dir / "config.json"
            providers_path = resources_dir / "providers.json"
            config_backup = config_path.read_text(encoding="utf-8") if config_path.exists() else None
            providers_backup = providers_path.read_text(encoding="utf-8") if providers_path.exists() else None
            try:
                payload = {
                    "config": {
                        "PROVIDER_LLM": "fal",
                        "FAL_API_KEY": "new_key",
                        "FAL_LLM_MODEL": "fal-ai/llama3.1-8b-instruct",
                    }
                }
                resp = client.post("/api/setup/save", json=payload)
                self.assertEqual(resp.status_code, 200)
                self.assertTrue(resp.json()["success"])

                self.assertEqual(os.environ.get("FAL_API_KEY"), "new_key")

                with patch(
                    "providers.fal_llm_provider.FalLLMProvider.chat",
                    new=AsyncMock(return_value={"success": True, "data": {"text": "ok"}, "error": None}),
                ):
                    test_resp = client.get("/api/providers/test?type=llm")
                    self.assertEqual(test_resp.status_code, 200)
                    body = test_resp.json()
                    self.assertTrue(body["success"])
                    self.assertTrue(body["data"]["results"]["llm"]["ok"])

                with patch(
                    "providers.fal_llm_provider.FalLLMProvider.chat",
                    new=AsyncMock(return_value={"success": True, "data": {"text": "ok"}, "error": None}),
                ):
                    run_resp = client.post("/api/agent/run", json={"prompt": "hi"})
                    self.assertEqual(run_resp.status_code, 200)
                    run_body = run_resp.json()
                    self.assertTrue(run_body["success"])
                    self.assertEqual(run_body["data"]["data"]["text"], "ok")
            finally:
                if config_backup is not None:
                    config_path.write_text(config_backup, encoding="utf-8")
                elif config_path.exists():
                    config_path.unlink()
                if providers_backup is not None:
                    providers_path.write_text(providers_backup, encoding="utf-8")
                elif providers_path.exists():
                    providers_path.unlink()

    def test_setup_test_endpoint_validates_fal_and_mongo(self):
        try:
            from fastapi.testclient import TestClient
            from engine.server import create_app
        except Exception as exc:
            self.skipTest(str(exc))
            return

        app = create_app()
        with TestClient(app) as client:
            with patch(
                "providers.fal_llm_provider.FalLLMProvider.chat",
                new=AsyncMock(return_value={"success": True, "data": {"text": "ok"}, "error": None}),
            ):
                resp = client.post(
                    "/api/setup/test?type=llm",
                    json={"config": {"PROVIDER_LLM": "fal", "FAL_API_KEY": "x"}},
                )
                self.assertEqual(resp.status_code, 200)
                body = resp.json()
                self.assertTrue(body["success"])
                self.assertTrue(body["data"]["results"]["llm"]["ok"])

            resp2 = client.post(
                "/api/setup/test?type=mongo",
                json={"config": {"AGENTFORGE_MONGO_URI": "mongodb://localhost:27017"}},
            )
            self.assertEqual(resp2.status_code, 200)
            body2 = resp2.json()
            self.assertTrue(body2["success"])
            self.assertIn("mongo", body2["data"]["results"])

    def test_frozen_resources_root_handles_nested_resources_folder(self):
        try:
            from fastapi.testclient import TestClient
            from engine.server import create_app
        except Exception as exc:
            self.skipTest(str(exc))
            return

        tmpdir = Path(tempfile.mkdtemp())
        exe_base = tmpdir / "resources"
        exe_base.mkdir(parents=True, exist_ok=True)
        nested = exe_base / "resources"
        nested.mkdir(parents=True, exist_ok=True)
        (nested / "config.json").write_text(json.dumps({"workspace_path": str(tmpdir / "ws")}), encoding="utf-8")
        (nested / "providers.json").write_text("{}", encoding="utf-8")
        fake_exe = exe_base / "backend.exe"
        fake_exe.write_text("", encoding="utf-8")

        with patch.object(os, "environ", dict(os.environ)), patch.object(sys, "frozen", True, create=True), patch.object(sys, "executable", str(fake_exe), create=True):
            app = create_app()
            with TestClient(app) as client:
                app_state = cast(Any, client.app).state
                self.assertEqual(Path(app_state.base_path), exe_base)
                self.assertEqual(app_state.config.get("workspace_path"), str(tmpdir / "ws"))
if __name__ == "__main__":
    unittest.main()
    unittest.main()
    unittest.main()
