from control.agent_supervisor import AgentSupervisor
from control.agent_pipeline import AgentPipeline
from control.execution_monitor import ExecutionMonitor
from control.scoring_engine import ScoringEngine
from control.recovery_engine import RecoveryEngine
from services.execution_history import ExecutionHistory
from agents.base_agent import BaseAgent


class FlakyAgent(BaseAgent):
    """
    Fails on first attempt, succeeds on subsequent attempts.
    """

    def __init__(self) -> None:
        super().__init__(name="flaky_agent", description="Fails once then succeeds", capabilities=["test"])
        self.calls = 0

    def run(self, input_data):  # type: ignore[override]
        self.calls += 1
        if self.calls == 1:
            raise ValueError("transient failure")
        return {
            "summary": f"Recovered on attempt {self.calls}",
            "engine": "unity",
            "suggested_steps": [],
            "assumptions": [],
        }


class AlwaysFailAgent(BaseAgent):
    """
    Always raises an error to trigger abort path.
    """

    def __init__(self) -> None:
        super().__init__(name="always_fail_agent", description="Always fails", capabilities=["test"])

    def run(self, input_data):  # type: ignore[override]
        raise RuntimeError("permanent failure")


class PassthroughAgent(BaseAgent):
    """
    Simple success agent to complete pipeline after recovery.
    """

    def __init__(self) -> None:
        super().__init__(name="passthrough_agent", description="Simple pass agent", capabilities=["test"])

    def run(self, input_data):  # type: ignore[override]
        return {
            "summary": "pass-through",
            "engine": "unity",
            "suggested_steps": ["noop"],
            "assumptions": [],
        }


def print_results(title: str, result) -> None:
    print(f"\n=== {title} ===")
    print(f"status: {result.status}")
    print(f"failed_step_index: {result.failed_step_index}")
    for step in result.steps:
        print(
            f"  step {step.step_index} {step.agent_name} -> {step.status} "
            f"retries={step.retry_attempts} duration_ms={step.duration_ms:.2f} error={step.error}"
        )
    print(f"pipeline_score: {result.metadata.get('pipeline_score')}")


def main() -> None:
    supervisor = AgentSupervisor()
    monitor = ExecutionMonitor()
    scoring = ScoringEngine()
    recovery = RecoveryEngine(max_retries_per_step=2)
    history = ExecutionHistory()
    pipeline = AgentPipeline(
        supervisor,
        monitor=monitor,
        scoring_engine=scoring,
        history=history,
        recovery_engine=recovery,
    )

    supervisor.register_agent(FlakyAgent())
    supervisor.register_agent(PassthroughAgent())
    supervisor.register_agent(AlwaysFailAgent())

    success_result = pipeline.run_pipeline(
        agent_names=["flaky_agent", "passthrough_agent"],
        initial_input={"request": "Test recovery"},
        route_context=None,
    )
    print_results("RECOVERY SUCCESS", success_result)

    print("\n--- Monitor Events (Success run) ---")
    for event in monitor.get_events(success_result.pipeline_id):
        print(f"{event.event_type} step={event.step_index} retry={event.data.get('retry_attempt')}")

    failure_result = pipeline.run_pipeline(
        agent_names=["always_fail_agent"],
        initial_input={"request": "Test abort"},
        route_context=None,
    )
    print_results("RECOVERY ABORT", failure_result)

    print("\n--- Monitor Events (Abort run) ---")
    for event in monitor.get_events(failure_result.pipeline_id):
        print(f"{event.event_type} step={event.step_index} retry={event.data.get('retry_attempt')}")

    print("\n--- Execution History ---")
    for record in history.list_all():
        print(f"{record.pipeline_id}: status={record.status} score={record.score} steps={len(record.steps)}")


if __name__ == "__main__":
    main()
