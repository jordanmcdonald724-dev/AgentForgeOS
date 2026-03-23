from __future__ import annotations

import json
import os
import time
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from fastapi import Request

from engine.router.config_loader import get_paths, load_engine_config_user_override


@dataclass(frozen=True)
class PreflightIssue:
    code: str
    message: str
    detail: Dict[str, Any]


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _safe_path(p: Any) -> str:
    try:
        return str(p)
    except Exception:
        return ""


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        if not path.is_file():
            return {}
        raw = json.loads(path.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else {}
    except Exception:
        return {}


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except Exception:
        return


def _resolve_workspace(request: Request) -> Tuple[Optional[Path], Optional[Path]]:
    base_raw = getattr(request.app.state, "base_path", "") or ""
    ws_raw = getattr(request.app.state, "workspace_path", "") or ""
    base = None
    ws = None
    try:
        if isinstance(base_raw, str) and base_raw.strip():
            base = Path(base_raw).resolve()
    except Exception:
        base = None
    try:
        if isinstance(ws_raw, str) and ws_raw.strip():
            ws = Path(ws_raw).resolve()
    except Exception:
        ws = None
    return ws, base


def _config_selected_provider(request: Request) -> Dict[str, str]:
    cfg_raw = getattr(request.app.state, "config", {}) or {}
    cfg = dict(cfg_raw) if isinstance(cfg_raw, dict) else {}
    providers = cfg.get("providers")
    providers = dict(providers) if isinstance(providers, dict) else {}
    out: Dict[str, str] = {}
    for k in ("llm", "image", "tts"):
        v = providers.get(k)
        if isinstance(v, str) and v.strip():
            out[k] = v.strip().lower()
    return out


def _provider_keys_snapshot() -> Dict[str, Dict[str, str]]:
    paths = get_paths()
    providers_path = paths.resources_dir / "providers.json"
    providers_cfg = _read_json(providers_path)
    out: Dict[str, Dict[str, str]] = {}
    for key in ("fal", "openai", "anthropic"):
        section = providers_cfg.get(key)
        if isinstance(section, dict):
            api_key = str(section.get("api_key") or "").strip()
            model = str(section.get("model") or "").strip()
            out[key] = {"api_key": api_key, "model": model}
    return out


def _engine_override_keys_snapshot() -> Dict[str, str]:
    override = load_engine_config_user_override()
    api_keys = override.get("api_keys")
    api_keys = dict(api_keys) if isinstance(api_keys, dict) else {}
    out: Dict[str, str] = {}
    for k, v in api_keys.items():
        if isinstance(k, str) and isinstance(v, str) and v.strip():
            out[k.strip().lower()] = v.strip()
    return out


def _get_key(engine: str) -> str:
    e = (engine or "").strip().lower()
    if e == "fal":
        return (os.environ.get("FAL_API_KEY") or "").strip()
    if e == "openai":
        return (os.environ.get("OPENAI_API_KEY") or "").strip()
    if e == "anthropic":
        return (os.environ.get("ANTHROPIC_API_KEY") or "").strip()
    return ""


def _has_key(engine: str, providers: Dict[str, Dict[str, str]], override_keys: Dict[str, str]) -> bool:
    e = (engine or "").strip().lower()
    if _get_key(e):
        return True
    if e in override_keys and override_keys[e]:
        return True
    if e in providers and providers[e].get("api_key"):
        return True
    return False


async def _mongo_ping(uri: str) -> Tuple[bool, str]:
    try:
        from motor.motor_asyncio import AsyncIOMotorClient  # type: ignore
    except Exception:
        return False, "motor unavailable"
    try:
        client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=1500)
        await client.admin.command("ping")
        client.close()
        return True, "ping ok"
    except Exception as exc:
        try:
            client.close()
        except Exception:
            pass
        return False, str(exc)


