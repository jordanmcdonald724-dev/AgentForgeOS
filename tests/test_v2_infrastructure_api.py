import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from engine.server import create_app


class TestV2InfrastructureAPI(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app())

    def tearDown(self) -> None:
        try:
            self.client.close()
        except Exception:
            pass

    def test_settings_round_trip(self) -> None:
        # Update a couple of settings
        payload = {
            "unity_path": "C:/Program Files/Unity/Editor/Unity.exe",
            "local_project_root": "C:/AgentForgeProjects",
            "auto_launch_editor": True,
        }
        resp = self.client.post("/api/v2/settings", json=payload)
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body["success"])
        data = body["data"]
        # Compare normalized paths so Windows path separators do not
        # cause spurious test failures.
        self.assertEqual(Path(data["unity_path"]), Path(payload["unity_path"]))
        self.assertEqual(Path(data["local_project_root"]), Path(payload["local_project_root"]))
        self.assertTrue(data["auto_launch_editor"])

        # Fetch settings and ensure they match
        resp2 = self.client.get("/api/v2/settings")
        self.assertEqual(resp2.status_code, 200)
        data2 = resp2.json()["data"]
        self.assertEqual(Path(data2["unity_path"]), Path(payload["unity_path"]))

    def test_model_routes_endpoint(self) -> None:
        resp = self.client.get("/api/v2/model_routing/routes")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body["success"])
        routes = body["data"]["routes"]
        self.assertIn("code", routes)
        self.assertIn("image", routes)
        self.assertIn("audio", routes)
        self.assertIn("three_d", routes)
        self.assertIn("generic", routes)

    def test_local_bridge_projects_endpoint(self) -> None:
        # This will typically return an empty list on CI / dev machines,
        # but the shape of the response should be stable.
        resp = self.client.get("/api/v2/local_bridge/projects")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body["success"])
        self.assertIn("projects", body["data"])
        self.assertIsInstance(body["data"]["projects"], list)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
