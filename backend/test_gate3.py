from control.ai_router import AIRouter
from control.agent_supervisor import AgentSupervisor
from control.agent_pipeline import AgentPipeline
from agents.planner_agent import PlannerAgent
from agents.unity_planner_agent import UnityPlannerAgent
from agents.unreal_planner_agent import UnrealPlannerAgent


def print_pipeline_result(label: str, result) -> None:
    print(f"\n=== {label} ===")
    print(f"pipeline_id: {result.pipeline_id}")
    print(f"status: {result.status}")
    print(f"failed_step_index: {result.failed_step_index}")
    print("steps:")
    for step in result.steps:
        print(
            f"  [{step.step_index}] {step.agent_name} -> {step.status} "
            f"duration_ms={step.duration_ms:.2f} output={step.output_data}"
        )
    print(f"final_output: {result.final_output}")
    print(f"metadata: {result.metadata}")


def main() -> None:
    router = AIRouter()
    supervisor = AgentSupervisor()
    pipeline = AgentPipeline(supervisor)

    supervisor.register_agent(PlannerAgent())
    supervisor.register_agent(UnityPlannerAgent())
    supervisor.register_agent(UnrealPlannerAgent())

    success_pipeline = ["planner_agent", "unity_planner_agent"]
    initial_input = {"request": "Build a Unity inventory system"}
    route_decision = router.route_request(request=initial_input["request"])
    success_result = pipeline.run_pipeline(
        agent_names=success_pipeline,
        initial_input=initial_input,
        route_context={
            "page": route_decision.page,
            "pipeline_type": route_decision.pipeline_type,
            "build_type": route_decision.build_type,
            "metadata": route_decision.metadata,
        },
    )
    print_pipeline_result("SUCCESS PIPELINE", success_result)

    failure_pipeline = ["planner_agent", "ghost_agent", "unity_planner_agent"]
    failure_result = pipeline.run_pipeline(
        agent_names=failure_pipeline,
        initial_input=initial_input,
        route_context=None,
    )
    print_pipeline_result("FAILURE PIPELINE", failure_result)


if __name__ == "__main__":
    main()
