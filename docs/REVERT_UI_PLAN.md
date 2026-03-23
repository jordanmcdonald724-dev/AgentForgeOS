# UI Revert Plan — Branch 25 → Beginning-of-Branch Reset

> **STATUS: PLAN ONLY — no files have been modified.**
> This document describes exactly what must change to revert the frontend to the
> clean state at commit `126b294` (the merge of PR #24, which is the true
> beginning of branch 25 / PR #25), and then restart the
> `UI_HOOKUP_CHECKLIST.md` from scratch.

---

## 1. What the screenshot shows (the UI we are removing)

The attached screenshot displays the **V2 React app** rendered through
`AppLayout.jsx`, routing to `CommandCenterPage.tsx`.  Visible elements:

| Element | Source file |
|---------|-------------|
| Left sidebar — "AGENTFORGE" + "Premium UI" badge | `frontend/src/ui/components/layout/AppLayout.jsx` |
| Nav items (Command Center … Research) with dot indicators | `AppLayout.jsx → NAV_ITEMS` |
| "Calm, state-driven glow. Dark-only." footer text | `AppLayout.jsx` |
| COMMAND CENTER heading + "Simulation-first orchestration" | `frontend/src/ui/pages/CommandCenterPage.tsx` |
| TASK GRAPH / AGENT ACTIVITY / RECURSIVE LOOP panels | `CommandCenterPage.tsx` |
| INPUT textarea + "Run Simulation" button | `CommandCenterPage.tsx` |
| BUILD QUEUE panel | `CommandCenterPage.tsx` |

This UI was visible **during an intermediate commit** on this branch
(`2507b9b`) when the React bootstrap was still present in `index.html`.

---

## 2. Current HEAD state (what is actually rendering right now)

`frontend/index.html` at HEAD contains **only the legacy HTML studio**
(the `<header class="nav">` version).  The React bootstrap (`<script
type="module" src="/src/main.jsx">`) was removed in commit `dbc1b36`.

This means the **React app is not loading at all** in the current build.
The browser shows the old static HTML studio, not the V2 React app.

---

## 3. State at beginning of branch 25 — commit `126b294`

At `126b294`, `frontend/index.html` contained **two `<html>` documents**:

1. React bootstrap (`<!doctype html>` … `<script src="/src/main.jsx">`)
2. Legacy HTML studio (`<!DOCTYPE html>` … `<body class="studio">`)

This dual-document was the root cause of the "bleed-through" issue
noted in commit `2507b9b`.  All other branch-25 changes (CORS, /ws
proxy, wiring, new pages) had **not yet been made** at `126b294`.

---

## 4. Files changed on this branch (what to revert)

| # | File | Change made on branch | Revert action |
|---|------|-----------------------|---------------|
| 1 | `frontend/index.html` | React bootstrap removed; old HTML kept only | Restore to 126b294 (dual-doc), **then** clean to single React bootstrap (see §5) |
| 2 | `frontend/postcss.config.js` | Deleted | Restore file |
| 3 | `frontend/src/router/Router.jsx` | Added Deployment/GameDev/SaasBuilder imports + router cases | Revert to 126b294 state (remove 3 new cases) |
| 4 | `frontend/src/ui/context/SystemContext.jsx` | Added live WebSocket connection (G-3) | Revert to 126b294 (pure reducer, no WS) |
| 5 | `frontend/src/ui/pages/CommandCenterPage.tsx` | Added CC-1/CC-2/CC-3 live API wiring | Revert to 126b294 (static mock only) |
| 6 | `frontend/src/ui/pages/Studio/StudioPage.jsx` | Added S-1–S-5 live API wiring | Revert to 126b294 (static mock only) |
| 7 | `frontend/vite.config.js` | Added `/ws` WebSocket proxy (G-2) | Revert to 126b294 (remove /ws block) |
| 8 | `engine/server.py` | Added CORSMiddleware (G-1) | Revert to 126b294 (remove CORS block) |
| 9 | `apps/assets/backend/routes.py` | Added `generate_asset` endpoint (G-5) | Revert to 126b294 (remove endpoint) |
| 10 | `apps/deployment/backend/routes.py` | Added `launch_engine` endpoint (G-6) | Revert to 126b294 (remove endpoint) |
| 11 | `docs/UI_HOOKUP_CHECKLIST.md` | Created on this branch (did not exist at 126b294); all tasks marked ✅ | Reset all task status markers back to ❌ / 🔴 / ⚠️ per original intent |
| 12 | `projects/session_default/intent.json` | Minor edit in planning commit | Revert to 126b294 state |

---

## 5. Files added on this branch — DO NOT DELETE

These files did not exist at `126b294` but must be **kept** (per
instructions: "do not delete anything"):

| File | Why keep |
|------|----------|
| `frontend/src/ui/pages/Deployment/DeploymentPage.jsx` | Page stub needed for G-4 when redo begins |
| `frontend/src/ui/pages/GameDev/GameDevPage.jsx` | Page stub needed for G-4 |
| `frontend/src/ui/pages/SaasBuilder/SaasBuilderPage.jsx` | Page stub needed for G-4 |
| `frontend/studio_legacy.html` | Legacy HTML backup — reference only |

---

## 6. The correct `frontend/index.html` after revert

The dual-document at `126b294` must be resolved.  After reverting, the
final `index.html` should contain **only** the React bootstrap:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>AgentForgeOS Studio</title>
  </head>
  <body style="margin: 0; background: #0b0f14;">
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

The legacy HTML studio content belongs in `frontend/studio_legacy.html`
(already saved there — do not delete).

---

## 7. Note: AgentForgeUI Image References folder

The problem statement references an **"AgentForgeUI_Image References"**
folder.  This folder **does not exist in the repository** at any
commit, including `126b294`.  Before implementing any visual changes,
this folder (or its contents) must be provided and added to the repo so
image reference files are available for comparison.

The closest existing reference material:
- `docs/UI_LAYOUT_FUNCTIONAL_SPEC.md` — full text spec of the intended 5-panel layout
- `docs/UI_STUDIO_LAYOUT.md` — Studio module layout details
- `frontend/src/ui/styles/agentforge.css` — design tokens and CSS classes
- `frontend/src/App.js` — original full-app component with NavBar, Sidebar, modules

---

## 8. Restart plan for UI hookup checklist

After the revert, the `UI_HOOKUP_CHECKLIST.md` tasks should all be
reset to **not started** and worked in strict order:

### Phase 1 — Global / Infrastructure (G-1 to G-6)

| ID | Task | File(s) |
|----|------|---------|
| G-1 | Add `CORSMiddleware` to `engine/server.py` | `engine/server.py` |
| G-2 | Add `ws: true` proxy in Vite config | `frontend/vite.config.js` |
| G-3 | Wire `SystemContext` reducer to live `/ws` events | `frontend/src/ui/context/SystemContext.jsx` |
| G-4 | Add `deployment` / `game` / `saas` router cases + confirm stub pages exist | `frontend/src/router/Router.jsx` (stubs already exist, do not delete) |
| G-5 | Add `POST /api/modules/assets/generate` endpoint | `apps/assets/backend/routes.py` |
| G-6 | Add engine-launch stub (`/api/modules/deployment/launch`) | `apps/deployment/backend/routes.py` |

### Phase 2 — Studio page (S-1 to S-5)
Wire `StudioPage.jsx` to live API after G-1–G-6 are confirmed working.

### Phase 3 — Command Center (CC-1 to CC-3)
Wire `CommandCenterPage.tsx` after Studio wiring is verified.

### Phase 4 — Remaining pages
Work through PW, RL, B, A, SB, R, D, GD, SS tasks in checklist order.

---

## 9. Recommended execution steps (summary)

1. **`git checkout 126b294 -- <file>`** for each file in the table in §4
   (restores those files to their 126b294 state without touching anything else)
2. Manually clean `frontend/index.html` to the single React bootstrap (§6)
3. Reset `docs/UI_HOOKUP_CHECKLIST.md` status markers to all ❌ / initial state
4. Commit with message: `revert: restore all branch-25 files to 126b294 base state`
5. Obtain and commit "AgentForgeUI_Image References" folder to `docs/AgentForgeUI_Image_References/`
6. Re-implement G-1 through G-6 following the checklist strictly, one task at a time
7. Build and verify UI renders correctly (React app, not legacy HTML) before proceeding
   to page-level wiring tasks (S, CC, PW, …)

---

*This plan was authored read-only. No source files were modified.*
