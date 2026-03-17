# AgentForgeOS — System API Contracts

Purpose:

Define the standard API endpoints used by the AgentForgeOS backend.

This document ensures that frontend modules, services, and agents interact with the backend using consistent endpoints.

Agents must not invent new endpoints outside this specification.

---

# API Base Path

All endpoints must follow the structure:

/api/<module>/<action>

Example:

/api/projects/list

---

# 1. Projects API

Base route:

/api/projects

Endpoints:

GET /api/projects
Returns list of projects.

POST /api/projects
Create new project.

GET /api/projects/{project_id}
Retrieve project details.

DELETE /api/projects/{project_id}
Delete project.

Response example:

```json
{
  "id": "proj_001",
  "name": "AgentForgeOS",
  "created_at": "timestamp"
}
```

---

# 2. Builds API

Base route:

/api/builds

Endpoints:

POST /api/builds/start
Start build pipeline.

GET /api/builds/status/{build_id}
Return pipeline status.

GET /api/builds/history
Return previous builds.

Example response:

```json
{
  "build_id": "build_001",
  "status": "running",
  "stage": "backend_engineer"
}
```

---

# 3. Research API

Base route:

/api/research

Endpoints:

POST /api/research/ingest
Upload research document.

GET /api/research/query
Query knowledge graph.

GET /api/research/graph
Return knowledge graph nodes.

---

# 4. Assets API

Base route:

/api/assets

Endpoints:

POST /api/assets/image
Generate image asset.

POST /api/assets/audio
Generate audio asset.

GET /api/assets/list
Return generated assets.

---

# 5. Providers API

Base route:

/api/providers

Endpoints:

GET /api/providers/status
Return provider health.

POST /api/providers/configure
Add API keys.

Example response:

```json
{
  "llm": "connected",
  "image": "connected",
  "tts": "offline"
}
```

---

# 6. Pipeline API

Base route:

/api/pipeline

Endpoints:

POST /api/pipeline/start
Start agent pipeline.

GET /api/pipeline/status
Return pipeline progress.

GET /api/pipeline/logs
Return execution logs.

---

# 7. Bridge API

Base route:

/api/bridge

Endpoints:

GET /api/bridge/health
Check bridge status.

POST /api/bridge/sync
Sync project files.

POST /api/bridge/launch
Launch external engine.

---

# 8. Setup Wizard API

Base route:

/api/setup

Endpoints:

GET /api/setup
Return current configuration state and whether setup is complete.

POST /api/setup/save
Persist wizard-submitted values to `config/.env`. Only allow-listed keys are accepted.

POST /api/setup/reset
Remove `SETUP_COMPLETE` flag so the wizard shows again on next visit.

POST /api/setup/bootstrap
Run dependency installation (`pip install`, optional `npm install`) from the repo root.

---

# API Response Standard

All API responses must follow this structure:

```json
{
  "success": true,
  "data": {},
  "error": null
}
```

Error responses must follow:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "provider_unavailable",
    "message": "LLM provider not configured"
  }
}
```

---

# End of API Contract
