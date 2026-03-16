# AgentForgeOS — System Capability Map

Purpose:

Document every capability available in AgentForgeOS, which system layer owns it, and whether the capability is implemented, scaffolded, or still to be built.

This map is the primary reference for understanding current system state and planning remaining work.

---

## Capability Status Legend

- ✅ COMPLETE — Implemented and functional
- ⚠️ SCAFFOLD — File exists with stub/in-memory implementation; not production-ready
- ❌ MISSING — Required by specification but not yet created

---

## 1. Engine Layer (`engine/`)

| Capability | File | Status |
|---|---|---|
| FastAPI application factory | `engine/server.py` | ✅ COMPLETE |
| Health check endpoint (`/api/health`) | `engine/server.py` | ✅ COMPLETE |
| Configuration loader with `.env` support | `engine/config.py` | ✅ COMPLETE |
| Async MongoDB connection (Motor) | `engine/database.py` | ✅ COMPLETE |
| Uvicorn entrypoint | `engine/main.py` | ✅ COMPLETE |
| Background worker system | `engine/worker_system.py` | ⚠️ SCAFFOLD |
| Dynamic module loader | `engine/module_loader.py` | ✅ COMPLETE |
| Modules API route (`/api/modules`) | `engine/routes/modules.py` | ✅ COMPLETE |

---

## 2. Desktop Layer (`desktop/`)

| Capability | File | Status |
|---|---|---|
| Tauri application scaffold | `desktop/tauri.conf.json` | ✅ COMPLETE |
| Rust backend launcher | `desktop/src/main.rs` | ✅ COMPLETE |
| Auto-spawn Python engine on startup | `desktop/src/main.rs` | ✅ COMPLETE |
| `launch_backend` Tauri command | `desktop/src/main.rs` | ✅ COMPLETE |

---

## 3. Control Layer (`control/`)

| Capability | File | Status |
|---|---|---|
| Task category classifier (5 types) | `control/ai_router.py` | ✅ COMPLETE |
| Protected path enforcement | `control/file_guard.py` | ✅ COMPLETE |
| Agent pipeline coordinator | `control/agent_supervisor.py` | ✅ COMPLETE |
| Runtime module registry (singleton) | `control/module_registry.py` | ✅ COMPLETE |
| Role-based permission matrix | `control/permission_matrix.yaml` | ✅ COMPLETE |

---

## 4. Provider Layer (`providers/`)

| Capability | File | Status |
|---|---|---|
| LLM provider interface (abstract) | `providers/llm_provider.py` | ✅ COMPLETE |
| Image provider interface (abstract) | `providers/image_provider.py` | ✅ COMPLETE |
| TTS provider interface (abstract) | `providers/tts_provider.py` | ✅ COMPLETE |
| Ollama local LLM adapter | `providers/ollama_provider.py` | ❌ MISSING |
| OpenAI LLM adapter | `providers/openai_provider.py` | ❌ MISSING |
| Fal image generation adapter | `providers/fal_provider.py` | ❌ MISSING |
| ComfyUI image adapter | `providers/comfyui_provider.py` | ❌ MISSING |
| Piper TTS adapter | `providers/piper_provider.py` | ❌ MISSING |

---

## 5. Services Layer (`services/`)

| Capability | File | Status |
|---|---|---|
| Agent task execution runner | `services/agent_service.py` | ⚠️ SCAFFOLD |
| Conversation history storage | `services/memory_manager.py` | ⚠️ SCAFFOLD |
| Semantic vector store | `services/vector_store.py` | ⚠️ SCAFFOLD |
| In-memory knowledge graph | `services/knowledge_graph.py` | ⚠️ SCAFFOLD |
| Embedding generation service | `services/embedding_service.py` | ⚠️ SCAFFOLD |
| Code pattern extractor | `services/pattern_extractor.py` | ⚠️ SCAFFOLD |
| Project genome tracker | `services/project_genome_service.py` | ⚠️ SCAFFOLD |
| Build autopsy analyzer | `services/autopsy_service.py` | ⚠️ SCAFFOLD |
| Ordered 12-agent pipeline definition | `services/agent_pipeline.py` | ✅ COMPLETE |

---

## 6. Agents Layer (`agents/`)

| Capability | File | Status |
|---|---|---|
| Agents package | `agents/__init__.py` | ✅ COMPLETE |
| Pipeline execution entry-point | `agents/pipeline.py` | ✅ COMPLETE |
| Project Planner agent class | `agents/planner_agent.py` | ❌ MISSING |
| System Architect agent class | `agents/architect_agent.py` | ❌ MISSING |
| Task Router agent class | `agents/router_agent.py` | ❌ MISSING |
| Module Builder agent class | `agents/builder_agent.py` | ❌ MISSING |
| Backend Engineer agent class | `agents/backend_agent.py` | ❌ MISSING |
| Frontend Engineer agent class | `agents/frontend_agent.py` | ❌ MISSING |
| Integration Tester agent class | `agents/tester_agent.py` | ❌ MISSING |
| Security Auditor agent class | `agents/auditor_agent.py` | ❌ MISSING |

