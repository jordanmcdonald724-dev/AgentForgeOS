# 🔴 AGENTFORGE OS — V1 SYSTEM BIBLE (STRICT IMPLEMENTATION SPEC)

---

## 🧠 CORE SYSTEM IDENTITY

AgentForge is a:

> **Self-directing software and asset creation engine with adaptive control, recovery, scoring, and memory**

NOT:

* a chatbot
* a generator
* a single-pass system

---

## ⚠️ GLOBAL NON-NEGOTIABLE RULES

1. **CONTROL LAYER IS MANDATORY**
   * No execution outside control layer

2. **NO SINGLE-PASS EXECUTION**
   * Everything must run through pipelines

3. **EVERY STEP MUST BE:**
   * monitored
   * scored
   * recoverable

4. **MEMORY IS ALWAYS USED**
   * before, during, after execution

5. **PIPELINES ARE NEVER FINAL**
   * must support modification mid-execution

6. **NO HARDCODING PIPELINES IN UI PAGES**
   * all logic lives in services/control

---

## 🏗 SYSTEM ARCHITECTURE

```
UI Pages
   ↓
Pipeline Layer
   ↓
CONTROL LAYER (CORE)
   ↓
Agents + Providers
   ↓
Memory System
```

---

## 🔴 CONTROL LAYER (CENTRAL NERVOUS SYSTEM)

### Purpose

Controls ALL execution across ALL pages

### Files

```
control/
  agent_supervisor.py
  ai_router.py
  execution_monitor.py
  recovery_engine.py
  learning_controller.py
  scoring_engine.py
  dynamic_pipeline_builder.py
  agent_factory.py
```

### CONTROL FLOW

```
Request
 ↓
ai_router
 ↓
learning_controller (context)
 ↓
agent_supervisor (execution)
 ↓
execution_monitor (tracking)
 ↓
scoring_engine (evaluation)
 ↓
recovery_engine (if needed)
 ↓
learning_controller (store results)
```

### HARD RULES

* ALL agents run through `agent_supervisor`
* ALL steps tracked by `execution_monitor`
* ALL outputs scored
* ALL failures handled
* ALL runs stored

---

## 🤖 AGENT SYSTEM

### Base Agent (MANDATORY)

```
agents/base_agent.py
```

```python
class BaseAgent:
    def run(self, input):
        pass

    def self_evaluate(self, output):
        pass

    def repair(self, output, feedback):
        pass
```

### RULES

* All agents MUST inherit BaseAgent
* Self-evaluation happens BEFORE failure escalation
* Max 1–2 repair attempts

---

## 🔗 EXECUTION PIPELINE

```
control/agent_pipeline.py
```

### Behavior

* Sequential execution
* Output passed step-to-step
* Controlled by supervisor

---

## 👁 MONITORING + SCORING

### Files

```
control/execution_monitor.py
control/scoring_engine.py
services/execution_history.py
```

### Responsibilities

**execution_monitor:**

* step start/end
* errors
* timing

**scoring_engine:**

* quality
* correctness
* speed
* stability

**execution_history:**

* pipelines
* outputs
* scores

---

## 🔁 RECOVERY SYSTEM

```
control/recovery_engine.py
```

### Actions

* retry agent
* swap agent
* insert step
* rewind pipeline
* abort safely

---

## 🧠 MEMORY + LEARNING

```
control/learning_controller.py
knowledge/context_index.py
```

### Uses

* execution_history
* vector_store
* knowledge_graph

### Responsibilities

**BEFORE:**

* inject context

**DURING:**

* adapt decisions

**AFTER:**

* store:
  * successes
  * failures
  * scores
  * patterns

---

## ⚙️ DYNAMIC SYSTEMS

```
control/dynamic_pipeline_builder.py
control/agent_factory.py
```

### Capabilities

* build pipelines at runtime
* modify pipelines mid-execution
* create new agents dynamically

---

## 📄 PAGE ARCHITECTURE

### FULL PIPELINE PAGES

```
Studio
Research
Builds
Game Dev
SaaS Builder
Deployment
Assets
Sandbox
```

### NON-PIPELINE PAGES

```
Providers
System Status
Settings
Profile
Projects
```

---

## 🧱 UNIVERSAL PIPELINE BACKBONE

ALL pipeline pages MUST implement:

```
1. Intake
2. Planner
3. Orchestrator
4. Controller
5. Recovery
6. Scoring
7. Memory
8. Registry
```

---

## 🏗 BUILDS PAGE (SOFTWARE FACTORY)

### Purpose

Structured system creation

### Pipeline

```
Input
 → system_designer
 → architecture_engine
 → task_decomposer
 → pipeline
 → execution
 → validation
 → recovery
 → scoring
 → memory
 → output registry
```

