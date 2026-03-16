import logging
from contextlib import asynccontextmanager
from typing import Iterable, Optional

from fastapi import APIRouter, FastAPI

from .config import get_settings
from .database import db
from .module_loader import load_modules
from .worker_system import worker_system
from control.module_registry import module_registry

logger = logging.getLogger(__name__)


def _health_router() -> APIRouter:
    router = APIRouter()

    @router.get("/health", tags=["system"])
    async def health_check():
        """Basic health endpoint used by the desktop runtime and monitors."""
        return {"success": True, "data": {"status": "ok"}, "error": None}

    return router


def _modules_router() -> APIRouter:
    router = APIRouter()

    @router.get("/modules", tags=["modules"])
    async def list_modules():
        """Expose active module manifests for the Studio UI."""
        return {"success": True, "data": module_registry.list_manifests(), "error": None}

    return router


@asynccontextmanager
async def engine_lifespan(app: FastAPI):
    logger.info("Starting AgentForgeOS engine")
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
    load_modules(registry=module_registry)
    register_routers(app, [_health_router(), _modules_router()], prefix="/api")
    return app
