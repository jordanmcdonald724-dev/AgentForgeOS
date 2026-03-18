import unittest

from build_system.recursive_loop import RecursiveBuilder
from orchestration.engine import OrchestrationEngine
from orchestration.task_model import Task, TaskStatus


class TestRecursiveBuilder(unittest.TestCase):
    def test_describe_stages(self) -> None:
        engine = OrchestrationEngine()
        builder = RecursiveBuilder(engine=engine)
        desc = builder.describe()
        self.assertIn("stages", desc)
        self.assertGreaterEqual(len(desc["stages"]), 1)

    def test_is_complete_false_when_no_tasks(self) -> None:
        engine = OrchestrationEngine()
        builder = RecursiveBuilder(engine=engine)
        self.assertFalse(builder.is_complete())

    def test_is_complete_true_when_all_done(self) -> None:
        engine = OrchestrationEngine()
        engine.add_task(Task(task_id="t1", assigned_agent="Origin", status=TaskStatus.COMPLETED))
        engine.add_task(Task(task_id="t2", assigned_agent="Builder", status=TaskStatus.BLOCKED))
        builder = RecursiveBuilder(engine=engine)
        self.assertTrue(builder.is_complete())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
