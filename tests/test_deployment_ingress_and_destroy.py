import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from engine.server import create_app


class DeploymentIngressAndDestroyTests(unittest.TestCase):
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

    def test_k8s_ingress_tls_manifest_generated(self) -> None:
        class Proc:
            def __init__(self, rc: int, out: str = "", err: str = "") -> None:
                self.returncode = rc
                self.stdout = out
                self.stderr = err

        def fake_run(argv, cwd=None, capture_output=False, text=False, timeout=None, input=None):
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
                json={
                    "project": "demo",
                    "version": "0.9.0",
                    "target": "kubernetes",
                    "port": 8089,
                    "host": "demo.example.com",
                    "use_tls": True,
                    "tls_secret": "demo-tls",
                },
            )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body["success"])
        manifests_dir = Path(body["data"]["k8s_manifests_dir"])
        ingress = manifests_dir / "ingress.yaml"
        self.assertTrue(ingress.is_file())
        text = ingress.read_text(encoding="utf-8")
        self.assertIn("demo.example.com", text)
        self.assertIn("secretName: demo-tls", text)

    def test_destroy_docker_container(self) -> None:
        class Proc:
            def __init__(self, rc: int, out: str = "", err: str = "") -> None:
                self.returncode = rc
                self.stdout = out
                self.stderr = err

        calls = []

        def fake_run(argv, cwd=None, capture_output=False, text=False, timeout=None, input=None):
            calls.append(list(argv))
            if argv[:2] == ["docker", "build"]:
                return Proc(0, "build ok", "")
            if argv[:3] == ["docker", "run", "-d"]:
                return Proc(0, "containerXYZ\n", "")
            if argv[:3] == ["docker", "rm", "-f"]:
                return Proc(0, "removed\n", "")
            return Proc(0, "", "")

        def fake_which(name: str):
            if name == "docker":
                return "C:\\docker.exe"
            return None

        with patch("apps.deployment.backend.routes.shutil.which", side_effect=fake_which), patch(
            "apps.deployment.backend.routes.subprocess.run", side_effect=fake_run
        ):
            dep = self.client.post(
                "/api/modules/deployment/deploy",
                json={"project": "demo", "version": "0.1.0", "target": "docker", "port": 8099},
            ).json()
            self.assertTrue(dep["success"])
            uid = dep["data"]["uid"]
            resp = self.client.post("/api/modules/deployment/destroy", json={"uid": uid})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body["success"])
        self.assertEqual(body["data"]["status"], "destroyed")
        self.assertTrue(any(c[:3] == ["docker", "rm", "-f"] for c in calls))


if __name__ == "__main__":
    unittest.main()

