# Sandbox Module

Isolated agent experimentation sandbox for AgentForgeOS.

Run agents in a safe, isolated environment to test prompts, tool integrations, and pipeline configurations without affecting production modules.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/modules/sandbox/status` | Module health check |
| POST | `/api/modules/sandbox/run` | Execute an isolated agent experiment |
| GET | `/api/modules/sandbox/experiments` | List saved experiments |
| DELETE | `/api/modules/sandbox/experiments/{id}` | Delete an experiment |
