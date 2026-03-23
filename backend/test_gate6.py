from control.ai_router import AIRouter
from control.agent_supervisor import AgentSupervisor
from control.agent_pipeline import AgentPipeline
from control.execution_monitor import ExecutionMonitor
from control.scoring_engine import ScoringEngine
from control.recovery_engine import RecoveryEngine
from control.learning_controller import LearningController
from knowledge.context_index import ContextIndex
from services.execution_history import ExecutionHistory
from agents.base_agent import BaseAgent


class MemoryAgent(BaseAgent):
    """
    Simple deterministic agent for Gate 6 testing.
    """

    def __init__(self, name: str) -> None:
        super().__init__(name=name, description="Memory test agent", capabilities=["test"])

    def run(self, input_data):  # type: ignore[override]
        return {
            "summary": f"Plan for {input_data.get('request')}",
            "engine": "unity",
            "suggested_steps": ["step1", "step2"],
            "assumptions": [],
        }


def print_context(label: str, data: dict) -> None:
    print(f"\n=== {label} ===")
    print(f"recommended_agents: {data.get('recommended_agents')}")
    print(f"similar_runs: {data.get('similar_runs')}")
    print(f"warnings: {data.get('warnings')}")


def main() -> None:
    context_index = ContextIndex()
    execution_history = ExecutionHistory()
    learning_controller = LearningController(context_index, execution_history)

    router = AIRouter(learning_controller=learning_controller)
    supervisor = AgentSupervisor()
    monitor = ExecutionMonitor()
    scoring = ScoringEngine()
    recovery = RecoveryEngine()
    pipeline = AgentPipeline(
        supervisor,
        monitor=monitor,
        scoring_engine=scoring,
        history=execution_history,
        recovery_engine=recovery,
        learning_controller=learning_controller,
    )

    request_text = "Build a Unity inventory system"

    # Register agent matching router choice.
    supervisor.register_agent(MemoryAgent("unity_planner_agent"))

    # First run (no memory yet).
    route1 = router.route_request(request_text)
    print_context("ROUTER CONTEXT FIRST RUN", route1.metadata.get("context_insights", {}))
    result1 = pipeline.run_pipeline(
        agent_names=route1.agents,
        initial_input={"request": request_text},
        route_context=route1.metadata,
    )
    print(f"\nFirst run status: {result1.status}")
    print(f"First run similar_runs_count: {result1.metadata.get('similar_runs_count')}")

    # Second run (should see similar history).
    route2 = router.route_request(request_text)
    print_context("ROUTER CONTEXT SECOND RUN", route2.metadata.get("context_insights", {}))
    result2 = pipeline.run_pipeline(
        agent_names=route2.agents,
        initial_input={"request": request_text},
        route_context=route2.metadata,
    )
    print(f"\nSecond run status: {result2.status}")
    print(f"Second run similar_runs_count: {result2.metadata.get('similar_runs_count')}")
    print(f"Recommended agents used: {result2.metadata.get('recommended_agents_used')}")

    # Inspect stored context entries.
    similar = context_index.query_similar(request_text, top_k=5)
    print("\n=== STORED CONTEXT ENTRIES ===")
    for idx, entry in enumerate(similar):
        print(
            f"{idx}: signature={entry.request_signature} agents={entry.pipeline_agents} "
            f"success={entry.success} score={entry.score}"
        )

    print("\n=== EXECUTION HISTORY ===")
    for record in execution_history.list_all():
        print(f"{record.pipeline_id}: status={record.status} score={record.score} steps={len(record.steps)}")


if __name__ == "__main__":
    main()
