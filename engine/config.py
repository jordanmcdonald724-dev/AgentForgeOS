import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

MIN_QUOTED_VALUE_LENGTH = 3


def _load_env_file(env_path: Optional[Path] = None) -> None:
    """
    Lightweight .env loader to keep the engine dependency-free beyond FastAPI.
    Values already present in the environment are not overwritten.
    """
    path = env_path or Path(__file__).resolve().parent.parent / "config" / ".env"
    if not path.exists():
        return

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = (part.strip() for part in stripped.split("=", 1))
        if not key:
            continue
        if (
            value
            and len(value) >= MIN_QUOTED_VALUE_LENGTH
            and value[0] == value[-1]
            and value[0] in {"'", '"'}
        ):
            inner = value[1:-1]
            if inner:
                value = inner
            else:
                continue
        if not value:
            continue
        if key not in os.environ:
            os.environ[key] = value


@dataclass
class Settings:
    app_name: str = "AgentForgeOS Engine"
    environment: str = os.getenv("AGENTFORGE_ENV", "development")
    host: str = os.getenv("AGENTFORGE_HOST", "127.0.0.1")
    port: int = int(os.getenv("AGENTFORGE_PORT", "8000"))
    mongo_uri: str = os.getenv("AGENTFORGE_MONGO_URI", "mongodb://localhost:27017")
    mongo_db: str = os.getenv("AGENTFORGE_MONGO_DB", "agentforge")


def get_settings(env_path: Optional[Path] = None) -> Settings:
    """
    Load configuration values from the environment (and optional .env file) and
    return a Settings instance. This keeps engine configuration centralized and
    easy to extend in future phases.
    """
    _load_env_file(env_path)
    return Settings()
