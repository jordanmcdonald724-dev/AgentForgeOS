"""Tests for the bridge filesystem layer.

``BridgeServer`` performs real filesystem I/O bounded to a root directory.
``BridgeSecurity`` validates every path before the server acts on it.

All tests use a temporary directory created by ``tempfile.mkdtemp`` so that
no production files are touched and cleanup is trivial.
"""

import os
import tempfile
import unittest
from pathlib import Path

from bridge.bridge_security import BridgeSecurity
from bridge.bridge_server import BridgeServer


class BridgeSecurityTests(unittest.TestCase):
    """BridgeSecurity rejects dangerous paths and honours the allow-list."""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.security = BridgeSecurity(self.root)

    # ------------------------------------------------------------------ #
    # Allowed paths                                                        #
    # ------------------------------------------------------------------ #

    def test_allowed_python_file(self):
        result = self.security.validate_path("src/main.py")
        self.assertTrue(result["allowed"])
        self.assertEqual(result["reason"], "")

    def test_allowed_json_file(self):
        self.assertTrue(self.security.is_allowed("config.json"))

    def test_allowed_markdown_file(self):
        self.assertTrue(self.security.is_allowed("README.md"))

    def test_allowed_directory(self):
        # Directories (no extension) should pass the extension check.
        self.assertTrue(self.security.is_allowed("subdir"))

    # ------------------------------------------------------------------ #
    # Denied paths                                                         #
    # ------------------------------------------------------------------ #

    def test_rejects_path_traversal(self):
        result = self.security.validate_path("../../etc/passwd")
        self.assertFalse(result["allowed"])
        self.assertIn("traversal", result["reason"].lower())

    def test_rejects_git_directory(self):
        result = self.security.validate_path(".git/config")
        self.assertFalse(result["allowed"])

    def test_rejects_env_file(self):
        result = self.security.validate_path(".env")
        self.assertFalse(result["allowed"])

    def test_rejects_pycache(self):
        result = self.security.validate_path("__pycache__/module.cpython-312.pyc")
        self.assertFalse(result["allowed"])

    def test_rejects_disallowed_extension(self):
        result = self.security.validate_path("binary.exe")
        self.assertFalse(result["allowed"])
        self.assertIn("extension", result["reason"].lower())

    def test_rejects_empty_path(self):
        result = self.security.validate_path("")
        self.assertFalse(result["allowed"])

    def test_rejects_whitespace_only_path(self):
        result = self.security.validate_path("   ")
        self.assertFalse(result["allowed"])


class BridgeServerReadTests(unittest.TestCase):
    """BridgeServer.read_file reads real files from the bridge root."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.server = BridgeServer(bridge_root=self.tmpdir)

    def test_reads_existing_file(self):
        path = Path(self.tmpdir) / "hello.txt"
        path.write_text("hello world", encoding="utf-8")

        result = self.server.read_file("hello.txt")
        self.assertTrue(result["success"])
        self.assertEqual(result["content"], "hello world")
        self.assertEqual(result["path"], "hello.txt")

    def test_read_missing_file_returns_error(self):
        result = self.server.read_file("missing.txt")
        self.assertFalse(result["success"])
        self.assertIn("not found", result["error"].lower())

    def test_read_denied_path_returns_error(self):
        result = self.server.read_file("../../etc/passwd")
        self.assertFalse(result["success"])
        self.assertIn("traversal", result["error"].lower())

    def test_reads_nested_file(self):
        nested = Path(self.tmpdir) / "sub" / "deep.py"
        nested.parent.mkdir(parents=True)
        nested.write_text("x = 1", encoding="utf-8")

        result = self.server.read_file("sub/deep.py")
        self.assertTrue(result["success"])
        self.assertEqual(result["content"], "x = 1")


class BridgeServerWriteTests(unittest.TestCase):
    """BridgeServer.write_file creates and overwrites files."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.server = BridgeServer(bridge_root=self.tmpdir)

    def test_writes_new_file(self):
        result = self.server.write_file("output.py", "print('hi')")
        self.assertTrue(result["success"])
        content = (Path(self.tmpdir) / "output.py").read_text()
        self.assertEqual(content, "print('hi')")

    def test_creates_parent_directories(self):
        result = self.server.write_file("a/b/c/new.py", "pass")
        self.assertTrue(result["success"])
        self.assertTrue((Path(self.tmpdir) / "a" / "b" / "c" / "new.py").exists())

    def test_overwrites_existing_file(self):
        (Path(self.tmpdir) / "existing.md").write_text("old", encoding="utf-8")
        self.server.write_file("existing.md", "new content")
        self.assertEqual(
            (Path(self.tmpdir) / "existing.md").read_text(), "new content"
        )

    def test_write_denied_path_returns_error(self):
        result = self.server.write_file("../../evil.py", "malicious")
        self.assertFalse(result["success"])

    def test_write_disallowed_extension_returns_error(self):
        result = self.server.write_file("binary.exe", "data")
        self.assertFalse(result["success"])


