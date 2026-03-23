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
from services.system_designer import SystemDesigner
from services.architecture_engine import ArchitectureEngine
from services.build_pipeline import BuildPipeline
from agents.planner_agent import PlannerAgent
from agents.unity_planner_agent import UnityPlannerAgent
from agents.unreal_planner_agent import UnrealPlannerAgent


def setup_pipeline() -> BuildPipeline:
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

    supervisor.register_agent(PlannerAgent())
    supervisor.register_agent(UnityPlannerAgent())
    supervisor.register_agent(UnrealPlannerAgent())

    agent_pipeline = AgentPipeline(
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

    system_designer = SystemDesigner()
    architecture_engine = ArchitectureEngine()

    return BuildPipeline(
        router=router,
        agent_pipeline=agent_pipeline,
        system_designer=system_designer,
        architecture_engine=architecture_engine,
        learning_controller=learning_controller,
    )


def run_example(build_pipeline: BuildPipeline, request: str) -> None:
    print("\n=== Running Build ===")
    print(f"Request: {request}")
    result = build_pipeline.run_build(request)

    print("\nDesign:")
    print(result["design"])

    print("\nArchitecture:")
    print(result["architecture"])

    print("\nAgent Sequence:")
    print(result["agent_sequence"])

    print("\nPipeline Result:")
    pipeline_result = result["pipeline_result"]
    print(f"status: {pipeline_result.get('status')}")
    print(f"final_output: {pipeline_result.get('final_output')}")
    print(f"metadata: {pipeline_result.get('metadata')}")


def main() -> None:
    build_pipeline = setup_pipeline()
    run_example(build_pipeline, "Build a Unity inventory system with UI")
    run_example(build_pipeline, "Build a web app with login and data storage")


if __name__ == "__main__":
    main()
