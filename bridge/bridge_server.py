"""
Bridge Server — local filesystem access with Unity/Unreal integration.

The bridge provides agents with sandboxed access to the local filesystem and
local development tools (compilers, linters, Unity/Unreal engines).

All operations are validated through BridgeSecurity before execution.

Enhanced with Unity and Unreal Engine integration capabilities.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from bridge.bridge_security import BridgeSecurity

logger = logging.getLogger(__name__)


class BridgeServer:
    """
    Provides sandboxed filesystem access with Unity/Unreal integration.

    The root directory (``bridge_root``) bounds all operations; agents cannot
    read from or write to paths outside it. Enhanced with game engine integration.
    """

    def __init__(self, bridge_root: Optional[str] = None) -> None:
        root_path = bridge_root or os.environ.get("BRIDGE_ROOT", "./workspace")
        self.root = Path(root_path).resolve()
        self.security = BridgeSecurity(self.root)
        
        # Game engine configurations
        self.unity_config = {
            'editor_path': os.getenv('UNITY_EDITOR_PATH', 'C:/Program Files/Unity/Editor/Unity.exe'),
            'project_extension': '.unity',
            'build_targets': ['StandaloneWindows', 'StandaloneWindows64', 'WebGL']
        }
        
        self.unreal_config = {
            'editor_path': os.getenv('UNREAL_EDITOR_PATH', 'C:/Program Files/Epic Games/UE_5.3/Engine/Binaries/Win64/UnrealEditor.exe'),
            'project_extension': '.uproject',
            'build_targets': ['Win64', 'Linux', 'Mac']
        }
        
        logger.info("BridgeServer initialised with root: %s", self.root)
        logger.info("Unity path: %s", self.unity_config['editor_path'])
        logger.info("Unreal path: %s", self.unreal_config['editor_path'])

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

    # ------------------------------------------------------------------ #
    # Game Engine Operations                                             #
    # ------------------------------------------------------------------ #

    async def launch_unity_editor(self, project_path: str, additional_args: Optional[List[str]] = None) -> Dict:
        """
        Launch Unity Editor for a specific project.
        
        Args:
            project_path: Relative path to Unity project directory
            additional_args: Additional command line arguments for Unity
            
        Returns:
            Result dict with success status and process information
        """
        result = self.security.validate_path(project_path)
        if not result["allowed"]:
            return {"success": False, "error": result["reason"], "path": project_path}

        abs_project_path = self.root / project_path
        
        # Verify Unity project structure
        if not self._is_unity_project(abs_project_path):
            return {"success": False, "error": "Not a valid Unity project", "path": project_path}

        unity_path = Path(self.unity_config['editor_path'])
        if not unity_path.exists():
            return {"success": False, "error": "Unity Editor not found", "path": str(unity_path)}

        try:
            # Prepare Unity command
            cmd = [
                str(unity_path),
                "-projectPath", str(abs_project_path),
                "-batchmode" if additional_args and "-batchmode" in additional_args else "",
            ]
            
            # Add additional arguments
            if additional_args:
                cmd.extend([arg for arg in additional_args if arg])
            
            # Remove empty strings
            cmd = [arg for arg in cmd if arg]
            
            # Launch Unity process
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(abs_project_path)
            )
            
            return {
                "success": True,
                "path": project_path,
                "pid": process.pid,
                "command": " ".join(cmd),
                "message": "Unity Editor launched successfully"
            }
            
        except Exception as exc:
            logger.warning("Unity launch failed for %s: %s", project_path, exc)
            return {"success": False, "error": str(exc), "path": project_path}

    async def launch_unreal_editor(self, project_path: str, additional_args: Optional[List[str]] = None) -> Dict:
        """
        Launch Unreal Editor for a specific project.
        
        Args:
            project_path: Relative path to Unreal project file (.uproject)
            additional_args: Additional command line arguments for Unreal
            
        Returns:
            Result dict with success status and process information
        """
        result = self.security.validate_path(project_path)
        if not result["allowed"]:
            return {"success": False, "error": result["reason"], "path": project_path}

        abs_project_path = self.root / project_path
        
        # Verify Unreal project structure
        if not self._is_unreal_project(abs_project_path):
            return {"success": False, "error": "Not a valid Unreal project", "path": project_path}

        unreal_path = Path(self.unreal_config['editor_path'])
        if not unreal_path.exists():
            return {"success": False, "error": "Unreal Editor not found", "path": str(unreal_path)}

        try:
            # Prepare Unreal command
            cmd = [str(unreal_path), str(abs_project_path)]
            
            # Add additional arguments
            if additional_args:
                cmd.extend(additional_args)
            
            # Launch Unreal process
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=abs_project_path.parent
            )
            
            return {
                "success": True,
                "path": project_path,
                "pid": process.pid,
                "command": " ".join(cmd),
                "message": "Unreal Editor launched successfully"
            }
            
        except Exception as exc:
            logger.warning("Unreal launch failed for %s: %s", project_path, exc)
            return {"success": False, "error": str(exc), "path": project_path}

    async def build_unity_project(self, project_path: str, build_target: str = "StandaloneWindows64", output_path: Optional[str] = None) -> Dict:
        """
        Build Unity project for specified target platform.
        
        Args:
            project_path: Relative path to Unity project
            build_target: Target build platform
            output_path: Output directory for build
            
        Returns:
            Result dict with build status and output information
        """
        if build_target not in self.unity_config['build_targets']:
            return {"success": False, "error": f"Invalid build target: {build_target}"}

        # Prepare build arguments
        build_args = [
            "-batchmode",
            "-quit",
            "-buildTarget", build_target,
        ]
        
        if output_path:
            abs_output_path = self.root / output_path
            build_args.extend(["-buildPath", str(abs_output_path)])
        
        return await self.launch_unity_editor(project_path, build_args)

    async def build_unreal_project(self, project_path: str, build_target: str = "Win64", output_path: Optional[str] = None) -> Dict:
        """
        Build Unreal project for specified target platform.
        
        Args:
            project_path: Relative path to Unreal project
            build_target: Target build platform
            output_path: Output directory for build
            
        Returns:
            Result dict with build status and output information
        """
        if build_target not in self.unreal_config['build_targets']:
            return {"success": False, "error": f"Invalid build target: {build_target}"}

        # Prepare build arguments
        build_args = [
            "-runcook",
            "-runbuild",
            "-targetplatform", build_target,
            "-project", str(self.root / project_path),
        ]
        
        if output_path:
            abs_output_path = self.root / output_path
            build_args.extend(["-stagingdirectory", str(abs_output_path)])
        
        return await self.launch_unreal_editor(project_path, build_args)

    def _is_unity_project(self, project_path: Path) -> bool:
        """Check if directory contains a valid Unity project."""
        # Look for Assets and ProjectSettings directories
        assets_dir = project_path / "Assets"
        project_settings_dir = project_path / "ProjectSettings"
        
        return assets_dir.exists() and assets_dir.is_dir() and project_settings_dir.exists() and project_settings_dir.is_dir()

    def _is_unreal_project(self, project_path: Path) -> bool:
        """Check if path points to a valid Unreal project."""
        # Check for .uproject file
        if project_path.suffix == ".uproject":
            return project_path.exists() and project_path.is_file()
        
        # Check directory for .uproject file
        uproject_files = list(project_path.glob("*.uproject"))
        return len(uproject_files) > 0

    def get_engine_status(self) -> Dict:
        """Get status of available game engines."""
        unity_available = Path(self.unity_config['editor_path']).exists()
        unreal_available = Path(self.unreal_config['editor_path']).exists()
        
        return {
            "unity": {
                "available": unity_available,
                "path": self.unity_config['editor_path'],
                "version": self._get_unity_version() if unity_available else None
            },
            "unreal": {
                "available": unreal_available,
                "path": self.unreal_config['editor_path'],
                "version": self._get_unreal_version() if unreal_available else None
            }
        }

    def _get_unity_version(self) -> Optional[str]:
        """Get Unity Editor version."""
        try:
            unity_path = Path(self.unity_config['editor_path'])
            if unity_path.exists():
                # Try to read version from executable properties
                result = subprocess.run(
                    [str(unity_path), "-version"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    return result.stdout.strip()
        except Exception:
            pass
        return None

    def _get_unreal_version(self) -> Optional[str]:
        """Get Unreal Engine version."""
        try:
            unreal_path = Path(self.unreal_config['editor_path'])
            if unreal_path.exists():
                # Extract version from path (e.g., UE_5.3 -> 5.3)
                parent_dir = unreal_path.parent
                if "UE_" in str(parent_dir):
                    version = parent_dir.name.replace("UE_", "")
                    return version
        except Exception:
            pass
        return None
