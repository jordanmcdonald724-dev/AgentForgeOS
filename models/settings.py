from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class SystemSettings:
    unity_path: Path | None = None
    unreal_path: Path | None = None
    local_project_root: Path = Path("C:/AgentForgeProjects")
    local_bridge_port: int = 3250
    auto_launch_editor: bool = False
    enable_simulation_mode: bool = True

