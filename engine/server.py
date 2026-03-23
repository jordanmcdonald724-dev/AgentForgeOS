import logging
from logging.handlers import RotatingFileHandler
import os
import asyncio
import json
import sys
import threading
from datetime import UTC, datetime
import zipfile
import subprocess
import warnings
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Awaitable, Callable, Iterable, Optional, TypeVar, cast, overload
from uuid import uuid4

from fastapi import APIRouter, FastAPI, Request, BackgroundTasks, Header, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

if any("unittest" in str(a).lower() for a in sys.argv):
    warnings.simplefilter("ignore", ResourceWarning)
    os.environ.setdefault("AGENTFORGE_RATE_LIMIT_ENABLED", "false")

from engine.config import get_settings
from engine.database import db
from engine.module_loader import load_modules, collect_module_routers
from engine.worker_system import worker_system
from engine.routes import (
    modules_router,
    agent_router,
    setup_router,
    preflight_router,
    tasks_router,
    bridge_router,
    engine_config_router,
    v2_orchestration_router,
    v2_infrastructure_router,
    v2_research_router,
    v2_loop_router,
)
from backend.routes.monitoring import monitoring_router
from apps.research.backend.routes import router as research_backend_router
from engine.websocket_routes import websocket_router, cleanup_websocket_connections
from engine.routes.pipeline import router as pipeline_router
from engine.ws import execution_ws
from engine.rate_limit import RateLimiter
from control.module_registry import module_registry
from knowledge import KnowledgeGraph, KnowledgeVectorStore, EmbeddingService
from engine.routes.tasks import create_task_internal, set_task_status_internal, complete_task_internal, fail_task_internal

logger = logging.getLogger(__name__)
DEFAULT_CORS_ORIGINS = (
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5175",
    "null",
)

_logging_ready = False
_kb_ready = False
_kb_graph: KnowledgeGraph | None = None
_kb_vectors: KnowledgeVectorStore | None = None
_kb_embeddings: EmbeddingService | None = None

T = TypeVar("T")


def _get_exe_base_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def _resources_root(exe_base: Path) -> Path:
    base = exe_base if exe_base.name.lower() == "resources" else exe_base / "resources"
    if (base / "config.json").is_file() or (base / "providers.json").is_file():
        return base
    nested = base / "resources"
    if (nested / "config.json").is_file() or (nested / "providers.json").is_file():
        return nested
    return base


def _token_valid(token: str | None) -> bool:
    expected = os.environ.get("AGENTFORGE_BRIDGE_TOKEN", "")
    if not expected.strip():
        return False
    if token is None or not token.strip():
        return False
    return token.strip() == expected.strip()


def _auth_token(request: Request, header_token: str | None) -> str | None:
    if isinstance(header_token, str) and header_token.strip():
        return header_token.strip()
    cookie_token = request.cookies.get("agentforge_session")
    if isinstance(cookie_token, str) and cookie_token.strip():
        return cookie_token.strip()
    return None


@overload
def _read_json_file(path: Path, default: dict[str, Any]) -> dict[str, Any]: ...


@overload
def _read_json_file(path: Path, default: list[Any]) -> list[Any]: ...


@overload
def _read_json_file(path: Path, default: T) -> T: ...


def _read_json_file(path: Path, default: Any) -> Any:
    try:
        if path.is_file():
            data: Any = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(default, dict):
                if isinstance(data, dict):
                    return cast(dict[str, Any], data)
                return cast(dict[str, Any], default)
            if isinstance(default, list):
                if isinstance(data, list):
                    return cast(list[Any], data)
                return cast(list[Any], default)
            return data if isinstance(data, type(default)) else default
    except Exception:
        return default
    return default


def _write_json_file(path: Path, data: object) -> bool:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return True
    except Exception:
        return False


def _ensure_workspace_layout(workspace_path: Path) -> None:
    for name in ["projects", "builds", "deployments", "assets", "temp", "knowledge", "logs", "database", "embeddings"]:
        try:
            (workspace_path / name).mkdir(parents=True, exist_ok=True)
        except Exception:
            pass


def _detect_project_type(project_dir: Path) -> str:
    if (project_dir / "package.json").is_file():
        return "node"
    if (project_dir / "pyproject.toml").is_file() or (project_dir / "requirements.txt").is_file():
        return "python"
    return "unknown"


