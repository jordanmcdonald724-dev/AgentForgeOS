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
| Background worker system | `engine/worker_system.py` | ✅ COMPLETE |
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
| Execution monitoring | `control/execution_monitor.py` | ✅ COMPLETE |
| Scoring engine | `control/scoring_engine.py` | ✅ COMPLETE |
| Recovery engine | `control/recovery_engine.py` | ✅ COMPLETE |
| Learning controller | `control/learning_controller.py` | ✅ COMPLETE |
| Dynamic pipeline builder | `control/dynamic_pipeline_builder.py` | ✅ COMPLETE |
| Agent factory | `control/agent_factory.py` | ✅ COMPLETE |
| Runtime module registry (singleton) | `control/module_registry.py` | ✅ COMPLETE |
| Role-based permission matrix | `control/permission_matrix.yaml` | ✅ COMPLETE |

---

## 4. Provider Layer (`providers/`)

| Capability | File | Status |
|---|---|---|
| LLM provider interface (abstract) | `providers/llm_provider.py` | ✅ COMPLETE |
| Image provider interface (abstract) | `providers/image_provider.py` | ✅ COMPLETE |
| TTS provider interface (abstract) | `providers/tts_provider.py` | ✅ COMPLETE |
| Ollama local LLM adapter | `providers/ollama_provider.py` | ✅ COMPLETE |
| OpenAI LLM adapter | `providers/openai_provider.py` | ✅ COMPLETE |
| Fal image generation adapter | `providers/fal_provider.py` | ✅ COMPLETE |
| ComfyUI image adapter | `providers/comfyui_provider.py` | ✅ COMPLETE |
| Piper TTS adapter | `providers/piper_provider.py` | ✅ COMPLETE |

---

## 5. Services Layer (`services/`)

| Capability | File | Status |
|---|---|---|
| Agent task execution runner | `services/agent_service.py` | ✅ COMPLETE |
| Conversation history storage (in-memory) | `services/memory_manager.py` | ✅ COMPLETE |
| MongoDB-backed memory manager | `services/mongo_memory.py` | ✅ COMPLETE |
| Semantic vector store (cosine similarity) | `services/vector_store.py` | ✅ COMPLETE |
| Knowledge graph with optional JSON persistence | `services/knowledge_graph.py` | ✅ COMPLETE |
| TF-IDF embedding generation | `services/embedding_service.py` | ✅ COMPLETE |
| Code pattern extractor | `services/pattern_extractor.py` | ✅ COMPLETE |
| Project genome tracker | `services/project_genome_service.py` | ✅ COMPLETE |
| Build autopsy analyzer | `services/autopsy_service.py` | ✅ COMPLETE |
| Ordered 12-agent pipeline definition | `services/agent_pipeline.py` | ✅ COMPLETE |

---

## 6. Agents Layer (`agents/`)

| Capability | File | Status |
|---|---|---|
| Agents package with AGENT_CLASS_MAP | `agents/__init__.py` | ✅ COMPLETE |
| Abstract base agent | `agents/base_agent.py` | ✅ COMPLETE |
| Pipeline execution entry-point | `agents/pipeline.py` | ✅ COMPLETE |
| Project Planner agent class | `agents/strategic/planner_agent.py` | ✅ COMPLETE |
| System Architect agent class | `agents/strategic/architect_agent.py` | ✅ COMPLETE |
| Task Router agent class | `agents/strategic/router_agent.py` | ✅ COMPLETE |
| Module Builder agent class | `agents/architecture/builder_agent.py` | ✅ COMPLETE |
| API Architect agent class | `agents/architecture/api_architect_agent.py` | ✅ COMPLETE |
| Data Architect agent class | `agents/architecture/data_architect_agent.py` | ✅ COMPLETE |
| Backend Engineer agent class | `agents/production/backend_agent.py` | ✅ COMPLETE |
| Frontend Engineer agent class | `agents/production/frontend_agent.py` | ✅ COMPLETE |
| AI Integration Engineer agent class | `agents/production/ai_integration_agent.py` | ✅ COMPLETE |
| Integration Tester agent class | `agents/validation/tester_agent.py` | ✅ COMPLETE |
| Security Auditor agent class | `agents/validation/auditor_agent.py` | ✅ COMPLETE |
| System Stabilizer agent class | `agents/validation/stabilizer_agent.py` | ✅ COMPLETE |

---

## 7. Knowledge Layer (`knowledge/`)

| Capability | File | Status |
|---|---|---|
| Knowledge graph with JSON persistence | `knowledge/knowledge_graph.py` | ✅ COMPLETE |
| Vector store with cosine similarity + JSON persistence | `knowledge/vector_store.py` | ✅ COMPLETE |
| TF-IDF embedding service (stdlib-only) | `knowledge/embedding_service.py` | ✅ COMPLETE |
| Pattern extractor | `knowledge/pattern_extractor.py` | ✅ COMPLETE |
| Project genome tracker | `knowledge/project_genome.py` | ✅ COMPLETE |
| Persistent vector database (Chroma/Weaviate) | — | ❌ MISSING |
| Neural embedding model integration | — | ❌ MISSING |

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
| Studio AI development environment | `apps/studio/` | ✅ COMPLETE |
| Builds — CI/CD pipeline manager | `apps/builds/` | ✅ COMPLETE |
| Research — knowledge search & analysis | `apps/research/` | ✅ COMPLETE |
| Assets — image/audio/model generator | `apps/assets/` | ✅ COMPLETE |
| Deployment — release manager | `apps/deployment/` | ✅ COMPLETE |
| Sandbox — isolated experiment runner | `apps/sandbox/` | ✅ COMPLETE |
| Game Dev module | `apps/game_dev/` | ✅ COMPLETE |
| SaaS Builder module | `apps/saas_builder/` | ✅ COMPLETE |

---

## 10. Frontend Layer (`frontend/`)

| Capability | File | Status |
|---|---|---|
| Five-region Studio layout | `frontend/index.html` | ✅ COMPLETE |
| Base styles, console, pipeline monitor | `frontend/style.css` | ✅ COMPLETE |
| Module panel loader (dynamic) | `frontend/index.html` | ✅ COMPLETE |
| Real-time agent progress display (pipeline monitor) | `frontend/index.html` | ✅ COMPLETE |
| Project file browser | `frontend/index.html` | ✅ COMPLETE |
| Terminal/output panel | `frontend/index.html` | ✅ COMPLETE |

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
| Engine | 8 | 8 | 0 | 0 |
| Desktop | 4 | 4 | 0 | 0 |
| Control | 11 | 11 | 0 | 0 |
| Providers | 8 | 8 | 0 | 0 |
| Services | 10 | 10 | 0 | 0 |
| Agents | 14 | 14 | 0 | 0 |
| Knowledge | 7 | 5 | 0 | 2 |
| Bridge | 5 | 3 | 0 | 2 |
| Apps | 8 | 8 | 0 | 0 |
| Frontend | 6 | 6 | 0 | 0 |
| Config | 3 | 2 | 0 | 1 |
| Database | 8 | 0 | 0 | 8 |
| **Total** | **92** | **79** | **0** | **13** |

Overall: 86% complete, 0% scaffolded, 14% missing.
