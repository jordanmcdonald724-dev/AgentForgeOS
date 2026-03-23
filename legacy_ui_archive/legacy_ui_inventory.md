# Legacy UI Inventory & Decommission Map

This document lists every frontend/UI asset that must be treated as **Legacy V1** (to be archived) versus the **Emergent V2** files that stay active. Use it as the authoritative checklist when relocating files so nothing touches the backend except the Emergent UI set.

## Emergent V2 (KEEP IN `frontend/src/`)
1. `App.js`
2. `App.css`
3. `index.js`
4. `index.css`
5. `components/ui/resizable.jsx`

Everything else in `frontend/` (and any other UI-related directories) is Legacy V1 and should be moved into `legacy_ui_archive/`.

## Legacy V1 Assets (MOVE OUT)

### A. Frontend Source (`frontend/src/`)
Move every item except the five Emergent files listed above. Key paths:
- `frontend/src/main.jsx`
- `frontend/src/components/` (all subfolders, including `ui/*` other than `resizable.jsx`, `realtime/`, etc.)
- `frontend/src/hooks/`, `frontend/src/lib/`, `frontend/src/router/`
- `frontend/src/ui/` (entire directory)
- `frontend/src/pages/` (all feature pages)
- `frontend/src/ui/styles/agentforge.css`

### B. Frontend Public & Build Assets
- `frontend/public/index.html`
- Entire `frontend/dist/` directory
- `frontend/studio_legacy.html`
- `frontend/wizard.html`, `frontend/wizard.css`
- `frontend/style.css`

### C. Frontend Tooling/Configs (Legacy Stack)
- `frontend/craco.config.js`
- `frontend/postcss.config.js`
- `frontend/tailwind.config.js`
- `frontend/vite.config.js`
- `frontend/components.json`
- `frontend/jsconfig.json`
- `frontend/tsconfig.json`
- `frontend/package.json` (and `package-lock.json`)
- Any files under `frontend/plugins/`

### D. Node Modules & Build Artifacts
- Entire `frontend/node_modules/` directory (legacy dependencies)
- `frontend/.gitignore`, `frontend/README.md` (legacy instructions)

### E. Miscellaneous UI Assets
- `frontend/AgentForgeUI_Image References/`
- `frontend/.emergent/` (if present) and any other design reference folders

### F. Backend/UI Wiring References (Document Only)
These files remain but must be updated so they no longer reference legacy assets once relocation is complete:
- `engine/server.py` (static mounts for `/`, `/wizard.html`, `/emergent-ui`)
- `backend/server.py` (old entrypoint; keep for reference, not active serving)
- `start_server.py` (launches `engine.server`)
- `engine/routes/*` (setup/modules/bridge/orchestration APIs consumed by the UI)
- `backend/routes/*` and `apps/*/backend/routes.py` (API endpoints surfaced in the UI)
- Documentation pointing to UI assets (`README.md`, `FINAL_BIBLE_COMPARISON.md`, `docs/`)

**Note:** After V1 assets move, update these files to remove any legacy references.

## Comprehensive UI File Breakdown (Frontend + Backend)

### Frontend Structure (`d:\AgentForgeOS\frontend`)
1. **Core Entry + Styles**
   - `src/index.js`, `src/index.css`, `src/App.js`, `src/App.css`, `src/main.jsx`
2. **Component Libraries**
   - `src/components/` (Shadcn UI set, realtime components, etc.)
   - `src/ui/` (layout, context, hooks, pipeline views, panels, agents)
3. **Support Modules**
   - `src/hooks/`, `src/lib/`, `src/router/`
4. **Pages & Panels**
   - `src/ui/pages/*`, `src/ui/components/panels/*`, `src/ui/components/agents/*`
5. **Static/Build Assets**
   - `public/index.html`, entire `dist/`, `style.css`, `wizard.html`, `wizard.css`, `studio_legacy.html`
6. **Tooling & Config**
   - `package.json`, `package-lock.json`, `vite.config.js`, `craco.config.js`, `tailwind.config.js`, `postcss.config.js`, `components.json`, `jsconfig.json`, `tsconfig.json`, `plugins/`
7. **Dependencies & Misc**
   - `node_modules/`, `AgentForgeUI_Image References/`, `.gitignore`, `README.md`, `.emergent/`

### Backend / Server UI Touch Points
1. `start_server.py` – launches the unified engine app.
2. `engine/server.py` – mounts `/`, `/wizard.html`, `/emergent-ui`, registers `/api` routers.
3. `backend/server.py` – legacy entry (kept for reference).
4. `engine/routes/*` – APIs hit by the UI (setup, modules, bridge, pipeline, orchestration, research, monitoring).
5. `backend/routes/*` and `apps/*/backend/routes.py` – additional API endpoints surfaced in the UI.
6. Docs & guides referencing UI entrypoints (`README.md`, `FINAL_BIBLE_COMPARISON.md`, files under `docs/`).

Everything listed above is considered UI-related; only the Emergent keep-set should remain in `frontend/src/` after the move, with all other assets archived and backend routes updated accordingly.

## Relocation Instructions
1. Create `d:\AgentForgeOS\legacy_ui_archive\frontend_src_v1\` (and parallel folders for `public`, `dist`, etc.).
2. Move each legacy file/directory listed above into the archive, keeping the same relative structure (e.g., `legacy_ui_archive/frontend_src_v1/components/ui/...`).
3. Leave only the Emergent files (App.js/App.css/index.js/index.css/components/ui/resizable.jsx) inside `frontend/src/`.
4. Once relocation is done, update `engine/server.py` static mounts to ensure `/` serves only the Emergent build directory, and remove any explicit references to the archived files (`wizard.html`, `studio_legacy.html`, etc.).
5. Record the date of relocation in this file so we always know when V1 was isolated.

### Status Log
- **2026-03-19** — Legacy V1 UI fully relocated into `legacy_ui_archive/Frontend_Backup`, leaving only the five Emergent files under `frontend/src/`. All wizard/static mounts were removed from `engine/server.py`, so the backend no longer serves any archived assets. Future UI hookups should mount the new Emergent bundle explicitly.

_Last updated: 2026-03-19_

