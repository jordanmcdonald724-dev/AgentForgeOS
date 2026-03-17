# Local Run Checklist (AgentForgeOS)

Use this short checklist to bring AgentForgeOS up locally.

## 1) Prerequisites
- Python 3.11+
- Node.js 20+ (desktop build)
- Rust + Cargo (Tauri desktop shell)
- (Optional) MongoDB for persistence

## 2) Install dependencies
```bash
pip install -r requirements.txt
```

## 3) Configure environment
```bash
cp config/.env.example config/.env
# edit config/.env as needed (providers, DB, etc.)
```

## 4) Start the backend (FastAPI)
```bash
python -m engine.main
# serves at http://localhost:8000
# /api/health to verify, /api/modules to list modules
```

## 5) Launch the UI
- Browser: open `frontend/index.html` directly, **or**
- Desktop: 
  ```bash
  cd desktop
  cargo tauri dev
  ```

## 6) Optional local providers
- Ollama (LLM): install & run `ollama serve`; set provider in `.env`.
- Piper (TTS), ComfyUI (images), Fal/OpenAI (remote) as configured in `.env`.

## 7) Tests
```bash
python -m unittest discover -s tests
```

## Notes
- The Windows setup wizard flow is documented in `docs/SETUP_WIZARD_WINDOWS.md`.
- Current build status and phase audit: see `docs/BUILD_STATUS.md` and `docs/PHASE_AUDIT.md`.
