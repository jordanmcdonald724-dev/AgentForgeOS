import unittest
import os
from pathlib import Path
import time
import json
import logging
import tempfile
from typing import Any


class LogsApiTests(unittest.TestCase):
    def _status_field(self, obj: Any) -> str:
        if isinstance(obj, dict):
            return str(obj.get("status") or "")
        getter = getattr(obj, "get", None)
        if callable(getter):
            return str(getter("status") or "")
        try:
            return str(obj["status"])
        except Exception:
            return ""

    def _wait_for_terminal_status(self, fetch: Any, timeout_sec: float = 20.0) -> Any:
        deadline = time.monotonic() + float(timeout_sec)
        last = None
        while time.monotonic() < deadline:
            last = fetch()
            if last and self._status_field(last) in {"completed", "failed"}:
                return last
            time.sleep(0.1)
        return last
    def test_api_logs_endpoint_returns_json(self):
        try:
            from fastapi.testclient import TestClient
        except Exception as exc:
            self.skipTest(str(exc))
            return

        from engine.server import create_app

        with TestClient(create_app()) as client:
            resp = client.get("/api/logs?source=system&limit=10")
            self.assertEqual(resp.status_code, 200)
            payload = resp.json()
            self.assertIn("success", payload)
            self.assertIn("data", payload)
            self.assertIn("entries", payload["data"])

    def test_build_bible_minimal_assets_deploy_and_projects_endpoints(self):
        try:
            from fastapi.testclient import TestClient
        except Exception as exc:
            self.skipTest(str(exc))
            return

        from engine.server import create_app

        os.environ["AGENTFORGE_BRIDGE_TOKEN"] = "testtoken"
        prev_ws = os.environ.get("WORKSPACE_PATH")
        with tempfile.TemporaryDirectory(prefix="agentforge_test_ws_") as ws:
            os.environ["WORKSPACE_PATH"] = ws
            try:
                with TestClient(create_app()) as client:
                    token = os.environ.get("AGENTFORGE_BRIDGE_TOKEN", "")
                    headers = {"X-AgentForge-Token": token} if token else {}
                    app_any = getattr(client, "app", None)
                    state: Any = getattr(app_any, "state", None)
                    base_path = Path(getattr(state, "base_path", "") or "")
                    workspace_path = Path(getattr(state, "workspace_path", "") or "")
                    log_dir = Path((getattr(state, "log_dir", "") or os.environ.get("AGENTFORGE_LOG_DIR", "")) or "")
                    resources_dir = base_path / "resources"
                    config_path = resources_dir / "config.json"
                    providers_path = resources_dir / "providers.json"
                    config_backup = config_path.read_text(encoding="utf-8") if config_path.exists() else None
                    providers_backup = providers_path.read_text(encoding="utf-8") if providers_path.exists() else None
                    if log_dir:
                        expected_logs = ["system.log", "errors.log", "pipeline.log", "agents.log", "deployment.log"]
                        for name in expected_logs:
                            self.assertTrue((log_dir / name).is_file())

                        logging.getLogger().info("test_system_log")
                        logging.getLogger("pipeline").info("test_pipeline_log")
                        logging.getLogger("agents").info("test_agents_log")
                        logging.getLogger("deployment").info("test_deployment_log")
                        time.sleep(0.05)

                        resp = client.get("/api/logs?source=system&limit=200")
                        self.assertEqual(resp.status_code, 200)
                        self.assertTrue(resp.json().get("success"))
                        combined = "\n".join(e.get("message", "") for e in resp.json()["data"]["entries"])
                        self.assertIn("test_system_log", combined)

                        resp = client.get("/api/logs?source=pipeline&limit=200")
                        self.assertEqual(resp.status_code, 200)
                        self.assertTrue(resp.json().get("success"))
                        combined = "\n".join(e.get("message", "") for e in resp.json()["data"]["entries"])
                        self.assertIn("test_pipeline_log", combined)

                        resp = client.get("/api/logs?source=agents&limit=200")
                        self.assertEqual(resp.status_code, 200)
                        self.assertTrue(resp.json().get("success"))
                        combined = "\n".join(e.get("message", "") for e in resp.json()["data"]["entries"])
                        self.assertIn("test_agents_log", combined)

                        resp = client.get("/api/logs?source=deployment&limit=200")
                        self.assertEqual(resp.status_code, 200)
                        self.assertTrue(resp.json().get("success"))
                        combined = "\n".join(e.get("message", "") for e in resp.json()["data"]["entries"])
                        self.assertIn("test_deployment_log", combined)

                    try:
                        alt_workspace = workspace_path / "alt_workspace"
                        alt_workspace.mkdir(parents=True, exist_ok=True)
                        resp = client.post("/api/workspace/set", headers=headers, json={"workspace_path": str(alt_workspace)})
                        self.assertEqual(resp.status_code, 200)
                        self.assertTrue(resp.json().get("success"))
                        workspace_path = Path(resp.json()["data"]["workspace_path"])

                        resp = client.post("/api/providers/config", headers=headers, json={"openai": {"api_key": "secret_key", "model": "gpt-4.1"}})
                        self.assertEqual(resp.status_code, 200)
                        self.assertTrue(resp.json().get("success"))
                        resp = client.get("/api/providers")
                        self.assertEqual(resp.status_code, 200)
                        payload = resp.json()
                        self.assertTrue(payload.get("success"))
                        providers = payload["data"]["providers"]
                        self.assertEqual(providers.get("openai", {}).get("api_key"), "********")
                        raw = json.loads(providers_path.read_text(encoding="utf-8"))
                        self.assertEqual(raw.get("openai", {}).get("api_key"), "secret_key")

                        resp = client.post("/api/knowledge/store", json={"content": "hello world", "metadata": {"kind": "test"}})
                        self.assertEqual(resp.status_code, 200)
                        self.assertTrue(resp.json().get("success"))
                        node_id = resp.json()["data"]["id"]
                        resp = client.get(f"/api/knowledge/node/{node_id}")
                        self.assertEqual(resp.status_code, 200)
                        self.assertTrue(resp.json().get("success"))
                        resp = client.post("/api/knowledge/search", json={"query": "hello", "top_k": 3})
                        self.assertEqual(resp.status_code, 200)
                        self.assertTrue(resp.json().get("success"))

                        resp = client.get("/api/research/status")
                        self.assertEqual(resp.status_code, 200)
                        self.assertTrue(resp.json().get("success"))
                        resp = client.post("/api/research/notes", json={"title": "t", "content": "hello"})
                        self.assertEqual(resp.status_code, 200)
                        self.assertTrue(resp.json().get("success"))
                        resp = client.get("/api/research/notes")
                        self.assertEqual(resp.status_code, 200)
                        self.assertTrue(resp.json().get("success"))

                        resp = client.get("/api/assets")
                        self.assertEqual(resp.status_code, 200)
                    finally:
                        if config_backup is not None:
                            config_path.write_text(config_backup, encoding="utf-8")
                        if providers_backup is not None:
                            providers_path.write_text(providers_backup, encoding="utf-8")
            finally:
                if prev_ws is not None:
                    os.environ["WORKSPACE_PATH"] = prev_ws
                else:
                    os.environ.pop("WORKSPACE_PATH", None)
        self.assertTrue(resp.json().get("success"))

        resp = client.post("/api/assets/generate", headers=headers, json={"type": "icon"})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json().get("success"))

        resp = client.post("/api/deploy", headers=headers, json={"target": "local"})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json().get("success"))
        global_deploy_id = resp.json()["data"]["deploy_id"]

        def _fetch_global_deploy():
            status = client.get(f"/api/deploy/status?deploy_id={global_deploy_id}")
            self.assertEqual(status.status_code, 200)
            return status.json()["data"]["job"]

        job = self._wait_for_terminal_status(_fetch_global_deploy, timeout_sec=30.0)
        self.assertIsNotNone(job)
        self.assertEqual(self._status_field(job), "completed")
        global_deploy_dir = workspace_path / "deployments" / global_deploy_id
        self.assertTrue((global_deploy_dir / "artifact.zip").is_file())
        self.assertTrue((global_deploy_dir / "deploy.json").is_file())

        resp = client.post("/api/projects/create", headers=headers, json={"name": "sample_project"})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json().get("success"))
        project_path = Path(resp.json()["data"]["path"])
        (project_path / "requirements.txt").write_text("requests\n", encoding="utf-8")
        (project_path / "main.py").write_text("print('ok')\n", encoding="utf-8")

        resp = client.post("/api/projects/sample_project/build", headers=headers)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json().get("success"))
        build_id = resp.json()["data"]["build_id"]

        def _fetch_build():
            status = client.get("/api/projects/sample_project/status")
            self.assertEqual(status.status_code, 200)
            builds = status.json()["data"]["builds"]
            return next((b for b in builds if b.get("build_id") == build_id), None)

        job = self._wait_for_terminal_status(_fetch_build, timeout_sec=30.0)
        self.assertIsNotNone(job)
        self.assertEqual(self._status_field(job), "completed")
        build_dir = workspace_path / "builds" / build_id
        self.assertTrue((build_dir / "artifact.zip").is_file())

        resp = client.post("/api/projects/sample_project/deploy", headers=headers)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json().get("success"))
        deploy_id = resp.json()["data"]["deploy_id"]

        def _fetch_project_deploy():
            status = client.get("/api/projects/sample_project/status")
            self.assertEqual(status.status_code, 200)
            deploys = status.json()["data"]["deployments"]
            return next((d for d in deploys if d.get("deploy_id") == deploy_id), None)

        djob = self._wait_for_terminal_status(_fetch_project_deploy, timeout_sec=30.0)
        self.assertIsNotNone(djob)
        self.assertEqual(self._status_field(djob), "completed")
        deploy_dir = workspace_path / "deployments" / deploy_id
        self.assertTrue((deploy_dir / "artifact.zip").is_file())
        self.assertTrue((deploy_dir / "deploy.json").is_file())


if __name__ == "__main__":
    unittest.main()
