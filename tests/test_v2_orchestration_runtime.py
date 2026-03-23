import unittest

from orchestration.runtime import OrchestrationRuntime
from orchestration.task_model import TaskStatus


class TestV2OrchestrationRuntime(unittest.TestCase):
    def test_simple_command_flow_completes(self) -> None:
        import asyncio
        runtime = OrchestrationRuntime()
        runtime.submit_command("build a sample project")
        asyncio.run(runtime.run_all())

        tasks = runtime.list_tasks()
        self.assertGreaterEqual(len(tasks), 4)

        # All tasks in the minimal graph should be completed or blocked,
        # but none should remain pending.
        statuses = {t.status for t in tasks.values()}
        self.assertNotIn(TaskStatus.PENDING, statuses)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
