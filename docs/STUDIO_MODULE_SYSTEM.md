# AgentForgeOS — Studio Module System

Purpose:

Define how feature modules integrate with the AgentForgeOS Studio environment.

This document ensures that all modules follow a consistent structure and integrate safely with the core system.

Modules are the primary way functionality is added to AgentForgeOS.

---

# 1. What Is a Module

A module is an isolated application component that extends AgentForgeOS.

Modules provide specific development capabilities while remaining independent from the core engine.

Examples:

studio
builds
research
assets
deployment
sandbox
game_dev
saas_builder

Modules must integrate with the Studio interface and the system services layer.

---

# 2. Module Location

All modules must live inside the apps directory.

Repository structure:

```text
apps/
    studio/
    builds/
    research/
    assets/
    deployment/
    sandbox/
    game_dev/
    saas_builder/
```

Each module must have its own directory.

Modules must never exist outside this directory.

---

# 3. Module Structure

Every module must follow the same internal structure.

Example:

```text
apps/module_name/

backend/
frontend/
module_config.json
README.md
```

Explanation:

backend/ — API routes and service integrations
frontend/ — UI components rendered in the Studio workspace
module_config.json — module metadata and registration
README.md — module documentation

---

# 4. Module Configuration

Each module must include a module configuration file.

Example file:

module_config.json

Example content:

```json
{
  "name": "research",
  "version": "1.0",
  "display_name": "Research",
  "icon": "brain",
  "entry_route": "/api/research",
  "ui_entry": "ResearchPanel",
  "enabled": true
}
```

Fields:

name — module identifier
version — module version
display_name — name shown in sidebar
icon — sidebar icon
entry_route — backend API entry
ui_entry — frontend panel entry component
enabled — module enabled state

---

# 5. Backend Integration

Backend code must live inside:

```text
apps/module_name/backend/
```

Typical structure:

```text
backend/

routes.py
services.py
models.py
```

Routes must be registered through the engine server.

Example:

```python
app.include_router(research_router, prefix="/api/research")
```

Modules must not modify engine code directly.

---

# 6. Frontend Integration

Frontend UI components live inside:

```text
apps/module_name/frontend/
```

Typical structure:

```text
frontend/

ResearchPanel.jsx
components/
hooks/
styles/
```

The module's UI must render inside the **Main Workspace panel**.

Modules must not modify the base layout.

---

# 7. Studio Registration

Modules must register themselves with the Studio.

Example registration entry:

```javascript
registerModule({
  name: "research",
  displayName: "Research",
  icon: "brain",
  component: ResearchPanel
})
```

Once registered, the module appears in the left sidebar.

---

# 8. Sidebar Integration

Modules automatically appear in the Studio sidebar.

Example sidebar list:

Studio
Build Pipelines
Research
Assets
Deployment
Sandbox
Game Dev
SaaS Builder

Modules may define custom icons.

Modules must not modify sidebar structure.

---

# 9. Module Lifecycle

Modules follow a simple lifecycle.

Startup

• module configuration loaded
• backend routes registered
• frontend component registered

Activation

• module selected from sidebar
• UI panel rendered

Runtime

• module interacts with services
• module may call providers

Shutdown

• module state saved

---

# 10. Service Access

Modules interact with system services.

Allowed services:

agent_service
memory_manager
knowledge_graph
vector_store
embedding_service

Example usage:

```python
knowledge_graph.add_node(...)
```

Modules must not modify service implementations.

---

# 11. Provider Access

Modules may use external AI providers through the provider layer.

Example:

```python
llm_provider.chat(...)
image_provider.generate(...)
```

Modules must never call external APIs directly.

---

# 12. Module Isolation Rules

Modules must follow these isolation rules.

Modules may not modify:

engine/
control/
providers/
services/

Modules may only modify their own directory.

---

# 13. Module Permissions

Modules must follow permission policies defined by the Control Layer.

Example:

code_generation modules may edit apps directory.

Modules cannot modify protected system layers.

---

# 14. Example Module

Example:

Research module.

Structure:

```text
apps/research/

backend/
    routes.py
    services.py

frontend/
    ResearchPanel.jsx
    components/

module_config.json
README.md
```

This module provides:

• document ingestion
• knowledge graph browsing
• research agent tools

---

# 15. Future Modules

AgentForgeOS supports future module expansion.

Possible modules:

ai_training
robotics
simulation
hardware_control
data_science

New modules must follow the same module structure.

---

# 16. Module Validation

Modules must pass the following checks.

Backend routes load successfully
Frontend component renders inside Studio workspace
Module configuration file is valid
Module does not modify protected directories

---

# End of Module System Specification
