from __future__ import annotations

import json
import shutil
from pathlib import Path
import unittest

from agents.v2.atlas import AtlasAgent
from orchestration.task_model import Task


class TestV2ArchitectAgent(unittest.TestCase):
    """Tests for ARCHITECT (Atlas) agent behavior and artifacts."""

    def setUp(self) -> None:
        self.project_root = Path("projects") / "test_architect_agent"
        if self.project_root.exists():
            shutil.rmtree(self.project_root)
        self.project_root.mkdir(parents=True, exist_ok=True)

        # Seed a simple intent.json so Atlas can read product_type/scope.
        intent = {
            "command": "build a small web app",
            "product_type": "web",
            "scope": {"has_gameplay": False},
        }
        (self.project_root / "intent.json").write_text(
            json.dumps(intent, indent=2), encoding="utf-8"
        )

    def tearDown(self) -> None:
        if self.project_root.exists():
            shutil.rmtree(self.project_root)

    def test_atlas_produces_architecture_artifacts(self) -> None:
        agent = AtlasAgent()
        task = Task(
            task_id="cmd:plan",
            assigned_agent="Atlas",
            inputs={"project_root": str(self.project_root)},
        )

        result = agent.handle_task(task)
        outputs = result.outputs

        arch_path = Path(outputs["architecture_path"])
        modules_path = Path(outputs["modules_path"])
        interfaces_path = Path(outputs["interfaces_path"])
        data_models_path = Path(outputs["data_models_path"])

        self.assertTrue(arch_path.is_file())
        self.assertTrue(modules_path.is_file())
        self.assertTrue(interfaces_path.is_file())
        self.assertTrue(data_models_path.is_file())

        architecture = json.loads(arch_path.read_text(encoding="utf-8"))
        self.assertEqual(architecture["product_type"], "web")

        modules = json.loads(modules_path.read_text(encoding="utf-8"))
        self.assertIn("frontend", modules)
        self.assertIn("backend", modules)

        interfaces = json.loads(interfaces_path.read_text(encoding="utf-8"))
        self.assertIn("frontend_backend", interfaces)

        data_models = json.loads(data_models_path.read_text(encoding="utf-8"))
        self.assertIn("Project", data_models)
        self.assertIn("Task", data_models)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
