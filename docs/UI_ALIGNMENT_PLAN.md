# UI Alignment Plan — Restore Emergent Layout to Match Reference Images

> **Date:** 2026-03-18  
> **Status:** PLAN ONLY — no code has been modified  
> **Action required:** User approval before any code changes

---

## 1. The Problem

The current UI **does not match** the reference images.

Two complete UI systems exist in the repo side-by-side:

| | Emergent UI (App.js) | V2 Premium UI (AppLayout.jsx) |
|---|---|---|
| **File** | `frontend/src/App.js` (1101 lines) | `frontend/src/ui/components/layout/AppLayout.jsx` (75 lines) |
| **Styles** | `frontend/src/App.css` (1270 lines) | `frontend/src/ui/styles/agentforge.css` (288 lines) |
| **Currently loaded?** | ❌ **NO** — nothing imports it | ✅ **YES** — active via `main.jsx → Router.jsx → pages` |
| **Matches reference images?** | ✅ **YES** | ❌ **NO** |

### What the reference images show (Emergent / App.js layout):

```
┌─────────────────────────────────────────────────────────────────────────┐
│  [AF] AgentForgeOS        [Project][Workspace][Providers][⚙ System][Settings][👤 Profile]
├──────────────┬──────────────────────────────────────────────────────────┤
│  MODULES     │  Studio  v1.0                                           │
│              │  Project workspace and file management                  │
│  ▸ Studio ◄  │                                                         │
│  ▸ Build Pipes│  PROJECT FILES                                         │
│  ▸ Research  │  workspace > ...                                        │
│  ▸ Assets    │  📁 backend    📁 frontend    📁 tests                  │
│  ▸ Deployment│  📄 README.md  📄 package.json                          │
│  ▸ Sandbox   │                                                         │
│  ▸ Game Dev  │                                                         │
│  ▸ SaaS Bldr │                                                         │
├──────────────┼────────────────────────┬────────────────────────────────┤
│ AGENT CONSOLE│   PIPELINE MONITOR     │  OUTPUT LOG                    │
│ 🧑‍💻🧑‍💻🧑‍💻🧑‍💻🧑‍💻🧑‍💻 +6│ [12 agent stage chips] │  HH:MM:SS [INFO] message       │
│              │                        │                                │
│ PLANNER:     │ Project Planner |      │  05:13:15 PM [INFO] initialized│
│ "Hey! ..."   │ System Architect | ... │                                │
│              │                        │                   ⟲ Emergent   │
│ [Type a prompt...] [▶]│              │                                │
└──────────────┴────────────────────────┴────────────────────────────────┘
```

**Key Emergent layout features (from reference images):**
- Top navigation bar: AF hexagon logo + "AgentForgeOS" + 6 pill buttons
- Left sidebar: "MODULES" heading, 8 clickable items with lucide icons, active item has red border + pulse
- Main workspace: Module-specific panel changes per sidebar selection
- Bottom split into 3 resizable panels: Agent Console (avatars + chat), Pipeline Monitor (12 chips), Output Log
- "Made with Emergent" badge in bottom-right corner
- Dark theme: `#0a0a0c` background, `#dc2626` accent red
- All 8 module panels fully implemented (Studio, Builds, Research graph, Assets, Deployment, Sandbox, Game Dev, SaaS Builder)

### What currently renders (V2 Premium / AppLayout.jsx):

```
┌──────────────────────────────────────────────────────────────┐
│ AgentForge │ Premium UI │               main               │
│────────────│            │  Studio — Unified workspace shell  │
│ Command Ctr│            │                                    │
│ Project WS │            │  Agents (5 cards with glow)       │
│ Research Lab│           │  Planner | Architect | Router...   │
│ Studio     │            │                                    │
│ Builds     │            ├───────────────┬────────────────────│
│ Assets     │            │ Input/Output  │ Pipeline (5 steps) │
│ Deployment │            │ [prompt] [Send]│ Plan|Route|Build  │
│ Sandbox    │            │               │ Test|Stabilize     │
│ Game Dev   │            │               │ Logs               │
│ SaaS Bldr  │            │               │                    │
│ Research   │            │               │                    │
│────────────│            │               │                    │
│ Calm, state│            │         [System State] [Snapshot]  │
│ driven glow│            │                                    │
└────────────┴────────────┴───────────────┴────────────────────┘
```

