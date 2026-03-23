import logging
from typing import Any, Optional, TYPE_CHECKING

from .config import get_settings

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from motor.motor_asyncio import AsyncIOMotorClient as MotorClient
else:
    MotorClient = Any

try:
    from motor.motor_asyncio import AsyncIOMotorClient as RuntimeMotorClient  # type: ignore
except ImportError as exc:  # pragma: no cover - dependency may be installed later
    logger.warning("motor is unavailable: %s", exc)
    RuntimeMotorClient = None  # type: ignore


class Database:
    """
    Simple MongoDB wrapper that defers connection until startup.
    The engine remains operational even if MongoDB or motor are unavailable.
    """

    def __init__(self) -> None:
        self.client: Optional[MotorClient] = None
        self.database: Optional[Any] = None

    async def connect(self) -> None:
        settings = get_settings()
        if RuntimeMotorClient is None:
            logger.warning("motor client unavailable; skipping MongoDB connection")
            return

        logger.info("Connecting to MongoDB at %s", settings.mongo_uri)
        self.client = RuntimeMotorClient(settings.mongo_uri)
        self.database = self.client[settings.mongo_db]

    async def disconnect(self) -> None:
        if self.client:
            logger.info("Closing MongoDB connection")
            self.client.close()
            self.client = None
            self.database = None


db = Database()
