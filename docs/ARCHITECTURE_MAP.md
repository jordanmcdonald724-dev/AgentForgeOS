# AgentForgeOS — Architecture Map

Purpose:

Provide a visual overview of how all major components of AgentForgeOS interact.

This document helps developers and AI agents understand the full system architecture before implementing code.

The architecture map acts as a high-level blueprint connecting the system layers, services, and modules.

---

# 1. System Overview

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

---

# 2. Repository Layer Map

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

---

# 3. Request Flow

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

---

# 4. AI Agent Pipeline Map

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

---

# 5. Module Interaction Map

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

---

# 6. Knowledge System Flow

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

---

# 7. Local Bridge Integration

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

---

# 8. Studio Interface Map

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

Modules render inside the Main Workspace.

---

# 9. Data Flow Map

```
Frontend UI
     │
     ▼
API Routes
     │
     ▼
Service Layer
     │
     ▼
Database
     │
     ▼
Knowledge System
```

Collections include:

projects
tasks
agents
pipeline_runs
knowledge_nodes
assets

---

# 10. System Startup Flow

```
Desktop App Launch
        │
        ▼
Backend Server Starts
        │
        ▼
Database Connects
        │
        ▼
Services Initialize
        │
        ▼
Control Layer Activates
        │
        ▼
Modules Register
        │
        ▼
Studio UI Loads
```

---

# 11. Architectural Boundaries

Agents must respect the following boundaries:

```
Engine Layer        → system runtime
Control Layer       → AI supervision
Service Layer       → system capabilities
Provider Layer      → external integrations
Apps Layer          → feature modules
```

Modules must never modify the engine layer.

---

# 12. Architecture Principles

The architecture follows these principles:

Layer Isolation
Provider Abstraction
Module Independence
Pipeline Governance
Local-First Runtime

---

# End of Architecture Map
