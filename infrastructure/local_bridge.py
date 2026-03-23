from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List


DEFAULT_ROOT = Path("C:/AgentForgeProjects")


@dataclass
class LocalBridgeSettings:
    root: Path = DEFAULT_ROOT
    allowed_subdirs: List[str] | None = None

    def __post_init__(self) -> None:
        if self.root is None:
            self.root = DEFAULT_ROOT
        elif isinstance(self.root, str):
            self.root = Path(self.root)
        if self.allowed_subdirs is None:
            self.allowed_subdirs = ["unity", "unreal", "web", "mobile", "ai_apps"]


@dataclass
class LocalBridge:
    """Project-dir-only bridge into local tools.

    This is a minimal, non-executing stub that enforces the
    project-directory-only rule described in BUILD_BIBLE_V2.
    """

    settings: LocalBridgeSettings = field(default_factory=LocalBridgeSettings)

    def list_projects(self) -> Iterable[Path]:
        root = self.settings.root
        if not root.exists():
            return []
        for sub in self.settings.allowed_subdirs or []:
            base = root / sub
            if base.exists() and base.is_dir():
                yield from (p for p in base.iterdir() if p.is_dir())

