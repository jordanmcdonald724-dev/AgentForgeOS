# Checklist — What “Done” Means (V2)

**DEPRECATED (UI):** The active Studio UI is `frontend/src/App.js` per the Build Bible. This document is kept for historical context only. Use [master_build_guideline.md](file:///d:/AgentForgeOS/docs/master_build_guideline.md) and [Audit_Checklist.md](file:///d:/AgentForgeOS/docs/Audit_Checklist.md) for current requirements.

Use this to verify V2 is actually working (runtime truth beats doc labels).

## 1) Local Run (Backend + UI)

- [ ] Python environment exists and installs dependencies from `requirements.txt`.
- [ ] Backend starts with the documented entrypoint from [LOCAL_RUN_CHECKLIST.md](file:///d:/AgentForgeOS/docs/LOCAL_RUN_CHECKLIST.md).
- [ ] `GET /api/health` returns OK.
- [ ] UI loads from the backend origin (no separate web server required for prod mode).
- [ ] First-run setup wizard appears when setup is incomplete; normal UI appears after setup.

## 2) Modules

- [ ] `GET /api/modules` returns a stable list and does not error.
- [ ] Each module route group is reachable under `/api/modules/<module_id>`.
- [ ] Missing/invalid module manifests fail gracefully with actionable errors.

## 3) WebSocket Truth

- [ ] UI establishes a websocket connection to `/ws`.
- [ ] Backend emits events during a run (agent/pipeline activity).
- [ ] UI consumes events to drive live state (no mocked pipeline/agents once connected).
- [ ] Event payloads follow the backend event schema (source of truth: engine `/ws` implementation).

## 4) UI ↔ Backend Hookup

- [ ] Any UI view that claims “live” data uses a real endpoint.
- [ ] No critical UI actions trigger 422 due to request/response mismatch.
- [ ] Module list and file tree are loaded from backend endpoints (not hardcoded).

## 5) Embedding & Learning (Priority)

- [ ] Ingest at least one source type (github/pdf/transcript) successfully.
- [ ] Ingestion writes artifacts (sources, extracted notes/patterns, embeddings).
- [ ] Search/retrieval returns relevant results (ranked, not empty).
- [ ] Restart backend and verify knowledge persists (reload works).

## 6) Optional Ingestion Safety

- [ ] Video ingestion does not crash backend at import/startup time.
- [ ] If video deps are missing, backend returns “feature unavailable” error clearly.

## 7) Desktop Packaging

- [ ] Desktop wrapper launches backend reliably.
- [ ] Desktop UI loads reliably.
- [ ] Packaged app passes health/modules/ws checks.
- [ ] No secrets are bundled in the distribution artifacts.

## 8) Regression Guardrails

- [ ] No mass deletion of UI features/components while “hooking up”.
- [ ] Existing routes/features remain available unless explicitly removed by a documented decision.
- [ ] Automated tests pass; add missing smoke tests for:
  - [ ] websocket events
  - [ ] ingest → persist → restart → query
  - [ ] desktop launch