async def run_preflight(request: Request, *, scope: str = "default") -> Dict[str, Any]:
    blockers: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []

    ws, base = _resolve_workspace(request)
    ws_raw = _safe_path(getattr(request.app.state, "workspace_path", ""))
    if ws is None:
        if ws_raw.strip():
            blockers.append(
                {
                    "code": "workspace.invalid",
                    "message": "Workspace path is not configured or not a directory",
                    "detail": {"workspace_path": ws_raw},
                }
            )
        else:
            ws = (Path.home() / "Documents" / "AgentForgeOS").resolve()
            warnings.append(
                {
                    "code": "workspace.unset",
                    "message": "Workspace path is not set; using default",
                    "detail": {"workspace_path": str(ws)},
                }
            )
    if ws is not None:
        if not ws.exists() or not ws.is_dir():
            warnings.append(
                {
                    "code": "workspace.missing",
                    "message": "Workspace directory does not exist yet",
                    "detail": {"workspace_path": str(ws)},
                }
            )
        if base is not None:
            try:
                if str(ws).lower().startswith(str(base).lower()):
                    blockers.append(
                        {
                            "code": "workspace.unsafe",
                            "message": "Workspace must not be inside the application install directory",
                            "detail": {"workspace_path": str(ws), "base_path": str(base)},
                        }
                    )
            except Exception:
                pass

    providers = _provider_keys_snapshot()
    override_keys = _engine_override_keys_snapshot()
    selected = _config_selected_provider(request)

    llm = selected.get("llm") or os.environ.get("PROVIDER_LLM", "").strip().lower()
    if llm in {"fal", "openai", "anthropic"}:
        if not _has_key(llm, providers, override_keys):
            blockers.append(
                {
                    "code": f"provider.{llm}.missing_key",
                    "message": f"Missing API key for selected LLM provider: {llm}",
                    "detail": {"provider": llm},
                }
            )
    elif llm:
        warnings.append({"code": "provider.llm.unknown", "message": f"Unknown LLM provider: {llm}", "detail": {"provider": llm}})
    else:
        warnings.append({"code": "provider.llm.unset", "message": "No LLM provider selected", "detail": {}})

    image = selected.get("image") or os.environ.get("PROVIDER_IMAGE", "").strip().lower()
    if image in {"fal"}:
        if not _has_key("fal", providers, override_keys):
            blockers.append(
                {
                    "code": "provider.fal.missing_key",
                    "message": "Missing API key for Fal (required for image provider)",
                    "detail": {"provider": "fal"},
                }
            )

    mongo_uri = (os.environ.get("AGENTFORGE_MONGO_URI") or "").strip()
    cfg_raw = getattr(request.app.state, "config", {}) or {}
    cfg = dict(cfg_raw) if isinstance(cfg_raw, dict) else {}
    mongo_cfg = cfg.get("mongo")
    if isinstance(mongo_cfg, dict):
        mongo_uri = mongo_uri or str(mongo_cfg.get("uri") or "").strip()
    if mongo_uri:
        ok, detail = await _mongo_ping(mongo_uri)
        if not ok:
            blockers.append({"code": "mongo.unreachable", "message": "MongoDB is configured but unreachable", "detail": {"error": detail}})

    token = (os.environ.get("AGENTFORGE_BRIDGE_TOKEN") or "").strip()
    if not token:
        warnings.append({"code": "bridge.token.missing", "message": "Bridge token is not configured", "detail": {}})

    scope_l = str(scope or "").strip().lower()
    if scope_l.startswith("deployment.apply."):
        if not bool(shutil.which("docker")):
            blockers.append({"code": "deploy.docker.missing", "message": "docker is required for deploy apply", "detail": {}})
        if not bool(shutil.which("kubectl")):
            blockers.append({"code": "deploy.kubectl.missing", "message": "kubectl is required for deploy apply", "detail": {}})
        else:
            try:
                ctx = subprocess.run(["kubectl", "config", "current-context"], capture_output=True, text=True, timeout=15)
                if ctx.returncode != 0 or not (ctx.stdout or "").strip():
                    blockers.append({"code": "deploy.kubectl.context", "message": "kubectl current context is not configured", "detail": {"stderr": (ctx.stderr or "")[-2000:]}})
            except Exception as exc:
                blockers.append({"code": "deploy.kubectl.context", "message": "kubectl current context check failed", "detail": {"error": str(exc)}})

        if scope_l.endswith(".aws"):
            if not bool(shutil.which("aws")):
                blockers.append({"code": "deploy.awscli.missing", "message": "aws cli is required for aws deploy", "detail": {}})
            else:
                try:
                    sts = subprocess.run(["aws", "sts", "get-caller-identity"], capture_output=True, text=True, timeout=20)
                    if sts.returncode != 0:
                        blockers.append({"code": "deploy.awscli.auth", "message": "aws cli is not authenticated", "detail": {"stderr": (sts.stderr or "")[-2000:]}})
                except Exception as exc:
                    blockers.append({"code": "deploy.awscli.auth", "message": "aws cli auth check failed", "detail": {"error": str(exc)}})

        if scope_l.endswith(".gcp"):
            if not bool(shutil.which("gcloud")):
                blockers.append({"code": "deploy.gcloud.missing", "message": "gcloud is required for gcp deploy", "detail": {}})
            else:
                try:
                    auth = subprocess.run(
                        ["gcloud", "auth", "list", "--filter=status:ACTIVE", "--format=value(account)"],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                    if auth.returncode != 0 or not (auth.stdout or "").strip():
                        blockers.append({"code": "deploy.gcloud.auth", "message": "gcloud is not authenticated", "detail": {"stderr": (auth.stderr or "")[-2000:]}})
                except Exception as exc:
                    blockers.append({"code": "deploy.gcloud.auth", "message": "gcloud auth check failed", "detail": {"error": str(exc)}})

    out = {
        "ok": len(blockers) == 0,
        "scope": scope,
        "ts": _now_iso(),
        "blockers": blockers,
        "warnings": warnings,
    }

    try:
        paths = get_paths()
        db_dir = paths.resources_dir / "database"
        _write_json(db_dir / "preflight.json", out)
    except Exception:
        pass

    return out


async def require_preflight_ok(request: Request, *, scope: str) -> Tuple[bool, Dict[str, Any]]:
    result = await run_preflight(request, scope=scope)
    return bool(result.get("ok")), result
