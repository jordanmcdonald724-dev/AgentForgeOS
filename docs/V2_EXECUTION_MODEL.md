# AgentForge V2 Execution Model

> Deterministic task-graph execution model (real OS, not a simulator).
> Source: user specification provided on March 17, 2026.

No fluff. No simulation language.
This is deterministic task graph execution.

---

## Core Idea (Locked)

The system does not "run agents".
The system executes tasks in a dependency graph, where each task:

- is assigned to exactly **one** agent
- has required inputs
- produces required artifacts
- unlocks downstream tasks

---

## 1. Task Graph = Execution Plan

Every project becomes:

```json
{
  "tasks": [],
  "artifacts": [],
  "state": "pending | running | blocked | complete | failed"
}
```

### Task Object (Final Form — Do Not Change)

```json
{
  "task_id": "t2.14",
  "agent": "builder",
  "phase": "production",
  "name": "implement projectile system",
  "inputs": {
    "architecture": "path",
    "module_spec": "path"
  },
  "dependencies": ["t2.11", "t2.12"],
  "outputs": [
    "/project/systems/combat/projectile.py"
  ],
  "status": "pending"
}
```

---

## 2. Execution States

Every task **must** be in one of:

| State    | Meaning              |
|----------|----------------------|
| pending  | waiting              |
| ready    | dependencies satisfied |
| running  | currently executing  |
| complete | outputs verified     |
| failed   | execution error      |
| blocked  | waiting on failed dependency |

---

## 3. Execution Loop (Real Engine)

This is the system heartbeat:

```python
while not all_tasks_complete:

    ready_tasks = find_tasks_with_status("ready")

    for task in ready_tasks:
        execute(task)

    update_task_states()
```

---

## 4. How a Task Becomes "Ready"

A task becomes ready **only if**:

```python
all(dep.status == "complete" for dep in task.dependencies)
```

**and**

```python
all(required_inputs_exist(task.inputs))
```

---

## 5. Task Execution (Real Core)

When executing a task:

```python
def execute(task):

    task.status = "running"

    agent = get_agent(task.agent)

    result = agent.run({
        "inputs": load_inputs(task.inputs),
        "context": project_context
    })

    save_outputs(result.outputs)

    verify_outputs(task.outputs)

    task.status = "complete"
```

---

## 6. Output Verification (Critical)

After execution:

```python
for path in task.outputs:
    if not file_exists(path):
        task.status = "failed"
```

- If output doesn’t exist → task **failed**.
- No exceptions.

---

## 7. Failure Handling

If a task fails:

```python
task.status = "failed"
```

Then:

```python
for dependent in downstream_tasks:
    dependent.status = "blocked"
```

---

## 8. Recursive Loop Integration

The loop is **not** separate — it’s built into the graph.

Example:

```text
[
  "t1_plan",
  "t2_build",
  "t3_test",
  "t4_review",
  "t5_refine",
  "t6_rebuild"
]
```

If:

- test fails → triggers refine
- refine modifies architecture → rebuild tasks regenerate

---

## 9. Real AAA Flow (Connected Graph)

Example simplified chain:

- `t0` → Origin → `intent.json`
- `t1` → Architect → `architecture.json`  
  depends on `t0`
- `t2` → Builder → backend code  
  depends on `t1`
- `t3` → Surface → UI  
  depends on `t1`
- `t4` → Analyst → `test_results.json`  
  depends on `t2`, `t3`
- `t5` → Guardian → `validation.json`  
  depends on `t4`
- `t6` → Launcher → build output  
  depends on `t5`

---

## 10. Artifact Registry (Global Tracking)

Every output must be registered:

```json
{
  "artifact_id": "a_001",
  "path": "/project/backend/routes.py",
  "created_by": "t2",
  "agent": "builder"
}
```

---

## 11. Project State Machine

Whole project state:

| State       | Meaning          |
|-------------|------------------|
| initializing| parsing command  |
| planning    | architecture phase |
| building    | production       |
| testing     | validation       |
| refining    | iteration        |
| deploying   | final build      |
| complete    | finished         |
| failed      | unrecoverable    |

---

## 12. Execution Rules (Non-Negotiable)

- tasks run **only** when dependencies are complete
- outputs **must** exist physically
- no agent can bypass task graph
- no task can execute twice without reset
- no silent failures
- no missing artifacts

---

## 13. Parallel Execution (Real Performance)

Tasks **can** run in parallel **if**:

- no shared dependencies, and
- no conflicting outputs

Example:

- UI + backend build → parallel
- both depend on architecture

---

# AgentForge V2 Agent Roles

> Canonical role definitions for the 12 V2 agents.
> Source: user specification provided on March 17, 2026.

Every agent is defined by:
- Domain ownership (what part of the product it owns)
- Inputs it is allowed to receive
- Exact tasks it is responsible for
- Outputs it must produce (artifacts only)
- What it is not allowed to do

No overlap. No guessing. No bleed between agents.

---

## 🧠 1. ORIGIN (Commander)

**Domain**  
Command interpretation; Task graph creation; Build coordination

**Inputs**
- user command
- system config
- knowledge graph context

**Tasks (EXACT)**
- parse raw command
- classify product type (game / web / app / hybrid)
- extract required systems (gameplay, UI, backend, etc.)
- define project scope boundaries
- generate initial task graph
- assign tasks to correct agents
- enforce simulation-before-build rule
- trigger recursive loop phases

