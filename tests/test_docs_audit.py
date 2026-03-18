"""Tests for the new scaffolds created during the docs audit:
- agents/ package (Phase 5 requirement)
- bridge/ package (bridge layer)
- config/ templates
- docs/BUILD_STATUS.md and docs/SYSTEM_CAPABILITY_MAP.md content
- app module manifests for builds, research, assets, deployment
"""

import os
import json
import unittest


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class AgentsScaffoldTests(unittest.TestCase):
    """Phase 5 agents/ package should exist and be importable."""

    def test_agents_package_exists(self):
        path = os.path.join(REPO_ROOT, "agents", "__init__.py")
        self.assertTrue(os.path.isfile(path), "agents/__init__.py missing")

    def test_agents_pipeline_exists(self):
        path = os.path.join(REPO_ROOT, "agents", "pipeline.py")
        self.assertTrue(os.path.isfile(path), "agents/pipeline.py missing")

    def test_agents_pipeline_importable(self):
        import agents.pipeline as pipeline_mod
        self.assertTrue(callable(getattr(pipeline_mod, "get_pipeline_stages", None)))

    def test_pipeline_stages_match_service_definition(self):
        from agents.pipeline import get_pipeline_stages
        from services.agent_pipeline import AGENT_PIPELINE
        self.assertEqual(get_pipeline_stages(), list(AGENT_PIPELINE))


class BridgeScaffoldTests(unittest.TestCase):
    """bridge/ package should exist with bridge_server and bridge_security."""

    def test_bridge_init_exists(self):
        path = os.path.join(REPO_ROOT, "bridge", "__init__.py")
        self.assertTrue(os.path.isfile(path), "bridge/__init__.py missing")

    def test_bridge_server_exists(self):
        path = os.path.join(REPO_ROOT, "bridge", "bridge_server.py")
        self.assertTrue(os.path.isfile(path), "bridge/bridge_server.py missing")

    def test_bridge_security_exists(self):
        path = os.path.join(REPO_ROOT, "bridge", "bridge_security.py")
        self.assertTrue(os.path.isfile(path), "bridge/bridge_security.py missing")

    def test_bridge_security_importable(self):
        from bridge.bridge_security import BridgeSecurity
        from pathlib import Path
        sec = BridgeSecurity(Path("/tmp"))
        self.assertIsNotNone(sec)

    def test_bridge_security_blocks_path_traversal(self):
        from bridge.bridge_security import BridgeSecurity
        from pathlib import Path
        sec = BridgeSecurity(Path("/tmp/workspace"))
        result = sec.validate_path("../../etc/passwd")
        self.assertFalse(result["allowed"])

    def test_bridge_security_allows_valid_path(self):
        from bridge.bridge_security import BridgeSecurity
        from pathlib import Path
        sec = BridgeSecurity(Path("/tmp/workspace"))
        result = sec.validate_path("src/main.py")
        self.assertTrue(result["allowed"])

    def test_bridge_security_blocks_git_directory(self):
        from bridge.bridge_security import BridgeSecurity
        from pathlib import Path
        sec = BridgeSecurity(Path("/tmp/workspace"))
        result = sec.validate_path(".git/config")
        self.assertFalse(result["allowed"])

    def test_bridge_server_importable(self):
        from bridge.bridge_server import BridgeServer
        server = BridgeServer(bridge_root="/tmp")
        self.assertIsNotNone(server)


