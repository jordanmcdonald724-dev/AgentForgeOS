from __future__ import annotations

import shutil
from pathlib import Path
import unittest

from agents.v2.frontend_engineer import FrontendEngineerAgent
from agents.v2.backend_engineer import BackendEngineerAgent
from orchestration.task_model import Task


class TestV2FrontendBackendAgents(unittest.TestCase):
    """Tests for SURFACE (Frontend) and CORE (Backend) agents."""

    def setUp(self) -> None:
        self.project_root = Path("projects") / "test_fe_be_agents"
        if self.project_root.exists():
            shutil.rmtree(self.project_root)

    def tearDown(self) -> None:
        if self.project_root.exists():
            shutil.rmtree(self.project_root)

    def test_frontend_engineer_scaffolds_v2_pages(self) -> None:
        agent = FrontendEngineerAgent()
        task = Task(
            task_id="cmd:frontend",
            assigned_agent="Frontend Engineer",
            inputs={"project_root": str(self.project_root)},
        )

        result = agent.handle_task(task)
        outputs = result.outputs

        project_root = Path(outputs["project_root"])
        pages_root = project_root / "frontend" / "src" / "pages"
        components_root = project_root / "frontend" / "src" / "components"

        self.assertTrue((pages_root / "CommandCenter.tsx").is_file())
        self.assertTrue((pages_root / "ProjectWorkspace.tsx").is_file())
        self.assertTrue((pages_root / "ResearchLab.tsx").is_file())
        self.assertTrue((components_root / "AppShell.tsx").is_file())

    def test_backend_engineer_scaffolds_api_services_models(self) -> None:
        agent = BackendEngineerAgent()
        task = Task(
            task_id="cmd:backend",
            assigned_agent="Backend Engineer",
            inputs={"project_root": str(self.project_root)},
        )

        result = agent.handle_task(task)
        outputs = result.outputs

        project_root = Path(outputs["project_root"])
        backend_root = project_root / "backend"

        api_main = backend_root / "api" / "routes.py"
        service_file = backend_root / "services" / "project_service.py"
        model_file = backend_root / "models" / "project.py"

        self.assertTrue(api_main.is_file())
        self.assertTrue(service_file.is_file())
        self.assertTrue(model_file.is_file())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