---

## 7. Knowledge Layer (`knowledge/`)

| Capability | File | Status |
|---|---|---|
| In-memory knowledge graph | `knowledge/knowledge_graph.py` | ⚠️ SCAFFOLD |
| In-memory vector store | `knowledge/vector_store.py` | ⚠️ SCAFFOLD |
| In-memory embedding service | `knowledge/embedding_service.py` | ⚠️ SCAFFOLD |
| In-memory pattern extractor | `knowledge/pattern_extractor.py` | ⚠️ SCAFFOLD |
| In-memory project genome | `knowledge/project_genome.py` | ⚠️ SCAFFOLD |
| Persistent vector database (Chroma/Weaviate) | — | ❌ MISSING |
| Real embedding model integration | — | ❌ MISSING |

---

## 8. Bridge Layer (`bridge/`)

| Capability | File | Status |
|---|---|---|
| Bridge package | `bridge/__init__.py` | ✅ COMPLETE |
| Local filesystem access server | `bridge/bridge_server.py` | ✅ COMPLETE |
| Bridge security and sandboxing | `bridge/bridge_security.py` | ✅ COMPLETE |
| Game engine integration (Godot/Unity) | — | ❌ MISSING |
| Local tool launcher (compiler, linter) | — | ❌ MISSING |

---

## 9. Apps Layer (`apps/`)

| Capability | Module | Status |
|---|---|---|
| Studio AI development environment | `apps/studio/` | ⚠️ SCAFFOLD |
| Builds — CI/CD pipeline manager | `apps/builds/` | ⚠️ SCAFFOLD |
| Research — knowledge search & analysis | `apps/research/` | ⚠️ SCAFFOLD |
| Assets — image/audio/model generator | `apps/assets/` | ⚠️ SCAFFOLD |
| Deployment — release manager | `apps/deployment/` | ⚠️ SCAFFOLD |
| Sandbox — isolated experiment runner | `apps/sandbox/` | ❌ MISSING |
| Game Dev module | `apps/game_dev/` | ❌ MISSING |
| SaaS Builder module | `apps/saas_builder/` | ❌ MISSING |

---

## 10. Frontend Layer (`frontend/`)

| Capability | File | Status |
|---|---|---|
| Five-region Studio layout scaffold | `frontend/index.html` | ⚠️ SCAFFOLD |
| Basic CSS layout | `frontend/style.css` | ⚠️ SCAFFOLD |
| Module panel loader (dynamic) | — | ❌ MISSING |
| Real-time agent progress display | — | ❌ MISSING |
| Project file browser | — | ❌ MISSING |
| Terminal/output panel | — | ❌ MISSING |

---

## 11. Configuration Layer (`config/`)

| Capability | File | Status |
|---|---|---|
| Environment variable template | `config/.env.example` | ✅ COMPLETE |
| System settings schema | `config/settings.json` | ✅ COMPLETE |
| Live `.env` configuration | `config/.env` | ❌ MISSING (user-provided) |

---

## 12. Database Collections

| Collection | Purpose | Status |
|---|---|---|
| `projects` | Project metadata | ❌ MISSING |
| `tasks` | Task queue entries | ❌ MISSING |
| `pipeline_runs` | Agent execution logs | ❌ MISSING |
| `agents` | Agent configurations | ❌ MISSING |
| `knowledge_nodes` | Knowledge graph nodes | ❌ MISSING |
| `memories` | Agent memory entries | ❌ MISSING |
| `assets` | Generated asset metadata | ❌ MISSING |
| `provider_config` | Provider credentials | ❌ MISSING |

---

## Summary

| Layer | Total Capabilities | Complete | Scaffold | Missing |
|---|---|---|---|---|
| Engine | 8 | 7 | 1 | 0 |
| Desktop | 4 | 4 | 0 | 0 |
| Control | 5 | 5 | 0 | 0 |
| Providers | 8 | 3 | 0 | 5 |
| Services | 9 | 1 | 8 | 0 |
| Agents | 9 | 2 | 0 | 7 |
| Knowledge | 7 | 0 | 5 | 2 |
| Bridge | 5 | 3 | 0 | 2 |
| Apps | 8 | 0 | 5 | 3 |
| Frontend | 6 | 0 | 2 | 4 |
| Config | 3 | 2 | 0 | 1 |
| Database | 8 | 0 | 0 | 8 |
| **Total** | **80** | **27** | **21** | **32** |

Overall: 34% complete, 26% scaffolded, 40% missing.