class ConfigScaffoldTests(unittest.TestCase):
    """config/ directory should contain environment and settings templates."""

    def test_env_example_exists(self):
        path = os.path.join(REPO_ROOT, "config", ".env.example")
        self.assertTrue(os.path.isfile(path), "config/.env.example missing")

    def test_settings_json_exists(self):
        path = os.path.join(REPO_ROOT, "config", "settings.json")
        self.assertTrue(os.path.isfile(path), "config/settings.json missing")

    def test_settings_json_is_valid_json(self):
        path = os.path.join(REPO_ROOT, "config", "settings.json")
        with open(path, "r", encoding="utf-8") as fp:
            data = json.load(fp)
        self.assertIn("server", data)
        self.assertIn("database", data)
        self.assertIn("bridge", data)

    def test_env_example_contains_key_variables(self):
        path = os.path.join(REPO_ROOT, "config", ".env.example")
        with open(path, "r", encoding="utf-8") as fp:
            content = fp.read()
        self.assertIn("MONGO_URI", content)
        self.assertIn("PROVIDER_LLM", content)
        self.assertIn("BRIDGE_ROOT", content)


class AppModuleManifestTests(unittest.TestCase):
    """All five app modules should have manifest.json and module.py."""

    MODULES = ["studio", "builds", "research", "assets", "deployment"]

    def _module_path(self, module_name: str, filename: str) -> str:
        return os.path.join(REPO_ROOT, "apps", module_name, filename)

    def test_all_manifests_exist(self):
        for module_name in self.MODULES:
            path = self._module_path(module_name, "manifest.json")
            self.assertTrue(os.path.isfile(path), f"manifest.json missing for {module_name}")

    def test_all_module_py_exist(self):
        for module_name in self.MODULES:
            path = self._module_path(module_name, "module.py")
            self.assertTrue(os.path.isfile(path), f"module.py missing for {module_name}")

    def test_all_manifests_valid(self):
        required_fields = {"id", "name", "version", "entry", "class"}
        for module_name in self.MODULES:
            path = self._module_path(module_name, "manifest.json")
            with open(path, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            for field in required_fields:
                self.assertIn(field, data, f"{module_name}/manifest.json missing field '{field}'")
                self.assertTrue(str(data[field]).strip(), f"{module_name}/manifest.json field '{field}' is empty")


class DocsAuditTests(unittest.TestCase):
    """New documentation files created during the docs audit should exist and have content."""

    def _doc_path(self, filename: str) -> str:
        return os.path.join(REPO_ROOT, "docs", filename)

    def test_system_capability_map_has_content(self):
        path = self._doc_path("SYSTEM_CAPABILITY_MAP.md")
        self.assertTrue(os.path.isfile(path), "SYSTEM_CAPABILITY_MAP.md missing")
        with open(path, "r", encoding="utf-8") as fp:
            content = fp.read()
        self.assertGreater(len(content), 500, "SYSTEM_CAPABILITY_MAP.md appears to be empty or a stub")
        self.assertIn("COMPLETE", content)
        self.assertIn("MISSING", content)

    def test_build_status_doc_exists(self):
        path = self._doc_path("BUILD_STATUS.md")
        self.assertTrue(os.path.isfile(path), "BUILD_STATUS.md missing")
        with open(path, "r", encoding="utf-8") as fp:
            content = fp.read()
        self.assertGreater(len(content), 500, "BUILD_STATUS.md appears to be empty")
        self.assertIn("TODO", content)

    def test_phase10_compliance_has_checklist(self):
        path = self._doc_path("PHASE10_COMPLIANCE.md")
        with open(path, "r", encoding="utf-8") as fp:
            content = fp.read()
        self.assertIn("python -m unittest discover -s tests", content)
        self.assertIn("test_phase_integration.py", content)
        self.assertIn("Known Gaps", content)

    def test_readme_is_not_stub(self):
        path = os.path.join(REPO_ROOT, "README.md")
        with open(path, "r", encoding="utf-8") as fp:
            content = fp.read()
        self.assertGreater(len(content), 300, "README.md is still a stub")
        self.assertIn("Quick Start", content)

    def test_phase_audit_covers_all_phases(self):
        path = self._doc_path("PHASE_AUDIT.md")
        with open(path, "r", encoding="utf-8") as fp:
            content = fp.read()
        for phase_num in range(1, 11):
            self.assertIn(f"Phase {phase_num}", content, f"PHASE_AUDIT.md missing Phase {phase_num}")


if __name__ == "__main__":
    unittest.main()
