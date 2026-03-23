# Tasks — V2 Audit To “Done”

This is the execution task list derived from:
- [spec.md](file:///d:/AgentForgeOS/docs/specs/v2_audit/spec.md)
- [UI_HOOKUP_CHECKLIST.md](file:///d:/AgentForgeOS/docs/UI_HOOKUP_CHECKLIST.md)
- [LOCAL_RUN_CHECKLIST.md](file:///d:/AgentForgeOS/docs/LOCAL_RUN_CHECKLIST.md)

## Phase 0 — Decide “Source Of Truth” For Conflicts

1. Define the authoritative UI architecture rule:
   - Confirm what “3 pages only” means in this repo (routes vs panels vs modules vs modals).
   - Declare which document wins when conflicts appear (master_build_guideline vs Build Bible vs UI Files vs UI Hookup Checklist).

2. Decide desktop packaging path:
   - Confirm desktop wrapper is Tauri-only (repo default) or adopt Electron as an additional deliverable.

3. Publish canonical API surface:
   - Document the actual engine endpoints used by the UI (health/modules/agent/pipeline/bridge/ws, plus `/api/v2/*`).

4. Resolve legacy stack ambiguity:
   - Decide whether `backend/` is legacy (documentation-only) or an active runtime, and prevent accidental wiring to the wrong stack.

## Phase 1 — Baseline Runtime Verification (No Code Changes)

5. Run backend locally and verify:
   - `/api/health`
   - `/api/modules`
   - module routes under `/api/modules/<id>`

6. Run UI and verify:
   - First-run wizard behavior (setup incomplete → wizard)
   - UI loads under engine-served origin (no separate dev server required for production mode)

7. Verify websocket:
   - UI can connect to `/ws`
   - Event schema matches docs and is stable under load

## Phase 2 — Close Critical UI ↔ Backend Wiring Gaps

8. Complete global wiring items (blockers for all pages/panels):
   - CORS behavior (only if required by actual runtime topology)
   - Vite websocket proxy for dev mode
   - SystemContext reducer wired to websocket events

9. Fix any request/response mismatches that cause hard failures (422/500):
   - Research ingestion request payload alignment
   - Any route expected by UI that backend does not implement (or vice versa)

10. Replace remaining mocked UI state with real data sources where required:
   - Agents/pipeline live state from websocket
   - Module lists from `/api/modules`
   - File tree from bridge endpoints

## Phase 3 — Embedding + Learning End-to-End

11. Trace and verify embedding call path:
   - Ingestion writes nodes/documents → embeddings generated → stored
   - Retrieval/search returns meaningful ranked results

12. Persist and reload learning artifacts:
   - Knowledge graph persistence
   - Vector store persistence
   - Research notes/insights persistence (as defined by module)

13. Ensure optional ingestion features are safe:
   - Video ingestion must not crash engine if optional deps are missing
   - Clear “feature unavailable” errors with actionable guidance

## Phase 4 — Packaging/Distribution

14. Desktop package validation (Tauri):
   - Backend starts from desktop wrapper
   - UI loads
   - Health/modules/ws pass

15. Optional: packaged backend executable (if required by distribution approach):
   - Bundle UI build assets and module directories needed for dynamic loading
   - Validate no import-time crashes from optional dependencies

## Phase 5 — Verification & Hardening

16. Run full automated tests and add missing integration tests:
   - Websocket event smoke test
   - “Ingest then query after restart” smoke test
   - Desktop launch smoke test (where feasible)

17. Produce a final “Done” report:
   - What is implemented vs stubbed
   - Known limitations and next recommended upgrades