### Files

```
services/
  build_pipeline.py
  build_templates.py
  system_designer.py
  architecture_engine.py
  build_orchestrator.py

systems/
  code_generator.py
  dependency_resolver.py
  runtime_validator.py
```

### Build Types

* Apps
* Game Systems
* Backend Systems
* AI Systems
* OS / Firmware

---

## 🎨 ASSETS PAGE (ASSET PRODUCTION PIPELINE)

### Purpose

Generate production-ready assets

### Pipeline

```
Input
 → reference analysis
 → asset planning
 → staged generation
 → validation
 → refinement loop
 → scoring
 → memory
 → registry
```

### Files

```
services/
  asset_pipeline.py
  asset_planner.py
  asset_registry.py

knowledge/
  reference_analyzer.py
  style_extractor.py

systems/
  model_generator.py
  texture_generator.py
  asset_validator.py
  engine_exporter.py
```

### RULES

* multi-stage ONLY
* must validate
* must refine (2–3 passes)
* must store versions
* must respect constraints

---

## 🔥 SANDBOX (EMERGENT SYSTEM)

### Purpose

Autonomous adaptive execution

### Pipeline

```
Intent
 → learning
 → dynamic pipeline
 → execution loop
 → monitor
 → recover
 → adapt
 → score
 → memory (live)
```

### Files

```
control/
  emergent_orchestrator.py

services/
  live_execution_loop.py
```

### Core Behavior

```python
while running:
    execute
    monitor
    score
    recover
    modify pipeline
```

### Rules

* no fixed pipeline
* real-time adaptation
* dynamic agent creation
* live memory updates

---

## 🧠 LEARNING SYSTEM

### Structure

```
knowledge/
  ingestion/
  learning/
  memory/
  execution/
```

### Capabilities

* pattern extraction
* skill building
* task decomposition
* execution learning

---

## 🔁 FULL SYSTEM LOOP

```
User Input
 ↓
Learning Controller
 ↓
Task Decomposition
 ↓
Pipeline Execution
 ↓
Monitoring + Scoring
 ↓
Recovery
 ↓
Memory Update
```

---

## 🧱 IMPLEMENTATION ORDER (GATES)

```
1. Core Control Spine
2. Base Agent System
3. Execution Pipeline
4. Monitoring + Scoring
5. Recovery System
6. Memory + Learning
7. Dynamic Systems
8. Builds Pipeline
9. Assets Pipeline
10. Sandbox System
```

---

## ⚠️ FINAL SYSTEM TRUTH

This system is:

✔ adaptive  
✔ self-healing  
✔ self-improving  
✔ self-expanding

---

## 🚨 FINAL ENFORCEMENT RULE

> If any component bypasses:
>
> * control layer
> * monitoring
> * scoring
> * recovery
> * memory
>
> → IT IS INVALID AND MUST BE REJECTED

---

## Initial V1 implementation scan (repo state)

* **Control layer coverage:** `control/` now includes the full spine from this spec — `ai_router.py`, `agent_supervisor.py`, `file_guard.py`, `module_registry.py`, `execution_monitor.py`, `scoring_engine.py`, `recovery_engine.py`, `learning_controller.py`, `dynamic_pipeline_builder.py`, and `agent_factory.py`. The supervisor wires monitoring, scoring, recovery, and learning hooks around every pipeline step.
* **Pipeline + agents:** A sequential pipeline and shared context are defined in `services/agent_pipeline.py`, with supervisor dispatch in `control/agent_supervisor.py` and agent implementations under `agents/` (all inheriting `agents/base_agent.py`). Monitoring, scoring, recovery, and learning hooks now execute for every stage; dynamic pipeline shaping is scaffolded but present.
* **Memory + knowledge:** Memory utilities (`services/mongo_memory.py`, `services/memory_manager.py`) and knowledge components (`knowledge/embedding_service.py`, `knowledge/vector_store.py`, `knowledge/knowledge_graph.py`) are orchestrated via the `LearningController` before/after pipeline runs to store scores and responses. Knowledge layers offer JSON persistence for graph/vector data.
* **Page/system pipelines:** The app modules for Studio, Research, Builds, Assets, Deployment, Sandbox, Game Dev, and SaaS Builder live under `apps/`, but dedicated pipelines for Builds/Assets (e.g., `services/build_pipeline.py`, `services/asset_pipeline.py`) and Sandbox emergent orchestration (`control/emergent_orchestrator.py`, `services/live_execution_loop.py`) have not been implemented yet.
* **Next-start focus:** Expand the dynamic pipeline builder beyond its current scaffold, add real recovery strategies, and introduce the specialized Builds/Assets/Sandbox pipelines to match the universal pipeline backbone.
