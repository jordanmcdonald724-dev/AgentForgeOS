from __future__ import annotations

import unittest
from pathlib import Path


class TestV2FrontendCompliance(unittest.TestCase):
    """Lightweight checks that the V2 frontend shell matches the Build Bible.

    These tests intentionally operate on source text only. They are not a
    substitute for a full JS test runner but give us guardrails against
    accidental drift of the 3-page V2 architecture.
    """

    def setUp(self) -> None:
        # Project root is tests/.. relative to this file
        self.root = Path(__file__).resolve().parents[1]

    def test_router_exposes_three_v2_pages(self) -> None:
        """Router must support command-center, workspace, and research-lab routes."""

        router_path = self.root / "frontend" / "src" / "router" / "Router.jsx"
        self.assertTrue(router_path.is_file(), msg=f"Missing router file at {router_path}")
        text = router_path.read_text(encoding="utf-8")

        # Basic route keys for the three V2 pages
        self.assertIn('case "command-center"', text)
        self.assertIn('case "workspace"', text)
        self.assertIn('case "research-lab"', text)

    def test_app_layout_nav_includes_three_v2_entries(self) -> None:
        """AppLayout navigation must include the three V2 entries."""

        candidate_paths = [
            self.root / "frontend" / "src" / "ui" / "components" / "layout" / "AppLayout.jsx",
            self.root / "docs" / "legacy_v1_ui" / "AppLayout.jsx",
        ]
        layout_path = next((p for p in candidate_paths if p.is_file()), None)
        self.assertIsNotNone(layout_path, msg=f"Missing AppLayout at any of: {candidate_paths}")
        text = layout_path.read_text(encoding="utf-8")

        # Each nav entry should include the expected href fragment
        self.assertIn('"#/command-center"', text)
        self.assertIn('"#/workspace"', text)
        self.assertIn('"#/research-lab"', text)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
