import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from engine.server import create_app


class DockerDeploymentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app()
        self.client = TestClient(self.app)
        self.ws = Path(tempfile.mkdtemp())
        self.app.state.workspace_path = str(self.ws)
        self.app.state.config = {"providers": {"llm": "noop"}}

        project_dir = self.ws / "projects" / "demo"
        dist_dir = project_dir / "frontend" / "dist"
        dist_dir.mkdir(parents=True, exist_ok=True)
        (dist_dir / "index.html").write_text("<html>ok</html>", encoding="utf-8")

    def tearDown(self) -> None:
        try:
            self.client.close()
        except Exception:
            pass

    def test_docker_deploy_builds_and_runs(self) -> None:
        class Proc:
            def __init__(self, rc: int, out: str = "", err: str = "") -> None:
                self.returncode = rc
                self.stdout = out
                self.stderr = err

        def fake_run(argv, cwd=None, capture_output=False, text=False, timeout=None):
            if argv[:2] == ["docker", "build"]:
                return Proc(0, "build ok", "")
            if argv[:3] == ["docker", "run", "-d"]:
                return Proc(0, "container123\n", "")
            return Proc(0, "", "")

        with patch("apps.deployment.backend.routes.shutil.which", return_value="C:\\docker.exe"), patch(
            "apps.deployment.backend.routes.subprocess.run", side_effect=fake_run
        ):
            resp = self.client.post(
                "/api/modules/deployment/deploy",
                json={"project": "demo", "version": "0.1.0", "target": "docker", "port": 8099},
            )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body["success"])
        self.assertEqual(body["data"]["status"], "completed")
        self.assertIn("docker_image", body["data"])
        self.assertEqual(body["data"]["docker_run"]["container_id"], "container123")
        self.assertEqual(body["data"]["docker_url"], "http://127.0.0.1:8099/")

    def test_docker_deploy_uses_compose_when_backend_detected(self) -> None:
        project_dir = self.ws / "projects" / "demo"
        backend_dir = project_dir / "backend"
        backend_dir.mkdir(parents=True, exist_ok=True)
        (backend_dir / "requirements.txt").write_text("fastapi\n", encoding="utf-8")
        (backend_dir / "main.py").write_text("from fastapi import FastAPI\napp = FastAPI()\n", encoding="utf-8")

        class Proc:
            def __init__(self, rc: int, out: str = "", err: str = "") -> None:
                self.returncode = rc
                self.stdout = out
                self.stderr = err

        def fake_run(argv, cwd=None, capture_output=False, text=False, timeout=None):
            if argv[:2] == ["docker", "compose"] and "up" in argv:
                return Proc(0, "compose up ok\n", "")
            return Proc(0, "", "")

        def fake_which(name: str):
            if name == "docker":
                return "C:\\docker.exe"
            if name == "docker-compose":
                return None
            return None

        with patch("apps.deployment.backend.routes.shutil.which", side_effect=fake_which), patch(
            "apps.deployment.backend.routes.subprocess.run", side_effect=fake_run
        ):
            resp = self.client.post(
                "/api/modules/deployment/deploy",
                json={"project": "demo", "version": "0.2.0", "target": "docker", "port": 8101},
            )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body["success"])
        self.assertEqual(body["data"]["status"], "completed")
        self.assertIn("docker_compose", body["data"])
        self.assertEqual(body["data"]["docker_url"], "http://127.0.0.1:8101/")


if __name__ == "__main__":
    unittest.main()
