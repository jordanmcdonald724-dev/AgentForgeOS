# AgentForgeOS Desktop Runtime

This Tauri scaffold launches the backend server and hosts the Studio frontend.

## Structure
- `Cargo.toml`: Rust package manifest for the Tauri app.
- `src/main.rs`: Starts the backend (`python -m engine.main`) and runs the Tauri window.
- `tauri.conf.json`: Configures window defaults and points to the frontend build (`../frontend/dist`) and dev server (`http://localhost:5173`).

## Usage
1. Ensure Python backend dependencies are installed (`fastapi`, `uvicorn`).
2. Install Rust + Tauri prerequisites (`cargo`, system toolchain).
3. From `desktop/`, run:
   - `cargo tauri dev` for development (expects frontend dev server).
   - `cargo tauri build` for packaging (uses `frontend/dist`).

The backend starts automatically on app setup; you can also invoke `launch_backend` via Tauri commands.
