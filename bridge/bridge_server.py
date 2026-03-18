"""
Bridge Server — local filesystem access scaffold.

The bridge provides agents with sandboxed access to the local filesystem and
local development tools (compilers, linters, game engines).

All operations are validated through BridgeSecurity before execution.

Current state: SCAFFOLD — read/write operations are defined but not yet wired
to the real filesystem.  Replace the stub implementations below with real
logic as the bridge layer is built out.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

from bridge.bridge_security import BridgeSecurity

logger = logging.getLogger(__name__)


class BridgeServer:
    """
    Provides sandboxed filesystem access to the rest of the system.

    The root directory (``bridge_root``) bounds all operations; agents cannot
    read from or write to paths outside it.
    """

    def __init__(self, bridge_root: Optional[str] = None) -> None:
        root_path = bridge_root or os.environ.get("BRIDGE_ROOT", "./workspace")
        self.root = Path(root_path).resolve()
        self.security = BridgeSecurity(self.root)
        logger.info("BridgeServer initialised with root: %s", self.root)

    # ------------------------------------------------------------------ #
    # Filesystem operations                                                #
    # ------------------------------------------------------------------ #

    def read_file(self, relative_path: str) -> Dict:
        """
        Read a file inside the bridge root.

        Returns a result dict with ``success``, ``path``, and ``content`` keys.
        """
        result = self.security.validate_path(relative_path)
        if not result["allowed"]:
            return {"success": False, "error": result["reason"], "path": relative_path}

        abs_path = self.root / relative_path
        try:
            content = abs_path.read_text(encoding="utf-8")
            return {"success": True, "path": relative_path, "content": content}
        except FileNotFoundError:
            return {"success": False, "error": "File not found", "path": relative_path}
        except Exception as exc:  # pragma: no cover
            logger.warning("BridgeServer.read_file failed for %s: %s", relative_path, exc)
            return {"success": False, "error": str(exc), "path": relative_path}

    def write_file(self, relative_path: str, content: str) -> Dict:
        """
        Write content to a file inside the bridge root.

        Creates parent directories as needed.
        Returns a result dict with ``success`` and ``path`` keys.
        """
        result = self.security.validate_path(relative_path)
        if not result["allowed"]:
            return {"success": False, "error": result["reason"], "path": relative_path}

        abs_path = self.root / relative_path
        try:
            abs_path.parent.mkdir(parents=True, exist_ok=True)
            abs_path.write_text(content, encoding="utf-8")
            return {"success": True, "path": relative_path}
        except Exception as exc:  # pragma: no cover
            logger.warning("BridgeServer.write_file failed for %s: %s", relative_path, exc)
            return {"success": False, "error": str(exc), "path": relative_path}

    def list_directory(self, relative_path: str = ".") -> Dict:
        """
        List the contents of a directory inside the bridge root.

        Returns a result dict with ``success``, ``path``, and ``entries`` keys.
        """
        result = self.security.validate_path(relative_path)
        if not result["allowed"]:
            return {"success": False, "error": result["reason"], "path": relative_path}

        abs_path = self.root / relative_path
        try:
            entries: List[Dict] = []
            for item in sorted(abs_path.iterdir()):
                entries.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None,
                })
            return {"success": True, "path": relative_path, "entries": entries}
        except FileNotFoundError:
            return {"success": False, "error": "Directory not found", "path": relative_path}
        except Exception as exc:  # pragma: no cover
            logger.warning("BridgeServer.list_directory failed for %s: %s", relative_path, exc)
            return {"success": False, "error": str(exc), "path": relative_path}

    def delete_file(self, relative_path: str) -> Dict:
        """
        Delete a file inside the bridge root.

        Returns a result dict with ``success`` and ``path`` keys.
        """
        result = self.security.validate_path(relative_path)
        if not result["allowed"]:
            return {"success": False, "error": result["reason"], "path": relative_path}

        abs_path = self.root / relative_path
        try:
            abs_path.unlink()
            return {"success": True, "path": relative_path}
        except FileNotFoundError:
            return {"success": False, "error": "File not found", "path": relative_path}
        except Exception as exc:  # pragma: no cover
            logger.warning("BridgeServer.delete_file failed for %s: %s", relative_path, exc)
            return {"success": False, "error": str(exc), "path": relative_path}
