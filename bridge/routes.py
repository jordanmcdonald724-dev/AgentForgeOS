"""Bridge API routes — expose the bridge layer over HTTP.

Provides REST endpoints so the frontend (and other consumers) can see and
interact with the project filesystem through the bridge.

Endpoints:
    GET  /bridge/health  — bridge status
    GET  /bridge/list    — list directory contents
    GET  /bridge/read    — read a single file
    POST /bridge/sync    — return a recursive snapshot of the project tree
"""

from __future__ import annotations

import logging
import json
import os
import subprocess
from pathlib import Path
import glob
from typing import Any

from fastapi import APIRouter, Header, Query, Request
from pydantic import BaseModel


from bridge.bridge_server import BridgeServer

logger = logging.getLogger(__name__)
audit_logger = logging.getLogger("bridge.audit")


def _auto_find_tool_exe(tool: str) -> str:
    t = (tool or "").strip().lower()
    if t == "unity":
        candidates: list[str] = []
        pf = os.environ.get("ProgramFiles", r"C:\Program Files")
        pf86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
        candidates += glob.glob(os.path.join(pf, "Unity", "Hub", "Editor", "*", "Editor", "Unity.exe"))
        candidates += glob.glob(os.path.join(pf86, "Unity", "Hub", "Editor", "*", "Editor", "Unity.exe"))
        candidates += glob.glob(os.path.join(pf, "Unity", "Editor", "Unity.exe"))
        candidates += glob.glob(os.path.join(pf86, "Unity", "Editor", "Unity.exe"))
        candidates = [c for c in candidates if isinstance(c, str) and c.strip() and Path(c).is_file()]
        if not candidates:
            return ""
        candidates.sort(reverse=True)
        return candidates[0]

    if t == "unreal":
        candidates = []
        pf = os.environ.get("ProgramFiles", r"C:\Program Files")
        base = os.path.join(pf, "Epic Games")
        candidates += glob.glob(os.path.join(base, "UE_*", "Engine", "Binaries", "Win64", "UnrealEditor.exe"))
        candidates += glob.glob(os.path.join(base, "UE_*", "Engine", "Binaries", "Win64", "UE4Editor.exe"))
        candidates = [c for c in candidates if isinstance(c, str) and c.strip() and Path(c).is_file()]
        if not candidates:
            return ""
        candidates.sort(reverse=True)
        return candidates[0]

    if t == "godot":
        candidates = []
        pf = os.environ.get("ProgramFiles", r"C:\Program Files")
        pf86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
        candidates += glob.glob(os.path.join(pf, "Godot", "Godot*.exe"))
        candidates += glob.glob(os.path.join(pf86, "Godot", "Godot*.exe"))
        candidates = [c for c in candidates if isinstance(c, str) and c.strip() and Path(c).is_file()]
        if not candidates:
            return ""
        candidates.sort(reverse=True)
        return candidates[0]

    return ""

router = APIRouter(prefix="/bridge", tags=["bridge"])

_bridge: BridgeServer | None = None


def _get_bridge() -> BridgeServer:
    """Lazy-initialise a module-level BridgeServer singleton."""
    global _bridge
    if _bridge is None:
        _bridge = BridgeServer()
    return _bridge


def reset_bridge() -> None:
    """Clear the cached BridgeServer singleton (used by tests)."""
    global _bridge
    _bridge = None


def _permission_level_for_role(role: str) -> int:
    r = (role or "").strip().lower()
    table = {
        "user": 5,
        "admin": 5,
        "system_admin": 4,
        "backend": 2,
        "backend_engineer": 2,
        "frontend": 2,
        "frontend_engineer": 2,
        "ai": 2,
        "ai_engineer": 2,
        "devops": 3,
        "devops_engineer": 3,
        "game_engine": 4,
        "game_engine_engineer": 4,
        "observer": 1,
        "readonly": 0,
        "read_only": 0,
    }
    if not r:
        return 2
    return max(0, min(int(table.get(r, 0)), 5))


