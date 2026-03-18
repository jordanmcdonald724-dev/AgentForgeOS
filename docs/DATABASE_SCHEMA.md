# AgentForgeOS — Database Schema

Purpose:

Define all database collections used by AgentForgeOS.

This prevents inconsistent schemas and duplicate collections.

---

# Database Engine

Recommended:

MongoDB

---

# 1. Projects

Collection:

projects

Fields:

id
name
description
created_at
updated_at

Example:

```json
{
  "id": "proj_001",
  "name": "AgentForgeOS",
  "description": "AI developer OS",
  "created_at": "timestamp"
}
```

---

# 2. Tasks

Collection:

tasks

Fields:

id
project_id
status
assigned_agent
created_at

---

# 3. Pipeline Runs

Collection:

pipeline_runs

Fields:

id
project_id
status
current_stage
logs

---

# 4. Agents

Collection:

agents

Fields:

id
name
role
status

---

# 5. Knowledge Nodes

Collection:

knowledge_nodes

Fields:

id
category
content
metadata

---

# 6. Memories

Collection:

memories

Fields:

id
agent_id
context
embedding

---

# 7. Assets

Collection:

assets

Fields:

id
type
prompt
file_path
created_at

---

# 8. Provider Config

Collection:

provider_config

Fields:

provider
api_key
enabled

---

# End of Database Schema
