import unittest

from fastapi.testclient import TestClient

from engine.server import create_app


class TestV2ResearchAPI(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app())

    def test_list_categories(self) -> None:
        resp = self.client.get("/api/v2/research/categories")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body["success"])
        cats = body["data"]["categories"]
        self.assertIn("architecture_patterns", cats)

    def test_ingest_and_list_nodes(self) -> None:
        payload = {"id": "r1", "kind": "github", "path": "https://github.com/example/repo", "label": "Sample"}
        resp = self.client.post("/api/v2/research/ingest", json=payload)
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body["success"])

        resp2 = self.client.get("/api/v2/research/nodes")
        self.assertEqual(resp2.status_code, 200)
        nodes = resp2.json()["data"]["nodes"]
        self.assertGreaterEqual(len(nodes), 1)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