def _require_level(actual: int, required: int) -> bool:
    try:
        return int(actual) >= int(required)
    except Exception:
        return False


def _token_valid(token: str | None) -> bool:
    expected = os.environ.get("AGENTFORGE_BRIDGE_TOKEN", "")
    if not expected.strip():
        return False
    if token is None or not token.strip():
        return False
    return token.strip() == expected.strip()


def _authenticated_role(token: str | None, role: str | None) -> str:
    if not _token_valid(token):
        return "readonly"
    return (role or "backend_engineer").strip() or "backend_engineer"


def _audit(request: Request, *, action: str, role: str, level: int, allowed: bool, details: dict[str, Any]) -> None:
    try:
        origin = request.client.host if request.client else ""
        audit_logger.info(
            "BRIDGE action=%s allowed=%s role=%s level=%s origin=%s details=%s",
            action,
            allowed,
            role,
            level,
            origin,
            json.dumps(details, ensure_ascii=False, separators=(",", ":")),
        )
    except Exception:
        return


def _command_allowed(cmd: list[str], level: int) -> tuple[bool, str]:
    if not cmd:
        return False, "Command is required"
    tool = str(cmd[0]).strip().lower()
    if tool not in {"python", "pip", "npm", "node", "git", "cargo"}:
        return False, "Tool is not permitted"
    for part in cmd:
        if not isinstance(part, str):
            continue
        if any(x in part for x in ["&&", "||", ";", "|", ">", "<", "\n", "\r"]):
            return False, "Shell operators are not permitted"
    lowered = [str(x).strip().lower() for x in cmd[1:]]
    if tool == "python" and "-c" in lowered and level < 5:
        return False, "Inline python execution is restricted"
    if tool == "pip":
        if any(x == "install" or x.startswith("install") for x in lowered) and level < 5:
            return False, "pip install is restricted"
    if tool == "npm":
        if any(x == "install" or x == "ci" for x in lowered) and level < 5:
            return False, "npm install is restricted"
    if tool == "git":
        if any(x in {"push", "remote", "config"} for x in lowered) and level < 5:
            return False, "git remote operations are restricted"
    return True, ""


class RunCommandRequest(BaseModel):
    command: list[str]
    cwd: str = "."
    role: str = "user"

class GitCommitRequest(BaseModel):
    message: str
    cwd: str = "."
    add_all: bool = True
    role: str = "user"


class GitPushRequest(BaseModel):
    cwd: str = "."
    remote: str = "origin"
    branch: str = ""
    role: str = "user"


class LaunchToolRequest(BaseModel):
    tool: str
    target: str = ""
    role: str = "user"


class FileWriteRequest(BaseModel):
    path: str
    content: str = ""
    role: str = "user"


class FilePathRequest(BaseModel):
    path: str
    role: str = "user"


class CreateDirRequest(BaseModel):
    path: str
    role: str = "user"


# ------------------------------------------------------------------ #
# GET /bridge/health                                                   #
# ------------------------------------------------------------------ #

@router.get("/health")
async def bridge_health() -> dict[str, Any]:
    """Return the bridge's operational status."""
    bridge = _get_bridge()
    root_exists = bridge.root.is_dir()
    return {
        "success": True,
        "data": {
            "status": "ok" if root_exists else "degraded",
            "root": str(bridge.root),
            "root_exists": root_exists,
        },
        "error": None,
    }


@router.get("/status")
async def bridge_status() -> dict[str, Any]:
    return await bridge_health()


