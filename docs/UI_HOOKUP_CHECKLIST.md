# AgentForgeOS V2 UI ↔ Backend Hookup Checklist

> **Reference guide for wiring the Emergent-built React UI to the FastAPI backend.**
> Use this document to stay on track. If work starts to veer, return to the **Global / Infrastructure** section first — every page-level task depends on those foundations.

---

## Status Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Complete |
| 🔴 | Critical — broken today |
| ⚠️ | Partial / stub |
| ❌ | Not started |

---

## 🌐 GLOBAL / INFRASTRUCTURE  ← **START HERE**

These tasks unblock every page. Do not wire individual pages until these are done.

| ID | Status | Task | File(s) |
|----|--------|------|---------|
| G-1 | ✅ | Add `CORSMiddleware` to `engine/server.py` | `engine/server.py` |
| G-2 | ✅ | Add `ws: true` to Vite dev-server proxy so `useEventStream` reaches `/ws` | `frontend/vite.config.js` |
| G-3 | ✅ | Wire `SystemContext` reducer to live `/ws` WebSocket events | `frontend/src/ui/context/SystemContext.jsx` |
| G-4 | ✅ | Add `deployment`, `game`, `saas` cases to `Router.jsx` + create stub page components | `frontend/src/router/Router.jsx` + 3 new pages |
| G-5 | ✅ | Add `POST /api/modules/assets/generate` image-gen endpoint | `apps/assets/backend/routes.py` |
| G-6 | ✅ | Add engine-launch stub endpoints (`/api/modules/deployment/launch`) | `apps/deployment/backend/routes.py` |

---

## 📄 PAGE 1 — Studio  (`#/studio` → `StudioPage.jsx`)

Backend: ✅ `/api/agent/run`, `/ws` all exist.

| ID | Status | Task |
|----|--------|------|
| S-1 | ✅ | Wire prompt `onSubmit` → `POST /api/agent/run` |
| S-2 | ✅ | Replace hardcoded agent list with `useAgentState({ wsUrl: "/ws" })` |
| S-3 | ✅ | Replace mock pipeline with `usePipelineState({ wsUrl: "/ws" })` |
| S-4 | ✅ | Stream agent output into Output panel from API response / WS events |
| S-5 | ✅ | Connect `SystemContext` dispatch to WebSocket (done by G-3; consume via `useSystem()`) |

---

## 📄 PAGE 2 — Command Center  (`#/command-center` → `CommandCenterPage.tsx`)

Backend: ✅ `/api/v2/command/preview`, `/api/v2/projects/{id}/status` both exist and are wired in the page already.

| ID | Status | Task |
|----|--------|------|
| CC-1 | ✅ | Surface `GET /api/v2/research/categories` as selectable context in the UI |
| CC-2 | ✅ | Pass selected categories as `research_sources[]` in the preview request body |
| CC-3 | ✅ | Display `simulation` response fields (complexity, duration_estimate, feasible) |

---

## 📄 PAGE 3 — Project Workspace  (`#/workspace` → `ProjectWorkspacePage.tsx`)

Backend: ⚠️ File tree + build history exist; engine launch now has a stub.

| ID | Status | Task |
|----|--------|------|
| PW-1 | ❌ | Wire project files tree → `GET /api/bridge/list?path=.` |
| PW-2 | ❌ | Wire Build History → `GET /api/modules/builds/runs` |
| PW-3 | ❌ | Wire Live Logs panel → `/ws` WebSocket |
| PW-4 | ❌ | Wire "Launch Web Build" → `POST /api/modules/deployment/launch { engine: "web" }` |
| PW-5 | ❌ | Disable Unity/Unreal buttons with "coming soon" tooltip until G-6 backend is real |
| PW-6 | ❌ | Show artifact checklist from `GET /api/v2/projects/session_default/status` |

---

## 📄 PAGE 4 — Research Lab  (`#/research-lab` → `ResearchLabPage.tsx`)

Backend: ⚠️ Endpoint exists but request body is mismatched (critical).

| ID | Status | Task |
|----|--------|------|
| RL-1 | 🔴 | **FIX:** page sends `{provider, repo}` but backend requires `{id, kind}` → 422 on every call |
| RL-2 | ❌ | Wire Knowledge Graph viz → `GET /api/v2/research/nodes` |
| RL-3 | ❌ | Show categories from `GET /api/v2/research/categories` as chips |
| RL-4 | ❌ | Wire "Ingest PDFs / docs" button → `POST /api/v2/research/ingest { kind: "pdf" }` |
| RL-5 | ❌ | Wire "Ingest transcripts" button → `POST /api/v2/research/ingest { kind: "transcript" }` |
| RL-6 | ❌ | Wire Research Notes scratchpad → `GET/POST /api/modules/research/notes` |

