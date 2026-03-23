# V2 Alignment Audit Report

This report compares:
- The current running implementation (code + tests)
- [master_build_guideline.md](file:///d:/AgentForgeOS/docs/master_build_guideline.md)
- Existing repo docs/checklists

## What Is Real Today (Code Truth)

### Backend (Engine)
- FastAPI app factory: [create_app](file:///d:/AgentForgeOS/engine/server.py#L136-L202)
- Core API prefix: `/api` (routers registered in [server.py](file:///d:/AgentForgeOS/engine/server.py#L154-L172))
- Core endpoints actually implemented:
  - `GET /api/health` ([server.py](file:///d:/AgentForgeOS/engine/server.py#L152-L172))
  - `GET /api/modules` ([modules.py](file:///d:/AgentForgeOS/engine/routes/modules.py#L5-L22))
  - `POST /api/agent/run` ([agent.py](file:///d:/AgentForgeOS/engine/routes/agent.py#L31-L53))
  - `POST /api/pipeline/run` + `GET /api/pipeline/events` ([pipeline.py](file:///d:/AgentForgeOS/engine/routes/pipeline.py#L38-L78))
  - Bridge: `/api/bridge/*` ([bridge/routes.py](file:///d:/AgentForgeOS/bridge/routes.py#L24-L134))
- Dynamic module routing:
  - `apps/*/backend/routes.py` routers mounted under `/api/modules/*` ([server.py](file:///d:/AgentForgeOS/engine/server.py#L177-L180), [module_loader.py](file:///d:/AgentForgeOS/engine/module_loader.py#L111-L242))

### WebSockets (UI Truth Stream)
- Event stream endpoint: `WS /ws` ([server.py](file:///d:/AgentForgeOS/engine/server.py#L174-L176), [ws.py](file:///d:/AgentForgeOS/engine/ws.py#L34-L63))
- Event schema matches the checklist schema: `schema: "agentforge.event.v1"` ([ws.py](file:///d:/AgentForgeOS/engine/ws.py#L25-L31))
- Additional session/project WS routes exist under `/api/ws/*` ([websocket_routes.py](file:///d:/AgentForgeOS/engine/websocket_routes.py#L63-L193)) but are not the primary UI stream today.

### Frontend (Studio UI)
- Actual entrypoint: [main.jsx](file:///d:/AgentForgeOS/frontend/src/main.jsx#L1-L9) renders [App.jsx](file:///d:/AgentForgeOS/frontend/src/App.jsx#L1-L1788)
- The live UI uses:
  - `WS /ws` (direct) and falls back to polling `/api/pipeline/events` ([App.jsx](file:///d:/AgentForgeOS/frontend/src/App.jsx#L1609-L1714))
  - `/api/agent/run`, `/api/bridge/list`, `/api/modules/*` endpoints (see call sites in [App.jsx](file:///d:/AgentForgeOS/frontend/src/App.jsx))
- Vite dev proxy is correctly configured for `/api` and `/ws` with upgrade support ([vite.config.js](file:///d:/AgentForgeOS/frontend/vite.config.js#L12-L26))

### V2 Orchestration (Task Graph + Simulation Gate)
- V2 orchestration runtime exists and is wired:
  - `POST /api/v2/command/preview` and `GET /api/v2/projects/{id}/status` ([v2_orchestration.py](file:///d:/AgentForgeOS/engine/routes/v2_orchestration.py#L66-L180))
  - Runtime executes ready tasks and enforces “declared outputs exist” ([runtime.py](file:///d:/AgentForgeOS/orchestration/runtime.py#L60-L123))

### Desktop Packaging (Two Paths Exist)
- Tauri desktop wrapper launches `python -m engine.main` ([desktop/main.rs](file:///d:/AgentForgeOS/desktop/src/main.rs#L31-L60))
  - This is dev-friendly but not an installer-grade “no Python needed” build yet.
- A separate Electron wrapper exists that spawns `backend.exe` ([AgentForgeOS-App/main.js](file:///d:/AgentForgeOS/AgentForgeOS-App/main.js#L8-L53))
  - A PyInstaller spec for `backend.exe` exists: [backend.spec](file:///d:/AgentForgeOS/backend.spec#L4-L33)
  - Engine supports “frozen” UI asset lookup (`frontend-build/`) ([server.py](file:///d:/AgentForgeOS/engine/server.py#L182-L201))

## Key Gaps vs master_build_guideline.md

### 1) “Installer-grade” desktop layout is not unified
- Guideline expects installed layout like `app.exe + backend.exe + resources/...`.
- Repo currently has:
  - Tauri wrapper that runs `python` (requires runtime) ([desktop/main.rs](file:///d:/AgentForgeOS/desktop/src/main.rs#L33-L38))
  - Electron wrapper that runs `backend.exe` (closer to the guideline) ([AgentForgeOS-App/main.js](file:///d:/AgentForgeOS/AgentForgeOS-App/main.js#L41-L45))
- Alignment decision needed: choose the primary packaging pipeline (or explicitly support both).

### 2) UI architecture terminology conflicts across docs
- The running UI is a single Studio shell in [App.jsx](file:///d:/AgentForgeOS/frontend/src/App.jsx) with module panels and internal switching.
- Some docs describe:
  - “3 pages only” (Build Bible V2)
  - a hash-router + `src/ui/pages/*` structure (UI hookup checklist)
  - an `App.js` monolith file (UI files doc)
- Alignment decision needed: define “page” as either:
  - “top-level operational modes” (Command Center / Workspace / Research) inside the Studio shell, or
  - actual URL routes (not used by the current running UI).

### 3) API surface naming differs from the guideline’s example list
- Guideline example includes `/api/system/*`, `/api/agents/*`, etc.
- Current engine uses `/api/health`, `/api/agent/run`, `/api/pipeline/run`, `/api/modules`, `/api/bridge/*`, plus `/api/v2/*`.
- This is not a failure, but it must be documented as the canonical surface to avoid UI/docs drift.

### 4) Duplicate legacy stacks exist in-tree
- Repo contains a second backend stack under `backend/` separate from `engine/` (see tree in repo root).
- This is a drift risk (developers may wire to the wrong stack) even if tests currently pass.
- Alignment decision needed: mark `backend/` as legacy (documentation-only) or formally remove/relocate it (only if explicitly approved).

## Immediate Next Work (Highest Leverage)

1. Lock “source of truth” precedence: runtime + tests + [master_build_guideline.md](file:///d:/AgentForgeOS/docs/master_build_guideline.md) wins; other docs become supporting references.
2. Publish canonical API surface table (actual endpoints) and point UI + docs to it.
3. Decide packaging target:
   - If “single downloadable installer”: formalize Electron + PyInstaller flow, or upgrade Tauri to ship a backend sidecar.
4. Define UI architecture contract:
   - Keep Studio shell and map “3 pages” into modules/panels (no rewriting).

