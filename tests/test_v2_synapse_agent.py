import json
import shutil
from pathlib import Path
import unittest

from agents.v2.ai_engineer import AIEngineerAgent
from orchestration.task_model import Task


class TestV2SynapseAgent(unittest.TestCase):
    def setUp(self) -> None:
        self.project_root = Path("projects/test_synapse_project")
        if self.project_root.exists():
            shutil.rmtree(self.project_root)

    def tearDown(self) -> None:
        if self.project_root.exists():
            shutil.rmtree(self.project_root)

    def test_synapse_writes_model_routes_and_logs(self) -> None:
        agent = AIEngineerAgent()
        task = Task(
            task_id="synapse-1",
            assigned_agent="Synapse",
            inputs={
                "project_root": str(self.project_root),
                "use_case": "code",
            },
        )

        result = agent.handle_task(task)

        routes_path = self.project_root / "model_routes.json"
        logs_path = self.project_root / "inference_logs.json"

        self.assertTrue(routes_path.exists(), "model_routes.json should be created")
        self.assertTrue(logs_path.exists(), "inference_logs.json should be created")

        with routes_path.open("r", encoding="utf-8") as f:
            routes = json.load(f)
        with logs_path.open("r", encoding="utf-8") as f:
            logs = json.load(f)

        self.assertEqual(routes.get("use_case"), "code")
        self.assertIn("route", routes)
        self.assertIsInstance(logs, list)
        self.assertGreaterEqual(len(logs), 1)

        self.assertIn("model_routes_path", result.outputs)
        self.assertIn("inference_logs_path", result.outputs)


if __name__ == "__main__":
    unittest.main()