---

## 📄 PAGE 5 — Builds  (`#/builds` → `BuildsPage.jsx`)

Backend: ✅ All endpoints exist.

| ID | Status | Task |
|----|--------|------|
| B-1 | ❌ | Replace hardcoded module list → `GET /api/modules` |
| B-2 | ❌ | Replace hardcoded build strip → `GET /api/modules/builds/runs` |
| B-3 | ❌ | Wire form submit → `POST /api/modules/builds/trigger` |
| B-4 | ❌ | Poll or subscribe to `/ws` for live build status updates |

---

## 📄 PAGE 6 — Assets  (`#/assets` → `AssetsPage.jsx`)

Backend: ⚠️ Metadata endpoints exist; generation endpoint now stubbed (G-5 done).

| ID | Status | Task |
|----|--------|------|
| A-1 | ❌ | Wire Generate button → `POST /api/modules/assets/generate` + register result |
| A-2 | ❌ | Load last asset preview from `GET /api/modules/assets/list` on mount |
| A-3 | ❌ | Bind stage transitions to backend events (step_complete from /ws) |
| A-4 | ❌ | Add scoring-engine endpoint and bind glow intensity to score |

---

## 📄 PAGE 7 — Sandbox  (`#/sandbox` → `SandboxPage.jsx`)

Backend: ✅ All endpoints exist.

| ID | Status | Task |
|----|--------|------|
| SB-1 | ❌ | Replace `setInterval` mock → `useAgentState({ wsUrl: "/ws" })` |
| SB-2 | ❌ | Wire "Add Node" → `POST /api/modules/sandbox/run` |
| SB-3 | ❌ | Load existing experiments on mount → `GET /api/modules/sandbox/experiments` |
| SB-4 | ❌ | Wire Activity Feed to `/ws` events |

---

## 📄 PAGE 8 — Research  (`#/research` → `ResearchPage.jsx`)

Backend: ✅ All endpoints exist.

| ID | Status | Task |
|----|--------|------|
| R-1 | ❌ | Replace hardcoded source list → `GET /api/v2/research/nodes` |
| R-2 | ❌ | Wire "Add GitHub repo" → `POST /api/v2/research/ingest { kind: "github" }` |
| R-3 | ❌ | Wire "Upload PDF / Docs" → `POST /api/v2/research/ingest { kind: "pdf" }` |
| R-4 | ❌ | Wire "Import transcript" → `POST /api/v2/research/ingest { kind: "transcript" }` |
| R-5 | ❌ | Replace hardcoded graph nodes → `GET /api/v2/research/nodes` |
| R-6 | ❌ | Add search panel → `POST /api/modules/research/search` |

---

## 📄 PAGE 9 — Deployment  (`#/deployment`) — ❌ PAGE WAS MISSING

Backend: ✅ All endpoints exist.

| ID | Status | Task |
|----|--------|------|
| D-1 | ✅ | Create `DeploymentPage.jsx` stub wired to deployment endpoints (done by G-4) |
| D-2 | ✅ | Add `case "deployment"` to `Router.jsx` (done by G-4) |

---

## 📄 PAGE 10 — Game Dev  (`#/game`) — ❌ PAGE WAS MISSING

Backend: ✅ All endpoints exist.

| ID | Status | Task |
|----|--------|------|
| GD-1 | ✅ | Create `GameDevPage.jsx` stub wired to game_dev endpoints (done by G-4) |
| GD-2 | ✅ | Add `case "game"` to `Router.jsx` (done by G-4) |

---

## 📄 PAGE 11 — SaaS Builder  (`#/saas`) — ❌ PAGE WAS MISSING

Backend: ✅ All endpoints exist.

| ID | Status | Task |
|----|--------|------|
| SS-1 | ✅ | Create `SaasBuilderPage.jsx` stub wired to saas_builder endpoints (done by G-4) |
| SS-2 | ✅ | Add `case "saas"` to `Router.jsx` (done by G-4) |

---

## ⚙️ SETTINGS / INFRASTRUCTURE  (no page yet)

| ID | Status | Task |
|----|--------|------|
| INF-1 | ❌ | Create Settings page or modal for `GET/POST /api/v2/settings` |
| INF-2 | ❌ | Surface model routing from `GET /api/v2/model_routing/routes` |
| INF-3 | ❌ | Consume `GET /api/v2/local_bridge/projects` in Workspace or Settings |

---

## API Quick Reference

