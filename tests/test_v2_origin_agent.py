from __future__ import annotations

import json
import shutil
from pathlib import Path
import unittest

from agents.v2.commander import CommanderAgent
from orchestration.task_model import Task


class TestV2OriginAgent(unittest.TestCase):
    """Tests for ORIGIN (Commander) agent behavior and artifacts."""

    def setUp(self) -> None:
        self.project_root = Path("projects") / "test_origin_agent"
        if self.project_root.exists():
            shutil.rmtree(self.project_root)

    def tearDown(self) -> None:
        if self.project_root.exists():
            shutil.rmtree(self.project_root)

    def test_commander_produces_intent_and_graph_artifacts(self) -> None:
        agent = CommanderAgent()
        task = Task(
            task_id="cmd:root",
            assigned_agent="Commander",
            inputs={
                "command": "build a small web app",
                "project_root": str(self.project_root),
            },
        )

        result = agent.handle_task(task)
        outputs = result.outputs

        intent_path = Path(outputs["intent_path"])
        task_graph_path = Path(outputs["task_graph_path"])
        build_plan_path = Path(outputs["build_plan_path"])

        self.assertTrue(intent_path.is_file())
        self.assertTrue(task_graph_path.is_file())
        self.assertTrue(build_plan_path.is_file())

        intent = json.loads(intent_path.read_text(encoding="utf-8"))
        self.assertEqual(intent["product_type"], "web")
        self.assertIn("scope", intent)

        task_graph = json.loads(task_graph_path.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(task_graph), 3)

        build_plan = json.loads(build_plan_path.read_text(encoding="utf-8"))
        self.assertIn("tasks", build_plan)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
