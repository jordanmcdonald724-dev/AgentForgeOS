import logging
import importlib
import os
import sys

from engine.config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

def _require(module_name: str) -> None:
    try:
        importlib.import_module(module_name)
    except Exception:
        raise SystemExit(
            "\n".join(
                [
                    f"Missing dependency: {module_name}",
                    f"Python executable: {sys.executable}",
                    "Fix (recommended): python -m pip install -r requirements.txt",
                    "If you intended to use the repo venv: .\\env311\\Scripts\\python.exe -m engine.main",
                ]
            )
        )


def run() -> None:
    if sys.version_info < (3, 11) or sys.version_info >= (3, 14):
        raise SystemExit(
            "\n".join(
                [
                    f"Unsupported Python version: {sys.version.split()[0]}",
                    "AgentForgeOS requires Python 3.11.x (or 3.12/3.13) because compiled dependencies",
                    "(e.g. pydantic-core, aiohttp) may not provide wheels for Python 3.14 yet.",
                    "Fix (recommended): use the repo venv: .\\env311\\Scripts\\python.exe -m engine.main",
                ]
            )
        )

    settings = get_settings()
    frozen = getattr(sys, "frozen", False)

    if frozen:
        if sys.stdout is None:
            sys.stdout = open(os.devnull, "w", encoding="utf-8")
        if sys.stderr is None:
            sys.stderr = open(os.devnull, "w", encoding="utf-8")

    if not frozen:
        for name in ("fastapi", "pydantic", "pydantic_settings", "uvicorn", "aiohttp", "motor"):
            _require(name)

    import uvicorn

    if settings.environment == "development" and not frozen:
        uvicorn.run(
            "engine.server:create_app",
            host=settings.host,
            port=settings.port,
            reload=True,
            factory=True,
        )
        return

    from engine.server import create_app

    app = create_app()
    uvicorn.run(app, host=settings.host, port=settings.port, reload=False)


if __name__ == "__main__":
    run()
