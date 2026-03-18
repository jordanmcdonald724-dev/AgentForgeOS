import json
import shutil
from pathlib import Path
import unittest

from agents.v2.sentinel import SentinelAgent
from orchestration.task_model import Task


class TestV2GuardianAgent(unittest.TestCase):
    def setUp(self) -> None:
        self.project_root = Path("projects/test_guardian_project")
        if self.project_root.exists():
            shutil.rmtree(self.project_root)

    def tearDown(self) -> None:
        if self.project_root.exists():
            shutil.rmtree(self.project_root)

    def test_guardian_writes_reports(self) -> None:
        agent = SentinelAgent()
        task = Task(
            task_id="guardian-1",
            assigned_agent="Guardian",
            inputs={"project_root": str(self.project_root)},
        )

        result = agent.handle_task(task)

        reports_dir = self.project_root / "reports"
        validation_path = reports_dir / "validation_report.json"
        security_path = reports_dir / "security_report.json"
        issues_path = reports_dir / "issues.json"

        self.assertTrue(reports_dir.exists(), "reports directory should be created")
        self.assertTrue(validation_path.exists(), "validation_report.json should be created")
        self.assertTrue(security_path.exists(), "security_report.json should be created")
        self.assertTrue(issues_path.exists(), "issues.json should be created")

        with validation_path.open("r", encoding="utf-8") as f:
            validation = json.load(f)
        with security_path.open("r", encoding="utf-8") as f:
            security = json.load(f)
        with issues_path.open("r", encoding="utf-8") as f:
            issues = json.load(f)

        self.assertIn("status", validation)
        self.assertIn("status", security)
        self.assertIn("critical", issues)
        self.assertIn("warnings", issues)

        self.assertIn("validation_report_path", result.outputs)
        self.assertIn("security_report_path", result.outputs)
        self.assertIn("issues_path", result.outputs)


if __name__ == "__main__":
    unittest.main()
