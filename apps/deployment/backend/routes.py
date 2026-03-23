"""Deployment module backend API routes.

Provides endpoints for the Deployment manager:
- listing deployments
- triggering a deployment action
- checking deployment status
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import shutil
import zipfile
import re
import uuid
import os
from typing import Any, Dict, List

from fastapi import APIRouter, Request

from engine.security.preflight import require_preflight_ok

router = APIRouter(prefix="/deployment", tags=["deployment"])

_deployments: List[Dict[str, Any]] = []

def _resources_db_dir(request: Request) -> Path:
    base_raw = getattr(request.app.state, "base_path", "") or ""
    base = Path(base_raw) if isinstance(base_raw, str) and base_raw else Path(__file__).resolve().parents[3]
    out = (base / "resources" / "database").resolve()
    out.mkdir(parents=True, exist_ok=True)
    return out


def _deployments_file(request: Request) -> Path:
    return _resources_db_dir(request) / "deployments.json"


def _load_deployments(request: Request) -> List[Dict[str, Any]]:
    path = _deployments_file(request)
    if not path.is_file():
        return []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return raw if isinstance(raw, list) else []
    except Exception:
        return []


def _save_deployments(request: Request, items: List[Dict[str, Any]]) -> None:
    path = _deployments_file(request)
    path.write_text(json.dumps(items, indent=2), encoding="utf-8")


def _workspace_path(request: Request) -> Path:
    raw = getattr(request.app.state, "workspace_path", "") or (Path.home() / "Documents" / "AgentForgeOS")
    return Path(raw)

def _deployment_uid() -> str:
    return f"deploy_{uuid.uuid4().hex[:12]}"


def _deployment_dir(workspace: Path, uid: str) -> Path:
    out = (workspace / "deployments" / uid).resolve()
    out.mkdir(parents=True, exist_ok=True)
    return out


def _persist_deployment_json(deployment_dir: Path, deployment: Dict[str, Any]) -> None:
    try:
        (deployment_dir / "deployment.json").write_text(json.dumps(deployment, indent=2), encoding="utf-8")
    except Exception:
        return


def _docker_available() -> bool:
    try:
        return bool(shutil.which("docker"))
    except Exception:
        return False


def _compose_argv() -> list[str]:
    try:
        if shutil.which("docker-compose"):
            return ["docker-compose"]
    except Exception:
        pass
    return ["docker", "compose"]

def _kubectl_available() -> bool:
    try:
        return bool(shutil.which("kubectl"))
    except Exception:
        return False


def _aws_available() -> bool:
    try:
        return bool(shutil.which("aws"))
    except Exception:
        return False


def _gcloud_available() -> bool:
    try:
        return bool(shutil.which("gcloud"))
    except Exception:
        return False


def _safe_k8s_name(text: str) -> str:
    s = re.sub(r"[^a-z0-9-]+", "-", str(text or "").strip().lower()).strip("-")
    s = re.sub(r"-{2,}", "-", s)
    if not s:
        s = "app"
    if len(s) > 63:
        s = s[:63].rstrip("-")
    return s or "app"


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_dockerignore(path: Path) -> None:
    _write_text(
        path,
        "\n".join(
            [
                ".git",
                "**/.git",
                "**/__pycache__",
                "**/.venv",
                "**/venv",
                "**/node_modules",
                "**/.DS_Store",
                "**/dist",
                "**/build",
            ]
        )
        + "\n",
    )


def _generate_static_web_dockerfile() -> str:
    return "\n".join(
        [
            "FROM nginx:alpine",
            "COPY dist/ /usr/share/nginx/html/",
            "EXPOSE 80",
        ]
    ) + "\n"


def _generate_proxy_nginx_conf() -> str:
    return "\n".join(
        [
            "server {",
            "  listen 80;",
            "  server_name _;",
            "  location / {",
            "    root /usr/share/nginx/html;",
            "    try_files $uri /index.html;",
            "  }",
            "  location /api/ {",
            "    proxy_pass http://backend:8000;",
            "    proxy_set_header Host $host;",
            "    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;",
            "  }",
            "  location /ws {",
            "    proxy_pass http://backend:8000/ws;",
            "    proxy_http_version 1.1;",
            "    proxy_set_header Upgrade $http_upgrade;",
            '    proxy_set_header Connection "upgrade";',
            "    proxy_set_header Host $host;",
            "  }",
            "}",
        ]
    ) + "\n"


def _generate_web_with_proxy_dockerfile() -> str:
    return "\n".join(
        [
            "FROM nginx:alpine",
            "COPY nginx.conf /etc/nginx/conf.d/default.conf",
            "COPY dist/ /usr/share/nginx/html/",
            "EXPOSE 80",
        ]
    ) + "\n"

def _generate_ingress_yaml(
    *,
    name: str,
    namespace: str,
    host: str,
    ingress_class: str | None,
    use_tls: bool,
    tls_secret: str | None,
    cluster_issuer: str | None,
    web_service: str,
    api_service: str | None,
) -> str:
    annotations: list[str] = []
    if ingress_class:
        annotations.append(f"    kubernetes.io/ingress.class: {ingress_class}")
    annotations.append("    nginx.ingress.kubernetes.io/proxy-read-timeout: \"3600\"")
    annotations.append("    nginx.ingress.kubernetes.io/proxy-send-timeout: \"3600\"")
    if cluster_issuer:
        annotations.append(f"    cert-manager.io/cluster-issuer: {cluster_issuer}")

    tls_block: list[str] = []
    if use_tls and tls_secret and host:
        tls_block = [
            "  tls:",
            "    - hosts:",
            f"        - {host}",
            f"      secretName: {tls_secret}",
        ]

    paths: list[str] = []
    if api_service:
        paths += [
            "          - path: /api",
            "            pathType: Prefix",
            "            backend:",
            "              service:",
            f"                name: {api_service}",
            "                port:",
            "                  number: 8000",
            "          - path: /ws",
            "            pathType: Prefix",
            "            backend:",
            "              service:",
            f"                name: {api_service}",
            "                port:",
            "                  number: 8000",
        ]
    paths += [
        "          - path: /",
        "            pathType: Prefix",
        "            backend:",
        "              service:",
        f"                name: {web_service}",
        "                port:",
        "                  number: 80",
    ]

    return "\n".join(
        [
            "apiVersion: networking.k8s.io/v1",
            "kind: Ingress",
            "metadata:",
            f"  name: {name}",
            "  annotations:",
            *annotations,
            "spec:",
            *(tls_block if tls_block else []),
            "  rules:",
            "    - host: " + host,
            "      http:",
            "        paths:",
            *paths,
            "",
        ]
    )


def _collect_secret_values(request: Request) -> dict[str, str]:
    values: dict[str, str] = {}
    for k in ("FAL_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "AGENTFORGE_MONGO_URI", "AGENTFORGE_MONGO_DB"):
        v = (os.environ.get(k) or "").strip()
        if v:
            values[k] = v
    cfg_raw = getattr(request.app.state, "config", {}) or {}
    cfg = dict(cfg_raw) if isinstance(cfg_raw, dict) else {}
    mongo = cfg.get("mongo")
    if isinstance(mongo, dict):
        uri = str(mongo.get("uri") or "").strip()
        dbn = str(mongo.get("db") or mongo.get("db_name") or "").strip()
        if uri and "AGENTFORGE_MONGO_URI" not in values:
            values["AGENTFORGE_MONGO_URI"] = uri
        if dbn and "AGENTFORGE_MONGO_DB" not in values:
            values["AGENTFORGE_MONGO_DB"] = dbn
    return values


def _kubectl_create_secret(namespace: str, name: str, values: dict[str, str]) -> dict[str, Any]:
    ns = subprocess.run(
        ["kubectl", "create", "namespace", namespace],
        capture_output=True,
        text=True,
        timeout=60,
    )
    delete = subprocess.run(
        ["kubectl", "delete", "secret", name, "-n", namespace, "--ignore-not-found"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    argv = ["kubectl", "create", "secret", "generic", name, "-n", namespace]
    for k, v in values.items():
        argv += ["--from-literal", f"{k}={v}"]
    create = subprocess.run(argv, capture_output=True, text=True, timeout=60)
    return {
        "namespace": {"returncode": ns.returncode, "stdout": (ns.stdout or "")[-2000:], "stderr": (ns.stderr or "")[-2000:]},
        "delete": {"returncode": delete.returncode, "stdout": (delete.stdout or "")[-2000:], "stderr": (delete.stderr or "")[-2000:]},
        "create": {"returncode": create.returncode, "stdout": (create.stdout or "")[-2000:], "stderr": (create.stderr or "")[-2000:]},
        "keys": list(values.keys()),
        "name": name,
    }


def _detect_fastapi_backend(project_dir: Path) -> dict[str, Any] | None:
    backend_dir = (project_dir / "backend").resolve()
    if not backend_dir.is_dir():
        return None
    candidates = [
        backend_dir / "main.py",
        backend_dir / "app.py",
        backend_dir / "server.py",
    ]
    for p in candidates:
        if not p.is_file():
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if "FastAPI" in text and "app" in text and ("FastAPI(" in text or "fastapi" in text.lower()):
            return {"backend_dir": backend_dir, "module": p.stem, "app_var": "app"}
    if (backend_dir / "requirements.txt").is_file():
        return {"backend_dir": backend_dir, "module": "main", "app_var": "app"}
    return None


def _generate_backend_dockerfile(module: str) -> str:
    mod = (module or "main").strip()
    return "\n".join(
        [
            "FROM python:3.11-slim",
            "WORKDIR /app",
            "ENV PYTHONDONTWRITEBYTECODE=1",
            "ENV PYTHONUNBUFFERED=1",
            "COPY . /app",
            "RUN pip install --no-cache-dir -U pip && \\",
            "    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi && \\",
            "    pip install --no-cache-dir 'uvicorn[standard]' 'fastapi'",
            "EXPOSE 8000",
            f'CMD ["python","-m","uvicorn","{mod}:app","--host","0.0.0.0","--port","8000"]',
        ]
    ) + "\n"


def _docker_compose_up(compose_dir: Path, project_name: str) -> dict[str, Any]:
    argv = _compose_argv() + ["-p", project_name, "up", "-d", "--build"]
    proc = subprocess.run(argv, cwd=str(compose_dir), capture_output=True, text=True, timeout=1800)
    return {"returncode": proc.returncode, "stdout": (proc.stdout or "")[-8000:], "stderr": (proc.stderr or "")[-8000:], "command": argv}

def _kubectl_apply(manifests_dir: Path, namespace: str) -> dict[str, Any]:
    create_ns = subprocess.run(
        ["kubectl", "create", "namespace", namespace],
        cwd=str(manifests_dir),
        capture_output=True,
        text=True,
        timeout=60,
    )
    apply = subprocess.run(
        ["kubectl", "apply", "-n", namespace, "-f", str(manifests_dir)],
        cwd=str(manifests_dir),
        capture_output=True,
        text=True,
        timeout=180,
    )
    return {
        "create_namespace": {
            "returncode": create_ns.returncode,
            "stdout": (create_ns.stdout or "")[-4000:],
            "stderr": (create_ns.stderr or "")[-4000:],
        },
        "apply": {"returncode": apply.returncode, "stdout": (apply.stdout or "")[-8000:], "stderr": (apply.stderr or "")[-8000:]},
    }

def _docker_tag(src: str, dest: str) -> dict[str, Any]:
    proc = subprocess.run(["docker", "tag", src, dest], capture_output=True, text=True, timeout=120)
    return {"returncode": proc.returncode, "stdout": (proc.stdout or "")[-4000:], "stderr": (proc.stderr or "")[-4000:]}


def _docker_push(tag: str) -> dict[str, Any]:
    proc = subprocess.run(["docker", "push", tag], capture_output=True, text=True, timeout=1800)
    return {"returncode": proc.returncode, "stdout": (proc.stdout or "")[-8000:], "stderr": (proc.stderr or "")[-8000:]}


def _aws_account_id(region: str) -> str:
    proc = subprocess.run(
        ["aws", "sts", "get-caller-identity", "--query", "Account", "--output", "text", "--region", region],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if proc.returncode != 0:
        return ""
    return (proc.stdout or "").strip()


def _aws_ensure_ecr_repo(region: str, repository: str) -> dict[str, Any]:
    describe = subprocess.run(
        ["aws", "ecr", "describe-repositories", "--repository-names", repository, "--region", region],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if describe.returncode == 0:
        return {"returncode": 0, "stdout": (describe.stdout or "")[-4000:], "stderr": (describe.stderr or "")[-2000:], "created": False}
    create = subprocess.run(
        ["aws", "ecr", "create-repository", "--repository-name", repository, "--region", region],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return {"returncode": create.returncode, "stdout": (create.stdout or "")[-4000:], "stderr": (create.stderr or "")[-2000:], "created": create.returncode == 0}


def _aws_ecr_login(region: str, registry: str) -> dict[str, Any]:
    pw = subprocess.run(
        ["aws", "ecr", "get-login-password", "--region", region],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if pw.returncode != 0:
        return {"returncode": pw.returncode, "stdout": (pw.stdout or "")[-2000:], "stderr": (pw.stderr or "")[-2000:]}
    login = subprocess.run(
        ["docker", "login", "--username", "AWS", "--password-stdin", registry],
        input=(pw.stdout or ""),
        capture_output=True,
        text=True,
        timeout=60,
    )
    return {"returncode": login.returncode, "stdout": (login.stdout or "")[-2000:], "stderr": (login.stderr or "")[-2000:]}


def _gcloud_configure_docker(host: str) -> dict[str, Any]:
    proc = subprocess.run(
        ["gcloud", "auth", "configure-docker", host, "-q"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    return {"returncode": proc.returncode, "stdout": (proc.stdout or "")[-4000:], "stderr": (proc.stderr or "")[-4000:]}


def _docker_build(context_dir: Path, tag: str) -> dict[str, Any]:
    proc = subprocess.run(
        ["docker", "build", "-t", tag, "."],
        cwd=str(context_dir),
        capture_output=True,
        text=True,
        timeout=1800,
    )
    return {"returncode": proc.returncode, "stdout": (proc.stdout or "")[-8000:], "stderr": (proc.stderr or "")[-8000:]}


def _docker_run(tag: str, host_port: int) -> dict[str, Any]:
    proc = subprocess.run(
        ["docker", "run", "-d", "-p", f"{host_port}:80", tag],
        capture_output=True,
        text=True,
        timeout=120,
    )
    cid = (proc.stdout or "").strip().splitlines()[-1] if proc.stdout else ""
    return {"returncode": proc.returncode, "stdout": (proc.stdout or "")[-4000:], "stderr": (proc.stderr or "")[-4000:], "container_id": cid}


@router.get("/status")
async def deployment_status(request: Request):
    """Return the Deployment module's current operational status."""
    items = _load_deployments(request)
    return {
        "success": True,
        "data": {
            "module": "deployment",
            "status": "ready",
            "description": "Project deployment manager",
            "total_deployments": len(items),
        },
        "error": None,
    }