**Key differences:**
- No top navigation bar (no AF hexagon, no pill buttons)
- Sidebar says "AgentForge" / "Premium UI" instead of "MODULES" with icons
- Navigation includes different items (Command Center, Project Workspace, Research Lab)
- Only 5 agents shown (not 12), only 5 pipeline steps (not 12)
- No agent avatars, no chat-style console
- Glass morphism styling instead of classic panel borders
- No "Made with Emergent" badge
- No resizable panels (fixed grid)

---

## 2. What Exists and What's Missing

### ✅ Emergent layout code IS in the repo

| Component | File | Status |
|---|---|---|
| NavBar (AF logo + 6 pills) | `App.js` lines 54-80 | ✅ Complete |
| Sidebar (8 modules + icons) | `App.js` lines 82-104 | ✅ Complete |
| StudioPanel (file browser) | `App.js` lines 107-184 | ✅ Complete |
| BuildsPanel (trigger + history) | `App.js` lines 186-243 | ✅ Complete |
| ResearchPanel (nodular graph) | `App.js` lines 246-440 | ✅ Complete |
| AssetsPanel (registry) | `App.js` lines 442-472 | ✅ Complete |
| DeploymentPanel (deploy manager) | `App.js` lines 474-529 | ✅ Complete |
| SandboxPanel (emergent experiment) | `App.js` lines 531-698 | ✅ Complete |
| GameDevPanel (design docs) | `App.js` lines 700-756 | ✅ Complete |
| SaasBuilderPanel (scaffolder) | `App.js` lines 758-816 | ✅ Complete |
| AgentConsole (12 avatars + chat) | `App.js` lines 849-979 | ✅ Complete |
| PipelineMonitor (12 stage chips) | `App.js` lines 982-1005 | ✅ Complete |
| OutputLog (timestamped entries) | `App.js` lines 1007-1031 | ✅ Complete |
| ResizablePanelGroup layout | `App.js` lines 1033-1086 | ✅ Complete |
| App.css (all Emergent styles) | `App.css` (1270 lines) | ✅ Complete |
| ResizablePanel component | `components/ui/resizable.jsx` | ✅ Complete |

### ✅ V2 features that should be PRESERVED

| Feature | File | Keep? |
|---|---|---|
| SystemContext (global state) | `ui/context/SystemContext.jsx` | ✅ Keep |
| useEventStream (WebSocket) | `ui/hooks/useEventStream.js` | ✅ Keep |
| useAgentState (agent tracking) | `ui/hooks/useAgentState.js` | ✅ Keep |
| usePipelineState (pipeline) | `ui/hooks/usePipelineState.js` | ✅ Keep |
| CommandCenterPage (V2 page) | `ui/pages/CommandCenterPage.tsx` | ✅ Keep |
| ProjectWorkspacePage (V2 page) | `ui/pages/ProjectWorkspacePage.tsx` | ✅ Keep |
| ResearchLabPage (V2 page) | `ui/pages/ResearchLabPage.tsx` | ✅ Keep |
| V2 Glass components | `ui/components/panels/*` | ✅ Keep |
| agentforge.css design system | `ui/styles/agentforge.css` | ✅ Keep |
| API proxy config | `vite.config.js` | ✅ Keep |

### ✅ In-repo reference images confirm target layout

14 JPEG reference images exist at `AgentForgeUI_Image References/`:
- `Studio UI layout.jpeg` — matches reference image 1
- `Build Pipelines.jpeg` — matches reference image 2 (likely)
- `Sandbox Page UI Layout.jpeg` — matches reference image 3 (likely)
- `Research UI layout.jpeg` — matches reference image 4 (likely)
- Plus: Assets, Deployment, Game Dev, SaaS Builder, and 6 top-nav modal pages

---

## 3. Plan of Attack

### Strategy: Restore Emergent layout as the primary UI shell, preserve V2 features

The goal is to make `main.jsx` render the Emergent (App.js) layout while keeping V2 hooks, context, and API wiring available for use within that shell.

### Phase 1 — Switch entry point (minimal change)

**Task 1.1:** Modify `main.jsx` to render the `App.js` Studio component as the main UI, wrapped in `SystemProvider`

```jsx
// main.jsx — target state
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.js";
import { SystemProvider } from "./ui/context/SystemContext";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <SystemProvider>
      <App />
    </SystemProvider>
  </React.StrictMode>
);
```

