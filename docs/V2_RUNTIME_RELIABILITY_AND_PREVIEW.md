# AgentForge V2 Runtime Reliability & Live Preview

This document describes how the V2 orchestration runtime, agents, and frontend should work together to provide **deterministic, inspectable builds** and a **live "emergent" preview** of what the system is doing.

It builds on:
- V2 build structure in `archive/BUILD_BIBLE_V2.md`
- Role definitions in `V2_EXECUTION_MODEL.md` (Agent Roles section)
- Execution rules in `V2_EXECUTION_MODEL.md`

---
## 1. Execution Contracts (Runtime Core)

### 1.1 Task model & declared outputs

Core model: `orchestration.task_model.Task`

Key fields:
- `task_id: str` – stable identifier.
- `assigned_agent: str` – one of the 12 role names.
- `inputs: dict` – immutable input payload for the agent, MUST include `project_root` for build tasks.
- `outputs: dict` – outputs returned by the agent at runtime.
- `dependencies: list[str]` – upstream task IDs.
- `status: TaskStatus` – `pending|ready|running|completed|failed|blocked`.
- `declared_outputs: list[str]` – **contract**: absolute or project-root-relative paths that MUST exist on disk when the task is "done".

Enforcement:
- `OrchestrationEngine.verify_outputs(task_id)` checks all `declared_outputs`.
- If any are missing, the task is marked `FAILED` and `missing_outputs` is recorded in `task.outputs`.
- `OrchestrationRuntime.step()` always calls `verify_outputs` after a non-Analyst task completes, and explicitly after Analyst’s `mark_simulation_result`.

### 1.2 Default project root

- Constant: `DEFAULT_PROJECT_ROOT = Path("projects") / "session_default"` in `orchestration.engine`.
- All tasks in the default command graph receive `inputs["project_root"] = str(DEFAULT_PROJECT_ROOT)`.
- All V2 agents default to this root when no explicit project root is provided.

This ensures every build has a **single, deterministic filesystem home**.

### 1.3 Agent artifact contracts (central mapping)

Helper: `get_default_declared_outputs(agent: str, project_root: Path) -> list[str>` in `orchestration.engine`.

This function encodes the **artifact responsibilities** for each role:

- **Origin** – intent & planning
  - `intent.json`
  - `task_graph.json`
  - `build_plan.json`

- **Architect** – system design
  - `architecture.json`
  - `modules.json`
  - `interfaces.json`
  - `data_models.json`

- **Analyst** – simulation & test summary
  - `tests/test_results.json`
  - `tests/performance_metrics.json`
  - `tests/failure_report.json`

- **Builder** – backend & systems scaffold
  - `backend/app.py`
  - `backend/routes.py`
  - `backend/`
  - `gameplay/`
  - `systems/`
  - `scripts/`

- **Surface** – per-project UI
  - `frontend/src/pages/CommandCenter.tsx`
  - `frontend/src/pages/ProjectWorkspace.tsx`
  - `frontend/src/pages/ResearchLab.tsx`
  - `frontend/src/components/AppShell.tsx`

- **Core** – per-project backend API/services/models
  - `backend/api/routes.py`
  - `backend/services/project_service.py`
  - `backend/models/project.py`

- **Simulator** – engine hooks
  - `unity/AgentForgeBootstrap.cs`
  - `unreal/AgentForgeBootstrap.cpp`
  - `engine_scripts/engine_bridge.md`

- **Synapse** – model routing
  - `model_routes.json`
  - `inference_logs.json`

- **Fabricator** – asset bundles
  - `assets/asset_manifest.json`
  - `assets/ui/core_ui_manifest.md`
  - `assets/audio/core_audio_manifest.md`

- **Guardian** – validation & security
  - `reports/validation_report.json`
  - `reports/security_report.json`
  - `reports/issues.json`

- **Launcher** – deployment plan & env
  - `deploy/deployment_plan.json`
  - `deploy/logs/build.log`
  - `deploy/env/environment.json`

- **Archivist** – research
  - `research/research_insights.json`
  - `research/patterns.json`
  - `research/extracted_systems.json`

A dedicated test (`tests/test_v2_agent_declared_outputs.py`) asserts that every agent in the registry has a non-empty mapping here.

### 1.4 Default command task graph

