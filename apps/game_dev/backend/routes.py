"""Game Dev module backend API routes."""

from __future__ import annotations

import datetime
import json
import os
import re
import subprocess
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel

from bridge.routes import _auto_find_tool_exe
from engine.security.preflight import require_preflight_ok

router = APIRouter(prefix="/game_dev", tags=["game_dev"])


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _slugify(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", str(text or "").strip()).strip("-").lower()
    return (s[:48] if s else uuid.uuid4().hex[:8]).strip("-") or uuid.uuid4().hex[:8]


def _resources_db_dir(request: Request) -> Path:
    base = getattr(request.app.state, "base_path", "") or str(Path.cwd())
    out = Path(str(base)) / "resources" / "database"
    out.mkdir(parents=True, exist_ok=True)
    return out


def _projects_path(request: Request) -> Path:
    return _resources_db_dir(request) / "game_dev_projects.json"


def _load_projects(request: Request) -> list[dict[str, Any]]:
    path = _projects_path(request)
    if not path.is_file():
        return []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return raw if isinstance(raw, list) else []
    except Exception:
        return []


def _save_projects(request: Request, projects: list[dict[str, Any]]) -> None:
    path = _projects_path(request)
    path.write_text(json.dumps(projects, indent=2), encoding="utf-8")


def _workspace_root(request: Request) -> Path:
    raw = getattr(request.app.state, "workspace_path", "")
    if isinstance(raw, str) and raw.strip():
        return Path(raw).resolve()
    return (Path.home() / "Documents" / "AgentForgeOS").resolve()


def _within_workspace(request: Request, target: Path) -> bool:
    ws = _workspace_root(request)
    try:
        t = target.resolve()
    except Exception:
        return False
    return str(t).lower().startswith(str(ws).lower())


def _ensure_unity_build_script(project_dir: Path) -> None:
    editor_dir = project_dir / "Assets" / "Editor"
    editor_dir.mkdir(parents=True, exist_ok=True)
    script_path = editor_dir / "AgentForgeBuild.cs"
    if script_path.is_file():
        return
    script_path.write_text(
        "\n".join(
            [
                "using UnityEditor;",
                "using UnityEditor.Build.Reporting;",
                "using UnityEngine;",
                "",
                "public static class AgentForgeBuild",
                "{",
                "    public static void BuildWindows()",
                "    {",
                "        var output = \"Builds/Windows\";",
                "        var scenes = EditorBuildSettings.scenes;",
                "        var enabled = new System.Collections.Generic.List<string>();",
                "        foreach (var s in scenes) { if (s.enabled) enabled.Add(s.path); }",
                "        if (enabled.Count == 0)",
                "        {",
                "            var scenePath = \"Assets/Main.unity\";",
                "            var scene = UnityEditor.SceneManagement.EditorSceneManager.NewScene(",
                "                UnityEditor.SceneManagement.NewSceneSetup.DefaultGameObjects,",
                "                UnityEditor.SceneManagement.NewSceneMode.Single",
                "            );",
                "            UnityEditor.SceneManagement.EditorSceneManager.SaveScene(scene, scenePath);",
                "            enabled.Add(scenePath);",
                "        }",
                "        var options = new BuildPlayerOptions",
                "        {",
                "            scenes = enabled.ToArray(),",
                "            locationPathName = output + \"/AgentForgeGame.exe\",",
                "            target = BuildTarget.StandaloneWindows64,",
                "            options = BuildOptions.None",
                "        };",
                "        var report = BuildPipeline.BuildPlayer(options);",
                "        if (report.summary.result != BuildResult.Succeeded)",
                "        {",
                "            Debug.LogError(\"Build failed: \" + report.summary.result);",
                "            EditorApplication.Exit(1);",
                "            return;",
                "        }",
                "        Debug.Log(\"Build succeeded: \" + report.summary.totalSize + \" bytes\");",
                "        EditorApplication.Exit(0);",
                "    }",
                "}",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _resolve_unity_exe() -> str:
    exe = (os.environ.get("AGENTFORGE_UNITY_EXE") or "").strip()
    if exe and Path(exe).is_file():
        return exe
    return _auto_find_tool_exe("unity")


def _resolve_unreal_editor_exe() -> str:
    exe = (os.environ.get("AGENTFORGE_UNREAL_EXE") or "").strip()
    if exe and Path(exe).is_file():
        return exe
    return _auto_find_tool_exe("unreal")


def _resolve_runuat(unreal_editor_exe: str) -> str:
    p = Path(unreal_editor_exe).resolve()
    for _ in range(8):
        candidate = p.parent.parent.parent / "Build" / "BatchFiles" / "RunUAT.bat"
        if candidate.is_file():
            return str(candidate)
        p = p.parent
    return ""


class DesignRequest(BaseModel):
    title: str
    genre: str | None = None
    platform: str | None = None
    description: str | None = None


class CreateProjectRequest(BaseModel):
    title: str
    engine: str
    prompt: str | None = None
    genre: str | None = None
    platform: str | None = None
    description: str | None = None


class ProjectActionRequest(BaseModel):
    project_id: str


class BuildProjectRequest(BaseModel):
    project_id: str
    target: str | None = None


@router.get("/status")
async def game_dev_status(request: Request):
    projects = _load_projects(request)
    return {
        "success": True,
        "data": {
            "module": "game_dev",
            "status": "ready",
            "description": "Game development assistant and engine integration",
            "total_projects": len(projects),
        },
        "error": None,
    }


@router.get("/engines")
async def detect_engines():
    unity_exe = _resolve_unity_exe()
    unreal_exe = _resolve_unreal_editor_exe()
    return {
        "success": True,
        "data": {
            "unity": {"exe": unity_exe, "detected": bool(unity_exe)},
            "unreal": {"exe": unreal_exe, "detected": bool(unreal_exe)},
        },
        "error": None,
    }


@router.get("/projects")
async def list_projects(request: Request):
    return {"success": True, "data": _load_projects(request), "error": None}


@router.post("/design")
async def generate_design(body: DesignRequest, request: Request):
    projects = _load_projects(request)
    project: Dict[str, Any] = {
        "id": str(uuid.uuid4())[:8],
        "title": body.title.strip() or "Untitled Game",
        "genre": (body.genre or "unknown"),
        "platform": (body.platform or "cross-platform"),
        "description": (body.description or ""),
        "status": "design",
        "created_at": _now(),
    }
    projects.append(project)
    _save_projects(request, projects)
    return {"success": True, "data": project, "error": None}


@router.post("/projects/create")
async def create_project(body: CreateProjectRequest, request: Request):
    ok, preflight = await require_preflight_ok(request, scope="game_dev.create")
    if not ok:
        return {"success": False, "data": {"preflight": preflight}, "error": "Preflight failed"}
    engine = body.engine.strip().lower()
    if engine not in {"unity", "unreal"}:
        return {"success": False, "data": None, "error": "engine must be unity or unreal"}

    ws = _workspace_root(request)
    slug = _slugify(body.title)
    project_dir = (ws / "game_dev" / engine / slug).resolve()
    project_dir.mkdir(parents=True, exist_ok=True)
    if not _within_workspace(request, project_dir):
        return {"success": False, "data": None, "error": "invalid project path"}

    prompt = (body.prompt or body.description or "").strip()
    (project_dir / "README.md").write_text(f"# {body.title}\n\nPrompt:\n{prompt}\n", encoding="utf-8")

    engine_target: str
    if engine == "unity":
        (project_dir / "Assets").mkdir(parents=True, exist_ok=True)
        _ensure_unity_build_script(project_dir)
        engine_target = str(project_dir)
    else:
        uproject_path = project_dir / f"{slug}.uproject"
        uproject = {
            "FileVersion": 3,
            "EngineAssociation": "",
            "Category": "Games",
            "Description": f"AgentForgeOS GameDev: {body.title}",
            "Modules": [],
            "Plugins": [],
        }
        uproject_path.write_text(json.dumps(uproject, indent=2), encoding="utf-8")
        engine_target = str(uproject_path)

    projects = _load_projects(request)
    project: Dict[str, Any] = {
        "id": str(uuid.uuid4())[:8],
        "title": body.title.strip() or "Untitled Game",
        "engine": engine,
        "path": str(project_dir),
        "target": engine_target,
        "prompt": prompt,
        "genre": body.genre or "unknown",
        "platform": body.platform or "pc",
        "description": body.description or "",
        "status": "created",
        "created_at": _now(),
        "updated_at": _now(),
    }
    projects.append(project)
    _save_projects(request, projects)
    return {"success": True, "data": project, "error": None}


def _find_project(request: Request, project_id: str) -> Optional[dict[str, Any]]:
    projects = _load_projects(request)
    for p in projects:
        if str(p.get("id")) == project_id:
            return p
    return None


@router.post("/projects/launch")
async def launch_project(body: ProjectActionRequest, request: Request):
    ok, preflight = await require_preflight_ok(request, scope="game_dev.launch")
    if not ok:
        return {"success": False, "data": {"preflight": preflight}, "error": "Preflight failed"}
    p = _find_project(request, body.project_id)
    if not p:
        return {"success": False, "data": None, "error": "project not found"}
    engine = str(p.get("engine") or "").strip().lower()
    target = Path(str(p.get("target") or "")).resolve()
    if not _within_workspace(request, target):
        return {"success": False, "data": None, "error": "invalid target path"}

    if engine == "unity":
        exe = _resolve_unity_exe()
        if not exe:
            return {"success": False, "data": None, "error": "Unity.exe not found"}
        argv = [exe, "-projectPath", str(target if target.is_dir() else target.parent)]
    elif engine == "unreal":
        exe = _resolve_unreal_editor_exe()
        if not exe:
            return {"success": False, "data": None, "error": "UnrealEditor.exe not found"}
        if target.is_dir() or target.suffix.lower() != ".uproject":
            return {"success": False, "data": None, "error": "Unreal target must be a .uproject file"}
        argv = [exe, str(target)]
    else:
        return {"success": False, "data": None, "error": "unsupported engine"}

    try:
        subprocess.Popen(argv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return {"success": True, "data": {"launched": True, "engine": engine, "target": str(target), "exe": exe}, "error": None}
    except Exception as exc:
        return {"success": False, "data": {"launched": False, "engine": engine}, "error": str(exc)}


@router.post("/projects/build")
async def build_project(body: BuildProjectRequest, request: Request):
    ok, preflight = await require_preflight_ok(request, scope="game_dev.build")
    if not ok:
        return {"success": False, "data": {"preflight": preflight}, "error": "Preflight failed"}
    p = _find_project(request, body.project_id)
    if not p:
        return {"success": False, "data": None, "error": "project not found"}

    engine = str(p.get("engine") or "").strip().lower()
    project_dir = Path(str(p.get("path") or "")).resolve()
    if not _within_workspace(request, project_dir):
        return {"success": False, "data": None, "error": "invalid project path"}

    if engine == "unity":
        exe = _resolve_unity_exe()
        if not exe:
            return {"success": False, "data": None, "error": "Unity.exe not found"}
        _ensure_unity_build_script(project_dir)
        (project_dir / "Builds" / "Windows").mkdir(parents=True, exist_ok=True)
        log_path = project_dir / "Builds" / "unity_build.log"
        argv = [
            exe,
            "-batchmode",
            "-nographics",
            "-quit",
            "-projectPath",
            str(project_dir),
            "-executeMethod",
            "AgentForgeBuild.BuildWindows",
            "-logFile",
            str(log_path),
        ]
        completed = subprocess.run(argv, capture_output=True, text=True, timeout=3600)
        tail = ""
        try:
            if log_path.is_file():
                tail = "\n".join(log_path.read_text(encoding="utf-8", errors="ignore").splitlines()[-80:])
        except Exception:
            tail = ""
        return {
            "success": completed.returncode == 0,
            "data": {
                "engine": "unity",
                "returncode": completed.returncode,
                "stdout": (completed.stdout or "")[-4000:],
                "stderr": (completed.stderr or "")[-4000:],
                "log_tail": tail,
                "output_dir": str((project_dir / "Builds" / "Windows").resolve()),
            },
            "error": None if completed.returncode == 0 else "Unity build failed",
        }

    if engine == "unreal":
        exe = _resolve_unreal_editor_exe()
        if not exe:
            return {"success": False, "data": None, "error": "UnrealEditor.exe not found"}
        target = Path(str(p.get("target") or "")).resolve()
        if target.suffix.lower() != ".uproject":
            return {"success": False, "data": None, "error": "Unreal target must be a .uproject file"}
        runuat = _resolve_runuat(exe)
        if not runuat:
            return {"success": False, "data": None, "error": "RunUAT.bat not found for this Unreal install"}
        out_dir = (project_dir / "Builds" / "Windows").resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        cmd = [
            "cmd.exe",
            "/c",
            runuat,
            "BuildCookRun",
            f"-project={str(target)}",
            "-noP4",
            "-platform=Win64",
            "-clientconfig=Development",
            "-build",
            "-cook",
            "-stage",
            "-pak",
            "-archive",
            f"-archivedirectory={str(out_dir)}",
        ]
        completed = subprocess.run(cmd, capture_output=True, text=True, timeout=7200)
        return {
            "success": completed.returncode == 0,
            "data": {
                "engine": "unreal",
                "returncode": completed.returncode,
                "stdout": (completed.stdout or "")[-8000:],
                "stderr": (completed.stderr or "")[-8000:],
                "output_dir": str(out_dir),
            },
            "error": None if completed.returncode == 0 else "Unreal build failed",
        }

    return {"success": False, "data": None, "error": "unsupported engine"}


@router.post("/scene")
async def scaffold_scene(body: Dict[str, Any] = {}):
    scene: Dict[str, Any] = {
        "project_id": body.get("project_id", ""),
        "scene_name": body.get("scene_name", "MainScene"),
        "entities": [],
        "generated_at": _now(),
    }
    return {"success": True, "data": scene, "error": None}
