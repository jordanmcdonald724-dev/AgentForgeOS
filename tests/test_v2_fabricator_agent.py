import json
import shutil
from pathlib import Path
import unittest

from agents.v2.prism import PrismAgent
from orchestration.task_model import Task


class TestV2FabricatorAgent(unittest.TestCase):
    def setUp(self) -> None:
        self.project_root = Path("projects/test_fabricator_project")
        if self.project_root.exists():
            shutil.rmtree(self.project_root)

    def tearDown(self) -> None:
        if self.project_root.exists():
            shutil.rmtree(self.project_root)

    def test_fabricator_creates_assets_and_manifest(self) -> None:
        agent = PrismAgent()
        task = Task(
            task_id="fabricator-1",
            assigned_agent="Fabricator",
            inputs={"project_root": str(self.project_root)},
        )

        result = agent.handle_task(task)

        assets_root = self.project_root / "assets"
        manifest_path = assets_root / "asset_manifest.json"
        ui_manifest = assets_root / "ui" / "core_ui_manifest.md"
        audio_manifest = assets_root / "audio" / "core_audio_manifest.md"

        self.assertTrue(assets_root.exists(), "assets directory should be created")
        self.assertTrue(manifest_path.exists(), "asset_manifest.json should be created")
        self.assertTrue(ui_manifest.exists(), "UI bundle manifest should be created")
        self.assertTrue(audio_manifest.exists(), "Audio bundle manifest should be created")

        with manifest_path.open("r", encoding="utf-8") as f:
            manifest = json.load(f)

        self.assertEqual(str(self.project_root), manifest.get("project_root"))
        self.assertEqual(str(assets_root), manifest.get("assets_root"))
        self.assertIn("bundles", manifest)
        self.assertGreaterEqual(len(manifest["bundles"]), 2)

        self.assertIn("assets_root", result.outputs)
        self.assertIn("asset_manifest_path", result.outputs)


if __name__ == "__main__":
    unittest.main()
