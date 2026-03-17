from control.ai_router import AIRouter
from control.agent_supervisor import AgentSupervisor
from agents.planner_agent import PlannerAgent
from agents.unity_planner_agent import UnityPlannerAgent
from agents.unreal_planner_agent import UnrealPlannerAgent


def main() -> None:
    router = AIRouter()
    supervisor = AgentSupervisor()

    supervisor.register_agent(PlannerAgent())
    supervisor.register_agent(UnityPlannerAgent())
    supervisor.register_agent(UnrealPlannerAgent())
    # Gate 1 quick test now uses Gate 2 compliant agents

    request = "Build a Unity inventory system with UI and item data"

    decision = router.route_request(request=request)

    result = supervisor.run_registered_agent(
        agent_name=decision.agents[0],
        input_data={"request": request},
        route_context={
            "page": decision.page,
            "pipeline_type": decision.pipeline_type,
            "build_type": decision.build_type,
            "metadata": decision.metadata,
        },
    )

    print("\n=== ROUTE DECISION ===")
    print(decision)

    print("\n=== EXECUTION RESULT ===")
    print(
        f"status={result.status} agent={result.agent_name} "
        f"confidence={result.confidence:.2f} output={result.output}"
    )


if __name__ == "__main__":
    main()