def _run_allowed_command(cmd: list[str], cwd: Path) -> dict[str, Any]:
    allowed_tools = {"python", "pip", "npm", "node", "git", "cargo"}
    tool = str(cmd[0]).strip().lower() if cmd else ""
    if tool not in allowed_tools:
        return {"ok": False, "returncode": 127, "stdout": "", "stderr": "Tool is not permitted"}
    try:
        proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=300)
        return {"ok": proc.returncode == 0, "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}
    except subprocess.TimeoutExpired:
        return {"ok": False, "returncode": 124, "stdout": "", "stderr": "Command timed out"}
    except Exception as exc:
        return {"ok": False, "returncode": 1, "stdout": "", "stderr": str(exc)}


def _zip_tree(source_dir: Path, archive_path: Path, *, root_name: str, ignore_dirs: set[str]) -> int:
    count = 0
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(str(archive_path), "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in source_dir.rglob("*"):
            if p.is_dir():
                continue
            rel = p.relative_to(source_dir)
            if any(part in ignore_dirs for part in rel.parts):
                continue
            zf.write(str(p), arcname=str(Path(root_name) / rel))
            count += 1
    return count


def _zip_tree_into(zf: zipfile.ZipFile, source_dir: Path, *, root_name: str, ignore_dirs: set[str]) -> int:
    count = 0
    for p in source_dir.rglob("*"):
        if p.is_dir():
            continue
        rel = p.relative_to(source_dir)
        if any(part in ignore_dirs for part in rel.parts):
            continue
        zf.write(str(p), arcname=str(Path(root_name) / rel))
        count += 1
    return count


def _zip_file_into(zf: zipfile.ZipFile, file_path: Path, *, arcname: str) -> int:
    try:
        if not file_path.is_file():
            return 0
        zf.write(str(file_path), arcname=arcname)
        return 1
    except Exception:
        return 0


def _write_build_artifacts(project_dir: Path, build_dir: Path, project_type: str) -> dict[str, Any]:
    artifacts_dir = build_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    artifact_zip = build_dir / "artifact.zip"

    if project_type == "node":
        candidates = ["dist", "build", "out"]
        for name in candidates:
            out_dir = project_dir / name
            if out_dir.is_dir():
                files = _zip_tree(out_dir, artifact_zip, root_name=name, ignore_dirs=set())
                return {"artifact_zip": str(artifact_zip), "artifact_kind": "directory", "artifact_source": name, "artifact_files": files}

    ignore = {".git", ".venv", "venv", "__pycache__", "node_modules", ".pytest_cache", ".mypy_cache", ".ruff_cache", "builds", "deployments"}
    files = _zip_tree(project_dir, artifact_zip, root_name="project", ignore_dirs=ignore)
    return {"artifact_zip": str(artifact_zip), "artifact_kind": "source", "artifact_source": "project", "artifact_files": files}


def _build_jobs_path(request: Request) -> Path:
    workspace_path = Path(getattr(request.app.state, "workspace_path", "") or (Path.home() / "Documents" / "AgentForgeOS"))
    _ensure_workspace_layout(workspace_path)
    return (workspace_path / "builds" / "build_jobs.json")


def _deploy_jobs_path(request: Request) -> Path:
    workspace_path = Path(getattr(request.app.state, "workspace_path", "") or (Path.home() / "Documents" / "AgentForgeOS"))
    _ensure_workspace_layout(workspace_path)
    return (workspace_path / "deployments" / "deploy_jobs.json")


def _assets_registry_path(exe_base: Path) -> Path:
    assets_dir = _resources_root(exe_base) / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    return assets_dir / "registry.json"


def _get_bundle_base_path() -> Path:
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if isinstance(meipass, str) and meipass:
            return Path(meipass)
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def _ensure_resources_layout(exe_base: Path) -> dict[str, Path]:
    resources_dir = _resources_root(exe_base)
    resources_dir.mkdir(parents=True, exist_ok=True)

    config_path = resources_dir / "config.json"
    providers_path = resources_dir / "providers.json"
    if not config_path.is_file():
        config_path.write_text("{}", encoding="utf-8")
    if not providers_path.is_file():
        providers_path.write_text("{}", encoding="utf-8")

    subdirs = {
        "config": resources_dir / "config",
        "workspace": resources_dir / "workspace",
        "logs": resources_dir / "logs",
        "knowledge": resources_dir / "knowledge",
        "database": resources_dir / "database",
        "embeddings": resources_dir / "embeddings",
        "assets": resources_dir / "assets",
    }
    for p in subdirs.values():
        p.mkdir(parents=True, exist_ok=True)

    engine_cfg = subdirs["config"] / "engine_config.json"
    if not engine_cfg.is_file():
        try:
            default_src = Path(__file__).resolve().parent.parent / "resources" / "config" / "engine_config.json"
            if default_src.is_file():
                engine_cfg.write_text(default_src.read_text(encoding="utf-8"), encoding="utf-8")
            else:
                engine_cfg.write_text("{}", encoding="utf-8")
        except Exception:
            try:
                engine_cfg.write_text("{}", encoding="utf-8")
            except Exception:
                pass

    return {"resources_dir": resources_dir, "config_path": config_path, "providers_path": providers_path, **subdirs}


def _ensure_bridge_token(exe_base: Path) -> str:
    env_token = os.getenv("AGENTFORGE_BRIDGE_TOKEN", "")
    if env_token.strip():
        return env_token.strip()
    cfg_path = _resources_root(exe_base) / "config.json"
    cfg: dict[str, Any]
    try:
        if cfg_path.is_file():
            loaded: Any = json.loads(cfg_path.read_text(encoding="utf-8"))
            cfg = loaded if isinstance(loaded, dict) else {}
        else:
            cfg = {}
    except Exception:
        cfg = {}
    token = cfg.get("bridge_token")
    if isinstance(token, str) and token.strip():
        return token.strip()
    token = uuid4().hex
    cfg["bridge_token"] = token
    try:
        cfg_path.parent.mkdir(parents=True, exist_ok=True)
        cfg_path.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    except Exception:
        pass
    return token


def _load_desktop_config(base_path: Path) -> dict[str, Any]:
    config_path = _resources_root(base_path) / "config.json"
    try:
        if config_path.is_file():
            return json.loads(config_path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return {}


def _resolve_workspace_path(config: dict[str, Any], exe_base: Optional[Path] = None) -> Path:
    configured = config.get("workspace_path")
    if isinstance(configured, str) and configured.strip():
        return Path(configured).expanduser().resolve()
    env_configured = os.getenv("WORKSPACE_PATH", "")
    if env_configured.strip():
        return Path(env_configured).expanduser().resolve()
    if isinstance(exe_base, Path):
        candidate = _resources_root(exe_base) / "workspace"
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            return candidate.resolve()
        except Exception:
            pass
    return Path.home() / "Documents" / "AgentForgeOS"


def _ensure_log_dir(exe_base: Path, workspace_path: Path) -> Path:
    preferred = _resources_root(exe_base) / "logs"
    try:
        preferred.mkdir(parents=True, exist_ok=True)
        return preferred
    except Exception:
        fallback = workspace_path / "logs"
        try:
            fallback.mkdir(parents=True, exist_ok=True)
        except Exception:
            return workspace_path
        return fallback


def _configure_file_logging(log_dir: Path, level_name: str) -> None:
    global _logging_ready
    if _logging_ready:
        return

    level = getattr(logging, (level_name or "INFO").upper(), logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")

    root = logging.getLogger()
    root.setLevel(level)

    system_handler = RotatingFileHandler(
        filename=str(log_dir / "system.log"),
        maxBytes=2_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    system_handler.setLevel(level)
    system_handler.setFormatter(fmt)
    root.addHandler(system_handler)

    error_handler = RotatingFileHandler(
        filename=str(log_dir / "errors.log"),
        maxBytes=2_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(fmt)
    root.addHandler(error_handler)

    pipeline_logger = logging.getLogger("pipeline")
    pipeline_logger.setLevel(level)
    pipeline_handler = RotatingFileHandler(
        filename=str(log_dir / "pipeline.log"),
        maxBytes=2_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    pipeline_handler.setLevel(level)
    pipeline_handler.setFormatter(fmt)
    pipeline_logger.addHandler(pipeline_handler)
    pipeline_logger.propagate = False

    agents_logger = logging.getLogger("agents")
    agents_logger.setLevel(level)
    agents_handler = RotatingFileHandler(
        filename=str(log_dir / "agents.log"),
        maxBytes=2_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    agents_handler.setLevel(level)
    agents_handler.setFormatter(fmt)
    agents_logger.addHandler(agents_handler)
    agents_logger.propagate = False

    deployment_logger = logging.getLogger("deployment")
    deployment_logger.setLevel(level)
    deployment_handler = RotatingFileHandler(
        filename=str(log_dir / "deployment.log"),
        maxBytes=2_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    deployment_handler.setLevel(level)
    deployment_handler.setFormatter(fmt)
    deployment_logger.addHandler(deployment_handler)
    deployment_logger.propagate = False

    _logging_ready = True


def _init_knowledge(workspace_path: Path) -> None:
    global _kb_ready, _kb_graph, _kb_vectors, _kb_embeddings
    if _kb_ready:
        return
    knowledge_dir = workspace_path / "knowledge"
    embeddings_dir = workspace_path / "embeddings"
    knowledge_dir.mkdir(parents=True, exist_ok=True)
    embeddings_dir.mkdir(parents=True, exist_ok=True)
    _kb_graph = KnowledgeGraph(persist_path=knowledge_dir / "knowledge_graph.json")
    _kb_vectors = KnowledgeVectorStore(persist_path=embeddings_dir / "knowledge_vectors.json")
    _kb_embeddings = EmbeddingService()
    _kb_ready = True


def _health_router() -> APIRouter:
    router = APIRouter()

    @router.get("/health", tags=["system"])
    async def health_check():
        """Basic health endpoint used by the desktop runtime and monitors."""
        return {"success": True, "data": {"status": "ok"}, "error": None}

    return router


def _system_router() -> APIRouter:
    router = APIRouter(prefix="/system", tags=["system"])

    @router.get("/health")
    async def system_health(request: Request) -> dict[str, Any]:
        return {"success": True, "data": {"status": "ok"}, "error": None}

    @router.get("/status")
    async def system_status(request: Request) -> dict[str, Any]:
        base_path = getattr(request.app.state, "base_path", "")
        workspace_path = getattr(request.app.state, "workspace_path", "")
        config_raw = getattr(request.app.state, "config", {}) or {}
        config: dict[str, Any] = dict(config_raw) if isinstance(config_raw, dict) else {}
        modules_map_raw = getattr(module_registry, "modules", {}) or {}
        modules_map: dict[str, Any] = dict(modules_map_raw) if isinstance(modules_map_raw, dict) else {}
        modules = list(modules_map.keys())
        return {
            "success": True,
            "data": {
                "environment": get_settings().environment,
                "base_path": base_path,
                "workspace_path": workspace_path,
                "modules_loaded": modules,
                "background_tasks": worker_system.running_task_count(),
                "config": {k: v for k, v in config.items() if k not in {"openai_key", "OPENAI_API_KEY"}},
            },
            "error": None,
        }

    @router.get("/config")
    async def get_system_config(request: Request) -> dict[str, Any]:
        config_raw = getattr(request.app.state, "config", {}) or {}
        config: dict[str, Any] = dict(config_raw) if isinstance(config_raw, dict) else {}
        return {"success": True, "data": {"config": config}, "error": None}

    @router.post("/config")
    async def set_system_config(request: Request, body: dict[str, Any]) -> dict[str, Any]:
        exe_base = Path(getattr(request.app.state, "base_path", "") or _get_exe_base_path())
        resources_dir = _resources_root(exe_base)
        resources_dir.mkdir(parents=True, exist_ok=True)
        config_path = resources_dir / "config.json"
        existing = _load_desktop_config(exe_base)
        incoming = body.get("config", body)
        if not isinstance(incoming, dict):
            incoming = {}
        allowed = {"workspace_path"}
        for k in allowed:
            if k in incoming and isinstance(incoming.get(k), str):
                existing[k] = incoming[k]
        try:
            config_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")
        except Exception:
            return {"success": False, "data": {"saved": False}, "error": "Failed to write config"}
        request.app.state.config = dict(existing)
        if "workspace_path" in existing:
            request.app.state.workspace_path = str(_resolve_workspace_path(existing))
        return {"success": True, "data": {"saved": True}, "error": None}

    @router.post("/start")
    async def system_start(request: Request):
        try:
            if worker_system.running_task_count() == 0:
                await worker_system.start()
            return {"success": True, "data": {"started": True, "background_tasks": worker_system.running_task_count()}, "error": None}
        except Exception as exc:
            return {"success": False, "data": {"started": False}, "error": str(exc)}

    @router.post("/shutdown")
    async def system_shutdown(request: Request):
        try:
            await worker_system.shutdown()
            return {"success": True, "data": {"shutdown": True, "background_tasks": worker_system.running_task_count()}, "error": None}
        except Exception as exc:
            return {"success": False, "data": {"shutdown": False}, "error": str(exc)}

    return router


def _logs_router() -> APIRouter:
    router = APIRouter(prefix="/logs", tags=["logs"])

    def _tail_lines(path: Path, limit: int) -> list[str]:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return []
        lines = [ln for ln in text.splitlines() if ln.strip()]
        return lines[-limit:]

    @router.get("")
    async def list_logs(request: Request, source: str = "system", limit: int = 200) -> dict[str, Any]:
        exe_base = Path(getattr(request.app.state, "base_path", "") or _get_exe_base_path())
        workspace_path = Path(getattr(request.app.state, "workspace_path", "") or (Path.home() / "Documents" / "AgentForgeOS"))
        log_dir = _ensure_log_dir(exe_base, workspace_path)
        safe_limit = max(1, min(int(limit), 500))
        mapping = {
            "system": log_dir / "system.log",
            "pipeline": log_dir / "pipeline.log",
            "agents": log_dir / "agents.log",
            "deployment": log_dir / "deployment.log",
            "errors": log_dir / "errors.log",
        }
        path = mapping.get(source, mapping["system"])
        lines = _tail_lines(path, safe_limit)
        entries: list[dict[str, str]] = []
        for ln in lines:
            parts = ln.split(" ", 3)
            if len(parts) >= 4:
                ts = " ".join(parts[:2])
                lvl = parts[2].lower()
                msg = parts[3]
            else:
                ts = ""
                lvl = "info"
                msg = ln
            entries.append({"time": ts, "level": lvl, "message": msg})
        return {"success": True, "data": {"source": source, "entries": entries}, "error": None}

    return router


def _providers_router() -> APIRouter:
    router = APIRouter(prefix="/providers", tags=["providers"])

    def _read_json(path: Path) -> dict[str, Any]:
        try:
            if path.is_file():
                loaded: Any = json.loads(path.read_text(encoding="utf-8"))
                return loaded if isinstance(loaded, dict) else {}
        except Exception:
            return {}
        return {}

    def _write_json(path: Path, data: dict[str, Any]) -> bool:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            return True
        except Exception:
            return False

    @router.get("")
    async def get_providers(request: Request) -> dict[str, Any]:
        exe_base = Path(getattr(request.app.state, "base_path", "") or _get_exe_base_path())
        providers_path = _resources_root(exe_base) / "providers.json"
        data = _read_json(providers_path)
        redacted: dict[str, Any] = dict(data)
        openai_section = redacted.get("openai")
        if isinstance(openai_section, dict) and openai_section.get("api_key"):
            redacted["openai"] = {**openai_section, "api_key": "********"}
        fal_section = redacted.get("fal")
        if isinstance(fal_section, dict) and fal_section.get("api_key"):
            redacted["fal"] = {**fal_section, "api_key": "********"}
        return {"success": True, "data": {"providers": redacted}, "error": None}

    @router.get("/test")
    async def test_providers(request: Request, type: str | None = None) -> dict[str, Any]:
        exe_base = Path(getattr(request.app.state, "base_path", "") or _get_exe_base_path())
        providers_path = _resources_root(exe_base) / "providers.json"
        providers_cfg = _read_json(providers_path)
        config_raw = getattr(request.app.state, "config", {}) or {}
        config: dict[str, Any] = dict(config_raw) if isinstance(config_raw, dict) else {}

        def _ok(ok: bool, detail: str) -> dict[str, Any]:
            return {"ok": bool(ok), "detail": str(detail)}

        async def _http_ok(url: str) -> tuple[bool, str]:
            try:
                import httpx  # type: ignore
            except Exception:
                return False, "httpx not installed"
            try:
                async with httpx.AsyncClient(timeout=2.5) as client:
                    r = await client.get(url)
                    if 200 <= r.status_code < 300:
                        return True, f"HTTP {r.status_code}"
                    return False, f"HTTP {r.status_code}"
            except Exception as exc:
                return False, str(exc)

        results: dict[str, Any] = {}

        cfg_providers = config.get("providers")
        selected = cfg_providers if isinstance(cfg_providers, dict) else {}
        llm = str(selected.get("llm") or "").strip().lower()
        image = str(selected.get("image") or "").strip().lower()
        tts = str(selected.get("tts") or "").strip().lower()

        if type in {None, "", "engine"}:
            results["engine"] = _ok(True, "ok")

        if type in {None, "", "llm"}:
            if llm == "ollama":
                ollama_cfg = config.get("ollama")
                base_url = ""
                if isinstance(ollama_cfg, dict):
                    base_url = str(ollama_cfg.get("base_url") or "").strip()
                base_url = base_url or "http://localhost:11434"
                ok, detail = await _http_ok(f"{base_url.rstrip('/')}/api/tags")
                results["llm"] = _ok(ok, f"ollama: {detail}")
            elif llm == "openai":
                openai_section = providers_cfg.get("openai")
                api_key = str(openai_section.get("api_key") or "").strip() if isinstance(openai_section, dict) else ""
                results["llm"] = _ok(bool(api_key), "openai: api_key configured" if api_key else "openai: missing api_key")
            elif llm == "fal":
                fal_section = providers_cfg.get("fal")
                api_key = str(fal_section.get("api_key") or "").strip() if isinstance(fal_section, dict) else ""
                if not api_key:
                    results["llm"] = _ok(False, "fal: missing api_key")
                else:
                    model = str(fal_section.get("model") or "").strip() if isinstance(fal_section, dict) else ""
                    try:
                        from providers.fal_llm_provider import FalLLMProvider

                        provider = FalLLMProvider(api_key=api_key, model=model or None, timeout=12.0)
                        resp = await provider.chat("ping")
                        ok = bool(resp.get("success"))
                        err = str(resp.get("error") or "").strip()
                        results["llm"] = _ok(ok, "fal: ok" if ok else f"fal: {err or 'failed'}")
                    except Exception as exc:
                        results["llm"] = _ok(False, f"fal: {exc}")
            elif llm:
                results["llm"] = _ok(False, f"unknown llm provider: {llm}")
            else:
                results["llm"] = _ok(False, "no llm provider selected")

        if type in {None, "", "image"}:
            if image == "comfyui":
                comfy_cfg = config.get("comfyui")
                base_url = ""
                if isinstance(comfy_cfg, dict):
                    base_url = str(comfy_cfg.get("base_url") or "").strip()
                base_url = base_url or "http://localhost:8188"
                ok, detail = await _http_ok(f"{base_url.rstrip('/')}/system_stats")
                results["image"] = _ok(ok, f"comfyui: {detail}")
            elif image == "fal":
                fal_section = providers_cfg.get("fal")
                api_key = str(fal_section.get("api_key") or "").strip() if isinstance(fal_section, dict) else ""
                results["image"] = _ok(bool(api_key), "fal: api_key configured" if api_key else "fal: missing api_key")
            elif image:
                results["image"] = _ok(False, f"unknown image provider: {image}")
            else:
                results["image"] = _ok(False, "no image provider selected")

        if type in {None, "", "tts"}:
            if tts == "piper":
                piper_cfg = config.get("piper")
                model_path = ""
                if isinstance(piper_cfg, dict):
                    model_path = str(piper_cfg.get("model_path") or "").strip()
                ok = bool(model_path and Path(model_path).exists())
                results["tts"] = _ok(ok, "piper: model_path exists" if ok else "piper: model_path missing")
            elif tts:
                results["tts"] = _ok(False, f"unknown tts provider: {tts}")
            else:
                results["tts"] = _ok(False, "no tts provider selected")

        return {"success": True, "data": {"results": results}, "error": None}

    @router.post("/config")
    async def set_providers_config(
        request: Request,
        body: dict[str, Any],
        x_agentforge_token: str | None = Header(default=None, alias="X-AgentForge-Token"),
    ) -> dict[str, Any]:
        if not _token_valid(_auth_token(request, x_agentforge_token)):
            return {"success": False, "data": None, "error": "Unauthorized"}
        exe_base = Path(getattr(request.app.state, "base_path", "") or _get_exe_base_path())
        providers_path = _resources_root(exe_base) / "providers.json"
        existing = _read_json(providers_path)
        incoming = body.get("providers", body.get("config", body))
        if not isinstance(incoming, dict):
            incoming = {}
        allowed = {
            ("openai", "api_key"),
            ("openai", "model"),
            ("fal", "api_key"),
            ("fal", "model"),
        }
        for section, key in allowed:
            section_data = incoming.get(section)
            if not isinstance(section_data, dict) or key not in section_data:
                continue
            existing_section = existing.get(section)
            if not isinstance(existing_section, dict):
                existing_section = {}
                existing[section] = existing_section
            existing_section[key] = str(section_data[key]).strip()
        ok = _write_json(providers_path, existing)
        return {"success": ok, "data": {"saved": ok}, "error": None if ok else "Failed to write providers config"}

    return router


def _workspace_router() -> APIRouter:
    router = APIRouter(prefix="/workspace", tags=["workspace"])

    @router.get("/status")
    async def workspace_status(request: Request) -> dict[str, Any]:
        workspace_path = Path(getattr(request.app.state, "workspace_path", "") or (Path.home() / "Documents" / "AgentForgeOS"))
        projects_dir = workspace_path / "projects"
        projects_dir.mkdir(parents=True, exist_ok=True)
        projects = [p.name for p in projects_dir.iterdir() if p.is_dir()]
        return {"success": True, "data": {"workspace_path": str(workspace_path), "projects_dir": str(projects_dir), "projects": sorted(projects)}, "error": None}

    @router.post("/set")
    async def workspace_set(
        request: Request,
        body: dict[str, Any],
        x_agentforge_token: str | None = Header(default=None, alias="X-AgentForge-Token"),
    ) -> dict[str, Any]:
        if not _token_valid(_auth_token(request, x_agentforge_token)):
            return {"success": False, "data": None, "error": "Unauthorized"}
        path = body.get("workspace_path") or body.get("path")
        if not isinstance(path, str) or not path.strip():
            return {"success": False, "data": None, "error": "workspace_path is required"}
        new_path = Path(path).expanduser().resolve()
        exe_base = Path(getattr(request.app.state, "base_path", "") or _get_exe_base_path())
        resources_dir = _resources_root(exe_base)
        resources_dir.mkdir(parents=True, exist_ok=True)
        config_path = resources_dir / "config.json"
        config = _load_desktop_config(exe_base)
        config["workspace_path"] = str(new_path)
        try:
            config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
        except Exception:
            return {"success": False, "data": None, "error": "Failed to write config"}
        request.app.state.config = dict(config)
        request.app.state.workspace_path = str(new_path)
        _init_knowledge(new_path)
        _ensure_workspace_layout(new_path)
        return {"success": True, "data": {"workspace_path": str(new_path)}, "error": None}

    return router


def _projects_router() -> APIRouter:
    router = APIRouter(prefix="/projects", tags=["projects"])

    def _project_dir(request: Request, project_id: str) -> Path:
        workspace_path = Path(getattr(request.app.state, "workspace_path", "") or (Path.home() / "Documents" / "AgentForgeOS"))
        return (workspace_path / "projects" / project_id).resolve()

    @router.get("")
    async def list_projects(request: Request) -> dict[str, Any]:
        workspace_path = Path(getattr(request.app.state, "workspace_path", "") or (Path.home() / "Documents" / "AgentForgeOS"))
        projects_dir = workspace_path / "projects"
        projects_dir.mkdir(parents=True, exist_ok=True)
        projects = [p.name for p in projects_dir.iterdir() if p.is_dir()]
        return {"success": True, "data": {"projects": sorted(projects)}, "error": None}

    @router.post("/create")
    async def create_project(
        request: Request,
        body: dict[str, Any],
        x_agentforge_token: str | None = Header(default=None, alias="X-AgentForge-Token"),
    ) -> dict[str, Any]:
        if not _token_valid(_auth_token(request, x_agentforge_token)):
            return {"success": False, "data": None, "error": "Unauthorized"}
        name = body.get("name") or body.get("id")
        if not isinstance(name, str) or not name.strip():
            return {"success": False, "data": None, "error": "name is required"}
        safe = "".join(c for c in name.strip() if c.isalnum() or c in {"-", "_"}).strip("-_")
        if not safe:
            return {"success": False, "data": None, "error": "invalid name"}
        workspace_path = Path(getattr(request.app.state, "workspace_path", "") or (Path.home() / "Documents" / "AgentForgeOS"))
        projects_dir = workspace_path / "projects"
        projects_dir.mkdir(parents=True, exist_ok=True)
        project_dir = projects_dir / safe
        project_dir.mkdir(parents=True, exist_ok=True)
        return {"success": True, "data": {"id": safe, "path": str(project_dir)}, "error": None}

    @router.get("/{project_id}")
    async def get_project(request: Request, project_id: str) -> dict[str, Any]:
        project_dir = _project_dir(request, project_id)
        if not project_dir.exists() or not project_dir.is_dir():
            return {"success": False, "data": None, "error": "project not found"}
        return {"success": True, "data": {"id": project_id, "path": str(project_dir)}, "error": None}

    @router.post("/{project_id}/build")
    async def build_project(
        request: Request,
        project_id: str,
        background: BackgroundTasks,
        x_agentforge_token: str | None = Header(default=None, alias="X-AgentForge-Token"),
    ) -> dict[str, Any]:
        if not _token_valid(_auth_token(request, x_agentforge_token)):
            return {"success": False, "data": None, "error": "Unauthorized"}
        project_dir = _project_dir(request, project_id)
        if not project_dir.exists() or not project_dir.is_dir():
            return {"success": False, "data": None, "error": "project not found"}

        workspace_path = Path(getattr(request.app.state, "workspace_path", "") or (Path.home() / "Documents" / "AgentForgeOS"))
        _ensure_workspace_layout(workspace_path)

        build_id = f"build_{uuid4().hex[:12]}"
        task = create_task_internal(request, type="build", description=f"Build project {project_id}", planned_files=5, planned_loc=500)

        jobs_path = _build_jobs_path(request)
        jobs_raw = _read_json_file(jobs_path, [])
        jobs: list[dict[str, Any]] = [cast(dict[str, Any], j) for j in jobs_raw if isinstance(j, dict)]
        record: dict[str, Any] = {
            "build_id": build_id,
            "project_id": project_id,
            "task_id": task.task_id,
            "status": "queued",
            "created_at": datetime.now(UTC).isoformat(),
            "updated_at": datetime.now(UTC).isoformat(),
        }
        jobs.append(record)
        _write_json_file(jobs_path, jobs)

        build_dir = workspace_path / "builds" / build_id
        build_dir.mkdir(parents=True, exist_ok=True)
        _write_json_file(build_dir / "build.json", record)

        def _run_build_job():
            set_task_status_internal(request, task.task_id, "in_progress")

            latest_raw = _read_json_file(jobs_path, [])
            latest: list[dict[str, Any]] = [cast(dict[str, Any], j) for j in latest_raw if isinstance(j, dict)]
            for j in latest:
                if j.get("build_id") == build_id:
                    j["status"] = "running"
                    j["updated_at"] = datetime.now(UTC).isoformat()
            _write_json_file(jobs_path, latest)

            status = "completed"
            message = "Build completed"
            output: list[str] = []
            output.append(f"build_id={build_id}")
            output.append(f"project_id={project_id}")
            output.append(f"project_dir={project_dir}")
            output.append(f"started_at={datetime.now(UTC).isoformat()}")

            try:
                has_files = any(project_dir.iterdir())
                if not has_files:
                    status = "failed"
                    message = "Project directory is empty"
                else:
                    kind = _detect_project_type(project_dir)
                    output.append(f"project_type={kind}")
                    if kind == "node":
                        result = _run_allowed_command(["npm", "run", "build", "--if-present"], cwd=project_dir)
                        output.append(f"returncode={result['returncode']}")
                        if result["stdout"]:
                            output.append("stdout:")
                            output.append(result["stdout"])
                        if result["stderr"]:
                            output.append("stderr:")
                            output.append(result["stderr"])
                        if not result["ok"]:
                            status = "failed"
                            message = "Node build command failed"
                    elif kind == "python":
                        result = _run_allowed_command(["python", "-m", "compileall", "."], cwd=project_dir)
                        output.append(f"returncode={result['returncode']}")
                        if result["stdout"]:
                            output.append("stdout:")
                            output.append(result["stdout"])
                        if result["stderr"]:
                            output.append("stderr:")
                            output.append(result["stderr"])
                        if not result["ok"]:
                            status = "failed"
                            message = "Python compile failed"
                    else:
                        message = "Unknown project type; no build executed"
                    if status == "completed":
                        artifacts = _write_build_artifacts(project_dir, build_dir, kind)
                        record.update({"project_type": kind, **artifacts})
                        output.append(f"artifact_zip={record.get('artifact_zip')}")
            except Exception as exc:
                status = "failed"
                message = str(exc)

            for j in latest:
                if j.get("build_id") == build_id:
                    j["status"] = status
                    j["message"] = message
                    if "project_type" in record:
                        j["project_type"] = record["project_type"]
                    if "artifact_zip" in record:
                        j["artifact_zip"] = record["artifact_zip"]
                        j["artifact_kind"] = record.get("artifact_kind")
                        j["artifact_source"] = record.get("artifact_source")
                        j["artifact_files"] = record.get("artifact_files")
                    j["updated_at"] = datetime.now(UTC).isoformat()
            _write_json_file(jobs_path, latest)
            job_record = next((j for j in latest if j.get("build_id") == build_id), record)
            _write_json_file(build_dir / "build.json", job_record)
            try:
                (build_dir / "build.log").write_text("\n".join(output + [f"status={status}", f"message={message}"]), encoding="utf-8")
            except Exception:
                pass

            if status == "completed":
                complete_task_internal(request, task.task_id, actual_files=0, actual_loc=0)
            else:
                fail_task_internal(request, task.task_id, message)

        threading.Thread(target=_run_build_job, daemon=True).start()
        return {"success": True, "data": {"build_id": build_id, "task_id": task.task_id, "status": "queued"}, "error": None}

    @router.post("/{project_id}/deploy")
    async def deploy_project(
        request: Request,
        project_id: str,
        background: BackgroundTasks,
        x_agentforge_token: str | None = Header(default=None, alias="X-AgentForge-Token"),
    ) -> dict[str, Any]:
        if not _token_valid(_auth_token(request, x_agentforge_token)):
            return {"success": False, "data": None, "error": "Unauthorized"}
        project_dir = _project_dir(request, project_id)
        if not project_dir.exists() or not project_dir.is_dir():
            return {"success": False, "data": None, "error": "project not found"}

        deploy_id = f"deploy_{uuid4().hex[:12]}"
        task = create_task_internal(request, type="deploy", description=f"Deploy project {project_id}", planned_files=5, planned_loc=500)

        jobs_path = _deploy_jobs_path(request)
        jobs_raw = _read_json_file(jobs_path, [])
        jobs: list[dict[str, Any]] = [cast(dict[str, Any], j) for j in jobs_raw if isinstance(j, dict)]
        record: dict[str, Any] = {
            "deploy_id": deploy_id,
            "project_id": project_id,
            "task_id": task.task_id,
            "status": "queued",
            "target": "local",
            "created_at": datetime.now(UTC).isoformat(),
            "updated_at": datetime.now(UTC).isoformat(),
        }
        jobs.append(record)
        _write_json_file(jobs_path, jobs)

        def _run_deploy_job():
            set_task_status_internal(request, task.task_id, "in_progress")

            latest_raw = _read_json_file(jobs_path, [])
            latest: list[dict[str, Any]] = [cast(dict[str, Any], j) for j in latest_raw if isinstance(j, dict)]
            for j in latest:
                if j.get("deploy_id") == deploy_id:
                    j["status"] = "running"
                    j["updated_at"] = datetime.now(UTC).isoformat()
            _write_json_file(jobs_path, latest)

            status = "completed"
            message = "Deploy completed"
            output: list[str] = []
            output.append(f"deploy_id={deploy_id}")
            output.append(f"project_id={project_id}")
            output.append(f"project_dir={project_dir}")
            output.append(f"started_at={datetime.now(UTC).isoformat()}")

            workspace_path = Path(getattr(request.app.state, "workspace_path", "") or (Path.home() / "Documents" / "AgentForgeOS"))
            _ensure_workspace_layout(workspace_path)
            deploy_dir = workspace_path / "deployments" / deploy_id
            deploy_dir.mkdir(parents=True, exist_ok=True)

            try:
                build_jobs_raw = _read_json_file(_build_jobs_path(request), [])
                build_jobs: list[dict[str, Any]] = [cast(dict[str, Any], b) for b in build_jobs_raw if isinstance(b, dict)]
                completed = [b for b in build_jobs if b.get("project_id") == project_id and b.get("status") == "completed"]
                build_id_value = completed[-1].get("build_id") if completed else None
                build_id = str(build_id_value).strip() if isinstance(build_id_value, str) and str(build_id_value).strip() else None
                if build_id is None:
                    status = "failed"
                    message = "No completed build found for project"
                else:
                    build_dir = workspace_path / "builds" / build_id
                    artifact_zip_path = build_dir / "artifact.zip"
                    source_dir = build_dir if build_dir.exists() else project_dir
                    output.append(f"build_id={build_id}")
                    output.append(f"source_dir={source_dir}")
                    archive_path = deploy_dir / "artifact.zip"
                    if artifact_zip_path.is_file():
                        archive_path.write_bytes(artifact_zip_path.read_bytes())
                        output.append(f"artifact_source_zip={artifact_zip_path}")
                        record["artifact_zip"] = str(archive_path)
                        record["artifact_source"] = "build_artifact_zip"
                    else:
                        files = _zip_tree(source_dir, archive_path, root_name="payload", ignore_dirs=set())
                        output.append(f"artifact_files={files}")
                        record["artifact_zip"] = str(archive_path)
                        record["artifact_source"] = "directory_snapshot"
            except Exception as exc:
                status = "failed"
                message = str(exc)

            for j in latest:
                if j.get("deploy_id") == deploy_id:
                    j["status"] = status
                    j["message"] = message
                    if "artifact_zip" in record:
                        j["artifact_zip"] = record["artifact_zip"]
                        j["artifact_source"] = record.get("artifact_source")
                    j["updated_at"] = datetime.now(UTC).isoformat()
            _write_json_file(jobs_path, latest)
            _write_json_file(deploy_dir / "deploy.json", next((j for j in latest if j.get("deploy_id") == deploy_id), record))
            try:
                (deploy_dir / "deploy.log").write_text("\n".join(output + [f"status={status}", f"message={message}"]), encoding="utf-8")
            except Exception:
                pass

            if status == "completed":
                complete_task_internal(request, task.task_id, actual_files=0, actual_loc=0)
            else:
                fail_task_internal(request, task.task_id, message)

        threading.Thread(target=_run_deploy_job, daemon=True).start()
        return {"success": True, "data": {"deploy_id": deploy_id, "task_id": task.task_id, "status": "queued"}, "error": None}

    @router.get("/{project_id}/status")
    async def project_status(request: Request, project_id: str) -> dict[str, Any]:
        project_dir = _project_dir(request, project_id)
        if not project_dir.exists() or not project_dir.is_dir():
            return {"success": False, "data": None, "error": "project not found"}
        builds_raw = _read_json_file(_build_jobs_path(request), [])
        builds: list[dict[str, Any]] = [cast(dict[str, Any], b) for b in builds_raw if isinstance(b, dict)]
        deploys_raw = _read_json_file(_deploy_jobs_path(request), [])
        deploys: list[dict[str, Any]] = [cast(dict[str, Any], d) for d in deploys_raw if isinstance(d, dict)]
        return {
            "success": True,
            "data": {
                "project_id": project_id,
                "builds": [b for b in builds if b.get("project_id") == project_id],
                "deployments": [d for d in deploys if d.get("project_id") == project_id],
            },
            "error": None,
        }

    return router


def _assets_router() -> APIRouter:
    router = APIRouter(prefix="/assets", tags=["assets"])

    @router.get("")
    async def list_assets(request: Request) -> dict[str, Any]:
        exe_base = Path(getattr(request.app.state, "base_path", "") or _get_exe_base_path())
        registry_path = _assets_registry_path(exe_base)
        data = _read_json_file(registry_path, {"assets": []})
        assets_raw = data.get("assets")
        assets: list[dict[str, Any]] = []
        if isinstance(assets_raw, list):
            assets = [cast(dict[str, Any], a) for a in assets_raw if isinstance(a, dict)]
        data["assets"] = assets
        return {"success": True, "data": {"assets": assets}, "error": None}

    @router.post("/generate")
    async def generate_asset(
        request: Request,
        body: dict[str, Any],
        x_agentforge_token: str | None = Header(default=None, alias="X-AgentForge-Token"),
    ) -> dict[str, Any]:
        if not _token_valid(_auth_token(request, x_agentforge_token)):
            return {"success": False, "data": None, "error": "Unauthorized"}
        exe_base = Path(getattr(request.app.state, "base_path", "") or _get_exe_base_path())
        registry_path = _assets_registry_path(exe_base)
        data = _read_json_file(registry_path, {"assets": []})
        assets_raw = data.get("assets")
        assets: list[dict[str, Any]] = []
        if isinstance(assets_raw, list):
            assets = [cast(dict[str, Any], a) for a in assets_raw if isinstance(a, dict)]
        data["assets"] = assets

        asset_type_value = body.get("type")
        asset_type = asset_type_value.strip() if isinstance(asset_type_value, str) and asset_type_value.strip() else "asset"
        name_value = body.get("name")
        name = name_value.strip() if isinstance(name_value, str) and name_value.strip() else None
        asset_id = f"asset_{uuid4().hex[:12]}"
        filename_value = body.get("filename")
        filename = filename_value.strip() if isinstance(filename_value, str) and filename_value.strip() else f"{asset_id}.txt"
        assets_dir = registry_path.parent
        file_path = assets_dir / filename
        if not file_path.exists():
            try:
                file_path.write_text(f"{asset_type}:{asset_id}", encoding="utf-8")
            except Exception:
                pass

        record = {
            "id": asset_id,
            "type": asset_type,
            "name": name or asset_id,
            "path": str(file_path),
            "created_at": datetime.now(UTC).isoformat(),
        }
        assets.append(record)
        _write_json_file(registry_path, data)
        return {"success": True, "data": {"asset": record}, "error": None}

    return router


def _deploy_router() -> APIRouter:
    router = APIRouter(tags=["deployment"])

    @router.post("/deploy")
    async def deploy(
        request: Request,
        body: dict[str, Any],
        background: BackgroundTasks,
        x_agentforge_token: str | None = Header(default=None, alias="X-AgentForge-Token"),
    ) -> dict[str, Any]:
        if not _token_valid(_auth_token(request, x_agentforge_token)):
            return {"success": False, "data": None, "error": "Unauthorized"}
        deploy_id = f"deploy_{uuid4().hex[:12]}"
        target_value = body.get("target")
        target = target_value.strip() if isinstance(target_value, str) and target_value.strip() else "local"
        jobs_path = _deploy_jobs_path(request)
        jobs_raw = _read_json_file(jobs_path, [])
        jobs: list[dict[str, Any]] = [cast(dict[str, Any], j) for j in jobs_raw if isinstance(j, dict)]
        record: dict[str, Any] = {
            "deploy_id": deploy_id,
            "project_id": None,
            "status": "queued",
            "target": target,
            "created_at": datetime.now(UTC).isoformat(),
            "updated_at": datetime.now(UTC).isoformat(),
        }
        jobs.append(record)
        _write_json_file(jobs_path, jobs)

        def _run_global_deploy_job():
            latest_raw = _read_json_file(jobs_path, [])
            latest: list[dict[str, Any]] = [cast(dict[str, Any], j) for j in latest_raw if isinstance(j, dict)]
            for j in latest:
                if j.get("deploy_id") == deploy_id:
                    j["status"] = "running"
                    j["updated_at"] = datetime.now(UTC).isoformat()
            _write_json_file(jobs_path, latest)

            workspace_path = Path(getattr(request.app.state, "workspace_path", "") or (Path.home() / "Documents" / "AgentForgeOS"))
            _ensure_workspace_layout(workspace_path)
            deploy_dir = workspace_path / "deployments" / deploy_id
            deploy_dir.mkdir(parents=True, exist_ok=True)

            status = "completed"
            message = "Deploy completed"
            output: list[str] = []
            output.append(f"deploy_id={deploy_id}")
            output.append(f"target={target}")
            output.append(f"workspace_path={workspace_path}")

            artifact_zip = deploy_dir / "artifact.zip"
            file_count = 0

            latest_raw = _read_json_file(jobs_path, [])
            latest: list[dict[str, Any]] = [cast(dict[str, Any], j) for j in latest_raw if isinstance(j, dict)]
            try:
                exe_base = Path(getattr(request.app.state, "base_path", "") or _get_exe_base_path())
                resources_dir = _resources_root(exe_base)
                ignore_projects = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", "out"}
                with zipfile.ZipFile(str(artifact_zip), "w", compression=zipfile.ZIP_DEFLATED) as zf:
                    file_count += _zip_file_into(zf, resources_dir / "config.json", arcname="resources/config.json")
                    file_count += _zip_file_into(zf, resources_dir / "providers.json", arcname="resources/providers.json")
                    file_count += _zip_file_into(zf, resources_dir / "assets" / "registry.json", arcname="resources/assets/registry.json")
                    projects_dir = workspace_path / "projects"
                    if projects_dir.is_dir():
                        file_count += _zip_tree_into(zf, projects_dir, root_name="workspace/projects", ignore_dirs=ignore_projects)
                    assets_dir = workspace_path / "assets"
                    if assets_dir.is_dir():
                        file_count += _zip_tree_into(zf, assets_dir, root_name="workspace/assets", ignore_dirs={"__pycache__"})
                record["artifact_zip"] = str(artifact_zip)
                record["artifact_files"] = file_count
                output.append(f"artifact_zip={artifact_zip}")
                output.append(f"artifact_files={file_count}")
            except Exception as exc:
                status = "failed"
                message = str(exc)

            for j in latest:
                if j.get("deploy_id") == deploy_id:
                    j["status"] = status
                    j["message"] = message
                    if "artifact_zip" in record:
                        j["artifact_zip"] = record["artifact_zip"]
                        j["artifact_files"] = record.get("artifact_files")
                    j["updated_at"] = datetime.now(UTC).isoformat()
            _write_json_file(jobs_path, latest)
            _write_json_file(deploy_dir / "deploy.json", next((j for j in latest if j.get("deploy_id") == deploy_id), record))
            try:
                (deploy_dir / "deploy.log").write_text("\n".join(output + [f"status={status}", f"message={message}"]), encoding="utf-8")
            except Exception:
                pass

        threading.Thread(target=_run_global_deploy_job, daemon=True).start()
        return {"success": True, "data": {"deploy_id": deploy_id, "status": "queued"}, "error": None}

    @router.get("/deploy/status")
    async def deploy_status(request: Request, deploy_id: str | None = None) -> dict[str, Any]:
        jobs_path = _deploy_jobs_path(request)
        jobs_raw = _read_json_file(jobs_path, [])
        jobs: list[dict[str, Any]] = [cast(dict[str, Any], j) for j in jobs_raw if isinstance(j, dict)]
        if deploy_id:
            job = next((j for j in jobs if j.get("deploy_id") == deploy_id), None)
            return {"success": True, "data": {"deploy_id": deploy_id, "job": job}, "error": None}
        return {"success": True, "data": {"jobs": jobs[-50:]}, "error": None}

    return router


def _knowledge_router() -> APIRouter:
    router = APIRouter(prefix="/knowledge", tags=["knowledge"])

    def _ensure_kb(request: Request) -> tuple[KnowledgeGraph, KnowledgeVectorStore, EmbeddingService]:
        workspace_path = Path(getattr(request.app.state, "workspace_path", "") or (Path.home() / "Documents" / "AgentForgeOS"))
        _init_knowledge(workspace_path)
        assert _kb_graph is not None and _kb_vectors is not None and _kb_embeddings is not None
        return _kb_graph, _kb_vectors, _kb_embeddings

    @router.post("/store")
    async def knowledge_store(request: Request, body: dict[str, Any]):
        graph, vectors, embed = _ensure_kb(request)
        content = body.get("content") or body.get("text")
        if not isinstance(content, str) or not content.strip():
            return {"success": False, "data": None, "error": "content is required"}
        node_id = body.get("id")
        if not isinstance(node_id, str) or not node_id.strip():
            node_id = f"node_{abs(hash(content))}"
        meta_value = body.get("metadata")
        meta: dict[str, Any] = cast(dict[str, Any], meta_value) if isinstance(meta_value, dict) else {}
        payload: dict[str, Any] = {"content": content, **meta}
        graph.add_node(node_id, payload)
        vectors.add(node_id, {"id": node_id, "content": content, **meta}, embed.get_embedding(content))
        return {"success": True, "data": {"id": node_id}, "error": None}

    @router.post("/search")
    async def knowledge_search(request: Request, body: dict[str, Any]):
        graph, vectors, embed = _ensure_kb(request)
        query = body.get("query") or body.get("text")
        if not isinstance(query, str) or not query.strip():
            return {"success": False, "data": None, "error": "query is required"}
        top_k = body.get("top_k", 5)
        try:
            k = max(1, min(int(top_k), 10))
        except Exception:
            k = 5
        results = vectors.query(embed.get_embedding(query), top_k=k)
        return {"success": True, "data": {"results": results}, "error": None}

    @router.get("/search")
    async def knowledge_search_get(request: Request, query: str, top_k: int = 5):
        graph, vectors, embed = _ensure_kb(request)
        if not isinstance(query, str) or not query.strip():
            return {"success": False, "data": None, "error": "query is required"}
        try:
            k = max(1, min(int(top_k), 10))
        except Exception:
            k = 5
        results = vectors.query(embed.get_embedding(query), top_k=k)
        return {"success": True, "data": {"results": results}, "error": None}

    @router.post("/graph/add")
    async def knowledge_graph_add(request: Request, body: dict[str, Any]):
        graph, _, _ = _ensure_kb(request)
        source = body.get("source")
        target = body.get("target")
        if not isinstance(source, str) or not source.strip():
            return {"success": False, "data": None, "error": "source is required"}
        if not isinstance(target, str) or not target.strip():
            return {"success": False, "data": None, "error": "target is required"}
        try:
            graph.add_edge(source.strip(), target.strip())
        except Exception as exc:
            return {"success": False, "data": None, "error": str(exc)}
        return {"success": True, "data": {"source": source.strip(), "target": target.strip()}, "error": None}

    @router.get("/node/{node_id}")
    async def knowledge_node(request: Request, node_id: str):
        graph, _, _ = _ensure_kb(request)
        node = graph.get_node(node_id)
        if not node:
            return {"success": False, "data": None, "error": "node not found"}
        return {"success": True, "data": {"id": node_id, "node": node}, "error": None}

    return router


@asynccontextmanager
async def engine_lifespan(app: FastAPI):
    logger.info("Starting AgentForgeOS engine")
    exe_base = _get_exe_base_path()
    _ensure_resources_layout(exe_base)
    bridge_token = _ensure_bridge_token(exe_base)
    os.environ.setdefault("AGENTFORGE_BRIDGE_TOKEN", bridge_token)
    config = _load_desktop_config(exe_base)
    try:
        providers_path = _resources_root(exe_base) / "providers.json"
        if providers_path.is_file():
            providers_cfg = json.loads(providers_path.read_text(encoding="utf-8"))
            if isinstance(providers_cfg, dict):
                openai = providers_cfg.get("openai")
                if isinstance(openai, dict):
                    api_key = str(openai.get("api_key") or "").strip()
                    model = str(openai.get("model") or "").strip()
                    if api_key and not os.environ.get("OPENAI_API_KEY", "").strip():
                        os.environ["OPENAI_API_KEY"] = api_key
                    if model and not os.environ.get("OPENAI_MODEL", "").strip():
                        os.environ["OPENAI_MODEL"] = model
                fal = providers_cfg.get("fal")
                if isinstance(fal, dict):
                    api_key = str(fal.get("api_key") or "").strip()
                    model = str(fal.get("model") or "").strip()
                    if api_key and not os.environ.get("FAL_API_KEY", "").strip():
                        os.environ["FAL_API_KEY"] = api_key
                    if model and not os.environ.get("FAL_LLM_MODEL", "").strip():
                        os.environ["FAL_LLM_MODEL"] = model
        raw_providers = config.get("providers")
        providers_sel: dict[str, Any] = raw_providers if isinstance(raw_providers, dict) else {}
        llm_sel = str(providers_sel.get("llm") or "").strip()
        if llm_sel and not os.environ.get("PROVIDER_LLM", "").strip():
            os.environ["PROVIDER_LLM"] = llm_sel
        image_sel = str(providers_sel.get("image") or "").strip()
        if image_sel and not os.environ.get("PROVIDER_IMAGE", "").strip():
            os.environ["PROVIDER_IMAGE"] = image_sel
        tts_sel = str(providers_sel.get("tts") or "").strip()
        if tts_sel and not os.environ.get("PROVIDER_TTS", "").strip():
            os.environ["PROVIDER_TTS"] = tts_sel
        raw_ollama = config.get("ollama")
        ollama_cfg: dict[str, Any] = raw_ollama if isinstance(raw_ollama, dict) else {}
        ollama_url = str(ollama_cfg.get("base_url") or "").strip()
        if ollama_url and not os.environ.get("OLLAMA_BASE_URL", "").strip():
            os.environ["OLLAMA_BASE_URL"] = ollama_url
        ollama_model = str(ollama_cfg.get("model") or "").strip()
        if ollama_model and not os.environ.get("OLLAMA_MODEL", "").strip():
            os.environ["OLLAMA_MODEL"] = ollama_model
        raw_mongo = config.get("mongo")
        mongo_cfg: dict[str, Any] = raw_mongo if isinstance(raw_mongo, dict) else {}
        mongo_uri = str(mongo_cfg.get("uri") or "").strip()
        if mongo_uri and not os.environ.get("AGENTFORGE_MONGO_URI", "").strip():
            os.environ["AGENTFORGE_MONGO_URI"] = mongo_uri
        mongo_db = str(mongo_cfg.get("db") or "").strip()
        if mongo_db and not os.environ.get("AGENTFORGE_MONGO_DB", "").strip():
            os.environ["AGENTFORGE_MONGO_DB"] = mongo_db
    except Exception:
        pass
    workspace_path = _resolve_workspace_path(config, exe_base=exe_base)
    try:
        workspace_path.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    _ensure_workspace_layout(workspace_path)
    app.state.base_path = str(exe_base)
    app.state.config = dict(config)
    app.state.workspace_path = str(workspace_path)
    _init_knowledge(workspace_path)
    log_dir = _ensure_log_dir(exe_base, workspace_path)
    app.state.log_dir = str(log_dir)
    os.environ.setdefault("AGENTFORGE_LOG_DIR", str(log_dir))
    _configure_file_logging(log_dir, os.getenv("LOG_LEVEL", "INFO"))
    load_modules(registry=module_registry)
    await db.connect()
    await worker_system.start()
    
    # Start WebSocket cleanup task
    cleanup_task = asyncio.create_task(cleanup_websocket_connections())
    
    try:
        yield
    finally:
        # Cancel cleanup task
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass
        
        await worker_system.shutdown()
        await db.disconnect()


def register_routers(
    app: FastAPI, routers: Iterable[APIRouter], prefix: Optional[str] = None
) -> None:
    for router in routers:
        if prefix:
            app.include_router(router, prefix=prefix)
        else:
            app.include_router(router)


REPO_FRONTEND_ROOT = Path(__file__).resolve().parent.parent / "frontend"
REPO_FRONTEND_DIST = REPO_FRONTEND_ROOT / "dist"
FRONTEND_ROOT = REPO_FRONTEND_DIST if (REPO_FRONTEND_DIST / "index.html").is_file() else REPO_FRONTEND_ROOT


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=engine_lifespan)
    exe_base = _get_exe_base_path()
    _ensure_resources_layout(exe_base)
    config = _load_desktop_config(exe_base)
    workspace_path = _resolve_workspace_path(config, exe_base=exe_base)
    app.state.base_path = str(exe_base)
    app.state.config = dict(config)
    app.state.workspace_path = str(workspace_path)
    log_dir = _ensure_log_dir(exe_base, workspace_path)
    app.state.log_dir = str(log_dir)
    os.environ.setdefault("AGENTFORGE_LOG_DIR", str(log_dir))
    _configure_file_logging(log_dir, os.getenv("LOG_LEVEL", "INFO"))
    cors_raw = os.getenv("CORS_ORIGINS")
    if cors_raw is None or not cors_raw.strip() or cors_raw.strip() == "*":
        cors_raw = ",".join(DEFAULT_CORS_ORIGINS)
    cors_origins = [origin.strip() for origin in cors_raw.split(",") if origin.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    audit_logger = logging.getLogger("audit")
    rate_limiter = RateLimiter()

    @app.middleware("http")
    async def audit_middleware(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        path = request.url.path
        method = request.method
        token = _auth_token(request, request.headers.get("X-AgentForge-Token"))
        role = request.headers.get("X-AgentForge-Role", "")
        authed = _token_valid(token)
        try:
            response = await call_next(request)
        except Exception:
            audit_logger.error("AUDIT method=%s path=%s authed=%s role=%s status=500", method, path, authed, role)
            raise
        audit_logger.info("AUDIT method=%s path=%s authed=%s role=%s status=%s", method, path, authed, role, getattr(response, "status_code", ""))
        return response

    @app.middleware("http")
    async def rate_limit_middleware(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        ok = await rate_limiter.allow(request)
        if not ok:
            return JSONResponse(status_code=429, content={"success": False, "data": None, "error": "rate limit exceeded"})
        return await call_next(request)

    @app.middleware("http")
    async def module_gate_middleware(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        path = request.url.path or ""
        prefix = "/api/modules/"
        if path.startswith(prefix):
            rest = path[len(prefix):]
            module_id = rest.split("/", 1)[0].strip()
            if module_id:
                known = module_registry.get_module(module_id) is not None
                if known and not module_registry.is_enabled(module_id):
                    return JSONResponse(status_code=403, content={"success": False, "data": None, "error": "module disabled"})
        return await call_next(request)

    app.include_router(_health_router())

    # Core engine routes
    register_routers(
        app,
        [
            _health_router(),
            _system_router(),
            _logs_router(),
            _providers_router(),
            _workspace_router(),
            _projects_router(),
            _knowledge_router(),
            _assets_router(),
            _deploy_router(),
            modules_router,
            agent_router,
            setup_router,
            preflight_router,
            tasks_router,
            bridge_router,
            engine_config_router,
            pipeline_router,
            v2_orchestration_router,
            v2_infrastructure_router,
            v2_research_router,
            v2_loop_router,
            monitoring_router,
            research_backend_router,
            websocket_router,  # Add WebSocket router
        ],
        prefix="/api",
    )

    # Real-time event stream (WebSocket)
    app.add_api_websocket_route("/ws", execution_ws)

    # Module-specific backend routes (discovered from apps/*/backend/routes.py)
    module_routers = collect_module_routers()
    for mod_router in module_routers:
        if isinstance(mod_router, APIRouter):
            app.include_router(mod_router, prefix="/api/modules")

    exe_base = _get_exe_base_path()
    bundle_base = _get_bundle_base_path()
    exe_ui_root = exe_base / "frontend-build"
    bundled_ui_root = bundle_base / "frontend-build"
    if (exe_ui_root / "index.html").is_file():
        ui_root = exe_ui_root
    elif (bundled_ui_root / "index.html").is_file():
        ui_root = bundled_ui_root
    else:
        ui_root = FRONTEND_ROOT
    index_path = ui_root / "index.html"
    if index_path.is_file():
        app.mount("/", StaticFiles(directory=str(ui_root), html=True), name="frontend")

        @app.get("/", include_in_schema=False)
        async def serve_emergent_root():
            return FileResponse(str(index_path))
    else:
        logger.warning("UI index.html not found at %s; backend will serve API only", index_path)

    return app


if __name__ == "__main__":
    uvicorn = __import__("uvicorn")
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
