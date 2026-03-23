import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from engine.server import create_app


class GameDevModuleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = Path(tempfile.mkdtemp())
        self.app = create_app()
        self.app.state.workspace_path = str(self.tmpdir)
        self.client = TestClient(self.app)

    def tearDown(self) -> None:
        try:
            self.client.close()
        except Exception:
            pass

    def test_create_unity_project(self) -> None:
        resp = self.client.post(
            "/api/modules/game_dev/projects/create",
            json={"title": "My Unity Game", "engine": "unity", "prompt": "make a small game"},
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body["success"])
        proj = body["data"]
        self.assertEqual(proj["engine"], "unity")
        self.assertTrue(Path(proj["path"]).exists())
        self.assertTrue((Path(proj["path"]) / "Assets" / "Editor" / "AgentForgeBuild.cs").exists())

    def test_create_unreal_project(self) -> None:
        resp = self.client.post(
            "/api/modules/game_dev/projects/create",
            json={"title": "My Unreal Game", "engine": "unreal", "prompt": "make a small game"},
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body["success"])
        proj = body["data"]
        self.assertEqual(proj["engine"], "unreal")
        self.assertTrue(Path(proj["target"]).suffix.lower() == ".uproject")
        self.assertTrue(Path(proj["target"]).exists())

    def test_launch_unity_project(self) -> None:
        create = self.client.post(
            "/api/modules/game_dev/projects/create",
            json={"title": "LaunchUnity", "engine": "unity", "prompt": ""},
        ).json()
        self.assertTrue(create["success"])
        pid = create["data"]["id"]

        with patch("apps.game_dev.backend.routes._auto_find_tool_exe", return_value="C:\\Unity.exe"), patch(
            "apps.game_dev.backend.routes.Path.is_file", return_value=True
        ), patch("apps.game_dev.backend.routes.subprocess.Popen") as popen:
            resp = self.client.post("/api/modules/game_dev/projects/launch", json={"project_id": pid})
            self.assertEqual(resp.status_code, 200)
            body = resp.json()
            self.assertTrue(body["success"])
            self.assertTrue(body["data"]["launched"])
            popen.assert_called()

    def test_build_unity_project_invokes_unity_batchmode(self) -> None:
        create = self.client.post(
            "/api/modules/game_dev/projects/create",
            json={"title": "BuildUnity", "engine": "unity", "prompt": ""},
        ).json()
        self.assertTrue(create["success"])
        pid = create["data"]["id"]

        class Completed:
            def __init__(self) -> None:
                self.returncode = 0
                self.stdout = "ok"
                self.stderr = ""

        with patch("apps.game_dev.backend.routes._auto_find_tool_exe", return_value="C:\\Unity.exe"), patch(
            "apps.game_dev.backend.routes.Path.is_file", return_value=True
        ), patch("apps.game_dev.backend.routes.subprocess.run", return_value=Completed()) as run:
            resp = self.client.post("/api/modules/game_dev/projects/build", json={"project_id": pid})
            self.assertEqual(resp.status_code, 200)
            body = resp.json()
            self.assertTrue(body["success"])
            self.assertEqual(body["data"]["engine"], "unity")
            run.assert_called()


if __name__ == "__main__":
    unittest.main()