@router.get("/list")
async def list_deployments(request: Request):
    """Return all recorded deployments."""
    return {"success": True, "data": _load_deployments(request), "error": None}


@router.post("/deploy")
async def trigger_deployment(request: Request, body: Dict[str, Any] = {}):
    """Create a deployment artifact for a workspace project."""
    import datetime

    ok, preflight = await require_preflight_ok(request, scope="deployment.deploy")
    deployments = _load_deployments(request)
    if not ok:
        deployment: Dict[str, Any] = {
            "id": len(deployments) + 1,
            "target": body.get("target", "local"),
            "project": body.get("project", "unknown"),
            "version": body.get("version", "0.0.1"),
            "status": "failed",
            "initiated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "finished_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "error": "Preflight failed",
            "preflight": preflight,
        }
        deployments.append(deployment)
        _save_deployments(request, deployments)
        return {"success": False, "data": deployment, "error": deployment["error"]}

    workspace = _workspace_path(request)
    uid = _deployment_uid()
    deploy_dir = _deployment_dir(workspace, uid)
    deployment: Dict[str, Any] = {
        "id": len(deployments) + 1,
        "uid": uid,
        "deploy_dir": str(deploy_dir),
        "target": body.get("target", "local"),
        "project": body.get("project", "unknown"),
        "version": body.get("version", "0.0.1"),
        "status": "pending",
        "initiated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    deployments.append(deployment)
    _save_deployments(request, deployments)
    _persist_deployment_json(deploy_dir, deployment)

    project = str(deployment.get("project") or "").strip()
    if not project or project == "unknown":
        deployment["status"] = "failed"
        deployment["error"] = "project is required"
        deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return {"success": False, "data": deployment, "error": deployment["error"]}

    project_dir = (workspace / "projects" / project).resolve()
    if not project_dir.is_dir():
        deployment["status"] = "failed"
        deployment["error"] = "project not found"
        deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _save_deployments(request, deployments)
        return {"success": False, "data": deployment, "error": deployment["error"]}

    target = str(deployment.get("target") or "local").strip().lower()
    version = str(deployment.get("version") or "0.0.1").strip()
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    artifact_name = f"{project}_{target}_{version}_{ts}.zip"
    artifact_path = (deploy_dir / artifact_name).resolve()

    def _should_skip(rel: str) -> bool:
        parts = rel.replace("\\", "/").split("/")
        if not parts:
            return False
        banned = {"node_modules", ".git", "__pycache__", ".venv", "venv"}
        return any(p in banned for p in parts)

    try:
        build_dir = (project_dir / "frontend" / "dist").resolve()
        if not build_dir.is_dir() and target in {"web", "local", "staging", "prod", "production"}:
            frontend_dir = (project_dir / "frontend").resolve()
            pkg = frontend_dir / "package.json"
            node_modules = frontend_dir / "node_modules"
            if pkg.is_file() and node_modules.is_dir():
                proc = subprocess.run(
                    ["npm", "run", "build"],
                    cwd=str(frontend_dir),
                    capture_output=True,
                    text=True,
                    timeout=900,
                )
                deployment["build_returncode"] = proc.returncode
                deployment["build_stdout"] = (proc.stdout or "")[-4000:]
                deployment["build_stderr"] = (proc.stderr or "")[-4000:]
                build_dir = (frontend_dir / "dist").resolve()
            else:
                deployment["status"] = "failed"
                deployment["error"] = "frontend build missing; run npm install in project/frontend"
                deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                _save_deployments(request, deployments)
                return {"success": False, "data": deployment, "error": deployment["error"]}

        if target == "docker":
            if not _docker_available():
                deployment["status"] = "failed"
                deployment["error"] = "docker not installed or not on PATH"
                deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                _save_deployments(request, deployments)
                return {"success": False, "data": deployment, "error": deployment["error"]}

            if not build_dir.is_dir():
                deployment["status"] = "failed"
                deployment["error"] = "frontend dist missing; build frontend first"
                deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                _save_deployments(request, deployments)
                return {"success": False, "data": deployment, "error": deployment["error"]}

            docker_ctx = (deploy_dir / "docker").resolve()
            docker_ctx.mkdir(parents=True, exist_ok=True)
            host_port = int(body.get("port") or 8088)
            if host_port < 1 or host_port > 65535:
                host_port = 8088

            backend = _detect_fastapi_backend(project_dir)
            if backend:
                web_dir = docker_ctx / "web"
                backend_dir = docker_ctx / "backend"
                web_dir.mkdir(parents=True, exist_ok=True)
                backend_dir.mkdir(parents=True, exist_ok=True)

                dist_out = web_dir / "dist"
                if dist_out.exists():
                    shutil.rmtree(dist_out)
                shutil.copytree(build_dir, dist_out)

                src_backend = Path(str(backend["backend_dir"])).resolve()
                if backend_dir.exists():
                    for child in backend_dir.iterdir():
                        if child.is_dir():
                            shutil.rmtree(child)
                        else:
                            child.unlink(missing_ok=True)
                shutil.copytree(src_backend, backend_dir, dirs_exist_ok=True)

                _write_text(web_dir / "Dockerfile", _generate_web_with_proxy_dockerfile())
                _write_text(web_dir / "nginx.conf", _generate_proxy_nginx_conf())
                _write_dockerignore(docker_ctx / ".dockerignore")

                _write_text(backend_dir / "Dockerfile", _generate_backend_dockerfile(str(backend.get("module") or "main")))

                compose = "\n".join(
                    [
                        "services:",
                        "  backend:",
                        "    build: ./backend",
                        "    restart: unless-stopped",
                        "  web:",
                        "    build: ./web",
                        "    ports:",
                        f'      - "{host_port}:80"',
                        "    depends_on:",
                        "      - backend",
                        "    restart: unless-stopped",
                        "",
                    ]
                )
                _write_text(docker_ctx / "docker-compose.yml", compose)

                project_name = f"af_{project}_{version}".replace(".", "_").replace("-", "_")
                up_result = _docker_compose_up(docker_ctx, project_name=project_name)
                deployment["docker_compose"] = up_result
                deployment["docker_compose"]["project_name"] = project_name
                deployment["docker_compose"]["compose_dir"] = str(docker_ctx)
                deployment["docker_url"] = f"http://127.0.0.1:{host_port}/"
                if int(up_result.get("returncode", 1)) != 0:
                    deployment["status"] = "failed"
                    deployment["error"] = "docker compose up failed"
                    deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                    _save_deployments(request, deployments)
                    return {"success": False, "data": deployment, "error": deployment["error"]}

                deployment["status"] = "completed"
                deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                _save_deployments(request, deployments)
                _persist_deployment_json(deploy_dir, deployment)
                return {"success": True, "data": deployment, "error": None}

            dist_out = docker_ctx / "dist"
            if dist_out.exists():
                shutil.rmtree(dist_out)
            shutil.copytree(build_dir, dist_out)

            dockerfile_path = docker_ctx / "Dockerfile"
            dockerignore_path = docker_ctx / ".dockerignore"
            _write_text(dockerfile_path, _generate_static_web_dockerfile())
            _write_dockerignore(dockerignore_path)

            image_tag = f"agentforgeos/{project}:{version}"
            build_result = _docker_build(docker_ctx, image_tag)
            deployment["docker_image"] = image_tag
            deployment["docker_build"] = build_result
            if int(build_result.get("returncode", 1)) != 0:
                deployment["status"] = "failed"
                deployment["error"] = "docker build failed"
                deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                _save_deployments(request, deployments)
                return {"success": False, "data": deployment, "error": deployment["error"]}

            run_result = _docker_run(image_tag, host_port)
            deployment["docker_run"] = run_result
            deployment["docker_url"] = f"http://127.0.0.1:{host_port}/"
            if int(run_result.get("returncode", 1)) != 0:
                deployment["status"] = "failed"
                deployment["error"] = "docker run failed"
                deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                _save_deployments(request, deployments)
                return {"success": False, "data": deployment, "error": deployment["error"]}

            deployment["status"] = "completed"
            deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            _save_deployments(request, deployments)
            _persist_deployment_json(deploy_dir, deployment)
            return {"success": True, "data": deployment, "error": None}

        if target in {"k8s", "kubernetes"}:
            apply_flag = bool(body.get("apply"))
            if apply_flag:
                ok2, preflight2 = await require_preflight_ok(request, scope="deployment.apply.kubernetes")
                if not ok2:
                    deployment["status"] = "failed"
                    deployment["error"] = "Preflight failed"
                    deployment["preflight_apply"] = preflight2
                    deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                    _save_deployments(request, deployments)
                    _persist_deployment_json(deploy_dir, deployment)
                    return {"success": False, "data": deployment, "error": deployment["error"]}
            if not _docker_available():
                deployment["status"] = "failed"
                deployment["error"] = "docker not installed or not on PATH"
                deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                _save_deployments(request, deployments)
                return {"success": False, "data": deployment, "error": deployment["error"]}

            if not build_dir.is_dir():
                deployment["status"] = "failed"
                deployment["error"] = "frontend dist missing; build frontend first"
                deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                _save_deployments(request, deployments)
                return {"success": False, "data": deployment, "error": deployment["error"]}

            host_port = int(body.get("port") or 8088)
            if host_port < 1 or host_port > 65535:
                host_port = 8088

            backend = _detect_fastapi_backend(project_dir)
            k8s_ctx = (deploy_dir / "k8s_ctx").resolve()
            k8s_ctx.mkdir(parents=True, exist_ok=True)

            app_name = _safe_k8s_name(project)
            namespace = _safe_k8s_name(f"agentforgeos-{project}")
            host = str(body.get("host") or "").strip()
            ingress_class = str(body.get("ingress_class") or "").strip() or None
            use_tls = bool(body.get("use_tls"))
            tls_secret = str(body.get("tls_secret") or "").strip() or None
            cluster_issuer = str(body.get("cluster_issuer") or "").strip() or None
            create_secrets = bool(body.get("create_secrets"))
            secret_name = str(body.get("secret_name") or "").strip() or f"{app_name}-secrets"

            if backend:
                web_dir = k8s_ctx / "web"
                backend_dir = k8s_ctx / "backend"
                manifests_dir = k8s_ctx / "k8s"
                web_dir.mkdir(parents=True, exist_ok=True)
                backend_dir.mkdir(parents=True, exist_ok=True)
                manifests_dir.mkdir(parents=True, exist_ok=True)

                dist_out = web_dir / "dist"
                if dist_out.exists():
                    shutil.rmtree(dist_out)
                shutil.copytree(build_dir, dist_out)

                src_backend = Path(str(backend["backend_dir"])).resolve()
                shutil.copytree(src_backend, backend_dir, dirs_exist_ok=True)

                _write_text(web_dir / "Dockerfile", _generate_web_with_proxy_dockerfile())
                _write_text(web_dir / "nginx.conf", _generate_proxy_nginx_conf())
                _write_text(backend_dir / "Dockerfile", _generate_backend_dockerfile(str(backend.get("module") or "main")))
                _write_dockerignore(k8s_ctx / ".dockerignore")

                web_image = f"agentforgeos/{app_name}-web:{version}"
                api_image = f"agentforgeos/{app_name}-api:{version}"

                web_build = _docker_build(web_dir, web_image)
                api_build = _docker_build(backend_dir, api_image)
                deployment["k8s_images"] = {"web": web_image, "api": api_image}
                deployment["k8s_docker_builds"] = {"web": web_build, "api": api_build}
                if int(web_build.get("returncode", 1)) != 0 or int(api_build.get("returncode", 1)) != 0:
                    deployment["status"] = "failed"
                    deployment["error"] = "docker build failed"
                    deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                    _save_deployments(request, deployments)
                    return {"success": False, "data": deployment, "error": deployment["error"]}

                _write_text(
                    manifests_dir / "api-deployment.yaml",
                    "\n".join(
                        [
                            "apiVersion: apps/v1",
                            "kind: Deployment",
                            "metadata:",
                            f"  name: {app_name}-api",
                            "spec:",
                            "  replicas: 1",
                            "  selector:",
                            "    matchLabels:",
                            f"      app: {app_name}-api",
                            "  template:",
                            "    metadata:",
                            "      labels:",
                            f"        app: {app_name}-api",
                            "    spec:",
                            "      containers:",
                            "        - name: api",
                            f"          image: {api_image}",
                            "          ports:",
                            "            - containerPort: 8000",
                            "",
                        ]
                    ),
                )
                _write_text(
                    manifests_dir / "api-service.yaml",
                    "\n".join(
                        [
                            "apiVersion: v1",
                            "kind: Service",
                            "metadata:",
                            f"  name: {app_name}-api",
                            "spec:",
                            "  selector:",
                            f"    app: {app_name}-api",
                            "  ports:",
                            "    - name: http",
                            "      port: 8000",
                            "      targetPort: 8000",
                            "",
                        ]
                    ),
                )
                _write_text(
                    manifests_dir / "web-deployment.yaml",
                    "\n".join(
                        [
                            "apiVersion: apps/v1",
                            "kind: Deployment",
                            "metadata:",
                            f"  name: {app_name}-web",
                            "spec:",
                            "  replicas: 1",
                            "  selector:",
                            "    matchLabels:",
                            f"      app: {app_name}-web",
                            "  template:",
                            "    metadata:",
                            "      labels:",
                            f"        app: {app_name}-web",
                            "    spec:",
                            "      containers:",
                            "        - name: web",
                            f"          image: {web_image}",
                            "          ports:",
                            "            - containerPort: 80",
                            "",
                        ]
                    ),
                )
                _write_text(
                    manifests_dir / "web-service.yaml",
                    "\n".join(
                        [
                            "apiVersion: v1",
                            "kind: Service",
                            "metadata:",
                            f"  name: {app_name}-web",
                            "spec:",
                            "  type: ClusterIP",
                            "  selector:",
                            f"    app: {app_name}-web",
                            "  ports:",
                            "    - name: http",
                            "      port: 80",
                            "      targetPort: 80",
                            "",
                        ]
                    ),
                )

                apply_result = None
                secret_result = None
                if apply_flag and _kubectl_available() and create_secrets:
                    values = _collect_secret_values(request)
                    if values:
                        secret_result = _kubectl_create_secret(namespace=namespace, name=secret_name, values=values)
                if apply_flag and _kubectl_available():
                    apply_result = _kubectl_apply(manifests_dir, namespace=namespace)
                deployment["k8s_manifests_dir"] = str(manifests_dir)
                deployment["k8s_namespace"] = namespace
                deployment["k8s_apply"] = apply_result
                deployment["k8s_secret"] = secret_result
                deployment["k8s_access"] = {
                    "port_forward_web": f"kubectl -n {namespace} port-forward svc/{app_name}-web {host_port}:80",
                    "port_forward_api": f"kubectl -n {namespace} port-forward svc/{app_name}-api {host_port+1}:8000",
                }
                if host:
                    _write_text(
                        manifests_dir / "ingress.yaml",
                        _generate_ingress_yaml(
                            name=f"{app_name}-ingress",
                            namespace=namespace,
                            host=host,
                            ingress_class=ingress_class,
                            use_tls=use_tls,
                            tls_secret=tls_secret,
                            cluster_issuer=cluster_issuer,
                            web_service=f"{app_name}-web",
                            api_service=f"{app_name}-api",
                        ),
                    )
                deployment["status"] = "completed"
                deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                _save_deployments(request, deployments)
                _persist_deployment_json(deploy_dir, deployment)
                return {"success": True, "data": deployment, "error": None}

            web_dir = k8s_ctx / "web"
            manifests_dir = k8s_ctx / "k8s"
            web_dir.mkdir(parents=True, exist_ok=True)
            manifests_dir.mkdir(parents=True, exist_ok=True)

            dist_out = web_dir / "dist"
            if dist_out.exists():
                shutil.rmtree(dist_out)
            shutil.copytree(build_dir, dist_out)

            _write_text(web_dir / "Dockerfile", _generate_static_web_dockerfile())
            _write_dockerignore(k8s_ctx / ".dockerignore")

            web_image = f"agentforgeos/{app_name}-web:{version}"
            web_build = _docker_build(web_dir, web_image)
            deployment["k8s_images"] = {"web": web_image}
            deployment["k8s_docker_builds"] = {"web": web_build}
            if int(web_build.get("returncode", 1)) != 0:
                deployment["status"] = "failed"
                deployment["error"] = "docker build failed"
                deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                _save_deployments(request, deployments)
                return {"success": False, "data": deployment, "error": deployment["error"]}

            _write_text(
                manifests_dir / "web-deployment.yaml",
                "\n".join(
                    [
                        "apiVersion: apps/v1",
                        "kind: Deployment",
                        "metadata:",
                        f"  name: {app_name}-web",
                        "spec:",
                        "  replicas: 1",
                        "  selector:",
                        "    matchLabels:",
                        f"      app: {app_name}-web",
                        "  template:",
                        "    metadata:",
                        "      labels:",
                        f"        app: {app_name}-web",
                        "    spec:",
                        "      containers:",
                        "        - name: web",
                        f"          image: {web_image}",
                        "          ports:",
                        "            - containerPort: 80",
                        "",
                    ]
                ),
            )
            _write_text(
                manifests_dir / "web-service.yaml",
                "\n".join(
                    [
                        "apiVersion: v1",
                        "kind: Service",
                        "metadata:",
                        f"  name: {app_name}-web",
                        "spec:",
                        "  type: ClusterIP",
                        "  selector:",
                        f"    app: {app_name}-web",
                        "  ports:",
                        "    - name: http",
                        "      port: 80",
                        "      targetPort: 80",
                        "",
                    ]
                ),
            )

            apply_result = None
            secret_result = None
            if apply_flag and _kubectl_available() and create_secrets:
                values = _collect_secret_values(request)
                if values:
                    secret_result = _kubectl_create_secret(namespace=namespace, name=secret_name, values=values)
            if apply_flag and _kubectl_available():
                apply_result = _kubectl_apply(manifests_dir, namespace=namespace)
            deployment["k8s_manifests_dir"] = str(manifests_dir)
            deployment["k8s_namespace"] = namespace
            deployment["k8s_apply"] = apply_result
            deployment["k8s_secret"] = secret_result
            deployment["k8s_access"] = {"port_forward_web": f"kubectl -n {namespace} port-forward svc/{app_name}-web {host_port}:80"}
            if host:
                _write_text(
                    manifests_dir / "ingress.yaml",
                    _generate_ingress_yaml(
                        name=f"{app_name}-ingress",
                        namespace=namespace,
                        host=host,
                        ingress_class=ingress_class,
                        use_tls=use_tls,
                        tls_secret=tls_secret,
                        cluster_issuer=cluster_issuer,
                        web_service=f"{app_name}-web",
                        api_service=None,
                    ),
                )
            deployment["status"] = "completed"
            deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            _save_deployments(request, deployments)
            _persist_deployment_json(deploy_dir, deployment)
            return {"success": True, "data": deployment, "error": None}

        if target in {"aws", "eks"}:
            apply_flag = bool(body.get("apply"))
            if apply_flag:
                ok2, preflight2 = await require_preflight_ok(request, scope="deployment.apply.aws")
                if not ok2:
                    deployment["status"] = "failed"
                    deployment["error"] = "Preflight failed"
                    deployment["preflight_apply"] = preflight2
                    deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                    _save_deployments(request, deployments)
                    _persist_deployment_json(deploy_dir, deployment)
                    return {"success": False, "data": deployment, "error": deployment["error"]}
            if not _docker_available():
                deployment["status"] = "failed"
                deployment["error"] = "docker not installed or not on PATH"
                deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                _save_deployments(request, deployments)
                return {"success": False, "data": deployment, "error": deployment["error"]}
            if not _aws_available():
                deployment["status"] = "failed"
                deployment["error"] = "aws cli not installed or not on PATH"
                deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                _save_deployments(request, deployments)
                return {"success": False, "data": deployment, "error": deployment["error"]}
            if not build_dir.is_dir():
                deployment["status"] = "failed"
                deployment["error"] = "frontend dist missing; build frontend first"
                deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                _save_deployments(request, deployments)
                return {"success": False, "data": deployment, "error": deployment["error"]}

            region = str(body.get("region") or "us-east-1").strip() or "us-east-1"
            repo_prefix = _safe_k8s_name(str(body.get("repo") or "agentforgeos"))
            apply_flag = bool(body.get("apply"))

            host_port = int(body.get("port") or 8088)
            if host_port < 1 or host_port > 65535:
                host_port = 8088

            aws_ctx = (deploy_dir / "aws").resolve()
            aws_ctx.mkdir(parents=True, exist_ok=True)
            app_name = _safe_k8s_name(project)
            namespace = _safe_k8s_name(f"agentforgeos-{project}")

            account_id = _aws_account_id(region)
            if not account_id:
                deployment["status"] = "failed"
                deployment["error"] = "aws sts get-caller-identity failed"
                deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                _save_deployments(request, deployments)
                return {"success": False, "data": deployment, "error": deployment["error"]}
            registry = f"{account_id}.dkr.ecr.{region}.amazonaws.com"
            login = _aws_ecr_login(region, registry)
            if int(login.get("returncode", 1)) != 0:
                deployment["status"] = "failed"
                deployment["error"] = "aws ecr login failed"
                deployment["aws_login"] = login
                deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                _save_deployments(request, deployments)
                return {"success": False, "data": deployment, "error": deployment["error"]}

            backend = _detect_fastapi_backend(project_dir)
            manifests_dir = aws_ctx / "k8s"
            manifests_dir.mkdir(parents=True, exist_ok=True)

            images: dict[str, str] = {}
            pushes: dict[str, Any] = {}
            builds: dict[str, Any] = {}
            repos: dict[str, Any] = {}

            web_dir = aws_ctx / "web"
            web_dir.mkdir(parents=True, exist_ok=True)
            dist_out = web_dir / "dist"
            if dist_out.exists():
                shutil.rmtree(dist_out)
            shutil.copytree(build_dir, dist_out)

            if backend:
                _write_text(web_dir / "Dockerfile", _generate_web_with_proxy_dockerfile())
                _write_text(web_dir / "nginx.conf", _generate_proxy_nginx_conf())
            else:
                _write_text(web_dir / "Dockerfile", _generate_static_web_dockerfile())
            _write_dockerignore(aws_ctx / ".dockerignore")

            web_repo = f"{repo_prefix}/{app_name}-web"
            repos["web"] = _aws_ensure_ecr_repo(region, web_repo)
            local_web = f"agentforgeos/{app_name}-web:{version}"
            builds["web"] = _docker_build(web_dir, local_web)
            if int(builds["web"].get("returncode", 1)) != 0:
                deployment["status"] = "failed"
                deployment["error"] = "docker build failed"
                deployment["aws_repos"] = repos
                deployment["aws_docker_builds"] = builds
                deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                _save_deployments(request, deployments)
                return {"success": False, "data": deployment, "error": deployment["error"]}
            remote_web = f"{registry}/{web_repo}:{version}"
            pushes["web_tag"] = _docker_tag(local_web, remote_web)
            pushes["web_push"] = _docker_push(remote_web)
            if int(pushes["web_push"].get("returncode", 1)) != 0:
                deployment["status"] = "failed"
                deployment["error"] = "docker push failed"
                deployment["aws_push"] = pushes
                deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                _save_deployments(request, deployments)
                return {"success": False, "data": deployment, "error": deployment["error"]}
            images["web"] = remote_web

            if backend:
                backend_dir = aws_ctx / "backend"
                backend_dir.mkdir(parents=True, exist_ok=True)
                src_backend = Path(str(backend["backend_dir"])).resolve()
                shutil.copytree(src_backend, backend_dir, dirs_exist_ok=True)
                _write_text(backend_dir / "Dockerfile", _generate_backend_dockerfile(str(backend.get("module") or "main")))
                api_repo = f"{repo_prefix}/{app_name}-api"
                repos["api"] = _aws_ensure_ecr_repo(region, api_repo)
                local_api = f"agentforgeos/{app_name}-api:{version}"
                builds["api"] = _docker_build(backend_dir, local_api)
                if int(builds["api"].get("returncode", 1)) != 0:
                    deployment["status"] = "failed"
                    deployment["error"] = "docker build failed"
                    deployment["aws_repos"] = repos
                    deployment["aws_docker_builds"] = builds
                    deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                    _save_deployments(request, deployments)
                    return {"success": False, "data": deployment, "error": deployment["error"]}
                remote_api = f"{registry}/{api_repo}:{version}"
                pushes["api_tag"] = _docker_tag(local_api, remote_api)
                pushes["api_push"] = _docker_push(remote_api)
                if int(pushes["api_push"].get("returncode", 1)) != 0:
                    deployment["status"] = "failed"
                    deployment["error"] = "docker push failed"
                    deployment["aws_push"] = pushes
                    deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                    _save_deployments(request, deployments)
                    return {"success": False, "data": deployment, "error": deployment["error"]}
                images["api"] = remote_api

                _write_text(
                    manifests_dir / "api-deployment.yaml",
                    "\n".join(
                        [
                            "apiVersion: apps/v1",
                            "kind: Deployment",
                            "metadata:",
                            f"  name: {app_name}-api",
                            "spec:",
                            "  replicas: 1",
                            "  selector:",
                            "    matchLabels:",
                            f"      app: {app_name}-api",
                            "  template:",
                            "    metadata:",
                            "      labels:",
                            f"        app: {app_name}-api",
                            "    spec:",
                            "      containers:",
                            "        - name: api",
                            f"          image: {images['api']}",
                            "          ports:",
                            "            - containerPort: 8000",
                            "",
                        ]
                    ),
                )
                _write_text(
                    manifests_dir / "api-service.yaml",
                    "\n".join(
                        [
                            "apiVersion: v1",
                            "kind: Service",
                            "metadata:",
                            f"  name: {app_name}-api",
                            "spec:",
                            "  selector:",
                            f"    app: {app_name}-api",
                            "  ports:",
                            "    - name: http",
                            "      port: 8000",
                            "      targetPort: 8000",
                            "",
                        ]
                    ),
                )

            _write_text(
                manifests_dir / "web-deployment.yaml",
                "\n".join(
                    [
                        "apiVersion: apps/v1",
                        "kind: Deployment",
                        "metadata:",
                        f"  name: {app_name}-web",
                        "spec:",
                        "  replicas: 1",
                        "  selector:",
                        "    matchLabels:",
                        f"      app: {app_name}-web",
                        "  template:",
                        "    metadata:",
                        "      labels:",
                        f"        app: {app_name}-web",
                        "    spec:",
                        "      containers:",
                        "        - name: web",
                        f"          image: {images['web']}",
                        "          ports:",
                        "            - containerPort: 80",
                        "",
                    ]
                ),
            )
            _write_text(
                manifests_dir / "web-service.yaml",
                "\n".join(
                    [
                        "apiVersion: v1",
                        "kind: Service",
                        "metadata:",
                        f"  name: {app_name}-web",
                        "spec:",
                        "  type: ClusterIP",
                        "  selector:",
                        f"    app: {app_name}-web",
                        "  ports:",
                        "    - name: http",
                        "      port: 80",
                        "      targetPort: 80",
                        "",
                    ]
                ),
            )
            apply_result = None
            host = str(body.get("host") or "").strip()
            ingress_class = str(body.get("ingress_class") or "").strip() or None
            use_tls = bool(body.get("use_tls"))
            tls_secret = str(body.get("tls_secret") or "").strip() or None
            cluster_issuer = str(body.get("cluster_issuer") or "").strip() or None
            create_secrets = bool(body.get("create_secrets"))
            secret_name = str(body.get("secret_name") or "").strip() or f"{app_name}-secrets"
            secret_result = None
            if apply_flag and _kubectl_available() and create_secrets:
                values = _collect_secret_values(request)
                if values:
                    secret_result = _kubectl_create_secret(namespace=namespace, name=secret_name, values=values)
            if apply_flag and _kubectl_available():
                apply_result = _kubectl_apply(manifests_dir, namespace=namespace)
            deployment["aws"] = {"region": region, "account_id": account_id, "registry": registry}
            deployment["aws_images"] = images
            deployment["aws_repos"] = repos
            deployment["aws_push"] = pushes
            deployment["aws_docker_builds"] = builds
            deployment["k8s_manifests_dir"] = str(manifests_dir)
            deployment["k8s_namespace"] = namespace
            deployment["k8s_apply"] = apply_result
            deployment["k8s_secret"] = secret_result
            deployment["k8s_access"] = {"port_forward_web": f"kubectl -n {namespace} port-forward svc/{app_name}-web {host_port}:80"}
            if "api" in images:
                deployment["k8s_access"]["port_forward_api"] = f"kubectl -n {namespace} port-forward svc/{app_name}-api {host_port+1}:8000"
            if host:
                _write_text(
                    manifests_dir / "ingress.yaml",
                    _generate_ingress_yaml(
                        name=f"{app_name}-ingress",
                        namespace=namespace,
                        host=host,
                        ingress_class=ingress_class,
                        use_tls=use_tls,
                        tls_secret=tls_secret,
                        cluster_issuer=cluster_issuer,
                        web_service=f"{app_name}-web",
                        api_service=f"{app_name}-api" if "api" in images else None,
                    ),
                )
            deployment["status"] = "completed"
            deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            _save_deployments(request, deployments)
            _persist_deployment_json(deploy_dir, deployment)
            return {"success": True, "data": deployment, "error": None}

        if target in {"gcp", "gke"}:
            apply_flag = bool(body.get("apply"))
            if apply_flag:
                ok2, preflight2 = await require_preflight_ok(request, scope="deployment.apply.gcp")
                if not ok2:
                    deployment["status"] = "failed"
                    deployment["error"] = "Preflight failed"
                    deployment["preflight_apply"] = preflight2
                    deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                    _save_deployments(request, deployments)
                    _persist_deployment_json(deploy_dir, deployment)
                    return {"success": False, "data": deployment, "error": deployment["error"]}
            if not _docker_available():
                deployment["status"] = "failed"
                deployment["error"] = "docker not installed or not on PATH"
                deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                _save_deployments(request, deployments)
                return {"success": False, "data": deployment, "error": deployment["error"]}
            if not _gcloud_available():
                deployment["status"] = "failed"
                deployment["error"] = "gcloud not installed or not on PATH"
                deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                _save_deployments(request, deployments)
                return {"success": False, "data": deployment, "error": deployment["error"]}
            if not build_dir.is_dir():
                deployment["status"] = "failed"
                deployment["error"] = "frontend dist missing; build frontend first"
                deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                _save_deployments(request, deployments)
                return {"success": False, "data": deployment, "error": deployment["error"]}

            gcp_project = str(body.get("gcp_project") or "").strip()
            if not gcp_project:
                deployment["status"] = "failed"
                deployment["error"] = "gcp_project is required"
                deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                _save_deployments(request, deployments)
                return {"success": False, "data": deployment, "error": deployment["error"]}
            region = str(body.get("region") or "us-central1").strip() or "us-central1"
            repo_name = _safe_k8s_name(str(body.get("repo") or "agentforgeos"))
            apply_flag = bool(body.get("apply"))

            host_port = int(body.get("port") or 8088)
            if host_port < 1 or host_port > 65535:
                host_port = 8088

            gcp_ctx = (deploy_dir / "gcp").resolve()
            gcp_ctx.mkdir(parents=True, exist_ok=True)
            app_name = _safe_k8s_name(project)
            namespace = _safe_k8s_name(f"agentforgeos-{project}")
            host = f"{region}-docker.pkg.dev"

            cfg = _gcloud_configure_docker(host)
            if int(cfg.get("returncode", 1)) != 0:
                deployment["status"] = "failed"
                deployment["error"] = "gcloud configure-docker failed"
                deployment["gcp_docker_auth"] = cfg
                deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                _save_deployments(request, deployments)
                return {"success": False, "data": deployment, "error": deployment["error"]}

            backend = _detect_fastapi_backend(project_dir)
            manifests_dir = gcp_ctx / "k8s"
            manifests_dir.mkdir(parents=True, exist_ok=True)

            images: dict[str, str] = {}
            pushes: dict[str, Any] = {}
            builds: dict[str, Any] = {}

            web_dir = gcp_ctx / "web"
            web_dir.mkdir(parents=True, exist_ok=True)
            dist_out = web_dir / "dist"
            if dist_out.exists():
                shutil.rmtree(dist_out)
            shutil.copytree(build_dir, dist_out)
            if backend:
                _write_text(web_dir / "Dockerfile", _generate_web_with_proxy_dockerfile())
                _write_text(web_dir / "nginx.conf", _generate_proxy_nginx_conf())
            else:
                _write_text(web_dir / "Dockerfile", _generate_static_web_dockerfile())
            _write_dockerignore(gcp_ctx / ".dockerignore")

            local_web = f"agentforgeos/{app_name}-web:{version}"
            builds["web"] = _docker_build(web_dir, local_web)
            if int(builds["web"].get("returncode", 1)) != 0:
                deployment["status"] = "failed"
                deployment["error"] = "docker build failed"
                deployment["gcp_docker_builds"] = builds
                deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                _save_deployments(request, deployments)
                return {"success": False, "data": deployment, "error": deployment["error"]}
            remote_web = f"{host}/{gcp_project}/{repo_name}/{app_name}-web:{version}"
            pushes["web_tag"] = _docker_tag(local_web, remote_web)
            pushes["web_push"] = _docker_push(remote_web)
            if int(pushes["web_push"].get("returncode", 1)) != 0:
                deployment["status"] = "failed"
                deployment["error"] = "docker push failed"
                deployment["gcp_push"] = pushes
                deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                _save_deployments(request, deployments)
                return {"success": False, "data": deployment, "error": deployment["error"]}
            images["web"] = remote_web

            if backend:
                backend_dir = gcp_ctx / "backend"
                backend_dir.mkdir(parents=True, exist_ok=True)
                src_backend = Path(str(backend["backend_dir"])).resolve()
                shutil.copytree(src_backend, backend_dir, dirs_exist_ok=True)
                _write_text(backend_dir / "Dockerfile", _generate_backend_dockerfile(str(backend.get("module") or "main")))
                local_api = f"agentforgeos/{app_name}-api:{version}"
                builds["api"] = _docker_build(backend_dir, local_api)
                if int(builds["api"].get("returncode", 1)) != 0:
                    deployment["status"] = "failed"
                    deployment["error"] = "docker build failed"
                    deployment["gcp_docker_builds"] = builds
                    deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                    _save_deployments(request, deployments)
                    return {"success": False, "data": deployment, "error": deployment["error"]}
                remote_api = f"{host}/{gcp_project}/{repo_name}/{app_name}-api:{version}"
                pushes["api_tag"] = _docker_tag(local_api, remote_api)
                pushes["api_push"] = _docker_push(remote_api)
                if int(pushes["api_push"].get("returncode", 1)) != 0:
                    deployment["status"] = "failed"
                    deployment["error"] = "docker push failed"
                    deployment["gcp_push"] = pushes
                    deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                    _save_deployments(request, deployments)
                    return {"success": False, "data": deployment, "error": deployment["error"]}
                images["api"] = remote_api

                _write_text(
                    manifests_dir / "api-deployment.yaml",
                    "\n".join(
                        [
                            "apiVersion: apps/v1",
                            "kind: Deployment",
                            "metadata:",
                            f"  name: {app_name}-api",
                            "spec:",
                            "  replicas: 1",
                            "  selector:",
                            "    matchLabels:",
                            f"      app: {app_name}-api",
                            "  template:",
                            "    metadata:",
                            "      labels:",
                            f"        app: {app_name}-api",
                            "    spec:",
                            "      containers:",
                            "        - name: api",
                            f"          image: {images['api']}",
                            "          ports:",
                            "            - containerPort: 8000",
                            "",
                        ]
                    ),
                )
                _write_text(
                    manifests_dir / "api-service.yaml",
                    "\n".join(
                        [
                            "apiVersion: v1",
                            "kind: Service",
                            "metadata:",
                            f"  name: {app_name}-api",
                            "spec:",
                            "  selector:",
                            f"    app: {app_name}-api",
                            "  ports:",
                            "    - name: http",
                            "      port: 8000",
                            "      targetPort: 8000",
                            "",
                        ]
                    ),
                )

            _write_text(
                manifests_dir / "web-deployment.yaml",
                "\n".join(
                    [
                        "apiVersion: apps/v1",
                        "kind: Deployment",
                        "metadata:",
                        f"  name: {app_name}-web",
                        "spec:",
                        "  replicas: 1",
                        "  selector:",
                        "    matchLabels:",
                        f"      app: {app_name}-web",
                        "  template:",
                        "    metadata:",
                        "      labels:",
                        f"        app: {app_name}-web",
                        "    spec:",
                        "      containers:",
                        "        - name: web",
                        f"          image: {images['web']}",
                        "          ports:",
                        "            - containerPort: 80",
                        "",
                    ]
                ),
            )
            _write_text(
                manifests_dir / "web-service.yaml",
                "\n".join(
                    [
                        "apiVersion: v1",
                        "kind: Service",
                        "metadata:",
                        f"  name: {app_name}-web",
                        "spec:",
                        "  type: ClusterIP",
                        "  selector:",
                        f"    app: {app_name}-web",
                        "  ports:",
                        "    - name: http",
                        "      port: 80",
                        "      targetPort: 80",
                        "",
                    ]
                ),
            )
            apply_result = None
            host = str(body.get("host") or "").strip()
            ingress_class = str(body.get("ingress_class") or "").strip() or None
            use_tls = bool(body.get("use_tls"))
            tls_secret = str(body.get("tls_secret") or "").strip() or None
            cluster_issuer = str(body.get("cluster_issuer") or "").strip() or None
            create_secrets = bool(body.get("create_secrets"))
            secret_name = str(body.get("secret_name") or "").strip() or f"{app_name}-secrets"
            secret_result = None
            if apply_flag and _kubectl_available() and create_secrets:
                values = _collect_secret_values(request)
                if values:
                    secret_result = _kubectl_create_secret(namespace=namespace, name=secret_name, values=values)
            if apply_flag and _kubectl_available():
                apply_result = _kubectl_apply(manifests_dir, namespace=namespace)
            deployment["gcp"] = {"project": gcp_project, "region": region, "repo": repo_name, "host": host}
            deployment["gcp_images"] = images
            deployment["gcp_push"] = pushes
            deployment["gcp_docker_builds"] = builds
            deployment["k8s_manifests_dir"] = str(manifests_dir)
            deployment["k8s_namespace"] = namespace
            deployment["k8s_apply"] = apply_result
            deployment["k8s_secret"] = secret_result
            deployment["k8s_access"] = {"port_forward_web": f"kubectl -n {namespace} port-forward svc/{app_name}-web {host_port}:80"}
            if "api" in images:
                deployment["k8s_access"]["port_forward_api"] = f"kubectl -n {namespace} port-forward svc/{app_name}-api {host_port+1}:8000"
            if host:
                _write_text(
                    manifests_dir / "ingress.yaml",
                    _generate_ingress_yaml(
                        name=f"{app_name}-ingress",
                        namespace=namespace,
                        host=host,
                        ingress_class=ingress_class,
                        use_tls=use_tls,
                        tls_secret=tls_secret,
                        cluster_issuer=cluster_issuer,
                        web_service=f"{app_name}-web",
                        api_service=f"{app_name}-api" if "api" in images else None,
                    ),
                )
            deployment["status"] = "completed"
            deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            _save_deployments(request, deployments)
            _persist_deployment_json(deploy_dir, deployment)
            return {"success": True, "data": deployment, "error": None}

        source_root = build_dir if build_dir.is_dir() else project_dir
        with zipfile.ZipFile(str(artifact_path), mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for p in source_root.rglob("*"):
                if not p.is_file():
                    continue
                rel = str(p.relative_to(source_root))
                if _should_skip(rel):
                    continue
                arcname = rel if source_root == project_dir else f"dist/{rel}"
                zf.write(str(p), arcname=arcname)

        deployment["status"] = "completed"
        deployment["artifact_path"] = str(artifact_path)
        deployment["artifact_bytes"] = artifact_path.stat().st_size if artifact_path.exists() else 0
        deployment["source_root"] = str(source_root)
        deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _save_deployments(request, deployments)
        _persist_deployment_json(deploy_dir, deployment)
        return {"success": True, "data": deployment, "error": None}
    except Exception as exc:
        deployment["status"] = "failed"
        deployment["error"] = str(exc)
        deployment["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _save_deployments(request, deployments)
        _persist_deployment_json(deploy_dir, deployment)
        return {"success": False, "data": deployment, "error": deployment["error"]}


@router.post("/destroy")
async def destroy_deployment(request: Request, body: Dict[str, Any] = {}):
    ok, preflight = await require_preflight_ok(request, scope="deployment.destroy")
    if not ok:
        return {"success": False, "data": {"preflight": preflight}, "error": "Preflight failed"}

    deployments = _load_deployments(request)
    target_id = body.get("id")
    target_uid = str(body.get("uid") or "").strip()
    match: Dict[str, Any] | None = None
    for d in deployments:
        if target_uid and str(d.get("uid") or "") == target_uid:
            match = d
            break
        if target_id is not None and str(d.get("id")) == str(target_id):
            match = d
            break
    if not match:
        return {"success": False, "data": None, "error": "deployment not found"}

    results: dict[str, Any] = {}
    if isinstance(match.get("docker_run"), dict):
        cid = str(match["docker_run"].get("container_id") or "").strip()
        if cid:
            proc = subprocess.run(["docker", "rm", "-f", cid], capture_output=True, text=True, timeout=120)
            results["docker_rm"] = {"returncode": proc.returncode, "stdout": (proc.stdout or "")[-2000:], "stderr": (proc.stderr or "")[-2000:]}
    if isinstance(match.get("docker_compose"), dict):
        comp = match["docker_compose"]
        compose_dir = str(comp.get("compose_dir") or "").strip()
        project_name = str(comp.get("project_name") or "").strip()
        if compose_dir and project_name:
            argv = _compose_argv() + ["-p", project_name, "down", "--remove-orphans"]
            proc = subprocess.run(argv, cwd=compose_dir, capture_output=True, text=True, timeout=600)
            results["docker_compose_down"] = {"returncode": proc.returncode, "stdout": (proc.stdout or "")[-4000:], "stderr": (proc.stderr or "")[-4000:]}

    ns = str(match.get("k8s_namespace") or "").strip()
    manifests_dir = str(match.get("k8s_manifests_dir") or "").strip()
    if ns and manifests_dir and Path(manifests_dir).is_dir():
        proc = subprocess.run(["kubectl", "delete", "-n", ns, "-f", manifests_dir, "--ignore-not-found"], capture_output=True, text=True, timeout=180)
        results["kubectl_delete"] = {"returncode": proc.returncode, "stdout": (proc.stdout or "")[-8000:], "stderr": (proc.stderr or "")[-8000:]}
        if bool(body.get("delete_namespace")):
            proc2 = subprocess.run(["kubectl", "delete", "namespace", ns, "--ignore-not-found"], capture_output=True, text=True, timeout=180)
            results["kubectl_delete_namespace"] = {"returncode": proc2.returncode, "stdout": (proc2.stdout or "")[-4000:], "stderr": (proc2.stderr or "")[-4000:]}

    match["destroyed_at"] = __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()
    match["destroy_result"] = results
    match["status"] = "destroyed"
    _save_deployments(request, deployments)
    deploy_dir = Path(str(match.get("deploy_dir") or "")).resolve()
    if deploy_dir.is_dir():
        _persist_deployment_json(deploy_dir, match)
    return {"success": True, "data": match, "error": None}


@router.post("/launch")
async def launch_engine(body: Dict[str, Any] = {}):
    import datetime
    import uuid

    engine_value = body.get("engine", "web")
    engine = engine_value if isinstance(engine_value, str) and engine_value else "web"
    launch: Dict[str, Any] = {
        "id": f"launch_{uuid.uuid4().hex[:12]}",
        "engine": engine,
        "project": body.get("project", ""),
        "status": "queued",
        "requested_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    return {"success": True, "data": launch, "error": None}
