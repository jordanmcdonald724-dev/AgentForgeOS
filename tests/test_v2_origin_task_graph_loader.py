import json
import shutil
from pathlib import Path
import unittest

from agents.v2.commander import CommanderAgent
from orchestration.engine import OrchestrationEngine
from orchestration.task_model import Task


class TestV2OriginTaskGraphLoader(unittest.TestCase):
    def setUp(self) -> None:
        self.project_root = Path("projects/test_origin_graph")
        if self.project_root.exists():
            shutil.rmtree(self.project_root)
        self.project_root.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        if self.project_root.exists():
            shutil.rmtree(self.project_root)

    def test_create_tasks_from_origin_graph(self) -> None:
        # First have Origin write task_graph.json for this project.
        agent = CommanderAgent()
        task = Task(
            task_id="origin-1",
            assigned_agent="Origin",
            inputs={"command": "build a small game", "project_root": str(self.project_root)},
        )
        agent.handle_task(task)

        spec_path = self.project_root / "task_graph.json"
        self.assertTrue(spec_path.exists(), "task_graph.json should be created by Origin")

        # Now load tasks from the spec using the engine helper.
        engine = OrchestrationEngine()
        created = engine.create_tasks_from_origin_graph(self.project_root)

        self.assertGreaterEqual(len(created), 7)
        ids = {t.task_id for t in created}
        self.assertIn("t0", ids)
        self.assertIn("t6", ids)

        # Every created task should have declared_outputs populated
        # according to the central contract mapping.
        for t in created:
            with self.subTest(task=t.task_id):
                self.assertTrue(t.declared_outputs, f"Task {t.task_id} missing declared_outputs")
                for raw in t.declared_outputs:
                    self.assertTrue(str(raw).startswith(str(self.project_root)))


if __name__ == "__main__":
    unittest.main()
