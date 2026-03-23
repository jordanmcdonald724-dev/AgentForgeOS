## Ship Checklist (AgentForgeOS)

This is the minimal, repeatable pre-ship checklist aligned with the Build Bible.

### 1) Clean build validation (repo machine)

- Backend tests: `python -m unittest -q`
- Frontend build: `npm -C frontend run build`

### 2) Desktop bundle validation (same machine)

If you have a built Electron `win-unpacked` folder:

- Backend-only smoke:
  - `powershell -ExecutionPolicy Bypass -File .\scripts\release_smoke.ps1 -InstallDir "<path-to-win-unpacked>" -StartBackend`
- App-start smoke (validates no-terminal startup path):
  - `powershell -ExecutionPolicy Bypass -File .\scripts\release_smoke.ps1 -InstallDir "<path-to-win-unpacked>" -StartApp`

Expected result: `RELEASE SMOKE: PASS`

### 3) Clean machine validation (required once per release)

- Install the generated installer
- Confirm installed layout contains:
  - `AgentForgeOS.exe` (or app exe)
  - `backend.exe`
  - `resources\config.json`
  - `resources\providers.json`
  - `resources\assets\registry.json` (optional initially)
- Confirm first run:
  - launches with no terminal window
  - backend responds at `/api/health`
  - Setup Wizard appears if not configured
  - UI refreshes (no stale cached wizard)

If the UI looks out-of-date after updating builds:

- Close the app
- Confirm no `backend.exe` is still running in Task Manager
- Launch the newest `win-unpacked\\AgentForgeOS.exe` or reinstall the newest installer

### 4) Secrets check (must be clean)

- Ensure `resources/config.json` in repo does not contain real `bridge_token`
- Ensure `resources/providers.json` in repo does not contain real API keys
