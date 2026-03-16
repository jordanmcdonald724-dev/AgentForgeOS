# AgentForgeOS — Master System Specification

Version: 1.0
Author: System Architecture Blueprint
Purpose: Define the architecture and rules for building AgentForgeOS as a stable local developer operating system.

---

# 1. Overview

AgentForgeOS is a **local-first developer operating system** designed to orchestrate AI agents, build software systems, manage projects, and integrate with local tools such as game engines and compilers.

The system must run entirely on a developer's machine and should not require cloud infrastructure to function.

External AI services are optional modules.

Primary goals:

• modular architecture
• local-first runtime
• replaceable AI providers
• safe autonomous agent workflows
• extensible development modules

---

# 2. Core Principles

The system must follow these principles:

1. **Layered Architecture**

   * Each layer has strict responsibilities.

2. **Provider Abstraction**

   * No module may directly call external AI APIs.

3. **Local First**

   * The system must function with no external services enabled.

4. **AI Safety**

   * Agents cannot modify protected system layers.

5. **Modularity**

   * Features are implemented as apps/modules.

---

# 3. System Architecture

The repository structure must follow this layout:

```
AgentForgeOS/

desktop/
engine/
control/
services/
providers/
apps/
bridge/
knowledge/
config/
frontend/
```

Each folder represents a specific system layer.

---

# 4. Desktop Layer

Location:

```
desktop/
```

Purpose:

Provide a local desktop runtime for AgentForgeOS.

Recommended technology:

Tauri

Responsibilities:

• launch frontend interface
• start backend server
• package the system into an installable application

Example result:

```
AgentForgeOS.exe
```

---

# 5. Engine Layer

Location:

```
engine/
```

Purpose:

Provide the core runtime engine for the system.

Files:

```
main.py
server.py
config.py
database.py
worker_system.py
```

Responsibilities:

• start FastAPI server
• initialize database
• register API routes
• manage background task workers
• load configuration

Restrictions:

The engine must never depend on:

```
providers/
apps/
```

---

# 6. Control Layer

Location:

```
control/
```

Purpose:

Prevent uncontrolled AI modifications.

Files:

```
ai_router.py
file_guard.py
agent_supervisor.py
permission_matrix.yaml
```

Responsibilities:

• classify AI tasks
• enforce repository edit permissions
• supervise multi-agent workflows
• prevent architecture drift

Protected directories:

```
engine/
services/
providers/
control/
```

AI agents must never modify these directories.

---

# 7. Services Layer

Location:

```
services/
```

Purpose:

Provide internal infrastructure used by applications.

Files:

```
agent_service.py
memory_manager.py
knowledge_graph.py
vector_store.py
embedding_service.py
pattern_extractor.py
project_genome_service.py
autopsy_service.py
```

Responsibilities:

• manage AI agents
• store and retrieve knowledge
• handle embeddings and vector search
• detect development patterns
• analyze projects and failures

Phase 4 scaffolding includes lightweight, in-memory versions of these services so later phases can integrate against stable interfaces before full persistence is introduced.

Services may depend on:

```
engine/
providers/
knowledge/
```

---

# 8. Provider Layer

Location:

```
providers/
```

Purpose:

Integrate external AI services through standardized interfaces.

Interfaces:

```
llm_provider.py
image_provider.py
tts_provider.py
```

Each interface defines the required API.

Example:

```
LLMProvider.chat()
ImageProvider.generate()
TTSProvider.speak()
```

Provider implementations may include:

```
FalProvider
OpenAIProvider
OllamaProvider
ComfyUIProvider
PiperProvider
```

The rest of the system must never call external APIs directly.

---

# 9. Apps Layer

Location:

```
apps/
```

Purpose:

Implement user-facing features.

Each module must be isolated.

Example modules:

```
studio/
builds/
research/
assets/
deployment/
sandbox/
game_dev/
saas_builder/
```

Rules:

Apps may depend on:

```
services/
providers/
```

Apps must never depend on:

```
engine internals
```

---

# 10. Bridge Layer

Location:

```
bridge/
```

Purpose:

Enable interaction with the local machine.

Files:

```
bridge_server.py
bridge_security.py
```

Capabilities:

• filesystem access
• launching local tools
• engine integration
• secure local communication

Example endpoints:

```
/bridge/sync
/bridge/launch
/bridge/health
```

---

# 11. Knowledge Layer

Location:

```
knowledge/
```

Purpose:

Provide persistent AI memory and learning capabilities.

Components:

```
knowledge_graph
vector_store
embedding_service
pattern_extractor
project_genome
```

Capabilities:

• store development patterns
• analyze project failures
• build long-term memory
• assist agent decision-making

Bootstrap status:

• Phase 7 adds in-memory scaffolds for the knowledge components (knowledge_graph, vector_store, embedding_service, pattern_extractor, project_genome) to keep downstream integrations unblocked while persistent storage is designed.

---

# 12. Configuration Layer

Location:

```
config/
```

Purpose:

Store system configuration.

Files:

```
.env
settings.json
```

Configuration includes:

• database connection
• provider API keys
• bridge settings
• system flags

The system must start even if provider keys are absent.

---

# 13. Frontend Layer

Location:

```
frontend/
```

Purpose:

Provide the developer interface.

Recommended stack:

```
React + Vite
```

Features:

• studio dashboard
• project management UI
• pipeline monitoring
• research dashboard
• module management

Bootstrap status:

• Phase 6 provides a static Studio scaffold in frontend/index.html and frontend/style.css that follows docs/UI_STUDIO_LAYOUT.md so downstream work can attach interactive components without breaking the required five-region layout.

---

# 14. Multi-Agent Development System

AgentForgeOS includes a coordinated AI team.

Agents operate through the Control Layer.

Core agents:

1. Project Planner
2. System Architect
3. Task Router
4. Module Builder
5. API Architect
6. Data Architect
7. Backend Engineer
8. Frontend Engineer
9. AI Integration Engineer
10. Integration Tester
11. Security Auditor
12. System Stabilizer

Agents produce artifacts which are validated before code is modified.

---

# 15. Development Workflow

Typical workflow:

1. User request
2. Planner generates project plan
3. Architect designs system
4. Router creates tasks
5. Production agents generate modules
6. Validation agents test results
7. Control layer approves changes

---

# 16. System Startup

Startup sequence:

1. Desktop runtime launches
2. Engine server starts
3. Database initializes
4. Services load
5. Control layer activates
6. Apps register
7. UI becomes available

---

# 17. Future Expansion

Future modules may include:

```
ai_training/
robotics/
hardware_control/
simulation/
```

These modules must follow the architecture rules defined in this document.

---

# 18. Governance Rules

All contributors and AI agents must follow:

• no direct modification of protected layers
• provider calls must go through providers/
• apps must remain modular
• services must remain provider-agnostic

---

# 19. Validation

The system is considered functional when:

• backend server runs locally
• frontend loads successfully
• bridge connects to local tools
• provider modules load dynamically
• apps can be enabled or disabled independently

---

# End of Specification
