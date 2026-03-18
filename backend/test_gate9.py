from services.asset_planner import AssetPlanner
from knowledge.reference_analyzer import ReferenceAnalyzer
from systems.model_generator import ModelGenerator
from systems.texture_generator import TextureGenerator
from systems.asset_validator import AssetValidator
from services.asset_registry import AssetRegistry
from services.asset_pipeline import AssetPipeline


def build_pipeline() -> AssetPipeline:
    planner = AssetPlanner()
    analyzer = ReferenceAnalyzer()
    model_generator = ModelGenerator()
    texture_generator = TextureGenerator()
    validator = AssetValidator()
    registry = AssetRegistry()

    return AssetPipeline(
        planner=planner,
        analyzer=analyzer,
        model_generator=model_generator,
        texture_generator=texture_generator,
        validator=validator,
        registry=registry,
    )


def run_example(title: str, request: str, references=None) -> None:
    print(f"\n=== {title} ===")
    pipeline = build_pipeline()
    result = pipeline.run_asset_pipeline(request, references or [])

    print("Plan:", result["plan"])
    print("Validation:", result["validation"])
    print("Asset ID:", result["asset_id"])
    print("Asset Data:", result["asset"])


def main() -> None:
    run_example("Primary flow", "Create a stylized dark fantasy sword for Unreal")

    # Force an initial validation failure to ensure refinement triggers.
    run_example(
        "Refinement flow",
        "Create a lowpoly prop with strict budget 500 triangles",
        references=["dark, grunge, stylized"],
    )


if __name__ == "__main__":
    main()