@router.post("/run_command")
async def bridge_run_command(
    body: RunCommandRequest,
    request: Request,
    x_agentforge_token: str | None = Header(default=None, alias="X-AgentForge-Token"),
    x_agentforge_role: str | None = Header(default=None, alias="X-AgentForge-Role"),
) -> dict[str, Any]:
    token = x_agentforge_token or request.cookies.get("agentforge_session")
    role = _authenticated_role(token, x_agentforge_role)
    level = _permission_level_for_role(role)
    if not _require_level(level, 3):
        _audit(request, action="run_command", role=role, level=level, allowed=False, details={"reason": "permission_denied"})
        return {"success": False, "data": None, "error": "Permission denied"}

    bridge = _get_bridge()
    if not body.command:
        _audit(request, action="run_command", role=role, level=level, allowed=False, details={"reason": "empty_command"})
        return {"success": False, "data": None, "error": "Command must be a non-empty list"}

    tool = str(body.command[0]).strip().lower()
    ok_cmd, reason = _command_allowed(body.command, level)
    if not ok_cmd:
        _audit(request, action="run_command", role=role, level=level, allowed=False, details={"reason": reason, "tool": tool})
        return {"success": False, "data": None, "error": reason}

    cwd_check = bridge.security.validate_path(body.cwd or ".")
    if not cwd_check["allowed"]:
        _audit(request, action="run_command", role=role, level=level, allowed=False, details={"reason": cwd_check["reason"], "cwd": body.cwd or "."})
        return {"success": False, "data": None, "error": cwd_check["reason"]}

    abs_cwd = (bridge.root / (body.cwd or ".")).resolve()
    try:
        proc = subprocess.run(
            body.command,
            cwd=str(abs_cwd),
            capture_output=True,
            text=True,
            timeout=300,
        )
        _audit(
            request,
            action="run_command",
            role=role,
            level=level,
            allowed=True,
            details={"tool": tool, "returncode": proc.returncode, "cwd": str(abs_cwd), "argv": body.command[:8]},
        )
        return {
            "success": True,
            "data": {
                "returncode": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "cwd": str(abs_cwd),
                "command": body.command,
            },
            "error": None,
        }
    except subprocess.TimeoutExpired:
        _audit(request, action="run_command", role=role, level=level, allowed=False, details={"reason": "timeout", "tool": tool, "cwd": str(abs_cwd)})
        return {"success": False, "data": None, "error": "Command timed out"}
    except Exception as exc:
        _audit(request, action="run_command", role=role, level=level, allowed=False, details={"reason": str(exc), "tool": tool, "cwd": str(abs_cwd)})
        return {"success": False, "data": None, "error": str(exc)}

@router.post("/run")
async def bridge_run(
    body: RunCommandRequest,
    request: Request,
    x_agentforge_token: str | None = Header(default=None, alias="X-AgentForge-Token"),
    x_agentforge_role: str | None = Header(default=None, alias="X-AgentForge-Role"),
) -> dict[str, Any]:
    return await bridge_run_command(body, request=request, x_agentforge_token=x_agentforge_token, x_agentforge_role=x_agentforge_role)


