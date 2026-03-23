# AgentForgeOS — Provider‑Agnostic Agent Behavior System

Version: 1.0  
Goal: Ensure each of the 12 agents behaves consistently regardless of LLM provider/model.

---

## 1) Problem Statement

LLM provider/model swaps change style, risk tolerance, verbosity, and reliability. If agent behavior is defined only by “which model runs”, the studio will drift. AgentForgeOS must define behavior as a system contract that is:

- explicit
- repeatable
- testable
- enforceable at runtime

This document defines how AgentForgeOS stores, injects, and enforces agent behavior guidelines.

---

## 2) Behavioral Contract Model

Each agent has a behavioral contract consisting of:

1) **Identity**
   - role name
   - mission
   - what the agent is not allowed to do

2) **Operating Standards**
   - required outputs
   - forbidden outputs
   - required format templates
   - “must ask vs must assume” rules

3) **Decision Rules**
   - explicit priorities (stability vs features, etc.)
   - acceptance criteria and gates
   - conflict resolution policy

4) **Tooling Policy**
   - which system tools the agent can invoke
   - what it must never do
   - file access boundaries

5) **Interaction Protocol**
   - how it hands off to other agents
   - what inputs it requires from upstream
   - what artifacts it produces downstream

This contract is stored as **immutable prompt text** plus **structured policy metadata**.

---

## 3) Storage Format (Recommended)

### 3.1 Canonical Agent Spec Files

Store agent behavior specs in:

- `docs/agents/<AGENT_NAME>_OPERATING_MANUAL.md` (human‑readable long form)
- `resources/config/agents/<agent_id>.json` (machine‑readable)

The JSON format should include:

- `agent_id`
- `role_name`
- `task_types[]`
- `system_prompt` (the canonical behavioral prompt)
- `output_schema` (if enforced)
- `guardrails` (forbidden behaviors, disallowed tools)
- `handoff_contract` (expected inputs/outputs)

### 3.2 Provider Independence Rule

Agent behavior must never be expressed as “use model X to behave like Y”. Behavior is defined independently; model selection is an execution detail.

---

## 4) Runtime Injection Flow (How behavior is enforced)

### 4.1 Mandatory Message Assembly

For every agent execution, the runtime must assemble the final prompt/messages in a deterministic order:

1) System: global platform constraints (security, no secrets, file access policy)
2) System: agent-specific behavioral contract (from agent spec)
3) System: current project context (project id, workspace paths, enabled modules)
4) Developer: task-specific instructions (task type, required output format)
5) User: the user request
6) Tool results: only when invoked and sanitized

### 4.2 Router and Provider Normalization

The router selects the engine/model. The engine adapter must normalize:

- response shape: always return `{ text, meta }`
- failure shape: always return `{ error, failure_class }`
- token/cost if available

No agent code may depend on provider-specific response formats.

---

## 5) Consistency Mechanisms (beyond prompts)

Prompts alone cannot guarantee consistency. AgentForgeOS must add enforcement:

### 5.1 Output Validation

Where possible, enforce schemas for outputs:

- Director outputs must include: scope, milestones, exit criteria, assignments.
- Architect outputs must include: interfaces, boundaries, ADR.
- Review outputs must include: pass/fail with evidence.

Validation options:

- lightweight JSON schemas for structured outputs
- regex validators for required headings

### 5.2 Behavioral Tests

Add deterministic tests that check that the agent output contains required sections. Use golden files for high-level formatting.

### 5.3 Guardrails

If an agent violates a rule (e.g., writes code when it must not), the runtime:

- rejects output
- re-prompts with a corrective instruction
- logs a behavioral violation event

### 5.4 Cross-Agent Handoff Contracts

Each agent must produce outputs in a form that downstream agents can consume. Handoff contracts reduce provider-driven stylistic drift.

---

## 6) Integration With Model Routing

AgentForgeOS routing should map:

- `agent_id` → `task_type`
- `task_type` → `(engine, model, fallback[])`

Behavior and routing are separate layers:

- behavior determines “how the agent acts”
- routing determines “which engine executes the agent”

---

## 7) Operational Rollout Plan (12 agents)

1) Create long-form manuals (this repo, docs) for each agent.
2) Convert each manual into a canonical `system_prompt` snippet.
3) Create machine-readable agent policy JSON files.
4) Update runtime to load the agent spec file and inject it before every call.
5) Add validation tests for required output structure.
6) Add an admin UI section to view/edit agent specs locally (never shipped).

---

## 8) Current Spec Status

- Completed manuals:
  - `docs/agents/DIRECTOR_AI_OPERATING_MANUAL.md`
  - `docs/agents/ARCHITECT_AI_OPERATING_MANUAL.md`

- Next manuals:
  - Task Router
  - Backend Engineer
  - Frontend Engineer
  - Database Engineer
  - AI Engineer
  - Game Engine Engineer
  - DevOps Engineer
  - Asset Generator
  - Documentation Agent
  - Review Agent
  - Refactor Agent
  - Deployment Agent
  - Learning Agent
