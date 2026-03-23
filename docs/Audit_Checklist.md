# AgentForgeOS — Audit Checklist (Blueprint + Runtime Truth)

Use this checklist to see what is **actually wired**, what is **stubbed**, and what is **still not hooked up**.

This checklist is based on:
- running code + tests (truth)
- [master_build_guideline.md](file:///d:/AgentForgeOS/docs/master_build_guideline.md) (Final Build Bible)
- [UI_HOOKUP_CHECKLIST.md](file:///d:/AgentForgeOS/docs/UI_HOOKUP_CHECKLIST.md) (supporting; must not contradict the Build Bible)

## Status Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Working now (verified by tests or runtime smoke check) |
| ⚠️ | Partially wired / present but not end-to-end validated |
| 🔴 | Broken (known mismatch or runtime failure) |
| ❌ | Not hooked up / not implemented |

---

## 0) Build Bible Compliance Snapshot (Full Project)

| Area | Status | What “done” means per Build Bible |
|---|---|---|
| Installer + desktop runtime | ⚠️ | Installs and launches with no terminal; `app.exe` starts `backend.exe` and opens Studio |
| Installed layout | ⚠️ | Installed tree includes `app.exe`, `backend.exe`, `resources/`, `workspace/`, `logs/`, `knowledge/`, `database/`, `embeddings/`, `assets/` |
| Setup wizard | ✅ | First-run wizard actually configures providers + workspace + storage and saves config |
| API surface | ✅ | Required route families exist (`/api/system/*`, `/api/projects/*`, `/api/agents/*`, etc.) |
| Modules | ✅ | Modules under `apps/<module>/` include `backend/`, `frontend/`, `module_config.json`, `README.md` |
| Task decomposition | ✅ | Task queue + `/api/tasks/*` exists and enforces size limits + validation-before-commit |
| Logging | ✅ | Real log files under `logs/` + `/api/logs` endpoint + UI Output Log reflects them |
| Bridge security | ✅ | Workspace sandbox + permission levels + safe command execution + full audit logging |

---

## 1) Desktop Installer + Installed Layout

| ID | Status | Check | Notes |
|---|---|---|---|
| W-1 | ⚠️ | Installer builds | Build exists, but “clean machine” validation is still required |
| W-2 | ⚠️ | Installed layout matches Build Bible | Engine now supports nested `resources/resources` layouts and ensures `resources/` + subdirs exist at startup; still needs packaged install validation |
| W-3 | ⚠️ | No-terminal launch works | Backend build spec is set to windowed (no console); still needs packaged desktop smoke: double-click app → backend starts → UI opens |
| W-4 | ✅ | Setup wizard is functional | Verified by tests: wizard is served, save persists config/providers and sets session cookie that authorizes bridge actions |

---

## 2) API Contract (Build Bible)

| Route family (required) | Status | What exists today |
|---|---|---|
| `/api/system/*` | ✅ | `GET /api/system/status`, `GET /api/system/health`, `GET/POST /api/system/config`, `POST /api/system/start`, `POST /api/system/shutdown` |
| `/api/projects/*` | ✅ | `GET /api/projects`, `POST /api/projects/create`, `GET /api/projects/{id}`, `POST /api/projects/{id}/build`, `POST /api/projects/{id}/deploy`, `GET /api/projects/{id}/status` (build produces `artifact.zip`; deploy produces `artifact.zip` + `deploy.json`) |
| `/api/agents/*` | ✅ | `POST /api/agents/run`, `GET /api/agents/list`, `GET /api/agents/status` (aliases to existing agent run) |
| `/api/pipeline/*` | ✅ | `POST /api/pipeline/start`, `GET /api/pipeline/status`, `GET /api/pipeline/logs`, `POST /api/pipeline/stop` |
| `/api/tasks/*` | ✅ | `POST /api/tasks/create`, `POST /api/tasks/run`, `POST /api/tasks/complete`, `GET /api/tasks`, `GET /api/tasks/status`, `POST /api/tasks/fail` |
| `/api/knowledge/*` | ✅ | `POST /api/knowledge/store`, `POST /api/knowledge/search`, `GET /api/knowledge/search`, `POST /api/knowledge/graph/add`, `GET /api/knowledge/node/{id}` |
| `/api/research/*` | ✅ | `GET /api/research/status`, `GET/POST /api/research/notes`, `POST /api/research/search`, `GET /api/research/search`, `POST /api/research/ingest`, `POST /api/research/video`, `POST /api/research/scan` |
| `/api/assets/*` | ✅ | `GET /api/assets`, `POST /api/assets/generate` (registry persists under `resources/assets/registry.json`) |
| `/api/deploy*` | ✅ | `POST /api/deploy`, `GET /api/deploy/status` (deploy writes `artifact.zip` + `deploy.json`) |
| `/api/modules` | ✅ | `GET /api/modules`, `POST /api/modules/load`, `POST /api/modules/unload` (disabled modules return 403 on `/api/modules/<id>/*`) |
| `/api/providers/*` | ✅ | `GET /api/providers`, `POST /api/providers/config` (persists to `resources/providers.json`, redacts secrets on read) |
| `/api/logs` | ✅ | `GET /api/logs?source=...` tails log files |
| `/api/workspace/*` | ✅ | `GET /api/workspace/status`, `POST /api/workspace/set` (persists to `resources/config.json`) |
| `/api/bridge/*` | ✅ | `health/status`, `run_command`, `run`, `git_commit`, `git_push`, `create_file`, `read_file`, `write_file`, `create_directory`, `delete_file`, `run_build`, `launch_tool`, `list`, `read`, `sync` |

---

## 3) Module System Contract (Build Bible)

| ID | Status | Check | Evidence |
|---|---|---|---|
| M-0 | ✅ | Modules use `module_config.json` | Loader supports `module_config.json` and built-ins include it ([module_loader.py](file:///d:/AgentForgeOS/engine/module_loader.py#L149-L205)) |
| M-1 | ✅ | Each module has `frontend/` directory | Built-in modules now include `apps/<module>/frontend/*.jsx` and Studio loads them dynamically |
| M-2 | ✅ | Each module has `backend/` routes | `apps/*/backend/routes.py` discovered and mounted |

---

## 4) Task Decomposition System (Build Bible)

| ID | Status | Check |
|---|---|---|
| T-1 | ✅ | `/api/tasks/*` exists (create/run/status/list) |
| T-2 | ✅ | Enforces per-task limits (≤5 files, ≤500 LOC, ≤3 parallel) |
| T-3 | ✅ | Validation-before-commit + retry-once + escalate policy exists |

---

## 5) Logging & Audit (Build Bible)

| ID | Status | Check | Notes |
|---|---|---|---|
| L-1 | ✅ | Writes log files to `logs/` (system/pipeline/agents/deployment/errors) | Verified via tests: log files exist and `/api/logs` returns entries for each source |
| L-2 | ✅ | `GET /api/logs` exists | `GET /api/logs?source=system&limit=200` |
| L-3 | ✅ | UI Output Log reflects real backend logs | Output Log panel polls `/api/logs?source=...` and supports system/pipeline/agents/deployment/errors |

---

## 6) Local Bridge (Build Bible)

| ID | Status | Check | Notes |
|---|---|---|---|
| B-1 | ✅ | Workspace sandbox/path traversal protection | Implemented via [BridgeSecurity](file:///d:/AgentForgeOS/bridge/bridge_security.py) |
| B-2 | ✅ | Permission levels 0–5 enforced per role | Roles map to levels 0–5; unauthenticated requests are forced to readonly (0) |
| B-3 | ✅ | Bridge endpoints match Build Bible verbs | Bridge exposes command + file operation verbs |
| B-4 | ✅ | Dangerous commands blocked + all actions logged | Commands are tool-allowlisted with additional restrictions (e.g. python -c requires level 5); all bridge actions emit audit log entries |

---

## 7) Setup Wizard (Build Bible)

| ID | Status | Check | Notes |
|---|---|---|---|
| SW-1 | ✅ | `GET /api/setup` exists | Setup state endpoint exists |
| SW-2 | ✅ | `POST /api/setup/save` allow-lists keys | Present |
| SW-3 | ✅ | Wizard UI completes first-run config | Verified by tests: wizard is served, `/api/setup/save` issues session cookie, and cookie authorizes bridge actions |

---

## 9) Active Studio UI (Build Bible) — `frontend/src/App.js`

This is the authoritative Studio UI implementation (five-panel layout) and the only UI surface that must be audited for Build Bible compliance.

| ID | Status | Check | Evidence |
|---|---|---|---|
| UI-1 | ✅ | Five-panel Studio layout exists (TopNav, Sidebar, Workspace, AgentConsole, PipelineMonitor, OutputLog) | [App.js](file:///d:/AgentForgeOS/frontend/src/App.js) |
| UI-2 | ✅ | Module sidebar includes default modules (Studio/Builds/Research/Assets/Deployment/Sandbox/Game Dev/SaaS Builder) | [App.js](file:///d:/AgentForgeOS/frontend/src/App.js#L37-L60) |
| UI-3 | ✅ | Agent console exposes the 12 core agents | [App.js](file:///d:/AgentForgeOS/frontend/src/App.js#L2198-L2212) |
| UI-4 | ✅ | Pipeline stages display the Build Bible stage list (or a strict superset) | [App.js](file:///d:/AgentForgeOS/frontend/src/App.js#L76-L88) |
| UI-5 | ✅ | Output Log reads backend logs (`/api/logs?source=...`) | [App.js](file:///d:/AgentForgeOS/frontend/src/App.js#L2686-L2737) |
| UI-6 | ✅ | Studio file browser hits Bridge list (`/api/bridge/list`) | [App.js](file:///d:/AgentForgeOS/frontend/src/App.js#L1133-L1144) |
| UI-7 | ✅ | Research notes + search are wired (`/api/modules/research/notes`, `/api/modules/research/search`) | [App.js](file:///d:/AgentForgeOS/frontend/src/App.js#L1631-L1715) |
| UI-8 | ✅ | Assets generate wired (`/api/modules/assets/generate`) | [App.js](file:///d:/AgentForgeOS/frontend/src/App.js#L1858-L1906) |
| UI-9 | ✅ | Builds trigger + runs wired (`/api/modules/builds/trigger`, `/api/modules/builds/runs`) | [App.js](file:///d:/AgentForgeOS/frontend/src/App.js#L1537-L1571) |
| UI-10 | ✅ | Deployment launch wired (`/api/modules/deployment/launch`) | [App.js](file:///d:/AgentForgeOS/frontend/src/App.js#L2052-L2104) |
| UI-11 | ✅ | Provider “Test Connection” validates real provider health (not just “/api/providers reachable”) | Implemented `/api/providers/test` and wired UI to it ([server.py](file:///d:/AgentForgeOS/engine/server.py#L575-L661), [App.js](file:///d:/AgentForgeOS/frontend/src/App.js#L554-L569)) |
| UI-12 | ✅ | Sandbox panel uses backend-driven step status (not local simulation) | Sandbox runs pipeline in module backend and streams status via `/ws` ([routes.py](file:///d:/AgentForgeOS/apps/sandbox/backend/routes.py#L43-L82), [App.js](file:///d:/AgentForgeOS/frontend/src/App.js#L2133-L2314)) |
| UI-13 | ✅ | System services list reflects real runtime services and state transitions | `/api/system/start` and `/api/system/shutdown` now control background tasks ([server.py](file:///d:/AgentForgeOS/engine/server.py#L487-L504)) |

## 10) Unfinished Build Bible Items (System-Level)

This section is the actionable “what is not finished” list derived directly from the Build Bible’s API + platform requirements.

| ID | Status | Requirement (Build Bible) | Current state |
|---|---|---|---|
| API-K-1 | ✅ | `GET /api/knowledge/search` | Implemented ([engine/server.py](file:///d:/AgentForgeOS/engine/server.py#L1152-L1167)) |
| API-K-2 | ✅ | `POST /api/knowledge/graph/add` | Implemented ([engine/server.py](file:///d:/AgentForgeOS/engine/server.py#L1169-L1182)) |
| API-R-1 | ✅ | `POST /api/research/ingest` | Implemented with persistent KB + vectors ([apps/research/backend/routes.py](file:///d:/AgentForgeOS/apps/research/backend/routes.py#L121-L138)) |
| API-R-2 | ✅ | `GET /api/research/search` | Implemented ([apps/research/backend/routes.py](file:///d:/AgentForgeOS/apps/research/backend/routes.py#L97-L105)) |
| API-M-1 | ✅ | `POST /api/modules/load` | Implemented (enables module routes) ([engine/routes/modules.py](file:///d:/AgentForgeOS/engine/routes/modules.py#L27-L37)) |
| API-M-2 | ✅ | `POST /api/modules/unload` | Implemented (disables module routes) ([engine/routes/modules.py](file:///d:/AgentForgeOS/engine/routes/modules.py#L40-L50)) |
| API-B-1 | ✅ | `POST /api/bridge/run` alias | Implemented ([bridge/routes.py](file:///d:/AgentForgeOS/bridge/routes.py#L249-L257)) |
| API-B-2 | ✅ | `POST /api/bridge/git_commit` | Implemented (restricted to level 5) ([bridge/routes.py](file:///d:/AgentForgeOS/bridge/routes.py#L260-L337)) |
| API-B-3 | ✅ | `POST /api/bridge/git_push` | Implemented (restricted to level 5) ([bridge/routes.py](file:///d:/AgentForgeOS/bridge/routes.py#L340-L407)) |
| API-B-4 | ✅ | Bridge tool launching is real (not “supported: false”) | Implemented for explorer/vscode/browser ([bridge/routes.py](file:///d:/AgentForgeOS/bridge/routes.py#L418-L480)) |
| DEPLOY-1 | ⚠️ | Deployment pipeline produces target-meaningful artifacts | Deployment creates ZIP artifacts and can run `npm run build` when `project/frontend/node_modules` exists ([routes.py](file:///d:/AgentForgeOS/apps/deployment/backend/routes.py#L92-L120)) |
| BRIDGE-ENG-1 | ✅ | Game engine control via bridge (Unity/Unreal/Godot) | Launch supported via `/api/bridge/launch_tool` when engine EXE env vars are set ([bridge/routes.py](file:///d:/AgentForgeOS/bridge/routes.py#L551-L588)) |
| DESK-1 | ⚠️ | Clean-machine install validation (no terminal, app starts backend + opens Studio) | Automated smoke exists for health/modules/ws, but clean-machine validation remains manual ([test_smoke_build_bible.py](file:///d:/AgentForgeOS/tests/test_smoke_build_bible.py)) |
| SEC-1 | ✅ | API-level rate limiting and global abuse controls | Basic rate limiting added (token/IP bucket) ([engine/rate_limit.py](file:///d:/AgentForgeOS/engine/rate_limit.py), [engine/server.py](file:///d:/AgentForgeOS/engine/server.py#L1295-L1305)) |

## 11) Documentation Hygiene (Remove Confusion)

| ID | Status | Check |
|---|---|---|
| DOC-1 | ✅ | Any V2 UI-only docs are explicitly marked deprecated (Build Bible is the only authority) |
| DOC-2 | ✅ | “Active UI entrypoint” is documented as `frontend/src/App.js` (and hash-router pages are non-authoritative) |
