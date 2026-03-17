from control.ai_router import AIRouter
from control.agent_supervisor import (
    AdaptivePlannerAgent,
    AgentSupervisor,
    AssetPlannerAgent,
    DeploymentPlannerAgent,
    GamePlannerAgent,
    PlannerAgent,
    ResearchIngestAgent,
    TexturePlannerAgent,
    UnrealPlannerAgent,
    UnityPlannerAgent,
)


def main() -> None:
    router = AIRouter()
    supervisor = AgentSupervisor()

    supervisor.register_agent(PlannerAgent())
    supervisor.register_agent(UnityPlannerAgent())
    supervisor.register_agent(UnrealPlannerAgent())
    supervisor.register_agent(AssetPlannerAgent())
    supervisor.register_agent(TexturePlannerAgent())
    supervisor.register_agent(AdaptivePlannerAgent())
    supervisor.register_agent(ResearchIngestAgent())
    supervisor.register_agent(GamePlannerAgent())
    supervisor.register_agent(DeploymentPlannerAgent())

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
    print(result)


if __name__ == "__main__":
    main()