**Task 1.2:** Verify the Emergent layout renders correctly — screenshot and compare against all 4 reference images

**Task 1.3:** Fix any import/CSS issues that arise from the switch (App.js uses `@/App.css` alias and `react-router-dom` BrowserRouter)

### Phase 2 — Wire V2 backend features into Emergent panels

The Emergent panels currently use mock data or direct `fetch()` calls. Wire them to the V2 backend:

| Panel | Current State | Wire To |
|---|---|---|
| StudioPanel | Mock file list + direct `/api/bridge/list` | Keep as-is (already API-wired) |
| BuildsPanel | Mock builds + direct `/api/modules/builds/*` | Keep as-is (already API-wired) |
| AgentConsole | Mock responses + direct `/api/agent/run` | Add `useAgentState` hook for real-time agent state |
| PipelineMonitor | Static 12 chips | Add `usePipelineState` hook for live execution tracking |
| OutputLog | Local state only | Connect to `useEventStream` for `/ws` events |
| ResearchPanel | Mock nodes only | Wire to `/api/v2/research/nodes` |

### Phase 3 — Add V2 pages as additional modules (optional)

The V2 pages (Command Center, Project Workspace, Research Lab) contain unique functionality not present in the Emergent panels. These can be added as additional sidebar modules:

| V2 Page | Add as Module? |
|---|---|
| CommandCenterPage | ✅ Add as "Command Center" module in sidebar |
| ProjectWorkspacePage | ✅ Add as "Workspace" module or merge into Studio |
| ResearchLabPage | ✅ Add as "Research Lab" module or merge into Research |

### Phase 4 — Top navigation modals

The reference images and `Tab Usages Info.txt` define 6 modal pages for the top nav pills:

1. **Project** — Recent/Starred/New project + templates
2. **Workspace** — Layout presets + module toggles
3. **Providers** — LLM/Image/TTS/Embeddings config cards
4. **System** — CPU/Memory/Agent stats + service controls
5. **Settings** — Theme/Notifications/Shortcuts/Privacy
6. **Profile** — Avatar/Stats/Achievements/Account

These are currently just buttons in the NavBar. Each would need a modal/overlay component.

---

## 4. Execution Order

```
Phase 1 (quick win — restores visual match)
  1.1  Switch main.jsx entry point to App.js
  1.2  Screenshot + verify against all 4 reference images
  1.3  Fix any import/style issues

Phase 2 (backend wiring — makes it functional)
  2.1  Wire PipelineMonitor to usePipelineState (live steps)
  2.2  Wire AgentConsole to useAgentState (real agent status)
  2.3  Wire OutputLog to useEventStream (WebSocket events)
  2.4  Wire ResearchPanel to /api/v2/research/nodes

Phase 3 (optional — adds V2 page features)
  3.1  Add Command Center as sidebar module
  3.2  Add Project Workspace features to Studio
  3.3  Add Research Lab features to Research

Phase 4 (future — top nav modals)
  4.1–4.6  Implement 6 modal pages per Tab Usages Info.txt
```

### Files that will change:

| File | Change |
|---|---|
| `frontend/src/main.jsx` | Switch import from `Router` to `App` |
| `frontend/src/App.js` | Add SystemProvider hooks to existing panels |
| `frontend/src/App.css` | No changes expected (already complete) |

### Files that will NOT change:

- `AppLayout.jsx` — kept as-is (not deleted, available for V2 pages)
- `Router.jsx` — kept as-is (not deleted, available for V2 routing)
- All V2 page components — kept as-is
- All V2 hooks and context — kept as-is
- `agentforge.css` — kept as-is
- `vite.config.js` — kept as-is

---

## 5. Risk Assessment

| Risk | Mitigation |
|---|---|
| App.js uses `process.env.REACT_APP_BACKEND_URL` (CRA-style) | Vite proxy already handles `/api` → backend, change to relative URLs |
| App.js uses `react-router-dom` BrowserRouter | Already in node_modules; or simplify since App.js only has one route |
| App.js agent avatars use external Unsplash URLs | Will work but may be slow; can replace with local placeholders later |
| Losing V2 page features (Command Center, etc.) | Not lost — files kept, can add as additional modules in Phase 3 |

---

*This plan was authored read-only. No source files were modified.*
