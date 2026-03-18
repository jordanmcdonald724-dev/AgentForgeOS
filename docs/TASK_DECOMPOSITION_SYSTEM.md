# AgentForgeOS — Task Decomposition System

Purpose:

Define how AI agents must break development work into controlled, safe tasks.

This prevents agents from making large uncontrolled changes to the repository.

The task decomposition system ensures that all work is divided into small, verifiable units before implementation.

---

# 1. Core Principle

Large development requests must never be executed as a single operation.

Every request must be decomposed into smaller tasks before code generation begins.

Example:

User Request

"Build a research module."

Must be decomposed into:

1. Create module structure
2. Define backend routes
3. Define database schema
4. Implement backend logic
5. Create frontend interface
6. Integrate module into Studio
7. Run validation tests

Each task is executed independently.

---

# 2. Task Decomposition Flow

All tasks follow this workflow:

User Request
→ Planner Agent
→ Task Breakdown
→ Task Queue
→ Execution Pipeline
→ Validation
→ Completion

The system must never skip decomposition.

---

# 3. Task Size Rules

Each task must follow size constraints.

Maximum files modified per task:

5

Maximum lines of code per task:

500

If a task exceeds these limits, it must be split into smaller tasks.

---

# 4. Task Types

Tasks are categorized to ensure correct agent assignment.

Task types:

architecture
backend
frontend
integration
testing
documentation

Example:

Create research module backend route

Task Type:

backend

Assigned Agent:

Backend Engineer

---

# 5. Task Queue Structure

Tasks are stored in a queue.

Example:

```json
{
  "task_id": "task_001",
  "type": "backend",
  "description": "Create research API route",
  "status": "pending",
  "assigned_agent": "backend_engineer"
}
```

Task states:

pending
in_progress
validation
completed
failed

---

# 6. Dependency Management

Tasks may depend on other tasks.

Example:

Create frontend panel depends on backend API.

Example structure:

```json
{
  "task_id": "task_004",
  "depends_on": ["task_002"]
}
```

Tasks cannot execute until dependencies are completed.

---

# 7. Execution Pipeline

Tasks must pass through the AI pipeline.

Pipeline stages:

Planner
Architect
Router
Production Agents
Validation Agents

Each stage validates task integrity before continuing.

---

# 8. Task Validation

After execution, tasks must pass validation checks.

Checks include:

• backend server runs
• API endpoints register
• frontend builds successfully
• architecture rules remain intact

Validation agents produce reports.

Example report:

```json
{
  "task_id": "task_001",
  "validation": "passed",
  "issues": []
}
```

---

# 9. Error Handling

If a task fails validation:

1. Task status becomes "failed"
2. Error report generated
3. System Stabilizer reviews issue

Example report:

task_failure_report.json

---

# 10. Task Retry Rules

Failed tasks may be retried once.

If the retry fails:

The task must be escalated to a human developer.

---

# 11. Task Logging

All tasks must be logged.

Logs include:

task_id
agent
files_modified
execution_time
validation_status

Logs are displayed in the Pipeline Monitor panel.

---

# 12. Incremental Development

Tasks must modify the smallest possible part of the system.

Agents must avoid large refactors.

Allowed changes:

• small feature additions
• bug fixes
• module creation

Forbidden actions:

• rewriting major subsystems
• renaming core directories
• large multi-module refactors

---

# 13. Safe Commit Policy

Each completed task generates a commit.

Commit message format:

[Task Completed] task_id – task description

Example:

[Task Completed] task_003 – implement research route

---

# 14. Parallel Execution

Tasks without dependencies may run in parallel.

Example:

Backend route creation and database schema creation may run simultaneously.

Parallel execution must not exceed 3 concurrent tasks.

---

# 15. Task Completion

A task is considered complete when:

• validation passes
• logs are recorded
• commit is created

The pipeline then proceeds to the next task.

---

# 16. Final Rule

AI agents must treat the task decomposition system as mandatory.

No code generation may begin until tasks have been fully decomposed and queued.

---

# End of Task Decomposition System
