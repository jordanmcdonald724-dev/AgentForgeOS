import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Iterable, Optional

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .database import db
from .module_loader import load_modules, collect_module_routers
from .worker_system import worker_system
from .routes import (
    modules_router,
    agent_router,
    setup_router,
    bridge_router,
    v2_orchestration_router,
    v2_infrastructure_router,
    v2_research_router,
)
from engine.routes.pipeline import router as pipeline_router
from control.module_registry import module_registry
from engine.ws import execution_ws

logger = logging.getLogger(__name__)


def _health_router() -> APIRouter:
    router = APIRouter()

    @router.get("/health", tags=["system"])
    async def health_check():
        """Basic health endpoint used by the desktop runtime and monitors."""
        return {"success": True, "data": {"status": "ok"}, "error": None}

    return router


@asynccontextmanager
async def engine_lifespan(app: FastAPI):
    logger.info("Starting AgentForgeOS engine")
    load_modules(registry=module_registry)
    await db.connect()
    await worker_system.start()
    try:
        yield
    finally:
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


FRONTEND_ROOT = Path(__file__).resolve().parent.parent / "frontend"


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=engine_lifespan)

    # CORS — allow the Vite dev server (port 5173) and Tauri shell to reach the
    # engine API without browser pre-flight failures.  In production the
    # frontend is served from the same origin so this is a no-op.
    # CORS_ORIGINS: comma-separated list of allowed origins,
    # e.g. "http://localhost:5173,https://my-app.example.com"
    _cors_origins = os.environ.get(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in _cors_origins],
        allow_origin_regex=r"tauri://.*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Core engine routes
    register_routers(
        app,
        [
            _health_router(),
            modules_router,
            agent_router,
            setup_router,
            bridge_router,
            pipeline_router,
            v2_orchestration_router,
            v2_infrastructure_router,
            v2_research_router,
        ],
        prefix="/api",
    )

    # Real-time event stream (WebSocket)
    app.add_api_websocket_route("/ws", execution_ws)

    # Module-specific backend routes (discovered from apps/*/backend/routes.py)
    module_routers = collect_module_routers()
    for mod_router in module_routers:
        app.include_router(mod_router, prefix="/api/modules")

    # Explicit setup wizard route so it remains available even when the
    # Studio frontend is served from a built ``frontend/dist`` directory
    # that does not contain ``wizard.html``.
    @app.get("/wizard.html", include_in_schema=False)
    async def wizard_page():
        wizard_path = FRONTEND_ROOT / "wizard.html"
        if wizard_path.is_file():
            return FileResponse(str(wizard_path), media_type="text/html")
        # Fallback: redirect to the Studio root if the wizard file is missing.
        return RedirectResponse("/")

    # Optional convenience redirect from /wizard → /wizard.html
    @app.get("/wizard", include_in_schema=False)
    async def wizard_redirect():
        return RedirectResponse("/wizard.html")

    # Serve the frontend (wizard, Studio, CSS, etc.) as static files.
    # Prefer built assets in frontend/dist when present; otherwise fall back to
    # the frontend/ directory for dev/scaffold mode.
    #
    # Mounted last so /api routes take priority.
    frontend_root = FRONTEND_ROOT
    dist_dir = frontend_root / "dist"
    serve_dir = dist_dir if dist_dir.is_dir() and (dist_dir / "index.html").exists() else frontend_root
    if serve_dir.is_dir():
        app.mount("/", StaticFiles(directory=str(serve_dir), html=True), name="frontend")

    return app
