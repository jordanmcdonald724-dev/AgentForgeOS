from __future__ import annotations

import unittest
from pathlib import Path

from infrastructure.local_bridge import LocalBridgeSettings, LocalBridge, DEFAULT_ROOT
from infrastructure.model_router import ModelRouter, RouteKind


class TestV2InfrastructureCompliance(unittest.TestCase):
    """Compliance checks for Local Bridge and Model Router per Build Bible."""

    def test_local_bridge_default_allowed_subdirs(self) -> None:
        """LocalBridgeSettings default subdirs match the V2 spec.

        Ensures the bridge only scans the expected project categories
        (unity, unreal, web, mobile, ai_apps).
        """

        settings = LocalBridgeSettings()
        self.assertEqual(
            settings.allowed_subdirs,
            ["unity", "unreal", "web", "mobile", "ai_apps"],
        )

    def test_local_bridge_uses_project_root_only(self) -> None:
        """LocalBridge lists projects only under the configured root.

        This guards the project-dir-only rule by asserting that when the
        root does not exist, no paths are yielded.
        """

        # Point the bridge at a path that should not exist in tests.
        fake_root = Path("__nonexistent_root_for_local_bridge_tests__")
        settings = LocalBridgeSettings(root=fake_root, allowed_subdirs=["unity"])
        bridge = LocalBridge(settings=settings)
        projects = list(bridge.list_projects())
        self.assertEqual(projects, [])

    def test_model_router_exposes_all_route_kinds(self) -> None:
        """RouteKind enum covers all Build Bible route types."""

        kinds = {kind.name for kind in RouteKind}
        expected = {"CODE", "IMAGE", "AUDIO", "THREE_D", "GENERIC"}
        self.assertEqual(kinds, expected)

    def test_model_router_returns_named_backends(self) -> None:
        """ModelRouter returns stable backend identifiers per kind."""

        router = ModelRouter()
        selected_route = router.select_route(RouteKind.CODE)
        self.assertIn(selected_route.name, [
            "deepseek-like-code-backend",
            "codellama"
        ])
        self.assertEqual(router.select_route(RouteKind.IMAGE).name, "flux-like-image-backend")
        self.assertEqual(router.select_route(RouteKind.THREE_D).name, "shape-e-like-3d-backend")
        self.assertEqual(router.select_route(RouteKind.AUDIO).name, "bark")  # Lowest cost route
        self.assertEqual(router.select_route(RouteKind.GENERIC).name, "generic-llm-backend")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