`OrchestrationEngine.create_command_task_graph(command: str)` builds an initial, linear task chain using the 12 roles:

1. `cmd:root` → **Origin**
   - Inputs: `{ "command": command, "project_root": DEFAULT_PROJECT_ROOT }`
   - Declares Origin’s three planning artifacts.
2. `cmd:simulate` → **Analyst**
   - Depends on `cmd:root`.
   - Declares the three test result files.
   - Uses `SimulationEngine` to compute feasibility.
3. `cmd:plan` → **Architect**
   - Depends on `cmd:simulate`.
   - Declares the four architecture artifacts.
4. `cmd:build` → **Builder**
   - Depends on `cmd:plan`.
   - Declares backend + gameplay + systems structure.
5. `cmd:guard` → **Guardian**
   - Depends on `cmd:build`.
   - Declares validation/security/issue reports.
6. `cmd:launch` → **Launcher**
   - Depends on `cmd:guard`.
   - Declares deployment plan, build log, environment descriptor.

Simulation gating:
- Analyst’s result is used by `mark_simulation_result()`.
- If feasibility is not approved, **all Builder and Launcher tasks are marked BLOCKED**.

All of these tasks are verified via `verify_outputs()` after they run.

### 1.5 Origin’s AAA task graph loader

Origin writes a richer AAA-style graph to `task_graph.json`:
- Nodes t0–t6 with `task_id`, `agent`, `name`, `dependencies`.

Helper: `OrchestrationEngine.create_tasks_from_origin_graph(project_root)`
- Loads `task_graph.json` from the given project.
- For each node:
  - Creates a Task with:
    - `task_id`, `assigned_agent`, `name`, `dependencies`.
    - `inputs = {"project_root": project_root}`.
    - `declared_outputs = get_default_declared_outputs(agent, project_root)`.
  - Skips any `task_id` already present in `engine.tasks`.
- Returns the list of Tasks it created.

A test (`tests/test_v2_origin_task_graph_loader.py`) verifies:
- Origin writes `task_graph.json`.
- Tasks t0–t6 can be instantiated.
- Every instantiated task has non-empty `declared_outputs` under the project root.

> NOTE: As of now, the default runtime uses the `cmd:*` tasks as the primary execution graph. The AAA graph loader is ready and tested but not yet wired into the main run loop.

---
## 2. Reliability & No-Drift Guarantees

### 2.1 Deterministic filesystem contracts

- For each role, the combination of:
  - `project_root` input,
  - `get_default_declared_outputs`, and
  - `verify_outputs`

  means the system **either**:
  - Produces the exact expected artifacts for that task, **or**
  - Marks the task as `FAILED` and lists missing paths.

There is no "silent" success – every task must fulfill its declared contract.

### 2.2 Idempotent agent behavior (design rule)

Agents must follow this rule:
- Given the same `project_root` and inputs, running `handle_task()` multiple times **must not corrupt or randomly mutate** artifacts.
- Current implementations follow a pattern:
  - Create directories if missing.
  - Create files if missing.
  - If files exist, either leave them untouched or keep behavior trivial.

Additional tests can be added to enforce idempotency per agent (call twice, assert structure and critical contents are stable).

### 2.3 Project health checks (planned)

Design for a `validate_project(project_root)` helper and API:
- Load all known artifacts for that project.
- Validate presence via `declared_outputs`.
- (Future) Validate shape via schemas (Pydantic/dataclasses) for key JSON files.
- Return a `project_status.json` summary, e.g.:
  - `{"ok": true, "failed_tasks": [], "missing_artifacts": []}`
  - or with detailed reasons when invalid.

This makes it possible to ask **"Is this project in a good, consistent state?"** and get a single, deterministic answer.

### 2.4 Spec freeze / evolution (planned)

To avoid mid-session drift:
- Once a project has a valid `intent.json` and `architecture.json`, changes to high-level spec should:
  - either create a **new version** (v2) of those artifacts, or
  - be rejected by the runtime unless explicitly allowed.

This can be enforced by:
- Recording a `spec_version` in `intent.json`.
- Adding rules that Origin/Architect must bump the version when making incompatible changes.

---
## 3. Project Status & Live Build Preview

This section ties the runtime contracts into the "emergent style" UI you described.

### 3.1 Backend project status API (design)

