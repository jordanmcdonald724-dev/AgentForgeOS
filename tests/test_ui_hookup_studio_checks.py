from __future__ import annotations

import unittest
from pathlib import Path


class TestUiHookupStudioChecks(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parents[1]

    def test_vite_proxy_includes_ws_upgrade(self) -> None:
        vite_path = self.root / "frontend" / "vite.config.js"
        text = vite_path.read_text(encoding="utf-8")

        self.assertIn('"/ws"', text)
        self.assertIn("ws: true", text)
        self.assertIn("target: \"http://127.0.0.1:8000\"", text)

    def test_system_context_consumes_ws_events(self) -> None:
        context_path = self.root / "frontend" / "src" / "ui" / "context" / "SystemContext.jsx"
        text = context_path.read_text(encoding="utf-8")

        self.assertIn("useEventStream", text)
        self.assertIn('url: "/ws"', text)
        self.assertIn('case "step_start"', text)
        self.assertIn('case "step_complete"', text)
        self.assertIn('case "step_failed"', text)

    def test_studio_page_wires_api_and_ws_hooks(self) -> None:
        studio_path = self.root / "frontend" / "src" / "ui" / "pages" / "Studio" / "StudioPage.jsx"
        text = studio_path.read_text(encoding="utf-8")

        self.assertIn("useAgentState", text)
        self.assertIn("usePipelineState", text)
        self.assertIn("useSystem", text)
        self.assertIn('wsUrl: "/ws"', text)
        self.assertIn('fetch("/api/agent/run"', text)

    def test_output_log_wires_logs_api_sources(self) -> None:
        app_path = self.root / "frontend" / "src" / "App.js"
        text = app_path.read_text(encoding="utf-8")

        self.assertIn("Output Log", text)
        self.assertTrue("/logs?source=" in text or "/api/logs?source=" in text)
        for src in ["system", "pipeline", "agents", "deployment", "errors"]:
            self.assertIn(f'<option value="{src}">', text)

    def test_monolith_ui_wires_assets_generate_and_pipeline_run(self) -> None:
        app_path = self.root / "frontend" / "src" / "App.js"
        text = app_path.read_text(encoding="utf-8")

        self.assertIn("/modules/assets/generate", text)
        self.assertIn("/modules/research/search", text)
        self.assertIn("/modules/deployment/launch", text)
        self.assertIn("/pipeline/run", text)
        self.assertIn("/bridge/list", text)
        self.assertIn("/modules/builds/trigger", text)
        self.assertIn("/modules/builds/runs", text)
        self.assertIn("/modules/research/notes", text)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

