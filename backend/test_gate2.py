from control.ai_router import AIRouter
from control.agent_supervisor import AgentSupervisor
from agents.planner_agent import PlannerAgent
from agents.unity_planner_agent import UnityPlannerAgent
from agents.unreal_planner_agent import UnrealPlannerAgent


def run_case(supervisor: AgentSupervisor, router: AIRouter, request: str) -> None:
    decision = router.route_request(request=request)
    agent_name = decision.agents[0]

    result = supervisor.run_registered_agent(
        agent_name=agent_name,
        input_data={"request": request},
        route_context={
            "page": decision.page,
            "pipeline_type": decision.pipeline_type,
            "build_type": decision.build_type,
            "metadata": decision.metadata,
        },
    )

    print("\n----------------------------------------")
    print(f"Request: {request}")
    print(f"RouteDecision: page={decision.page}, pipeline={decision.pipeline_type}, build={decision.build_type}")
    print(f"Selected Agent: {agent_name}")
    print(f"Result Status: {result.status}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Output: {result.output}")
    print("----------------------------------------")


def main() -> None:
    router = AIRouter()
    supervisor = AgentSupervisor()

    supervisor.register_agent(PlannerAgent())
    supervisor.register_agent(UnityPlannerAgent())
    supervisor.register_agent(UnrealPlannerAgent())

    requests = [
        "Build a backend API with auth and CRUD",
        "Build a Unity inventory system with UI and item data",
        "Create an Unreal combat system with UI and save game",
    ]

    for req in requests:
        run_case(supervisor, router, req)


if __name__ == "__main__":
    main()
