import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from engine.server import create_app


class TestV2ResearchAPI(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app())

    def tearDown(self) -> None:
        try:
            self.client.close()
        except Exception:
            pass

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

    def test_ingest_url_web(self) -> None:
        with patch("research.internet_scanner.fetch_webpage_content", return_value="hello world"):
            resp = self.client.post("/api/v2/research/ingest_url", json={"url": "https://example.com", "label": "Example"})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body["success"])
        self.assertIn("node_id", body["data"])

    def test_upload_and_ingest_file(self) -> None:
        tmpdir = Path(tempfile.mkdtemp())
        self.client.app.state.workspace_path = str(tmpdir)  # type: ignore[attr-defined]
        resp = self.client.post(
            "/api/v2/research/upload",
            files={"file": ("note.txt", b"hello", "text/plain")},
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body["success"])
        self.assertIn("node_id", body["data"])

    def test_ingest_url_youtube_uses_captions_without_google(self) -> None:
        with patch("research.video_processor.fetch_youtube_transcript", return_value="captions text"), patch(
            "research.video_processor.download_youtube_video", side_effect=AssertionError("should not download")
        ), patch("research.video_processor.transcribe_audio", side_effect=AssertionError("should not transcribe")):
            resp = self.client.post(
                "/api/v2/research/ingest_url",
                json={"url": "https://www.youtube.com/watch?v=abc123", "label": "Vid"},
            )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body["success"])
        self.assertIn("node_id", body["data"])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
