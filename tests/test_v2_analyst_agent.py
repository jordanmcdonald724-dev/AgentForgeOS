import json
import shutil
from pathlib import Path
import unittest

from agents.v2.probe import ProbeAgent
from orchestration.task_model import Task


class TestV2AnalystAgent(unittest.TestCase):
    def setUp(self) -> None:
        self.project_root = Path("projects/test_analyst_project")
        if self.project_root.exists():
            shutil.rmtree(self.project_root)

    def tearDown(self) -> None:
        if self.project_root.exists():
            shutil.rmtree(self.project_root)

    def test_analyst_writes_test_artifacts(self) -> None:
        agent = ProbeAgent()
        task = Task(
            task_id="analyst-1",
            assigned_agent="Analyst",
            inputs={
                "project_root": str(self.project_root),
                "brief": {"goal": "test build feasibility"},
            },
        )

        result = agent.handle_task(task)

        tests_dir = self.project_root / "tests"
        test_results_path = tests_dir / "test_results.json"
        performance_path = tests_dir / "performance_metrics.json"
        failure_path = tests_dir / "failure_report.json"

        self.assertTrue(tests_dir.exists(), "tests directory should be created")
        self.assertTrue(test_results_path.exists(), "test_results.json should be created")
        self.assertTrue(performance_path.exists(), "performance_metrics.json should be created")
        self.assertTrue(failure_path.exists(), "failure_report.json should be created")

        with test_results_path.open("r", encoding="utf-8") as f:
            test_results = json.load(f)
        with performance_path.open("r", encoding="utf-8") as f:
            metrics = json.load(f)
        with failure_path.open("r", encoding="utf-8") as f:
            failures = json.load(f)

        self.assertIn("summary", test_results)
        self.assertIn("feasible", test_results)
        self.assertIsInstance(metrics, dict)
        self.assertIsInstance(failures, list)

        self.assertIn("test_results_path", result.outputs)
        self.assertIn("performance_metrics_path", result.outputs)
        self.assertIn("failure_report_path", result.outputs)


if __name__ == "__main__":
    unittest.main()
