from __future__ import annotations

import shutil
from pathlib import Path
import unittest

from agents.v2.forge import ForgeAgent
from orchestration.task_model import Task


class TestV2BuilderAgent(unittest.TestCase):
    """Tests for BUILDER (Forge) agent behavior and artifacts."""

    def setUp(self) -> None:
        self.project_root = Path("projects") / "test_builder_agent"
        if self.project_root.exists():
            shutil.rmtree(self.project_root)

    def tearDown(self) -> None:
        if self.project_root.exists():
            shutil.rmtree(self.project_root)

    def test_forge_creates_project_structure_and_backend_scaffold(self) -> None:
        agent = ForgeAgent()
        task = Task(
            task_id="cmd:build",
            assigned_agent="Forge",
            inputs={"project_root": str(self.project_root)},
        )

        result = agent.handle_task(task)
        outputs = result.outputs

        project_root = Path(outputs["project_root"])
        backend_root = project_root / "backend"
        gameplay_root = project_root / "gameplay"
        systems_root = project_root / "systems"
        scripts_root = project_root / "scripts"

        self.assertTrue(backend_root.is_dir())
        self.assertTrue(gameplay_root.is_dir())
        self.assertTrue(systems_root.is_dir())
        self.assertTrue(scripts_root.is_dir())

        app_py = backend_root / "app.py"
        routes_py = backend_root / "routes.py"
        self.assertTrue(app_py.is_file())
        self.assertTrue(routes_py.is_file())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
