import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from engine.server import create_app


class K8sDeploymentTests(unittest.TestCase):
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

    def test_k8s_deploy_generates_manifests_frontend_only(self) -> None:
        class Proc:
            def __init__(self, rc: int, out: str = "", err: str = "") -> None:
                self.returncode = rc
                self.stdout = out
                self.stderr = err

        def fake_run(argv, cwd=None, capture_output=False, text=False, timeout=None):
            if argv[:2] == ["docker", "build"]:
                return Proc(0, "ok", "")
            return Proc(0, "", "")

        def fake_which(name: str):
            if name == "docker":
                return "C:\\docker.exe"
            if name == "kubectl":
                return None
            return None

        with patch("apps.deployment.backend.routes.shutil.which", side_effect=fake_which), patch(
            "apps.deployment.backend.routes.subprocess.run", side_effect=fake_run
        ):
            resp = self.client.post(
                "/api/modules/deployment/deploy",
                json={"project": "demo", "version": "0.3.0", "target": "kubernetes", "port": 8089},
            )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body["success"])
        data = body["data"]
        self.assertEqual(data["status"], "completed")
        self.assertIn("k8s_manifests_dir", data)
        self.assertTrue(Path(data["k8s_manifests_dir"]).is_dir())
        self.assertIn("port_forward_web", data["k8s_access"])


if __name__ == "__main__":
    unittest.main()

