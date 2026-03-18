from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from orchestration.task_model import Task
from .base import AgentResult


@dataclass
class PrismAgent:
    """FABRICATOR agent: builds asset bundles for the project.

    Implements the Fabricator role from V2_AGENT_ROLES by creating a
    predictable asset folder structure and a simple manifest that
    downstream agents can rely on.
    """

    name: str = "Fabricator"

    def _resolve_project_root(self, task: Task) -> Path:
        raw = task.inputs.get("project_root")
        base = Path(raw) if raw else Path("projects") / "session_default"
        base.mkdir(parents=True, exist_ok=True)
        return base

    def handle_task(self, task: Task) -> AgentResult:
        project_root = self._resolve_project_root(task)
        assets_root = project_root / "assets"
        textures_dir = assets_root / "textures"
        models_dir = assets_root / "models"
        audio_dir = assets_root / "audio"
        ui_dir = assets_root / "ui"

        for d in (assets_root, textures_dir, models_dir, audio_dir, ui_dir):
            d.mkdir(parents=True, exist_ok=True)

        # A minimal manifest that records the structure and a couple of
        # placeholder assets. Real generation can plug into this later.
        manifest = {
            "project_root": str(project_root),
            "assets_root": str(assets_root),
            "bundles": [
                {
                    "name": "core_ui",
                    "type": "ui",
                    "path": str(ui_dir / "core_ui_manifest.md"),
                },
                {
                    "name": "core_audio",
                    "type": "audio",
                    "path": str(audio_dir / "core_audio_manifest.md"),
                },
            ],
        }

        # Write simple placeholder bundle descriptors so the manifest is true.
        (ui_dir / "core_ui_manifest.md").write_text(
            "# Core UI Bundle\n\nPlaceholder description for UI assets.",
            encoding="utf-8",
        )
        (audio_dir / "core_audio_manifest.md").write_text(
            "# Core Audio Bundle\n\nPlaceholder description for audio assets.",
            encoding="utf-8",
        )

        manifest_path = assets_root / "asset_manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        return AgentResult(
            outputs={
                "assets_root": str(assets_root),
                "asset_manifest_path": str(manifest_path),
            },
            logs=[f"Fabricator created asset bundles under {assets_root}"],
        )
