import json
import shutil
from pathlib import Path
import unittest

from agents.v2.devops_engineer import DevOpsEngineerAgent
from orchestration.task_model import Task


class TestV2LauncherAgent(unittest.TestCase):
    def setUp(self) -> None:
        self.project_root = Path("projects/test_launcher_project")
        if self.project_root.exists():
            shutil.rmtree(self.project_root)

    def tearDown(self) -> None:
        if self.project_root.exists():
            shutil.rmtree(self.project_root)

    def test_launcher_writes_deployment_artifacts(self) -> None:
        agent = DevOpsEngineerAgent()
        task = Task(
            task_id="launcher-1",
            assigned_agent="Launcher",
            inputs={"project_root": str(self.project_root), "environment": "dev"},
        )

        result = agent.handle_task(task)

        deploy_dir = self.project_root / "deploy"
        logs_dir = deploy_dir / "logs"
        env_dir = deploy_dir / "env"
        deployment_plan_path = deploy_dir / "deployment_plan.json"
        build_log_path = logs_dir / "build.log"
        env_path = env_dir / "environment.json"

        self.assertTrue(deploy_dir.exists(), "deploy directory should be created")
        self.assertTrue(logs_dir.exists(), "logs directory should be created")
        self.assertTrue(env_dir.exists(), "env directory should be created")
        self.assertTrue(deployment_plan_path.exists(), "deployment_plan.json should be created")
        self.assertTrue(build_log_path.exists(), "build.log should be created")
        self.assertTrue(env_path.exists(), "environment.json should be created")

        with deployment_plan_path.open("r", encoding="utf-8") as f:
            plan = json.load(f)
        with env_path.open("r", encoding="utf-8") as f:
            env = json.load(f)

        self.assertIn("steps", plan)
        self.assertEqual(env.get("environment"), "dev")

        self.assertIn("deployment_plan_path", result.outputs)
        self.assertIn("build_log_path", result.outputs)
        self.assertIn("environment_path", result.outputs)


if __name__ == "__main__":
    unittest.main()
