from .modules import router as modules_router
from .agent import router as agent_router
from .setup import router as setup_router

from bridge.routes import router as bridge_router

__all__ = ["modules_router", "agent_router", "setup_router", "bridge_router"]
