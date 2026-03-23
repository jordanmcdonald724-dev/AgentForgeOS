import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from engine.server import create_app


class PreflightGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app()
        self.client = TestClient(self.app)
        self.base_path = Path(getattr(self.app.state, "base_path", "")).resolve()
        self.resources_dir = self.base_path / "resources"
        self.providers_path = self.resources_dir / "providers.json"
        self._providers_backup = self.providers_path.read_text(encoding="utf-8") if self.providers_path.exists() else None

    def tearDown(self) -> None:
        try:
            self.client.close()
        except Exception:
            pass
        if self._providers_backup is not None:
            self.providers_path.write_text(self._providers_backup, encoding="utf-8")

    def test_preflight_blocks_workspace_inside_install_dir(self) -> None:
        self.app.state.workspace_path = str(self.base_path)
        resp = self.client.get("/api/system/preflight")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body["success"])
        data = body["data"]
        self.assertFalse(data["ok"])
        self.assertTrue(any(b["code"] == "workspace.unsafe" for b in data["blockers"]))

    def test_pipeline_start_blocked_when_fal_selected_missing_key(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        self.app.state.workspace_path = str(tmp)
        self.app.state.config = {"providers": {"llm": "fal"}}
        self.providers_path.write_text("{}", encoding="utf-8")
        os.environ.pop("FAL_API_KEY", None)

        with patch("engine.security.preflight.load_engine_config_user_override", return_value={}):
            resp = self.client.post("/api/pipeline/start", json={"prompt": "hi"})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertFalse(body["success"])
        self.assertEqual(body["error"], "Preflight failed")
        self.assertIn("preflight", body["data"])
        self.assertFalse(body["data"]["preflight"]["ok"])

    def test_pipeline_start_allowed_with_fal_key(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        self.app.state.workspace_path = str(tmp)
        self.app.state.config = {"providers": {"llm": "fal"}}
        self.providers_path.write_text('{"fal":{"api_key":"x","model":"m"}}', encoding="utf-8")
        with patch("engine.security.preflight.load_engine_config_user_override", return_value={}), patch("agents.pipeline.run", new=AsyncMock(return_value=[])):
            resp = self.client.post("/api/pipeline/start", json={"prompt": "hi"})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body["success"])
        self.assertTrue(body["started"])
        self.assertTrue(body["pipeline_id"])


if __name__ == "__main__":
    unittest.main()