@router.post("/git_commit")
async def bridge_git_commit(
    body: GitCommitRequest,
    request: Request,
    x_agentforge_token: str | None = Header(default=None, alias="X-AgentForge-Token"),
    x_agentforge_role: str | None = Header(default=None, alias="X-AgentForge-Role"),
) -> dict[str, Any]:
    token = x_agentforge_token or request.cookies.get("agentforge_session")
    role = _authenticated_role(token, x_agentforge_role)
    level = _permission_level_for_role(role)
    if not _require_level(level, 5):
        _audit(request, action="git_commit", role=role, level=level, allowed=False, details={"reason": "permission_denied"})
        return {"success": False, "data": None, "error": "Permission denied"}

    msg = (body.message or "").strip()
    if not msg or "\n" in msg or "\r" in msg:
        _audit(request, action="git_commit", role=role, level=level, allowed=False, details={"reason": "invalid_message"})
        return {"success": False, "data": None, "error": "Invalid commit message"}

    bridge = _get_bridge()
    cwd_check = bridge.security.validate_path(body.cwd or ".")
    if not cwd_check["allowed"]:
        _audit(request, action="git_commit", role=role, level=level, allowed=False, details={"reason": cwd_check["reason"], "cwd": body.cwd or "."})
        return {"success": False, "data": None, "error": cwd_check["reason"]}
    abs_cwd = (bridge.root / (body.cwd or ".")).resolve()
    if not (abs_cwd / ".git").exists():
        _audit(request, action="git_commit", role=role, level=level, allowed=False, details={"reason": "not_a_git_repo", "cwd": str(abs_cwd)})
        return {"success": False, "data": None, "error": "Not a git repository"}

    steps: list[dict[str, Any]] = []
    try:
        if body.add_all:
            add_cmd = ["git", "add", "-A"]
            ok_add, reason = _command_allowed(add_cmd, level)
            if not ok_add:
                return {"success": False, "data": None, "error": reason}
            proc_add = subprocess.run(add_cmd, cwd=str(abs_cwd), capture_output=True, text=True, timeout=300)
            steps.append({"command": add_cmd, "returncode": proc_add.returncode, "stdout": proc_add.stdout, "stderr": proc_add.stderr})
            if proc_add.returncode != 0:
                _audit(request, action="git_commit", role=role, level=level, allowed=False, details={"reason": "git_add_failed", "cwd": str(abs_cwd)})
                return {"success": False, "data": {"steps": steps}, "error": "git add failed"}

        commit_cmd = ["git", "commit", "-m", msg]
        ok_commit, reason = _command_allowed(commit_cmd, level)
        if not ok_commit:
            return {"success": False, "data": None, "error": reason}
        proc_commit = subprocess.run(commit_cmd, cwd=str(abs_cwd), capture_output=True, text=True, timeout=300)
        steps.append({"command": commit_cmd, "returncode": proc_commit.returncode, "stdout": proc_commit.stdout, "stderr": proc_commit.stderr})
        allowed = proc_commit.returncode == 0
        _audit(request, action="git_commit", role=role, level=level, allowed=allowed, details={"cwd": str(abs_cwd), "returncode": proc_commit.returncode})
        if proc_commit.returncode != 0:
            return {"success": False, "data": {"steps": steps}, "error": proc_commit.stderr.strip() or "git commit failed"}
        return {"success": True, "data": {"steps": steps}, "error": None}
    except subprocess.TimeoutExpired:
        _audit(request, action="git_commit", role=role, level=level, allowed=False, details={"reason": "timeout", "cwd": str(abs_cwd)})
        return {"success": False, "data": {"steps": steps}, "error": "Command timed out"}
    except Exception as exc:
        _audit(request, action="git_commit", role=role, level=level, allowed=False, details={"reason": str(exc), "cwd": str(abs_cwd)})
        return {"success": False, "data": {"steps": steps}, "error": str(exc)}


