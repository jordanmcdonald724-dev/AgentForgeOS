import unittest

from fastapi.testclient import TestClient

from engine.server import create_app


class TestBuildBibleSmoke(unittest.TestCase):
    def test_frontend_index_served(self) -> None:
        app = create_app()
        with TestClient(app) as client:
            r = client.get("/")
            self.assertEqual(r.status_code, 200)
            self.assertIn("<!doctype html", r.text.lower())

    def test_health(self) -> None:
        app = create_app()
        with TestClient(app) as client:
            r = client.get("/api/health")
            self.assertEqual(r.status_code, 200)
            payload = r.json()
            self.assertTrue(payload.get("success"))

    def test_modules(self) -> None:
        app = create_app()
        with TestClient(app) as client:
            r = client.get("/api/modules")
            self.assertEqual(r.status_code, 200)
            payload = r.json()
            self.assertTrue(payload.get("success"))
            self.assertIsInstance(payload.get("data"), list)

    def test_websocket_connect(self) -> None:
        app = create_app()
        with TestClient(app) as client:
            with client.websocket_connect("/ws") as ws:
                ws.close()

    def test_knowledge_search_get_and_graph_add(self) -> None:
        app = create_app()
        with TestClient(app) as client:
            a = client.post("/api/knowledge/store", json={"id": "smoke:a", "content": "hello world", "metadata": {"type": "note"}})
            b = client.post("/api/knowledge/store", json={"id": "smoke:b", "content": "world hello", "metadata": {"type": "note"}})
            self.assertTrue(a.json().get("success"))
            self.assertTrue(b.json().get("success"))

            s = client.get("/api/knowledge/search", params={"query": "hello", "top_k": 3})
            self.assertEqual(s.status_code, 200)
            self.assertTrue(s.json().get("success"))

            e = client.post("/api/knowledge/graph/add", json={"source": "smoke:a", "target": "smoke:b"})
            self.assertEqual(e.status_code, 200)
            self.assertTrue(e.json().get("success"))

    def test_research_ingest_and_get_search(self) -> None:
        app = create_app()
        with TestClient(app) as client:
            ing = client.post("/api/research/ingest", json={"id": "smoke:source", "kind": "docs", "label": "Smoke Source"})
            self.assertEqual(ing.status_code, 200)
            self.assertTrue(ing.json().get("success"))

            s = client.get("/api/research/search", params={"query": "Smoke", "top_k": 5})
            self.assertEqual(s.status_code, 200)
            self.assertTrue(s.json().get("success"))
