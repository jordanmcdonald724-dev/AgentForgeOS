# AgentForgeOS

A local-first developer operating system that orchestrates AI agents to design, build, and validate software.

---

## Overview

AgentForgeOS runs entirely on your machine. It coordinates a team of AI agents through a structured pipeline, manages projects via a Studio interface, and integrates with local tools such as game engines and compilers.

External AI services (OpenAI, Fal, etc.) are optional providers. The system is designed to work offline using local models (Ollama, Piper, ComfyUI).

---

## Architecture

```
Desktop (Tauri)
    └── Frontend (Studio UI)
            └── Engine (FastAPI)
                    └── Control Layer (AI Supervision)
                            └── Services (Memory, Knowledge, Tasks)
                                    └── Providers (LLM, Image, TTS)
                                            └── Bridge (Filesystem, Tools)
```

For a detailed view see `docs/ARCHITECTURE_MAP.md` and `docs/SYSTEM_ARCHITECTURE.md`.

---

## Quick Start

### Requirements

- Python 3.11+
- Node.js 20+ (for desktop build)
- Rust + Cargo (for Tauri desktop)
- MongoDB (optional, for persistence)

### Install Python dependencies

```bash
pip install -r requirements.txt
```

### Configure environment

```bash
cp config/.env.example config/.env
# Edit config/.env with your settings
```

### Start the backend engine

```bash
python -m engine.main
```

The API server starts at `http://localhost:8000`.

Endpoints:
- `GET /api/health` — server health check
- `GET /api/modules` — list loaded modules
- `GET /api/setup` — setup wizard state (first-run redirect)

### Open the frontend

Navigate to `http://localhost:8000` in a browser — the engine serves the Studio UI
and setup wizard automatically. On first run, you will be redirected to the wizard.

Alternatively, run the Tauri desktop app:

```bash
cd desktop
cargo tauri dev
```

---

## Running Tests

```bash
python -m unittest discover -s tests
```

---

## Project Structure

```
AgentForgeOS/
├── engine/          FastAPI backend runtime
├── desktop/         Tauri desktop wrapper (Rust)
├── control/         AI supervision and safety layer
├── services/        Business logic and data services
├── providers/       Pluggable AI provider adapters
├── agents/          AI agent pipeline
├── knowledge/       Knowledge graph and vector store
├── bridge/          Local filesystem and tool integration
├── apps/            Feature modules (studio, builds, research, ...)
├── frontend/        Studio web interface
├── config/          Configuration templates
├── docs/            Architecture and specification documents
└── tests/           Test suite
```

---

## Documentation

| Document | Purpose |
|---|---|
| `docs/AGENTFORGE_OS_SPEC.md` | Master system specification |
| `docs/AGENTFORGE_BOOTSTRAP_PROMPT.md` | Bootstrap instructions for AI coding agents |
| `docs/AI_DEVELOPMENT_RULES.md` | Mandatory rules for AI agent code changes |
| `docs/AI_PIPELINE_SYSTEM.md` | 12-agent pipeline description |
| `docs/AGENT_SYSTEM.md` | AI agent team roles and responsibilities |
| `docs/ARCHITECTURE_DECISION_RECORDS.md` | Architecture decision records (ADR) |
| `docs/ARCHITECTURE_MAP.md` | Visual component diagram |
| `docs/BOOTSTRAP_PLAN.md` | Phase-by-phase build plan |
| `docs/BUILD_STATUS.md` | What is done vs. still needed |
| `docs/CONTROL_LAYER.md` | AI safety system description |
| `docs/DATABASE_SCHEMA.md` | MongoDB collection schemas |
| `docs/ERROR_HANDLING_SYSTEM.md` | Consistent error response format |
| `docs/ICON_PACK.md` | Icon pack generation script |
| `docs/LOCAL_RUN_CHECKLIST.md` | Quick-start local run checklist |
| `docs/PHASE_AUDIT.md` | Phase-by-phase completion audit |
| `docs/PHASE7-10_REPORT.md` | Phase 7–10 build verification report |
| `docs/PHASE10_COMPLIANCE.md` | Compliance checklist |
| `docs/PROVIDER_IMPLEMENTATION_GUIDE.md` | How to add a new provider |
| `docs/REPOSITORY_STRUCTURE.md` | Required repository layout |
| `docs/SETUP_WIZARD_WINDOWS.md` | Local Windows 10 setup wizard flow |
| `docs/STUDIO_MODULE_SYSTEM.md` | Module structure rules |
| `docs/SYSTEM_API_CONTRACTS.md` | API endpoint specifications |
| `docs/SYSTEM_ARCHITECTURE.md` | Architecture layer definitions |
| `docs/SYSTEM_CAPABILITY_MAP.md` | Per-capability build status |
| `docs/TASK_DECOMPOSITION_SYSTEM.md` | Agent task decomposition rules |
| `docs/UI_SHELL_LOCK.md` | Immutable Studio shell layout |
| `docs/UI_STUDIO_LAYOUT.md` | Five-region Studio UI spec |

---

## Current Build State

See `docs/BUILD_STATUS.md` for the full breakdown.

**Summary:**
- ✅ Engine, desktop, control layer, providers, agents, and bridge are complete
- ✅ Services, knowledge, and apps are implemented (in-memory by default, MongoDB optional)
- ⚠️ End-to-end integration requires a running Ollama instance for live LLM execution

---

## License

This project is provided as a development scaffold. See repository root for license information.
