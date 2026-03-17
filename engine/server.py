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

    # Module-specific backend routes (discovered from apps/*/backend/routes.py)
    module_routers = collect_module_routers()
    for mod_router in module_routers:
        app.include_router(mod_router, prefix="/api/modules")

    # Serve the frontend (wizard, Studio, CSS, etc.) as static files.
    # Mounted last so /api routes take priority.  ``html=True`` makes "/"
    # serve ``index.html`` and "/wizard.html" resolve correctly.
    frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
    if frontend_dir.is_dir():
        app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")

    return app
