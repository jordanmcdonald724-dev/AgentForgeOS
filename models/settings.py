from __future__ import annotations

from dataclasses import dataclass, field
import os


@dataclass
class SystemSettings:
    # AI Model Settings
    fal_api_key: str = ""
    openai_api_key: str = ""
    default_model_provider: str = "fal"
    model_temperature: float = 0.7
    max_tokens: int = 4096

    # Database Settings
    mongo_url: str = field(
        default_factory=lambda: os.getenv(
            "MONGO_URL",
            "mongodb+srv://jordanmcdonald724_db_user:<db_password>@agentforge.mvysvrz.mongodb.net/?appName=AgentForge",
        )
    )
    db_name: str = field(default_factory=lambda: os.getenv("MONGO_DB_NAME", "agentforge_v2"))
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""
    qdrant_host: str = "localhost"
    qdrant_port: str = "6333"

    # Game Engine Settings
    unity_editor_path: str = "C:/Program Files/Unity/Editor/Unity.exe"
    unreal_editor_path: str = "C:/Program Files/Epic Games/UE_5.3/Engine/Binaries/Win64/UnrealEditor.exe"
    default_game_engine: str = "unity"

    # Sandbox Settings
    docker_enabled: bool = True
    sandbox_image: str = "agentforge/build-sandbox:latest"
    memory_limit: str = "2g"
    cpu_limit: str = "1.0"
    timeout: int = 300

    # System Settings
    log_level: str = "INFO"
    max_concurrent_tasks: int = 5
    enable_realtime_updates: bool = True
    enable_telemetry: bool = False

    # Bridge / Simulation Settings
    local_project_root: str = "C:/AgentForgeProjects"
    local_bridge_port: int = 3250
    auto_launch_editor: bool = False
    enable_simulation_mode: bool = True

