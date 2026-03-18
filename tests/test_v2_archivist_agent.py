import json
import shutil
from pathlib import Path
import unittest

from agents.v2.research_agent import ResearchAgent
from orchestration.task_model import Task


class TestV2ArchivistAgent(unittest.TestCase):
    def setUp(self) -> None:
        self.project_root = Path("projects/test_archivist_project")
        if self.project_root.exists():
            shutil.rmtree(self.project_root)

    def tearDown(self) -> None:
        if self.project_root.exists():
            shutil.rmtree(self.project_root)

    def test_archivist_writes_research_artifacts(self) -> None:
        agent = ResearchAgent()
        task = Task(
            task_id="archivist-1",
            assigned_agent="Archivist",
            inputs={
                "project_root": str(self.project_root),
                "brief": {"sources": ["paper1", "repo2"]},
            },
        )

        result = agent.handle_task(task)

        research_dir = self.project_root / "research"
        insights_path = research_dir / "research_insights.json"
        patterns_path = research_dir / "patterns.json"
        systems_path = research_dir / "extracted_systems.json"

        self.assertTrue(research_dir.exists(), "research directory should be created")
        self.assertTrue(insights_path.exists(), "research_insights.json should be created")
        self.assertTrue(patterns_path.exists(), "patterns.json should be created")
        self.assertTrue(systems_path.exists(), "extracted_systems.json should be created")

        with insights_path.open("r", encoding="utf-8") as f:
            insights = json.load(f)

        self.assertEqual(["paper1", "repo2"], insights.get("sources"))
        self.assertIn("high_level_summary", insights)

        self.assertIn("research_insights_path", result.outputs)
        self.assertIn("patterns_path", result.outputs)
        self.assertIn("extracted_systems_path", result.outputs)


if __name__ == "__main__":
    unittest.main()
