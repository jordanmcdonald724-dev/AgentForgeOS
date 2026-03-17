import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Iterable, Optional

from fastapi import APIRouter, FastAPI
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .database import db
from .module_loader import load_modules, collect_module_routers
from .worker_system import worker_system
from .routes import modules_router, agent_router, setup_router, bridge_router
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


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=engine_lifespan)

    # Core engine routes
    register_routers(
        app, [_health_router(), modules_router, agent_router, setup_router, bridge_router, pipeline_router], prefix="/api"
    )

    # Real-time event stream (WebSocket)
    app.add_api_websocket_route("/ws", execution_ws)

    # Module-specific backend routes (discovered from apps/*/backend/routes.py)
    module_routers = collect_module_routers()
    for mod_router in module_routers:
        app.include_router(mod_router, prefix="/api/modules")

    # Serve the frontend (wizard, Studio, CSS, etc.) as static files.
    # Prefer built assets in frontend/dist when present; otherwise fall back to
    # the frontend/ directory for dev/scaffold mode.
    #
    # Mounted last so /api routes take priority. ``html=True`` makes "/"
    # serve ``index.html`` and "/wizard.html" resolve correctly.
    frontend_root = Path(__file__).resolve().parent.parent / "frontend"
    dist_dir = frontend_root / "dist"
    serve_dir = dist_dir if dist_dir.is_dir() and (dist_dir / "index.html").exists() else frontend_root
    if serve_dir.is_dir():
        app.mount("/", StaticFiles(directory=str(serve_dir), html=True), name="frontend")

    return app
