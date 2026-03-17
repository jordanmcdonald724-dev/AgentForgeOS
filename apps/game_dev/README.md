# Game Dev Module

Game development assistant and asset pipeline for AgentForgeOS.

Provides AI-assisted game design, asset generation, scene planning, and integration with game engines (Godot, Unity).

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/modules/game_dev/status` | Module health check |
| POST | `/api/modules/game_dev/design` | Generate a game design document |
| POST | `/api/modules/game_dev/scene` | Scaffold a new game scene |
| GET | `/api/modules/game_dev/projects` | List active game projects |
