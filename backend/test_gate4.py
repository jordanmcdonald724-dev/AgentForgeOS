from control.ai_router import AIRouter
from control.agent_supervisor import AgentSupervisor
from control.agent_pipeline import AgentPipeline
from control.execution_monitor import ExecutionMonitor
from control.scoring_engine import ScoringEngine
from services.execution_history import ExecutionHistory
from agents.planner_agent import PlannerAgent
from agents.unity_planner_agent import UnityPlannerAgent
from agents.unreal_planner_agent import UnrealPlannerAgent


def print_events(monitor: ExecutionMonitor) -> None:
    print("\n--- Execution Events ---")
    for event in monitor.get_events():
        print(
            f"{event.timestamp} | {event.event_type} | pipeline={event.pipeline_id} "
            f"step={event.step_index} agent={event.agent_name} data={event.data}"
        )


def print_scores(metadata: dict) -> None:
    step_scores = metadata.get("step_scores", [])
    pipeline_score = metadata.get("pipeline_score", {})
    print("\n--- Step Scores ---")
    for idx, score in enumerate(step_scores):
        print(f"step {idx}: score={score.get('score')} confidence={score.get('confidence')} issues={score.get('issues')}")
    print("\n--- Pipeline Score ---")
    print(f"score={pipeline_score.get('score')} confidence={pipeline_score.get('confidence')} issues={pipeline_score.get('issues')}")


def print_history(history: ExecutionHistory) -> None:
    print("\n--- Execution History ---")
    for record in history.list_all():
        print(
            f"pipeline_id={record.pipeline_id} status={record.status} score={record.score} "
            f"created_at={record.created_at} steps={len(record.steps)}"
        )


def main() -> None:
    router = AIRouter()
    supervisor = AgentSupervisor()
    monitor = ExecutionMonitor()
    scoring = ScoringEngine()
    history = ExecutionHistory()
    pipeline = AgentPipeline(supervisor, monitor=monitor, scoring_engine=scoring, history=history)

    supervisor.register_agent(PlannerAgent())
    supervisor.register_agent(UnityPlannerAgent())
    supervisor.register_agent(UnrealPlannerAgent())

    success_pipeline = ["planner_agent", "unity_planner_agent"]
    initial_input = {"request": "Build a Unity inventory system"}
    decision = router.route_request(request=initial_input["request"])
    success_result = pipeline.run_pipeline(
        agent_names=success_pipeline,
        initial_input=initial_input,
        route_context={
            "page": decision.page,
            "pipeline_type": decision.pipeline_type,
            "build_type": decision.build_type,
            "metadata": decision.metadata,
        },
    )

    print("\n=== SUCCESS PIPELINE ===")
    print(f"pipeline_id: {success_result.pipeline_id}")
    print(f"status: {success_result.status}")
    for step in success_result.steps:
        print(
            f"  [{step.step_index}] {step.agent_name} -> {step.status} "
            f"duration_ms={step.duration_ms:.2f} output_keys={list(step.output_data.keys())}"
        )
    print(f"final_output: {success_result.final_output}")
    print_scores(success_result.metadata)

    failure_pipeline = ["planner_agent", "ghost_agent", "unity_planner_agent"]
    failure_result = pipeline.run_pipeline(
        agent_names=failure_pipeline,
        initial_input=initial_input,
        route_context=None,
    )

    print("\n=== FAILURE PIPELINE ===")
    print(f"pipeline_id: {failure_result.pipeline_id}")
    print(f"status: {failure_result.status}")
    for step in failure_result.steps:
        print(
            f"  [{step.step_index}] {step.agent_name} -> {step.status} "
            f"duration_ms={step.duration_ms:.2f} output_keys={list(step.output_data.keys())}"
        )
    print(f"final_output: {failure_result.final_output}")
    print_scores(failure_result.metadata)

    print_events(monitor)
    print_history(history)


if __name__ == "__main__":
    main()
