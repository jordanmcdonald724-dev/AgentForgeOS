# Setup Wizard — Local Windows 10 Flow

This document captures the exact end-to-end setup wizard flow for running AgentForgeOS locally on **Windows 10** for beta testing. It outlines prerequisites, the bootstrap/self-install steps, and what the wizard collects before launching Studio.

---

## 1) Prerequisites (one-time)

- Windows 10 (64-bit) with PowerShell
- Git
- Python 3.11+ (`winget install Python.Python.3.11`)
- Node.js 20+ (`winget install OpenJS.NodeJS.LTS`) — required only for the Tauri desktop wrapper
- Rust + Cargo (`winget install Rustlang.Rust.MSVC`) — required only for the Tauri desktop wrapper
- Optional local providers:
  - **Ollama** (LLM) — install from https://ollama.com/download/windows and pull a model (e.g., `ollama pull llama3`)
  - **ComfyUI** (image) — run your local ComfyUI server on port `8188`
  - **Piper** (TTS) — download a voice model if you want offline speech

---

## 2) Bootstrap / Self-install command (PowerShell)

Run these commands from the repository root to prepare a local virtual environment and install dependencies:

```powershell
cd AgentForgeOS
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
# For the desktop shell (optional):
cd desktop
npm install
cd ..
```

What this does:
- Creates/activates an isolated `.venv`
- Installs Python requirements (FastAPI, httpx, etc.) so backend/tests run
- Installs desktop dependencies if you plan to launch via Tauri

---

## 3) Launch the engine

```powershell
.\.venv\Scripts\Activate.ps1
python -m engine.main
```

This starts FastAPI on `http://127.0.0.1:8000`. Leave it running while you complete the wizard.

---

## 4) Open the setup wizard

Choose one:
- **Web**: open `frontend/wizard.html` in your browser (it will call the engine on `localhost:8000`).
- **Desktop shell (optional)**: from `desktop`, run `npm run tauri dev` to open the Tauri window; it loads the same wizard and will redirect there automatically when `SETUP_COMPLETE` is missing.

---

## 5) Wizard steps (what gets collected)

1. **Welcome** — confirm engine host/port (default `127.0.0.1:8000`).
2. **LLM Provider** — pick **Ollama (local)** or **OpenAI (cloud)**.
   - Ollama: base URL + model name.
   - OpenAI: API key.
3. **Image & Voice** — choose **ComfyUI** (URL) or **Fal** (API key) for images; choose **Piper** (optional model path) or disable TTS.
4. **Storage & Bridge** — set `BRIDGE_ROOT` sandbox path and `LOG_LEVEL`.
5. **Review & Save** — writes values to `config/.env`, sets `SETUP_COMPLETE`, then loads Studio.

Allowed keys are restricted by the setup API (`/api/setup/save`) to prevent accidental writes.

---

## 6) Post-install checks

- `config/.env` exists and includes `SETUP_COMPLETE=true`.
- Engine health: `Invoke-WebRequest http://127.0.0.1:8000/api/health`.
- Studio loads without redirecting back to the wizard.
- Optional services reachable (if selected):
  - `http://localhost:11434` for Ollama
  - `http://localhost:8188` for ComfyUI

---

## 7) Known gaps to monitor for beta

- Users must still install optional local providers themselves (Ollama/ComfyUI/Piper downloads). The wizard only records their endpoints/paths.
- No automated download of TTS models; provide a model path if using Piper.
- MongoDB is optional; leaving it unset runs in in-memory mode.

This flow should cover local Windows 10 bring-up with minimal manual steps and clarifies exactly what the setup wizard is expected to collect before Studio opens.
