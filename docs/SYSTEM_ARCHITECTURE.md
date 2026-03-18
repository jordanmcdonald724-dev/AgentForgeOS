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

---

## High-Level Architecture Map

The following map provides a visual overview of how major components interact.

### 1. System Overview

AgentForgeOS is structured as a layered development operating system.

High-level structure:

```
┌─────────────────────────────────────────┐
│               Desktop App               │
│              (Tauri Runtime)            │
└─────────────────────────────────────────┘
			  │
			  ▼
┌─────────────────────────────────────────┐
│               Frontend UI               │
│        (Studio Multi-Pane Interface)    │
└─────────────────────────────────────────┘
			  │
			  ▼
┌─────────────────────────────────────────┐
│              API Gateway                │
│             FastAPI Backend             │
└─────────────────────────────────────────┘
			  │
			  ▼
┌─────────────────────────────────────────┐
│             Control Layer               │
│      AI Supervision + Safety System     │
└─────────────────────────────────────────┘
			  │
			  ▼
┌─────────────────────────────────────────┐
│              Service Layer              │
│      Knowledge, Agents, Memory, Tasks   │
└─────────────────────────────────────────┘
			  │
			  ▼
┌─────────────────────────────────────────┐
│             Provider Layer              │
│     LLM / Image / TTS / Embeddings      │
└─────────────────────────────────────────┘
			  │
			  ▼
┌─────────────────────────────────────────┐
│             Local Bridge                │
│   File System / Game Engines / Tools    │
└─────────────────────────────────────────┘
```

### 2. Repository Layer Map

```
AgentForgeOS/

desktop/        → Desktop runtime (Tauri)

frontend/       → Studio interface

engine/         → FastAPI server runtime

control/        → AI supervision system

services/       → Internal system capabilities

providers/      → External AI integrations

apps/           → Feature modules

bridge/         → Local machine control

knowledge/      → AI learning system

config/         → environment configuration

docs/           → system specifications
```

### 3. Request Flow

Typical system request flow:

```
User Action
   │
   ▼
Frontend UI
   │
   ▼
FastAPI Backend
   │
   ▼
Control Layer
   │
   ▼
Service Layer
   │
   ▼
Provider Layer (optional)
   │
   ▼
Response returned to UI
```

Example:

User asks AI to generate a module.

```
User Prompt
 → Agent Console
 → Pipeline Start
 → Planner Agent
 → Architect Agent
 → Builder Agents
 → Validation Agents
 → Code Commit
```

### 4. AI Agent Pipeline Map

```
User Request
	│
	▼
Project Planner
	│
	▼
System Architect
	│
	▼
Task Router
	│
	▼
Production Agents
  ├ Backend Engineer
  ├ Frontend Engineer
  └ AI Integration Engineer
	│
	▼
Validation Agents
  ├ Integration Tester
  ├ Security Auditor
  └ System Stabilizer
	│
	▼
Approved Code Changes
```

The Control Layer supervises every stage.

### 5. Module Interaction Map

All modules integrate through the services layer.

```
Studio Module
	  │
	  ▼
Service Layer
	  │
	  ├ Agent Service
	  ├ Memory Manager
	  ├ Knowledge Graph
	  └ Vector Store
	  │
	  ▼
Providers
	  │
	  ▼
External AI Systems
```

Modules never access providers directly.

### 6. Knowledge System Flow

```
Agent Action
     │
     ▼
Embedding Service
     │
     ▼
Vector Store
     │
     ▼
Knowledge Graph
     │
     ▼
Agent Memory Retrieval
```

This enables learning from:

• previous projects  
• bug patterns  
• architecture patterns

### 7. Local Bridge Integration

The bridge allows AgentForgeOS to interact with the host system.

```
AgentForgeOS
	│
	▼
Bridge API
	│
	▼
Local Bridge Server
	│
	▼
System Operations
  ├ File writing
  ├ Project syncing
  ├ Launch Unreal/Unity
  └ Tool automation
```

### 8. Studio Interface Map

```
┌──────────────────────────────────────────────┐
│ Top Navigation Bar                           │
├──────────────┬───────────────────────────────┤
│ Sidebar      │ Main Workspace                │
│              │                               │
│ Modules      │ Panels / Editors              │
│              │                               │
├──────────────┼───────────────────────────────┤
│ Agent Console│ Pipeline Monitor              │
└──────────────┴───────────────────────────────┘
```