| Endpoint | Method | Purpose | Consumer |
|----------|--------|---------|---------|
| `/api/health` | GET | Engine health | Monitoring |
| `/api/setup` | GET | Check setup complete | Router.jsx |
| `/api/setup/save` | POST | Save wizard config | wizard.html |
| `/api/setup/bootstrap` | POST | Install dependencies | wizard.html |
| `/api/agent/run` | POST | Run agent or full pipeline | Studio S-1 |
| `/api/pipeline/run` | POST | Direct pipeline execution | - |
| `/api/modules` | GET | List active modules | Builds B-1 |
| `/api/bridge/list` | GET | Browse project files | PW-1 |
| `/api/bridge/read` | GET | Read file content | PW-1 |
| `/api/bridge/sync` | POST | Sync file tree | PW-1 |
| `/api/v2/command/preview` | POST | Simulate command, build task graph | Command Center |
| `/api/v2/projects/{id}/status` | GET | Task + artifact status | Command Center / PW-6 |
| `/api/v2/research/categories` | GET | Knowledge categories | CC-1 / RL-3 |
| `/api/v2/research/ingest` | POST | Ingest source into knowledge graph | RL-1..RL-5 / R-2..R-4 |
| `/api/v2/research/nodes` | GET | List knowledge graph nodes | RL-2 / R-5 |
| `/api/v2/settings` | GET/POST | System settings (engine paths) | INF-1 |
| `/api/v2/local_bridge/projects` | GET | Local projects via bridge | INF-3 |
| `/api/v2/model_routing/routes` | GET | Active model routes | INF-2 |
| `/api/modules/studio/workspace` | GET | Studio file tree | Studio |
| `/api/modules/builds/status` | GET | Builds module status | B-1 |
| `/api/modules/builds/runs` | GET | Build run history | B-2 / PW-2 |
| `/api/modules/builds/trigger` | POST | Trigger a build | B-3 |
| `/api/modules/assets/status` | GET | Assets module status | - |
| `/api/modules/assets/list` | GET | List registered assets | A-2 |
| `/api/modules/assets/register` | POST | Register generated asset | A-1 |
| `/api/modules/assets/generate` | POST | Generate image asset | A-1 (G-5) |
| `/api/modules/deployment/status` | GET | Deployment module status | D-1 |
| `/api/modules/deployment/list` | GET | List deployments | D-1 |
| `/api/modules/deployment/deploy` | POST | Trigger deployment | D-1 |
| `/api/modules/deployment/launch` | POST | Launch engine (Unity/Unreal/Web) | PW-4 / G-6 |
| `/api/modules/sandbox/status` | GET | Sandbox module status | - |
| `/api/modules/sandbox/experiments` | GET | List experiments | SB-3 |
| `/api/modules/sandbox/run` | POST | Run experiment | SB-2 |
| `/api/modules/research/notes` | GET/POST | Research notes | RL-6 |
| `/api/modules/research/search` | POST | Search knowledge | R-6 |
| `/api/modules/game_dev/projects` | GET | List game projects | GD-1 |
| `/api/modules/game_dev/design` | POST | Create game design doc | GD-1 |
| `/api/modules/game_dev/scene` | POST | Scaffold scene | GD-1 |
| `/api/modules/saas_builder/projects` | GET | List SaaS projects | SS-1 |
| `/api/modules/saas_builder/scaffold` | POST | Scaffold SaaS project | SS-1 |
| `/api/modules/saas_builder/projects/{id}/feature` | POST | Add feature to project | SS-1 |
| `/ws` | WS | Real-time execution events | All pages |

---

## WebSocket Event Schema

All events from `/ws` follow:
```json
{
  "schema": "agentforge.event.v1",
  "type": "step_start | step_complete | step_failed | step_retry | pipeline_modified | agent_created | loop_iteration",
  "ts": 1234567890.0,
  "source": "execution_monitor",
  "data": { ... }
}
```

`data` fields by event type:
- `step_start` / `step_complete` / `step_failed` / `step_retry` → `{ pipeline_id, step_id, step_index, agent_id, agent_name, error? }`
- `agent_created` → `{ agent_id, agent_name, role }`
- `loop_iteration` → `{ pipeline_id, iteration }`
- `pipeline_modified` → `{ pipeline_id, steps: [...] }`

`SystemContext` action mapping:
| WS event type | SystemContext action |
|---------------|---------------------|
| `step_start` | `STEP_START` |
| `step_complete` | `STEP_COMPLETE` |
| `step_failed` | `STEP_FAILED` |
| `step_retry` | `STEP_RETRY` |
| `pipeline_modified` | `PIPELINE_MODIFIED` |
| `agent_created` | `AGENT_CREATED` |
| `loop_iteration` | `LOOP_ITERATION` |
