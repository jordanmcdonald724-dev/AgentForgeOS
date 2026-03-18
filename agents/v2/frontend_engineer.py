from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from orchestration.task_model import Task
from .base import AgentResult


@dataclass
class FrontendEngineerAgent:
        """SURFACE (Frontend Engineer) agent.

        Implements the role defined in V2_AGENT_ROLES:
        - implements the 3-page UI ONLY
        - creates components and layouts
        - binds data to UI (later)
        Outputs live under frontend/src/pages and frontend/src/components
        for the project workspace, without touching the main app's own
        frontend directory.
        """

        name: str = "Surface"

        def _resolve_project_root(self, task: Task) -> Path:
                raw = task.inputs.get("project_root")
                base = Path(raw) if raw else Path("projects") / "session_default"
                base.mkdir(parents=True, exist_ok=True)
                return base

        def handle_task(self, task: Task) -> AgentResult:
                project_root = self._resolve_project_root(task)
                fe_root = project_root / "frontend" / "src"
                pages_root = fe_root / "pages"
                components_root = fe_root / "components"

                for root in (pages_root, components_root):
                        root.mkdir(parents=True, exist_ok=True)

                # Minimal 3-page V2 shell for the generated project workspace.
                command_page = pages_root / "CommandCenter.tsx"
                workspace_page = pages_root / "ProjectWorkspace.tsx"
                research_page = pages_root / "ResearchLab.tsx"

                if not command_page.exists():
                        command_page.write_text(
                                """import React from "react";

export const CommandCenter: React.FC = () => {
    return (
        <main style={{ padding: 16 }}>
            <h1>Command Center</h1>
            <p>Submit commands and review build state.</p>
        </main>
    );
};
""",
                                encoding="utf-8",
                        )

                if not workspace_page.exists():
                        workspace_page.write_text(
                                """import React from "react";

export const ProjectWorkspace: React.FC = () => {
    return (
        <main style={{ padding: 16 }}>
            <h1>Project Workspace</h1>
            <p>Code, assets, and build artifacts appear here.</p>
        </main>
    );
};
""",
                                encoding="utf-8",
                        )

                if not research_page.exists():
                        research_page.write_text(
                                """import React from "react";

export const ResearchLab: React.FC = () => {
    return (
        <main style={{ padding: 16 }}>
            <h1>Research & Knowledge Lab</h1>
            <p>Ingest and inspect research sources.</p>
        </main>
    );
};
""",
                                encoding="utf-8",
                        )

                layout_component = components_root / "AppShell.tsx"
                if not layout_component.exists():
                        layout_component.write_text(
                                """import React from "react";

export const AppShell: React.FC<React.PropsWithChildren> = ({ children }) => {
    return (
        <div style={{ display: "flex", minHeight: "100vh" }}>
            <aside style={{ width: 240, padding: 16, background: "#020617", color: "#e5e7eb" }}>
                <h2>AgentForge Project UI</h2>
                <ul style={{ listStyle: "none", padding: 0, marginTop: 16 }}>
                    <li>Command Center</li>
                    <li>Workspace</li>
                    <li>Research Lab</li>
                </ul>
            </aside>
            <section style={{ flex: 1, background: "#020617", color: "#e5e7eb" }}>{children}</section>
        </div>
    );
};
""",
                                encoding="utf-8",
                        )

                created = [
                        str(command_page),
                        str(workspace_page),
                        str(research_page),
                        str(layout_component),
                ]

                return AgentResult(
                        outputs={"created_paths": created, "project_root": str(project_root)},
                        logs=[f"Frontend Engineer scaffolded V2 pages under {project_root}"],
                )
