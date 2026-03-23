# AgentForgeOS — Control Layer

The Control Layer prevents uncontrolled modifications by AI agents.

It ensures the system architecture remains stable.

## Components

ai_router.py
file_guard.py
agent_supervisor.py
permission_matrix.yaml

---

## AI Router

Classifies AI tasks.

Example task categories:

code_generation
bug_fix
refactor
research
deployment

---

## File Guard

Prevents agents from modifying protected directories.

Protected directories:

engine/
services/
providers/
control/

Any attempt to modify these directories must be rejected.

---

## Agent Supervisor

Coordinates multi-agent workflows.

Responsibilities:

• enforce execution order
• validate outputs
• prevent conflicting changes

---

## Permission Matrix

Defines which directories agents may modify.

Example:

code_generation → apps/
bug_fix → apps/, services/
deployment → apps/deployment

Agents must not modify core system directories.