@router.post("/git_push")
async def bridge_git_push(
    body: GitPushRequest,
    request: Request,
    x_agentforge_token: str | None = Header(default=None, alias="X-AgentForge-Token"),
    x_agentforge_role: str | None = Header(default=None, alias="X-AgentForge-Role"),
) -> dict[str, Any]:
    token = x_agentforge_token or request.cookies.get("agentforge_session")
    role = _authenticated_role(token, x_agentforge_role)
    level = _permission_level_for_role(role)
    if not _require_level(level, 5):
        _audit(request, action="git_push", role=role, level=level, allowed=False, details={"reason": "permission_denied"})
        return {"success": False, "data": None, "error": "Permission denied"}

    bridge = _get_bridge()
    cwd_check = bridge.security.validate_path(body.cwd or ".")
    if not cwd_check["allowed"]:
        _audit(request, action="git_push", role=role, level=level, allowed=False, details={"reason": cwd_check["reason"], "cwd": body.cwd or "."})
        return {"success": False, "data": None, "error": cwd_check["reason"]}
    abs_cwd = (bridge.root / (body.cwd or ".")).resolve()
    if not (abs_cwd / ".git").exists():
        _audit(request, action="git_push", role=role, level=level, allowed=False, details={"reason": "not_a_git_repo", "cwd": str(abs_cwd)})
        return {"success": False, "data": None, "error": "Not a git repository"}

    remote = (body.remote or "origin").strip()
    branch = (body.branch or "").strip()
    if not remote or remote.startswith("-") or branch.startswith("-"):
        return {"success": False, "data": None, "error": "Invalid remote/branch"}

    cmd = ["git", "push", remote] + ([branch] if branch else [])
    ok_cmd, reason = _command_allowed(cmd, level)
    if not ok_cmd:
        _audit(request, action="git_push", role=role, level=level, allowed=False, details={"reason": reason, "cwd": str(abs_cwd)})
        return {"success": False, "data": None, "error": reason}

    try:
        proc = subprocess.run(cmd, cwd=str(abs_cwd), capture_output=True, text=True, timeout=300)
        allowed = proc.returncode == 0
        _audit(request, action="git_push", role=role, level=level, allowed=allowed, details={"cwd": str(abs_cwd), "returncode": proc.returncode})
        if proc.returncode != 0:
            return {"success": False, "data": {"returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}, "error": proc.stderr.strip() or "git push failed"}
        return {"success": True, "data": {"returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}, "error": None}
    except subprocess.TimeoutExpired:
        _audit(request, action="git_push", role=role, level=level, allowed=False, details={"reason": "timeout", "cwd": str(abs_cwd)})
        return {"success": False, "data": None, "error": "Command timed out"}
    except Exception as exc:
        _audit(request, action="git_push", role=role, level=level, allowed=False, details={"reason": str(exc), "cwd": str(abs_cwd)})
        return {"success": False, "data": None, "error": str(exc)}


@router.post("/create_file")
async def bridge_create_file(
    body: FileWriteRequest,
    request: Request,
    x_agentforge_token: str | None = Header(default=None, alias="X-AgentForge-Token"),
    x_agentforge_role: str | None = Header(default=None, alias="X-AgentForge-Role"),
) -> dict[str, Any]:
    token = x_agentforge_token or request.cookies.get("agentforge_session")
    role = _authenticated_role(token, x_agentforge_role)
    level = _permission_level_for_role(role)
    if not _require_level(level, 2):
        _audit(request, action="create_file", role=role, level=level, allowed=False, details={"path": body.path, "reason": "permission_denied"})
        return {"success": False, "data": None, "error": "Permission denied"}
    bridge = _get_bridge()
    result = bridge.write_file(body.path, body.content or "")
    if result.get("success"):
        _audit(request, action="create_file", role=role, level=level, allowed=True, details={"path": body.path, "bytes": len(body.content or "")})
        return {"success": True, "data": result, "error": None}
    _audit(request, action="create_file", role=role, level=level, allowed=False, details={"path": body.path, "reason": result.get("error")})
    return {"success": False, "data": None, "error": result.get("error")}


@router.post("/write_file")
async def bridge_write_file(
    body: FileWriteRequest,
    request: Request,
    x_agentforge_token: str | None = Header(default=None, alias="X-AgentForge-Token"),
    x_agentforge_role: str | None = Header(default=None, alias="X-AgentForge-Role"),
) -> dict[str, Any]:
    return await bridge_create_file(body, request=request, x_agentforge_token=x_agentforge_token, x_agentforge_role=x_agentforge_role)


@router.post("/read_file")
async def bridge_read_file(
    body: FilePathRequest,
    request: Request,
    x_agentforge_token: str | None = Header(default=None, alias="X-AgentForge-Token"),
    x_agentforge_role: str | None = Header(default=None, alias="X-AgentForge-Role"),
) -> dict[str, Any]:
    token = x_agentforge_token or request.cookies.get("agentforge_session")
    role = _authenticated_role(token, x_agentforge_role) if _token_valid(token) else "readonly"
    level = _permission_level_for_role(role)
    if not _require_level(level, 0):
        _audit(request, action="read_file", role=role, level=level, allowed=False, details={"path": body.path, "reason": "permission_denied"})
        return {"success": False, "data": None, "error": "Permission denied"}
    bridge = _get_bridge()
    result = bridge.read_file(body.path)
    if result.get("success"):
        _audit(request, action="read_file", role=role, level=level, allowed=True, details={"path": body.path})
        return {"success": True, "data": result, "error": None}
    _audit(request, action="read_file", role=role, level=level, allowed=False, details={"path": body.path, "reason": result.get("error")})
    return {"success": False, "data": None, "error": result.get("error")}


@router.post("/create_directory")
async def bridge_create_directory(
    body: CreateDirRequest,
    request: Request,
    x_agentforge_token: str | None = Header(default=None, alias="X-AgentForge-Token"),
    x_agentforge_role: str | None = Header(default=None, alias="X-AgentForge-Role"),
) -> dict[str, Any]:
    token = x_agentforge_token or request.cookies.get("agentforge_session")
    role = _authenticated_role(token, x_agentforge_role)
    level = _permission_level_for_role(role)
    if not _require_level(level, 2):
        _audit(request, action="create_directory", role=role, level=level, allowed=False, details={"path": body.path, "reason": "permission_denied"})
        return {"success": False, "data": None, "error": "Permission denied"}
    bridge = _get_bridge()
    check = bridge.security.validate_path(body.path)
    if not check["allowed"]:
        _audit(request, action="create_directory", role=role, level=level, allowed=False, details={"path": body.path, "reason": check["reason"]})
        return {"success": False, "data": None, "error": check["reason"]}
    abs_path = (bridge.root / body.path).resolve()
    try:
        abs_path.mkdir(parents=True, exist_ok=True)
        _audit(request, action="create_directory", role=role, level=level, allowed=True, details={"path": body.path})
        return {"success": True, "data": {"path": body.path}, "error": None}
    except Exception as exc:
        _audit(request, action="create_directory", role=role, level=level, allowed=False, details={"path": body.path, "reason": str(exc)})
        return {"success": False, "data": None, "error": str(exc)}


@router.post("/delete_file")
async def bridge_delete_file(
    body: FilePathRequest,
    request: Request,
    x_agentforge_token: str | None = Header(default=None, alias="X-AgentForge-Token"),
    x_agentforge_role: str | None = Header(default=None, alias="X-AgentForge-Role"),
) -> dict[str, Any]:
    token = x_agentforge_token or request.cookies.get("agentforge_session")
    role = _authenticated_role(token, x_agentforge_role)
    level = _permission_level_for_role(role)
    if not _require_level(level, 2):
        _audit(request, action="delete_file", role=role, level=level, allowed=False, details={"path": body.path, "reason": "permission_denied"})
        return {"success": False, "data": None, "error": "Permission denied"}
    bridge = _get_bridge()
    result = bridge.delete_file(body.path)
    if result.get("success"):
        _audit(request, action="delete_file", role=role, level=level, allowed=True, details={"path": body.path})
        return {"success": True, "data": result, "error": None}
    _audit(request, action="delete_file", role=role, level=level, allowed=False, details={"path": body.path, "reason": result.get("error")})
    return {"success": False, "data": None, "error": result.get("error")}


@router.post("/run_build")
async def bridge_run_build(
    body: RunCommandRequest,
    request: Request,
    x_agentforge_token: str | None = Header(default=None, alias="X-AgentForge-Token"),
    x_agentforge_role: str | None = Header(default=None, alias="X-AgentForge-Role"),
) -> dict[str, Any]:
    return await bridge_run_command(body, request=request, x_agentforge_token=x_agentforge_token, x_agentforge_role=x_agentforge_role)


@router.post("/launch_tool")
async def bridge_launch_tool(
    body: LaunchToolRequest,
    request: Request,
    x_agentforge_token: str | None = Header(default=None, alias="X-AgentForge-Token"),
    x_agentforge_role: str | None = Header(default=None, alias="X-AgentForge-Role"),
) -> dict[str, Any]:
    token = x_agentforge_token or request.cookies.get("agentforge_session")
    role = _authenticated_role(token, x_agentforge_role)
    level = _permission_level_for_role(role)
    if not _require_level(level, 4):
        _audit(request, action="launch_tool", role=role, level=level, allowed=False, details={"reason": "permission_denied"})
        return {"success": False, "data": None, "error": "Permission denied"}

    tool = (body.tool or "").strip().lower()
    target = (body.target or "").strip()
    bridge = _get_bridge()

    if tool in {"explorer", "vscode"}:
        check = bridge.security.validate_path(target or ".")
        if not check["allowed"]:
            _audit(request, action="launch_tool", role=role, level=level, allowed=False, details={"reason": check["reason"], "tool": tool, "target": target})
            return {"success": False, "data": None, "error": check["reason"]}
        abs_target = (bridge.root / (target or ".")).resolve()
        try:
            if tool == "explorer":
                subprocess.Popen(["explorer.exe", str(abs_target)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                subprocess.Popen(["code", str(abs_target)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            _audit(request, action="launch_tool", role=role, level=level, allowed=True, details={"launched": True, "supported": True, "tool": tool, "target": str(abs_target)})
            return {"success": True, "data": {"launched": True, "supported": True, "tool": tool, "target": str(abs_target)}, "error": None}
        except Exception as exc:
            _audit(request, action="launch_tool", role=role, level=level, allowed=False, details={"reason": str(exc), "tool": tool, "target": str(abs_target)})
            return {"success": False, "data": {"launched": False, "supported": True, "tool": tool}, "error": str(exc)}

    if tool == "browser":
        if not (target.startswith("http://") or target.startswith("https://")):
            _audit(request, action="launch_tool", role=role, level=level, allowed=False, details={"reason": "invalid_url", "tool": tool, "target": target})
            return {"success": False, "data": None, "error": "Invalid URL"}
        try:
            os.startfile(target)
            _audit(request, action="launch_tool", role=role, level=level, allowed=True, details={"launched": True, "supported": True, "tool": tool, "target": target})
            return {"success": True, "data": {"launched": True, "supported": True, "tool": tool, "target": target}, "error": None}
        except Exception as exc:
            _audit(request, action="launch_tool", role=role, level=level, allowed=False, details={"reason": str(exc), "tool": tool, "target": target})
            return {"success": False, "data": {"launched": False, "supported": True, "tool": tool}, "error": str(exc)}

    if tool in {"unity", "unreal", "godot"}:
        exe_env = {
            "unity": "AGENTFORGE_UNITY_EXE",
            "unreal": "AGENTFORGE_UNREAL_EXE",
            "godot": "AGENTFORGE_GODOT_EXE",
        }[tool]
        exe = (os.getenv(exe_env, "") or "").strip()
        resolved = exe if (exe and Path(exe).is_file()) else _auto_find_tool_exe(tool)
        if not resolved or not Path(resolved).is_file():
            _audit(request, action="launch_tool", role=role, level=level, allowed=True, details={"launched": False, "supported": False, "tool": tool})
            return {"success": True, "data": {"launched": False, "supported": False, "tool": tool}, "error": None}

        check = bridge.security.validate_path(target or ".")
        if not check["allowed"]:
            _audit(request, action="launch_tool", role=role, level=level, allowed=False, details={"reason": check["reason"], "tool": tool, "target": target})
            return {"success": False, "data": None, "error": check["reason"]}
        abs_target = (bridge.root / (target or ".")).resolve()

        argv: list[str]
        if tool == "unity":
            argv = [resolved, "-projectPath", str(abs_target)]
        elif tool == "godot":
            argv = [resolved, "--path", str(abs_target)]
        else:
            if abs_target.is_dir():
                _audit(request, action="launch_tool", role=role, level=level, allowed=False, details={"reason": "uproject_required", "tool": tool, "target": str(abs_target)})
                return {"success": False, "data": None, "error": "Unreal requires a .uproject file path"}
            if abs_target.suffix.lower() != ".uproject":
                _audit(request, action="launch_tool", role=role, level=level, allowed=False, details={"reason": "invalid_uproject", "tool": tool, "target": str(abs_target)})
                return {"success": False, "data": None, "error": "Invalid .uproject path"}
            argv = [resolved, str(abs_target)]
        try:
            subprocess.Popen(argv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            _audit(request, action="launch_tool", role=role, level=level, allowed=True, details={"launched": True, "supported": True, "tool": tool, "target": str(abs_target)})
            return {"success": True, "data": {"launched": True, "supported": True, "tool": tool, "target": str(abs_target), "exe": str(resolved)}, "error": None}
        except Exception as exc:
            _audit(request, action="launch_tool", role=role, level=level, allowed=False, details={"reason": str(exc), "tool": tool, "target": str(abs_target)})
            return {"success": False, "data": {"launched": False, "supported": True, "tool": tool}, "error": str(exc)}

    _audit(request, action="launch_tool", role=role, level=level, allowed=True, details={"launched": False, "supported": False, "tool": tool})
    return {"success": True, "data": {"launched": False, "supported": False, "tool": tool}, "error": None}


# ------------------------------------------------------------------ #
# GET /bridge/list?path=.                                              #
# ------------------------------------------------------------------ #

@router.get("/list")
async def bridge_list(
    request: Request,
    path: str = Query(".", description="Relative path within the bridge root"),
) -> dict[str, Any]:
    """List the contents of a directory inside the bridge root."""
    bridge = _get_bridge()
    result = bridge.list_directory(path)
    if result["success"]:
        _audit(request, action="list", role="readonly", level=0, allowed=True, details={"path": path, "count": len(result.get("entries", []) or [])})
        return {"success": True, "data": result, "error": None}
    _audit(request, action="list", role="readonly", level=0, allowed=False, details={"path": path, "reason": result.get("error")})
    return {"success": False, "data": None, "error": result.get("error")}


# ------------------------------------------------------------------ #
# GET /bridge/read?path=<file>                                         #
# ------------------------------------------------------------------ #

@router.get("/read")
async def bridge_read(
    request: Request,
    path: str = Query(..., description="Relative file path within the bridge root"),
) -> dict[str, Any]:
    """Read a single file inside the bridge root."""
    bridge = _get_bridge()
    result = bridge.read_file(path)
    if result["success"]:
        _audit(request, action="read", role="readonly", level=0, allowed=True, details={"path": path})
        return {"success": True, "data": result, "error": None}
    _audit(request, action="read", role="readonly", level=0, allowed=False, details={"path": path, "reason": result.get("error")})
    return {"success": False, "data": None, "error": result.get("error")}


# ------------------------------------------------------------------ #
# POST /bridge/sync                                                    #
# ------------------------------------------------------------------ #

def _walk_tree(bridge: BridgeServer, rel: str = ".") -> list[dict[str, Any]]:
    """Recursively walk the bridge root and return a flat file list."""
    result = bridge.list_directory(rel)
    if not result["success"]:
        return []

    items: list[dict[str, Any]] = []
    for entry in result.get("entries", []):
        child_path = entry["name"] if rel == "." else f"{rel}/{entry['name']}"
        items.append({"path": child_path, "type": entry["type"], "size": entry.get("size")})
        if entry["type"] == "directory":
            items.extend(_walk_tree(bridge, child_path))
    return items


@router.post("/sync")
async def bridge_sync(request: Request) -> dict[str, Any]:
    """Return a recursive snapshot of every file in the project tree.

    This is the ``/bridge/sync`` endpoint described in the system API
    contracts.  It walks the bridge root and returns all visible files
    and directories so that callers can build a complete project view.
    """
    bridge = _get_bridge()
    if not bridge.root.is_dir():
        _audit(request, action="sync", role="readonly", level=0, allowed=False, details={"reason": "root_missing"})
        return {
            "success": False,
            "data": None,
            "error": "Bridge root does not exist",
        }
    tree = _walk_tree(bridge)
    _audit(request, action="sync", role="readonly", level=0, allowed=True, details={"entries": len(tree)})
    return {
        "success": True,
        "data": {"root": str(bridge.root), "entries": tree},
        "error": None,
    }
