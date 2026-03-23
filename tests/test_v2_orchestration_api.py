import unittest

from fastapi.testclient import TestClient

from engine.server import create_app


class TestV2OrchestrationAPI(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app())

    def tearDown(self) -> None:
        try:
            self.client.close()
        except Exception:
            pass

    def test_command_preview_endpoint(self) -> None:
        payload = {
            "command": "build a small web app",
            "brief": {"project_type": "web", "scale": "small"},
        }
        response = self.client.post("/api/v2/command/preview", json=payload)
        self.assertEqual(response.status_code, 200)

        body = response.json()
        self.assertTrue(body["success"])
        data = body["data"]

        # Should contain tasks and a simulation report
        self.assertIn("tasks", data)
        self.assertGreaterEqual(len(data["tasks"]), 4)
        self.assertIn("simulation", data)

        # Build status should be present
        self.assertIn("build_status", data)

        # Recursive loop description should expose the stages list
        self.assertIn("recursive_loop", data)
        self.assertIn("stages", data["recursive_loop"])
        self.assertGreaterEqual(len(data["recursive_loop"]["stages"]), 1)

    def test_command_preview_with_research_sources(self) -> None:
        payload = {
            "command": "analyze prior work",
            "brief": {},
            "research_sources": [
                {"id": "r1", "kind": "github", "path": "https://github.com/example/repo", "label": "Sample"}
            ],
        }
        response = self.client.post("/api/v2/command/preview", json=payload)
        self.assertEqual(response.status_code, 200)

        body = response.json()
        self.assertTrue(body["success"])
        data = body["data"]
        self.assertIn("research", data)
        self.assertIn("ingested", data["research"])
        self.assertGreaterEqual(len(data["research"]["ingested"]), 1)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
