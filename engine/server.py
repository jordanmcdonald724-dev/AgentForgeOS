import logging
import os
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Iterable, Optional

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from engine.config import get_settings
from engine.database import db
from engine.module_loader import load_modules, collect_module_routers
from engine.worker_system import worker_system
from engine.routes import (
    modules_router,
    agent_router,
    setup_router,
    bridge_router,
    v2_orchestration_router,
    v2_infrastructure_router,
    v2_research_router,
)
from engine.websocket_routes import websocket_router, cleanup_websocket_connections
from engine.routes.pipeline import router as pipeline_router
from engine.ws import execution_ws
from control.module_registry import module_registry

logger = logging.getLogger(__name__)
DEFAULT_CORS_ORIGINS = (
    "http://localhost:5173",
    "http://127.0.0.1:5173",
)


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


FRONTEND_ROOT = Path(__file__).resolve().parent.parent / "frontend"


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=engine_lifespan)
    cors_origins = [
        origin.strip()
        for origin in (os.getenv("CORS_ORIGINS") or ",".join(DEFAULT_CORS_ORIGINS)).split(",")
        if origin.strip()
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
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
            websocket_router,  # Add WebSocket router
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

    # Mount the Emergent UI static files
    app.mount("/emergent-ui", StaticFiles(directory="d:/AgentForgeOS/frontend"), name="emergent-ui")

    # Add route to serve the Emergent UI wizard.html file
    @app.get("/emergent-ui", include_in_schema=False)
    def serve_emergent_ui():
        emergent_ui_path = FRONTEND_ROOT / "wizard.html"
        if emergent_ui_path.is_file():
            return FileResponse(str(emergent_ui_path), media_type="text/html")
        return {"detail": "File not found"}

    return app


if __name__ == "__main__":
    import uvicorn
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
