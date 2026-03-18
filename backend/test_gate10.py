from control.ai_router import AIRouter
from control.agent_pipeline import AgentPipeline
from control.agent_supervisor import AgentSupervisor
from control.dynamic_pipeline_builder import DynamicPipelineBuilder
from control.execution_monitor import ExecutionMonitor
from control.learning_controller import LearningController
from control.recovery_engine import RecoveryEngine
from control.scoring_engine import ScoringEngine
from control.agent_factory import AgentFactory
from control.emergent_orchestrator import EmergentOrchestrator
from services.live_execution_loop import LiveExecutionLoop
from knowledge.context_index import ContextIndex
from services.execution_history import ExecutionHistory
from agents.planner_agent import PlannerAgent
from agents.base_agent import BaseAgent


class FailureAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__("failure_agent", "Always fails", ["fail"])

    def run(self, input_data):
        raise RuntimeError("intentional failure")


def build_system():
    context_index = ContextIndex()
    execution_history = ExecutionHistory()
    learning_controller = LearningController(context_index, execution_history)

    router = AIRouter(learning_controller=learning_controller)
    supervisor = AgentSupervisor()
    supervisor.register_agent(PlannerAgent())
    supervisor.register_agent(FailureAgent())

    monitor = ExecutionMonitor()
    scoring = ScoringEngine()
    recovery = RecoveryEngine(max_retries_per_step=0)
    builder = DynamicPipelineBuilder()
    factory = AgentFactory()

    pipeline = AgentPipeline(
        supervisor,
        monitor=monitor,
        scoring_engine=scoring,
        history=execution_history,
        recovery_engine=recovery,
        learning_controller=learning_controller,
        dynamic_pipeline_builder=builder,
        agent_factory=factory,
        max_steps=10,
    )

    orchestrator = EmergentOrchestrator(
        router=router,
        pipeline=pipeline,
        learning_controller=learning_controller,
        dynamic_builder=builder,
        agent_factory=factory,
    )

    loop = LiveExecutionLoop(orchestrator=orchestrator, pipeline=pipeline)
    return loop, orchestrator, monitor


def main() -> None:
    loop, orchestrator, monitor = build_system()

    print("\n=== Gate 10: Success-oriented request ===")
    success_request = "Build a Unity inventory system"
    success_result = loop.run(success_request, max_iterations=3)
    print(f"Iterations: {success_result['iterations']}")
    print(f"Final pipeline: {success_result['final_pipeline']}")
    print(f"Final result status: {success_result['final_result'].get('status')}")
    print(f"Score: {success_result['final_result'].get('metadata', {}).get('pipeline_score')}")

    print("\n=== Gate 10: Failure then adaptation ===")
    # Force an initial failing agent to trigger adaptation on next iteration.
    def failing_init_task(request: str):
        return {"agent_sequence": ["failure_agent"], "context": {"request": request}}

    orchestrator.initialize_task = failing_init_task  # type: ignore[assignment]
    failure_request = "Cause an adaptation cycle"
    failure_result = loop.run(failure_request, max_iterations=3)
    print(f"Iterations: {failure_result['iterations']}")
    print(f"Final pipeline after adaptation: {failure_result['final_pipeline']}")
    print(f"Final result status: {failure_result['final_result'].get('status')}")
    print(f"Score: {failure_result['final_result'].get('metadata', {}).get('pipeline_score')}")

    print("\n=== Monitor Events ===")
    for event in monitor.get_events():
        print(f"{event.event_type} | iter={event.data.get('iteration')} | step={event.step_index} | agent={event.agent_name}")


if __name__ == "__main__":
    main()
