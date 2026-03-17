from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class RouteDecision:
    """
    Structured routing result returned by AIRouter.

    page:
        The originating UI page or intended system area.

    pipeline_type:
        High-level execution mode.

    build_type:
        More specific subtype if applicable.

    agents:
        Initial agent chain suggestion. In Gate 1, this will usually be a
        single agent so the supervisor can execute something real.

    metadata:
        Extra structured details that later gates can use.
    """

    page: str
    pipeline_type: str
    build_type: str
    agents: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AIRouter:
    """
    Gate 1 router.

    Responsibilities:
    - Accept raw request input
    - Determine which page / pipeline type it belongs to
    - Suggest an initial agent list
    - Return a structured RouteDecision

    This is intentionally simple for Gate 1.
    """

    def __init__(self) -> None:
        self._page_keywords = {
            "assets": ["asset", "3d", "model", "mesh", "texture", "material", "fbx", "obj"],
            "builds": ["build", "app", "system", "backend", "firmware", "os", "desktop", "mobile", "web"],
            "sandbox": ["autonomous", "emergent", "adaptive", "self-healing", "dynamic"],
            "research": ["research", "learn", "training", "memory", "knowledge", "ingest", "document", "video", "audio"],
            "game_dev": ["unity", "unreal", "game", "inventory", "combat", "hud", "level", "player"],
            "deployment": ["deploy", "release", "publish", "package", "ship", "hosting", "environment"],
        }

        self._default_agents = {
            "assets": ["asset_planner_agent"],
            "builds": ["planner_agent"],
            "sandbox": ["adaptive_planner_agent"],
            "research": ["research_ingest_agent"],
            "game_dev": ["game_planner_agent"],
            "deployment": ["deployment_planner_agent"],
            "general": ["planner_agent"],
        }

    def route_request(
        self,
        request: str,
        page_hint: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RouteDecision:
        """
        Route a raw user request into a structured decision.

        Args:
            request: User request text.
            page_hint: Optional direct UI page hint from frontend.
            metadata: Optional extra context.

        Returns:
            RouteDecision
        """
        if not isinstance(request, str) or not request.strip():
            raise ValueError("route_request requires a non-empty request string.")

        clean_request = request.strip()
        lower_request = clean_request.lower()
        meta = metadata.copy() if metadata else {}

        page = self._resolve_page(lower_request, page_hint)
        pipeline_type = self._resolve_pipeline_type(page)
        build_type = self._resolve_build_type(lower_request, page)
        agents = self._resolve_agents(page, lower_request)

        meta.update(
            {
                "original_request": clean_request,
                "page_hint": page_hint,
                "keyword_page_match": page,
                "gate": 1,
            }
        )

        return RouteDecision(
            page=page,
            pipeline_type=pipeline_type,
            build_type=build_type,
            agents=agents,
            metadata=meta,
        )

    def _resolve_page(self, request: str, page_hint: Optional[str]) -> str:
        """
        Determine which page/system area best matches the request.
        """
        if page_hint:
            normalized = page_hint.strip().lower().replace(" ", "_")
            if normalized in self._default_agents:
                return normalized

        scores: Dict[str, int] = {page: 0 for page in self._page_keywords}

        for page, keywords in self._page_keywords.items():
            for keyword in keywords:
                if keyword in request:
                    scores[page] += 1

        if "unity" in request:
            scores["game_dev"] += 2
        if "unreal" in request:
            scores["game_dev"] += 2

        best_page = max(scores, key=lambda page: scores[page])
        if scores[best_page] == 0:
            return "builds"

        return best_page

    def _resolve_pipeline_type(self, page: str) -> str:
        """
        Gate 1 simplified pipeline mapping.
        """
        pipeline_map = {
            "assets": "asset_execution",
            "builds": "structured_execution",
            "sandbox": "adaptive_execution",
            "research": "learning_ingestion",
            "game_dev": "domain_execution",
            "deployment": "deployment_execution",
        }
        return pipeline_map.get(page, "structured_execution")

    def _resolve_build_type(self, request: str, page: str) -> str:
        """
        Lightweight subtype classification for Gate 1.
        """
        if page == "assets":
            if any(word in request for word in ["texture", "material"]):
                return "asset_material"
            if any(word in request for word in ["3d", "model", "mesh"]):
                return "asset_3d"
            return "asset_general"

        if page == "game_dev":
            if "unity" in request:
                return "unity_system"
            if "unreal" in request:
                return "unreal_system"
            return "game_system"

        if page == "research":
            return "knowledge_ingestion"

        if page == "deployment":
            return "deployment_job"

        if page == "sandbox":
            return "emergent_build"

        if any(word in request for word in ["os", "firmware"]):
            return "os_or_firmware"

        if "backend" in request:
            return "backend_system"

        if "app" in request:
            return "application"

        return "general_build"

    def _resolve_agents(self, page: str, request: str) -> List[str]:
        """
        Suggest the initial agent chain.

        Gate 1 stays intentionally minimal. Usually one agent is enough.
        """
        if page == "game_dev":
            if "unity" in request:
                return ["unity_planner_agent"]
            if "unreal" in request:
                return ["unreal_planner_agent"]

        if page == "assets":
            if "texture" in request or "material" in request:
                return ["texture_planner_agent"]

        return self._default_agents.get(page, self._default_agents["general"])


if __name__ == "__main__":
    router = AIRouter()

    example = router.route_request(
        request="Build a Unity inventory system with UI and item data",
        page_hint=None,
        metadata={"source": "manual_test"},
    )

    print("=== ROUTE DECISION ===")
    print(f"page: {example.page}")
    print(f"pipeline_type: {example.pipeline_type}")
    print(f"build_type: {example.build_type}")
    print(f"agents: {example.agents}")
    print(f"metadata: {example.metadata}")
