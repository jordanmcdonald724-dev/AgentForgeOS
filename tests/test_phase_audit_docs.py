import os
import unittest


class PhaseAuditDocsTests(unittest.TestCase):
    """Validate audit documentation covers all phases including compliance."""

    def setUp(self):
        self.repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.audit_path = os.path.join(self.repo_root, "docs", "PHASE_AUDIT.md")
        self.compliance_path = os.path.join(self.repo_root, "docs", "PHASE10_COMPLIANCE.md")
        self.report_path = os.path.join(self.repo_root, "docs", "PHASE7-10_REPORT.md")

    def test_audit_doc_lists_phase_10(self):
        with open(self.audit_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Phase 10 — Compliance", content)
        self.assertIn("python -m unittest discover -s tests", content)
        self.assertIn("tests/test_phase_integration.py", content)

    def test_compliance_doc_exists_and_references_tests(self):
        self.assertTrue(os.path.isfile(self.compliance_path), "Compliance checklist missing")
        with open(self.compliance_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Compliance", content)
        self.assertIn("python -m unittest discover -s tests", content)
        self.assertIn("test_phase_integration.py", content)

    def test_phase7_knowledge_scaffold_present(self):
        knowledge_dir = os.path.join(self.repo_root, "knowledge")
        expected_files = [
            "knowledge_graph.py",
            "vector_store.py",
            "embedding_service.py",
            "pattern_extractor.py",
            "project_genome.py",
            "__init__.py",
        ]
        for filename in expected_files:
            path = os.path.join(knowledge_dir, filename)
            self.assertTrue(os.path.isfile(path), f"Missing Phase 7 file: {filename}")

    def test_phase8_apps_scaffold_present(self):
        apps_dir = os.path.join(self.repo_root, "apps")
        expected_entries = [
            os.path.join(apps_dir, "README.md"),
            os.path.join(apps_dir, "studio", "README.md"),
            os.path.join(apps_dir, "builds", "README.md"),
            os.path.join(apps_dir, "research", "README.md"),
            os.path.join(apps_dir, "assets", "README.md"),
            os.path.join(apps_dir, "deployment", "README.md"),
        ]
        for path in expected_entries:
            self.assertTrue(os.path.isfile(path), f"Missing Phase 8 artifact: {path}")

    def test_phase9_integration_artifacts_present(self):
        required_paths = [
            os.path.join(self.repo_root, "engine", "main.py"),
            os.path.join(self.repo_root, "engine", "server.py"),
            os.path.join(self.repo_root, "desktop", "src", "main.rs"),
            os.path.join(self.repo_root, "frontend", "index.html"),
            os.path.join(self.repo_root, "frontend", "style.css"),
        ]
        for path in required_paths:
            self.assertTrue(os.path.isfile(path), f"Missing Phase 9 artifact: {path}")

    def test_phase_report_exists(self):
        self.assertTrue(os.path.isfile(self.report_path), "Phase 7–10 report is missing")


if __name__ == "__main__":
    unittest.main()
