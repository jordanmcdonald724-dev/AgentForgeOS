"""
Bridge Security — sandboxing rules for the local bridge layer.

Validates every filesystem path before the BridgeServer acts on it.
Rules enforce that agents cannot escape the bridge root or touch
sensitive system files.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Extensions the bridge is allowed to read/write by default.
_DEFAULT_ALLOWED_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx",
    ".json", ".yaml", ".yml", ".toml",
    ".md", ".txt", ".html", ".css",
    ".rs", ".go", ".sh",
}

# Path fragments that are always denied, regardless of root.
_DEFAULT_DENIED_FRAGMENTS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".env",
}


class BridgeSecurity:
    """
    Validates filesystem paths before the bridge acts on them.

    All paths are resolved relative to *bridge_root* and checked against:
    - allowed file extensions
    - denied path fragments
    - containment within the bridge root (no path traversal)
    """

    def __init__(
        self,
        bridge_root: Path,
        allowed_extensions: Optional[List[str]] = None,
        denied_fragments: Optional[List[str]] = None,
    ) -> None:
        self.root = bridge_root.resolve()
        self.allowed_extensions: set = (
            set(allowed_extensions) if allowed_extensions is not None
            else set(_DEFAULT_ALLOWED_EXTENSIONS)
        )
        self.denied_fragments: set = (
            set(denied_fragments) if denied_fragments is not None
            else set(_DEFAULT_DENIED_FRAGMENTS)
        )
        self._load_settings()

    # ------------------------------------------------------------------ #
    # Settings loader                                                      #
    # ------------------------------------------------------------------ #

    def _load_settings(self) -> None:
        """Optionally override defaults from config/settings.json."""
        settings_path = (
            Path(__file__).resolve().parent.parent / "config" / "settings.json"
        )
        if not settings_path.exists():
            return
        try:
            with settings_path.open() as fp:
                settings = json.load(fp)
            bridge_settings = settings.get("bridge", {})
            if "allowed_extensions" in bridge_settings:
                self.allowed_extensions = set(bridge_settings["allowed_extensions"])
            if "denied_paths" in bridge_settings:
                self.denied_fragments = set(bridge_settings["denied_paths"])
        except Exception as exc:
            logger.warning("BridgeSecurity: could not load settings.json: %s", exc)

    # ------------------------------------------------------------------ #
    # Validation                                                           #
    # ------------------------------------------------------------------ #

    def validate_path(self, relative_path: str) -> Dict:
        """
        Validate a path before the bridge acts on it.

        Returns a dict with ``allowed`` (bool) and ``reason`` (str) keys.
        ``reason`` is an empty string when the path is allowed.
        """
        if not relative_path or not relative_path.strip():
            return {"allowed": False, "reason": "Path must not be empty"}

        # Resolve to absolute and check containment
        try:
            abs_path = (self.root / relative_path).resolve()
        except Exception as exc:
            return {"allowed": False, "reason": f"Invalid path: {exc}"}

        if not str(abs_path).startswith(str(self.root)):
            return {
                "allowed": False,
                "reason": "Path traversal detected — access denied",
            }

        # Check denied fragments
        for fragment in self.denied_fragments:
            if fragment in abs_path.parts or fragment in relative_path:
                return {
                    "allowed": False,
                    "reason": f"Access to '{fragment}' is not permitted",
                }

        # Check allowed extension (directories pass without extension check)
        suffix = abs_path.suffix
        if suffix and suffix not in self.allowed_extensions:
            return {
                "allowed": False,
                "reason": f"File extension '{suffix}' is not permitted",
            }

        return {"allowed": True, "reason": ""}

    def is_allowed(self, relative_path: str) -> bool:
        """Convenience wrapper — returns True when the path passes validation."""
        return self.validate_path(relative_path)["allowed"]
