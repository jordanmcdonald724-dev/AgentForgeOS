"""Tests for the bridge API routes.

Validates that the ``/api/bridge/*`` endpoints return correct responses
using a temporary bridge root so no production files are touched.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from bridge.routes import _get_bridge, router as bridge_router

# Reset the module-level singleton before every test.
import bridge.routes as _bridge_routes


def _build_test_app():
    """Return a minimal FastAPI app with only the bridge routes."""
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(bridge_router, prefix="/api")
    return app


class BridgeHealthRouteTests(unittest.TestCase):
    """GET /api/bridge/health returns bridge status."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        _bridge_routes._bridge = None
        self.env_patch = patch.dict(os.environ, {"BRIDGE_ROOT": self.tmpdir})
        self.env_patch.start()
        self.client = TestClient(_build_test_app())

    def tearDown(self):
        self.env_patch.stop()
        _bridge_routes._bridge = None

    def test_health_returns_ok(self):
        resp = self.client.get("/api/bridge/health")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body["success"])
        self.assertEqual(body["data"]["status"], "ok")
        self.assertTrue(body["data"]["root_exists"])


class BridgeListRouteTests(unittest.TestCase):
    """GET /api/bridge/list returns directory contents."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        root = Path(self.tmpdir)
        (root / "readme.md").write_text("# Hello")
        (root / "src").mkdir()
        (root / "src" / "main.py").write_text("pass")

        _bridge_routes._bridge = None
        self.env_patch = patch.dict(os.environ, {"BRIDGE_ROOT": self.tmpdir})
        self.env_patch.start()
        self.client = TestClient(_build_test_app())

    def tearDown(self):
        self.env_patch.stop()
        _bridge_routes._bridge = None

    def test_list_root_returns_entries(self):
        resp = self.client.get("/api/bridge/list")
        body = resp.json()
        self.assertTrue(body["success"])
        names = {e["name"] for e in body["data"]["entries"]}
        self.assertIn("readme.md", names)
        self.assertIn("src", names)

    def test_list_subdirectory(self):
        resp = self.client.get("/api/bridge/list", params={"path": "src"})
        body = resp.json()
        self.assertTrue(body["success"])
        names = {e["name"] for e in body["data"]["entries"]}
        self.assertIn("main.py", names)

    def test_list_nonexistent_returns_error(self):
        resp = self.client.get("/api/bridge/list", params={"path": "ghost"})
        body = resp.json()
        self.assertFalse(body["success"])


class BridgeReadRouteTests(unittest.TestCase):
    """GET /api/bridge/read returns file content."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        (Path(self.tmpdir) / "hello.txt").write_text("world")

        _bridge_routes._bridge = None
        self.env_patch = patch.dict(os.environ, {"BRIDGE_ROOT": self.tmpdir})
        self.env_patch.start()
        self.client = TestClient(_build_test_app())

    def tearDown(self):
        self.env_patch.stop()
        _bridge_routes._bridge = None

    def test_read_file_returns_content(self):
        resp = self.client.get("/api/bridge/read", params={"path": "hello.txt"})
        body = resp.json()
        self.assertTrue(body["success"])
        self.assertEqual(body["data"]["content"], "world")

    def test_read_missing_file_returns_error(self):
        resp = self.client.get("/api/bridge/read", params={"path": "nope.txt"})
        body = resp.json()
        self.assertFalse(body["success"])

    def test_read_denied_path_returns_error(self):
        resp = self.client.get("/api/bridge/read", params={"path": "../../etc/passwd"})
        body = resp.json()
        self.assertFalse(body["success"])


class BridgeSyncRouteTests(unittest.TestCase):
    """POST /api/bridge/sync returns a recursive project tree."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        root = Path(self.tmpdir)
        (root / "app.py").write_text("main()")
        (root / "lib").mkdir()
        (root / "lib" / "utils.py").write_text("pass")

        _bridge_routes._bridge = None
        self.env_patch = patch.dict(os.environ, {"BRIDGE_ROOT": self.tmpdir})
        self.env_patch.start()
        self.client = TestClient(_build_test_app())

    def tearDown(self):
        self.env_patch.stop()
        _bridge_routes._bridge = None

    def test_sync_returns_full_tree(self):
        resp = self.client.post("/api/bridge/sync")
        body = resp.json()
        self.assertTrue(body["success"])
        paths = {e["path"] for e in body["data"]["entries"]}
        self.assertIn("app.py", paths)
        self.assertIn("lib", paths)
        self.assertIn("lib/utils.py", paths)

    def test_sync_includes_type_info(self):
        resp = self.client.post("/api/bridge/sync")
        by_path = {e["path"]: e for e in resp.json()["data"]["entries"]}
        self.assertEqual(by_path["app.py"]["type"], "file")
        self.assertEqual(by_path["lib"]["type"], "directory")


if __name__ == "__main__":
    unittest.main()