**Outputs**
- intent.json
- task_graph.json
- build_plan.json

**Not allowed**
- cannot generate code
- cannot design systems
- cannot validate architecture
- cannot execute tasks

---

## 🏗️ 2. ARCHITECT (Atlas)

**Domain**  
System design; Structure definition

**Inputs**
- intent.json
- research data

**Tasks**
- define system modules
- define gameplay systems (if game)
- define service layers (if backend)
- define UI structure (high-level only)
- define data models
- define interfaces between systems
- define engine/framework selection
- define dependency graph

**Outputs**
- architecture.json
- modules.json
- interfaces.json
- data_models.json

**Not allowed**
- cannot write code
- cannot test
- cannot deploy

---

## 📚 3. ARCHIVIST (Research Agent)

**Domain**  
External knowledge ingestion; Pattern extraction

**Inputs**
- URLs
- repos
- PDFs
- docs
- transcripts

**Tasks**
- ingest sources
- extract mechanics (for games)
- extract architecture patterns
- extract code patterns
- extract optimization strategies
- normalize data into structured format
- store into knowledge graph

**Outputs**
- research_insights.json
- patterns.json
- extracted_systems.json

**Not allowed**
- cannot design system
- cannot generate code
- cannot modify architecture

---

## 🛡️ 4. GUARDIAN (Sentinel)

**Domain**  
Validation; Safety; Rule enforcement

**Inputs**
- architecture.json
- code outputs
- configs

**Tasks**
- validate architecture integrity
- check for conflicts in dependencies
- enforce anti-drift rules
- validate execution safety rules
- detect invalid system designs
- verify sandbox compliance

**Outputs**
- validation_report.json
- security_report.json
- issues.json

**Not allowed**
- cannot generate code
- cannot modify systems
- cannot deploy

---

## 🧪 5. ANALYST (Probe)

**Domain**  
Testing; Simulation (real validation, not fake)

**Inputs**
- architecture
- code
- systems

**Tasks**
- run system tests
- run integration tests
- simulate execution conditions
- detect failures
- measure performance
- validate outputs

**Outputs**
- test_results.json
- performance_metrics.json
- failure_report.json

**Not allowed**
- cannot fix code
- cannot redesign system

---

## ⚒️ 6. BUILDER (Forge)

**Domain**  
Code generation

**Inputs**
- architecture.json
- modules.json
- interfaces.json

**Tasks**
- generate project directory structure
- generate backend code
- generate gameplay systems
- generate core logic systems
- implement APIs
- implement system modules exactly as defined

**Outputs**
- /project/
  - backend/
  - gameplay/
  - systems/
  - scripts/

(Real code files, not descriptions.)

**Not allowed**
- cannot design architecture
- cannot test
- cannot deploy

---

## 🎨 7. SURFACE (Frontend Engineer)

**Domain**  
UI systems

**Inputs**
- architecture UI definitions
- system states

**Tasks**
- implement 3-page UI ONLY
- create components
- connect UI to system state
- implement layouts
- bind data to UI

**Outputs**
- frontend/src/pages/*
- frontend/src/components/*

**Not allowed**
- cannot change architecture
- cannot generate backend logic

---

## 🧱 8. CORE (Backend Engineer)

**Domain**  
API + services

**Inputs**
- architecture.json
- data_models.json

**Tasks**
- implement FastAPI routes
- implement service layers
- implement data handling
- implement orchestration hooks
- implement system APIs

**Outputs**
- backend/api/*
- backend/services/*
- backend/models/*

**Not allowed**
- cannot design architecture
- cannot deploy

---

## 🧬 9. SYNTH (Model & Provider Routing)

**Domain**  
Model selection; provider routing

**Tasks**
- choose correct model based on task
- apply safety filters
- route through approved providers

Outputs: routing logs and model selection metadata.

---

## 🚀 10. LAUNCHER (Release Engine)

**Domain**  
Build + deploy orchestration

Tasks:
- coordinate build artifacts
- prepare deployable bundles
- trigger local engine runs (Unity/Unreal/Web)

---

## 🧩 11. AUTOPSY (Postmortem)

**Domain**  
Failure analysis; learning from crashes

Tasks:
- ingest logs and crash reports
- cluster failure modes
- feed improvements back into Origin / Architect / Guardian

---

## 📈 12. CHRONICLE (History & Insight)

**Domain**  
Long-term memory; project history

Tasks:
- maintain project timelines
- surface prior decisions and patterns
- provide insight dashboards for builds and failures

---

## 14. Where Each Agent Fits (Final)

| Agent      | Task Type        |
|------------|------------------|
| Origin     | graph creation   |
| Architect  | planning tasks   |
| Builder    | code tasks       |
| Surface    | UI tasks         |
| Core       | API tasks        |
| Simulator  | engine tasks     |
| Synapse    | routing tasks    |
| Fabricator | asset tasks      |
| Guardian   | validation tasks |
| Analyst    | testing tasks    |
| Launcher   | deployment tasks |
| Archivist  | research tasks   |

---

## Final Result

You now have:

- deterministic execution
- real dependency system
- artifact enforcement
- AAA production mapping
- zero ambiguity

### What This Unlocks

Now the system can:

- actually build projects
- fail correctly
- recover correctly
- iterate like a real dev pipeline
