# DEPRECATED — V2 Full-System Spec & Gap Audit

This document is deprecated and must not be used as a specification or source of truth.

Canonical Build Bible: [master_build_guideline.md](file:///d:/AgentForgeOS/docs/master_build_guideline.md)

## Purpose

Historical reference only.

The focus is:
- **Surgical hookup only** (no mass deletions / no UI rewrites).
- **Embedding + learning reliability** as a top priority.
- **Boot + packaging reliability** (local run and distributable desktop).

## Scope

In-scope:
- Backend runtime (FastAPI engine + module loader + websocket events).
- Frontend/Studio UI hookup to real backend state.
- Research ingestion + knowledge persistence + “learning” loop.
- Packaging/distribution (desktop wrapper + packaged backend runtime as needed).
- Consistency across docs (resolve conflicting specs into one “source of truth”).

Out-of-scope:
- Redesigning the UI architecture, styling system, or page structure.
- Replacing the orchestration model with a different workflow.
- Replacing providers or embedding approach unless required for stability.

## Sources Of Truth (And Conflicts To Resolve)

These repo documents conflict in key places; implementation must follow an explicit precedence order:

### Primary references
- [docs/master_build_guideline.md](file:///d:/AgentForgeOS/docs/master_build_guideline.md): canonical Build Bible.

All other docs are supporting references only and must not contradict the Build Bible.

### Precedence rule
When conflicts exist, the precedence is:
1. Running code + automated tests
2. [docs/master_build_guideline.md](file:///d:/AgentForgeOS/docs/master_build_guideline.md)
3. The rest of `docs/` (checklists and status docs)
4. Archived targets (e.g. Build Bible) as aspirational guidance

### Known conflicts (must be decided, not hand-waved)
- **Frontend page architecture**
  - BUILD_BIBLE_V2: “strictly 3 pages only”.
  - UI_Files_v2: “App.js monolith with sidebar modules + modal pages”.
  - UI_HOOKUP_CHECKLIST: “many routes/pages + stubs”.
  - Current runtime: Vite boots `frontend/src/App.jsx`, not `App.js`; routing is effectively single-route Studio with internal module switching.
  - Requirement: **preserve the Studio shell** and define what “pages” means in practice (routes vs panels vs modals).
- **Desktop shell**
  - README/LOCAL_RUN_CHECKLIST/BUILD_STATUS imply **Tauri** is the desktop wrapper.
  - Repo also contains an Electron wrapper that launches `backend.exe`; treat it as a supported packaging path only if explicitly adopted.
- **“Done” status**
  - BUILD_STATUS claims broad completion.
  - UI_HOOKUP_CHECKLIST marks multiple critical items as not started.
  - Requirement: trust **runtime verification** over docs labels.

## System Definition (Target Behavior)

### Boot Contract (Engine + UI)
- One command starts the backend engine and serves UI at the same origin.
- Health endpoint is stable and fast.
- Module loader discovers app modules and mounts them under `/api/modules/<module_id>`.
- UI loads without separate dev server in production mode.

### API Contract
- `GET /api/health` returns OK quickly.
- `GET /api/modules` returns a stable list of module manifests.
- Websocket endpoint `/ws` streams execution events using the documented event schema.

### WebSocket Contract (Truthful UI)
- Websocket events are the single authoritative stream for “what is running”.
- UI must **not** fabricate agent/pipeline states when backend is connected.
- Event schema must match [UI_HOOKUP_CHECKLIST.md](file:///d:/AgentForgeOS/docs/UI_HOOKUP_CHECKLIST.md) and remain backwards compatible when extended.

### Embedding & Knowledge Contract (Priority)
- Embedding is required for search, retrieval, and learning.
- Embedding implementation must be:
  - Import-safe (no heavy optional deps at import time).
  - Deterministic given fixed inputs (for repeatability).
  - Persisted or reproducible (knowledge survives restarts).

### Research Ingestion & Learning Contract
- The system supports ingestion of:
  - GitHub repos
  - PDFs / docs
  - transcripts
  - videos (optional feature; must not crash the engine if deps are missing)
- Ingestion produces:
  - stored source records
  - extracted patterns/notes
  - embeddings and searchable nodes
- “Learning” means:
  - New knowledge becomes queryable by later runs.
  - Failures generate autopsy artifacts and improve subsequent execution guidance.

### Packaging/Distribution Contract

Minimum deliverable distribution:
- A user can launch a desktop app that:
  - starts the backend reliably
  - loads the UI reliably
  - performs core actions (health/modules/ws) without manual setup

Packaging must include:
- UI build assets
- module directories required for dynamic loading
- configuration templates (without secrets)
- clear logs and failure modes (no silent exits)

## Gap Audit (What Must Be Verified)

This section defines what “spec everything” means operationally: verify each contract with runtime checks, then implement gaps.

### A) Runtime Boot
- Verify engine boots on a clean machine profile.
- Verify UI is served by the engine without a separate dev server.

### B) Module Loading
- Verify `/api/modules` is correct and modules mount under `/api/modules/<id>`.
- Verify missing module folders fail gracefully with actionable errors.

### C) WebSocket Event Plumbing
- Verify `/ws` accepts connections from the UI.
- Verify events are emitted during pipeline execution and consumed by UI state.

### D) UI ↔ Backend Hookup
- Verify any UI panel/page that claims “live data” uses real endpoints.
- Verify no UI page breaks because of request/response mismatches.

### E) Embedding & Learning
- Verify embedding service is called by research ingestion and retrieval flows.
- Verify persistence (JSON/Mongo/other) actually saves and reloads.

### F) Packaging
- Verify the desktop wrapper starts the backend and serves UI.
- Verify packaged builds do not crash from optional dependencies at import time.

## Acceptance Criteria (High-Level)

This spec is “met” when:
- Local run checklist completes successfully end-to-end.
- UI shows live websocket-driven state (no mocked agent/pipeline once connected).
- Research ingestion succeeds for at least one source type and is queryable after restart.
- Desktop packaged app launches reliably and passes health/modules/ws checks.
