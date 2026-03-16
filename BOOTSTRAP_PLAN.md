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

---

## Phase 5 — Agent System

Implement AI orchestration.

agents/
control/

---

## Phase 6 — Studio Interface

Implement frontend workspace.

frontend/

---

## Phase 7 — Knowledge System

Implement learning system.

knowledge/

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
