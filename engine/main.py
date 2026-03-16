import logging

from engine.config import get_settings
from engine.server import create_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

app = create_app()


def run() -> None:
    try:
        import uvicorn
    except ImportError:  # pragma: no cover - runtime dependency
        raise SystemExit(
            "uvicorn is required to run the server. "
            "Install it with `pip install uvicorn[standard]`."
        )

    settings = get_settings()
    uvicorn.run(
        "engine.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
    )


if __name__ == "__main__":
    run()
