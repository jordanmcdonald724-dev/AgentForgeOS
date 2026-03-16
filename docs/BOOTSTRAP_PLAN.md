# AgentForgeOS — Bootstrap Plan

This document defines the order in which the system must be built.

The build must follow these phases.

---

## Phase 1 — Engine

Create:

engine/main.py
engine/server.py
engine/database.py
engine/config.py

Verify backend server starts.

---

## Phase 2 — Desktop Runtime

Create Tauri wrapper.

desktop/

Verify the application launches locally.

---

## Phase 3 — Provider System

Create provider interfaces.

providers/llm_provider.py
providers/image_provider.py
providers/tts_provider.py

---

## Phase 4 — Services Layer

Implement core services.

services/agent_service.py
services/memory_manager.py
services/vector_store.py
services/knowledge_graph.py
services/embedding_service.py
services/pattern_extractor.py
services/project_genome_service.py
services/autopsy_service.py

---

## Phase 5 — Agent System

Implement AI orchestration.

agents/
control/

---

## Phase 6 — Studio Interface

Implement frontend workspace.

frontend/
frontend/index.html
frontend/style.css
Follow layout in docs/UI_STUDIO_LAYOUT.md for the five-region studio scaffold.

---

## Phase 7 — Knowledge System

Implement learning system.

knowledge/
knowledge/knowledge_graph.py
knowledge/vector_store.py
knowledge/embedding_service.py
knowledge/pattern_extractor.py
knowledge/project_genome.py

---

## Phase 8 — Applications

Implement modules.

apps/studio
apps/builds
apps/research
apps/assets
apps/deployment

---

## Phase 9 — Final Integration

Validate:

• backend server runs
• frontend loads
• agents execute tasks
• providers load correctly
