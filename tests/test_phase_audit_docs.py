import os
import unittest


class PhaseAuditDocsTests(unittest.TestCase):
    """Validate audit documentation covers all phases including compliance."""

    def setUp(self):
        self.repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.audit_path = os.path.join(self.repo_root, "docs", "PHASE_AUDIT.md")
        self.compliance_path = os.path.join(self.repo_root, "docs", "PHASE10_COMPLIANCE.md")

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


if __name__ == "__main__":
    unittest.main()
