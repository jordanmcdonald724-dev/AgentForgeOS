# AgentForgeOS — System Architecture

This document defines the architectural layers of AgentForgeOS.

The system follows a strict layered architecture to prevent architectural drift and uncontrolled AI modifications.

## Core Layers

AgentForgeOS is composed of four primary layers:

Engine Layer
Control Layer
Services Layer
Apps Layer

Each layer has strict responsibilities.

---

## Engine Layer

Location:

engine/

Responsibilities:

• FastAPI runtime
• database initialization
• configuration loading
• background worker orchestration

Files:

main.py
server.py
config.py
database.py
worker_system.py

Rules:

• Engine must not depend on providers
• Engine must not depend on apps
• Engine must remain stable and rarely modified

---

## Control Layer

Location:

control/

Purpose:

Prevent uncontrolled AI modifications.

Components:

ai_router.py
file_guard.py
agent_supervisor.py
permission_matrix.yaml

Responsibilities:

• classify AI tasks
• enforce edit permissions
• supervise multi-agent workflows

Protected directories:

engine/
services/
providers/
control/

AI agents may not modify these directories.

---

## Services Layer

Location:

services/

Purpose:

Provide internal system functionality.

Examples:

agent_service.py
memory_manager.py
knowledge_graph.py
vector_store.py
embedding_service.py
pattern_extractor.py
project_genome_service.py
autopsy_service.py

Responsibilities:

• agent orchestration
• system knowledge
• embeddings and vector search
• pattern analysis

Phase 4 scaffolding provides lightweight, in-memory implementations of these services so downstream layers can integrate without external dependencies.

Services may depend on:

engine/
providers/
knowledge/

---

## Knowledge Layer

Location:

knowledge/

Purpose:

Provide persistent learning utilities for agents.

Components:

knowledge_graph.py
vector_store.py
embedding_service.py
pattern_extractor.py
project_genome.py

Notes:

Phase 7 scaffolding offers in-memory placeholders so services and apps can integrate without external databases or vector backends.

---

## Apps Layer

Location:

apps/

Purpose:

Contain all user-facing modules.

Examples:

studio/
builds/
research/
assets/
deployment/
sandbox/
game_dev/
saas_builder/

Apps may depend on:

services/
providers/

Apps must not depend on engine internals.

---

## Frontend / Studio Interface

Location:

frontend/

Purpose:

Render the Studio UI following the five-region layout defined in docs/UI_STUDIO_LAYOUT.md.

Notes:

• Phase 6 scaffold lives in frontend/index.html and frontend/style.css as a static mock of the required layout.  
• Interactive behavior can layer on top of this scaffold using the recommended frontend stack (e.g., React + Vite).

---

## Architecture Rules

1. Engine is the stable kernel.
2. Control layer protects the architecture.
3. Services implement internal capabilities.
4. Apps implement features.
5. Providers integrate external AI systems.
