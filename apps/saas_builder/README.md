# SaaS Builder Module

End-to-end SaaS project scaffolding and management for AgentForgeOS.

AI-driven scaffolding of full-stack SaaS applications: database schema generation, API design, auth flow setup, billing integration planning, and deployment configuration.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/modules/saas_builder/status` | Module health check |
| POST | `/api/modules/saas_builder/scaffold` | Scaffold a new SaaS project |
| GET | `/api/modules/saas_builder/projects` | List scaffolded projects |
| POST | `/api/modules/saas_builder/projects/{id}/feature` | Add a feature to a project |