class BridgeServerListTests(unittest.TestCase):
    """BridgeServer.list_directory enumerates directory contents."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.server = BridgeServer(bridge_root=self.tmpdir)

    def _populate(self):
        root = Path(self.tmpdir)
        (root / "alpha.py").write_text("a")
        (root / "beta.md").write_text("b")
        sub = root / "subdir"
        sub.mkdir()
        (sub / "gamma.json").write_text("{}")

    def test_lists_root_directory(self):
        self._populate()
        result = self.server.list_directory(".")
        self.assertTrue(result["success"])
        names = {e["name"] for e in result["entries"]}
        self.assertIn("alpha.py", names)
        self.assertIn("beta.md", names)
        self.assertIn("subdir", names)

    def test_entry_type_classification(self):
        self._populate()
        result = self.server.list_directory(".")
        by_name = {e["name"]: e for e in result["entries"]}
        self.assertEqual(by_name["alpha.py"]["type"], "file")
        self.assertEqual(by_name["subdir"]["type"], "directory")

    def test_lists_subdirectory(self):
        self._populate()
        result = self.server.list_directory("subdir")
        self.assertTrue(result["success"])
        names = {e["name"] for e in result["entries"]}
        self.assertIn("gamma.json", names)

    def test_list_missing_directory_returns_error(self):
        result = self.server.list_directory("nonexistent")
        self.assertFalse(result["success"])

    def test_list_denied_path_returns_error(self):
        result = self.server.list_directory("../../etc")
        self.assertFalse(result["success"])


class BridgeServerDeleteTests(unittest.TestCase):
    """BridgeServer.delete_file removes files within the root."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.server = BridgeServer(bridge_root=self.tmpdir)

    def test_deletes_existing_file(self):
        target = Path(self.tmpdir) / "todelete.txt"
        target.write_text("bye")
        result = self.server.delete_file("todelete.txt")
        self.assertTrue(result["success"])
        self.assertFalse(target.exists())

    def test_delete_missing_file_returns_error(self):
        result = self.server.delete_file("ghost.txt")
        self.assertFalse(result["success"])
        self.assertIn("not found", result["error"].lower())

    def test_delete_denied_path_returns_error(self):
        result = self.server.delete_file("../../important.txt")
        self.assertFalse(result["success"])


class BridgeServerRoundTripTests(unittest.TestCase):
    """End-to-end write → read → list → delete round-trip."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.server = BridgeServer(bridge_root=self.tmpdir)

    def test_full_round_trip(self):
        # Write
        write_result = self.server.write_file("notes.md", "# Notes\nline 1")
        self.assertTrue(write_result["success"])

        # Read back
        read_result = self.server.read_file("notes.md")
        self.assertTrue(read_result["success"])
        self.assertEqual(read_result["content"], "# Notes\nline 1")

        # List — file must appear
        list_result = self.server.list_directory(".")
        names = {e["name"] for e in list_result["entries"]}
        self.assertIn("notes.md", names)

        # Delete
        del_result = self.server.delete_file("notes.md")
        self.assertTrue(del_result["success"])
        self.assertFalse((Path(self.tmpdir) / "notes.md").exists())


if __name__ == "__main__":
    unittest.main()
