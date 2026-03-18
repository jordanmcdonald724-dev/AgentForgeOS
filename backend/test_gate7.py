from control.ai_router import AIRouter
from control.agent_supervisor import AgentSupervisor
from control.agent_pipeline import AgentPipeline
from control.execution_monitor import ExecutionMonitor
from control.scoring_engine import ScoringEngine
from control.recovery_engine import RecoveryEngine
from control.learning_controller import LearningController
from control.dynamic_pipeline_builder import DynamicPipelineBuilder
from control.agent_factory import AgentFactory
from knowledge.context_index import ContextIndex
from services.execution_history import ExecutionHistory
from agents.base_agent import BaseAgent
from agents.planner_agent import PlannerAgent


class LowScoreAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__("low_score_agent", "Returns minimal output to trigger adaptation", ["test"])

    def run(self, input_data):
        return {"engine": "test"}  # intentionally sparse to keep score low


class FailureAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__("failure_agent", "Always fails to trigger replacement", ["fail"])

    def run(self, input_data):
        raise RuntimeError("intentional failure")


def main() -> None:
    context_index = ContextIndex()
    execution_history = ExecutionHistory()
    learning_controller = LearningController(context_index, execution_history)

    router = AIRouter(learning_controller=learning_controller)
    supervisor = AgentSupervisor()
    monitor = ExecutionMonitor()
    scoring = ScoringEngine()
    recovery = RecoveryEngine(max_retries_per_step=1)
    builder = DynamicPipelineBuilder()
    factory = AgentFactory()

    supervisor.register_agent(LowScoreAgent())
    supervisor.register_agent(FailureAgent())
    supervisor.register_agent(PlannerAgent())

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

    request_text = "Test adaptive pipeline"
    route = router.route_request(request_text)

    adaptive_agents = ["low_score_agent", "failure_agent"]
    result = pipeline.run_pipeline(
        agent_names=adaptive_agents,
        initial_input={"request": request_text},
        route_context=route.metadata,
    )

    print("\n=== Gate 7 Adaptive Pipeline Result ===")
    print(f"status: {result.status}")
    print(f"final_pipeline: {result.metadata.get('final_pipeline')}")
    print(f"adaptive_changes: {result.metadata.get('adaptive_changes')}")
    print(f"created_agents: {result.metadata.get('created_agents')}")

    print("\n=== Monitor Events ===")
    for event in monitor.get_events():
        print(f"{event.event_type} | step={event.step_index} | agent={event.agent_name} | data={event.data}")

    print("\n=== Execution History ===")
    for record in execution_history.list_all():
        print(f"{record.pipeline_id}: status={record.status} steps={len(record.steps)} score={record.score}")


if __name__ == "__main__":
    main()