Proposed endpoint:
- `GET /api/v2/projects/{project_id}/status`

Behavior:
- Resolve the project root (e.g. `projects/{project_id}`).
- Introspect the orchestration engine and filesystem to return:

```jsonc
{
  "project_id": "{project_id}",
  "tasks": [
    {
      "task_id": "cmd:root",
      "agent": "Origin",
      "status": "completed | failed | blocked | pending | running",
      "dependencies": ["..."],
      "declared_outputs": ["..."],
      "missing_outputs": ["..."],  // only when failed
      "phase": "planning | building | testing | validation | launch",
      "name": "interpret command"
    },
    // ... all other tasks, including AAA tasks if loaded
  ],
  "artifact_index": {
    "intent": true,
    "architecture": true,
    "tests": {
      "results": true,
      "performance": true,
      "failures": true
    },
    "reports": {
      "validation": true,
      "security": true
    },
    "deploy": {
      "plan": true,
      "build_log": true
    }
  }
}
```

Implementation notes:
- `tasks` can be built from `engine.list_tasks()` plus `verify_outputs` results.
- `artifact_index` can be a thin wrapper over `get_default_declared_outputs` + filesystem checks.
- For "real-time" feel, the frontend can either poll this endpoint or, later, subscribe via WebSocket.

### 3.2 Command Center integration (BUILD_BIBLE_V2 alignment)

`archive/BUILD_BIBLE_V2.md` already defines PAGE 1: COMMAND CENTER with:
- Required subareas:
  - command input
  - simulation report
  - agent activity
  - build queue
  - task graph / architecture preview
  - **live execution status**

This status API plus the existing orchestration contracts give that page a **real, deterministic data source**:

- Command input → calls existing `/api/v2/command/preview` (already implemented & tested).
- Simulation report → uses Analyst outputs and feasibility data from the preview/engine.
- Task graph / architecture preview → uses either:
  - `create_command_task_graph` outputs, or
  - AAA graph loaded via `create_tasks_from_origin_graph`.
- Build queue & agent activity → use `tasks` with statuses from `/projects/{id}/status`.
- Live execution status → use `tasks` + `artifact_index` to show which artifacts are present and which tasks are blocked/failed.

### 3.3 Emergent-style "live build" UI behavior

On the frontend (Command Center page), the emergent preview can be structured as:

- **Left column – Task/agent view**
  - List or graph of tasks with:
    - Name, agent, status icon, phase.
    - Hover or click to see declared vs actual outputs.

- **Middle column – Artifacts & project tree**
  - Tree derived from `artifact_index` + known patterns:
    - Planning (intent, task_graph, build_plan).
    - Architecture.
    - Code/scaffolds.
    - Tests & reports.
    - Deploy outputs.
  - Clicking a file:
    - Loads and pretty-prints JSON.
    - Renders markdown (reports, manifests) when appropriate.
    - Shows code snippets for Python/TS files.

- **Right column – Details/logs**
  - For selected task:
    - Show its inputs (sanitized).
    - Show outputs summary (from `Task.outputs`).
    - Show any `missing_outputs` or errors.
    - Show associated logs from the agent.

Because this UI is powered by the runtime’s own contracts and status checks, it **cannot drift into fantasy**: it’s always reflecting the actual tasks, statuses, and artifacts on disk.

---
## 4. Next Reliability Enhancements (Future Work)

The current V2 runtime already:
- Defines deterministic task contracts and declared outputs for all 12 roles.
- Enforces artifact existence after task completion.
- Provides utilities to load Origin’s task_graph.json into executable Tasks.
- Has tests covering agent registry, contracts, orchestration flow, and the AAA graph loader.

Future tightening steps that fit this document:

1. **Schema validation** for key JSON artifacts via Pydantic/dataclasses.
2. **Project health API**: `GET /api/v2/projects/{id}/validate` that runs `validate_project` and returns a `project_status.json`.
3. **Idempotency tests** for each agent.
4. **Spec versioning** in `intent.json` / `architecture.json` with enforcement in Origin/Architect.
5. **Wire AAA graph into runtime** (optional mode): use `create_tasks_from_origin_graph` so the Origin-defined t0–t6 graph drives execution instead of only `cmd:*` tasks.

These additions will further reduce guesswork and make every build step and artifact traceable, explainable, and checkable from both backend and UI.
