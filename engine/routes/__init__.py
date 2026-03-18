from .modules import router as modules_router
from .agent import router as agent_router
from .setup import router as setup_router
from .v2_orchestration import router as v2_orchestration_router
from .v2_infrastructure import router as v2_infrastructure_router
from .v2_research import router as v2_research_router

from bridge.routes import router as bridge_router

__all__ = [
	"modules_router",
	"agent_router",
	"setup_router",
	"bridge_router",
	"v2_orchestration_router",
	"v2_infrastructure_router",
	"v2_research_router",
]
