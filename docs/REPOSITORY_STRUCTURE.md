# AgentForgeOS — Repository Structure

This document defines the required repository layout.

The structure must remain consistent to maintain system stability.

## Root Structure

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
docs/

---

## Folder Descriptions

### desktop/

Desktop runtime environment using Tauri.

Responsibilities:

• start backend server
• launch frontend UI
• package desktop application

---

### engine/

Core runtime system.

Contains:

main.py
server.py
database.py
config.py
worker_system.py
module_loader.py
routes/modules.py
routes/agent.py
routes/setup.py

---

### control/

AI supervision system.

Contains:

ai_router.py
file_guard.py
agent_supervisor.py
permission_matrix.yaml

---

### services/

Internal system services.

Examples:

agent_service.py
memory_manager.py
mongo_memory.py
vector_store.py
knowledge_graph.py
embedding_service.py
pattern_extractor.py
project_genome_service.py
autopsy_service.py
agent_pipeline.py
agent_registry.py

---

### providers/

External AI integrations.

Examples:

llm_provider.py
image_provider.py
tts_provider.py

Provider implementations:

fal_provider.py
openai_provider.py
ollama_provider.py

---

### apps/

Feature modules.

Examples:

studio/
builds/
research/
assets/
deployment/

Phase 8 scaffold creates these directories as placeholders for future implementation.

---

### bridge/

Local system integration.

Contains:

bridge_server.py
bridge_security.py

Handles:

• file access
• launching engines
• local automation

---

### knowledge/

AI learning system.

Contains:

knowledge_graph
vector_store
embedding_service
pattern_extractor
project_genome

Phase 7 provides in-memory scaffolds for these components.

---

### config/

System configuration.

Contains:

.env.example
settings.json

---

### frontend/

Developer interface.

Recommended stack:

React + Vite

Responsibilities:

• Studio UI
• pipeline monitoring
• project management
• static scaffold lives at frontend/index.html + frontend/style.css following docs/UI_STUDIO_LAYOUT.md

---

### docs/

System documentation.

Contains all architecture specifications.
