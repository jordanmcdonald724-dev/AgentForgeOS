# AgentForgeOS — AI Development Rules

Purpose:

Define mandatory rules that all AI agents must follow when generating or modifying code in the AgentForgeOS repository.

These rules prevent architecture drift, uncontrolled refactoring, and accidental system corruption.

The Control Layer enforces these rules.

---

# 1. Core Rule

AI agents must follow the architecture defined in:

AGENTFORGE_OS_SPEC.md
SYSTEM_ARCHITECTURE.md
REPOSITORY_STRUCTURE.md

If a requested change conflicts with these documents, the change must be rejected.

---

# 2. Protected System Layers

The following directories are protected and may not be modified by AI agents unless explicitly authorized.

Protected directories:

engine/
services/
providers/
control/

These layers form the system core.

Any modification to these layers must require explicit developer approval.

---

# 3. Allowed Modification Areas

AI agents may modify only the following directories by default:

apps/
frontend/
knowledge/
bridge/

These directories contain modular system extensions.

---

# 4. File Modification Rules

AI agents must follow these rules when editing files.

• Prefer modifying existing files over creating new duplicates.
• Never create files with similar names to existing modules.
• Avoid refactoring unrelated code when fixing a bug.
• Do not rename functions or directories unless required.

If a change requires editing more than five files, the agent must stop and request approval.

---

# 5. Architecture Preservation

AI agents must not:

• restructure repository layout
• introduce new top-level directories
• change module boundaries
• move core engine files

Architecture changes must be approved by a human developer.

---

# 6. Provider Integration Rules

All external AI services must be accessed through the provider layer.

Valid provider usage:

LLMProvider.chat()
ImageProvider.generate()
TTSProvider.speak()

Agents must never call external APIs directly.

Example forbidden usage:

Direct HTTP calls to OpenAI or fal endpoints.

---

# 7. Module Development Rules

All new functionality must be implemented as modules.

Modules must live in:

apps/

Each module must follow the structure defined in:

STUDIO_MODULE_SYSTEM.md

Modules must include:

module_config.json
backend/
frontend/
README.md

---

# 8. UI Development Rules

All UI components must follow the layout defined in:

UI_STUDIO_LAYOUT.md

Agents must not:

• modify the base layout
• create new dashboard structures
• reposition core panels

Modules may only render inside the **Main Workspace panel**.

---

# 9. AI Pipeline Compliance

AI agents must follow the pipeline defined in:

AI_PIPELINE_SYSTEM.md

Pipeline stages must not be skipped.

Agents must produce artifacts before generating code.

Required artifacts:

project_plan.json
architecture_plan.json
task_queue.json

These artifacts must be validated before code changes occur.

---

# 10. Testing Requirement

All generated code must pass the following checks:

Backend server starts successfully
Frontend builds without errors
API routes register correctly

If tests fail, the change must be rejected.

---

# 11. Security Rules

AI agents must not:

• commit API keys
• store credentials in code
• expose environment variables

Credentials must be stored only in:

config/.env

---

# 12. Logging Requirements

AI agents must log significant actions.

Example events:

• module creation
• provider integration
• pipeline execution
• architecture violation attempts

Logs should appear in the Agent Console panel.

---

# 13. Error Handling

If an AI agent encounters an error, it must:

1. stop the current operation
2. generate an error report
3. request human review

Example report:

pipeline_failure_report.json

---

# 14. Code Generation Limits

AI agents must limit scope of changes.

Maximum changes per task:

• 5 files modified
• 500 lines of code

If changes exceed this threshold, the task must be broken into smaller tasks.

---

# 15. Documentation Requirements

AI agents must update documentation when adding modules.

Required updates:

README.md
module_config.json

Documentation must remain synchronized with the codebase.

---

# 16. Human Override

Developers may override AI restrictions when necessary.

Override must be explicitly marked in commit messages.

Example:

[OVERRIDE] Engine modification approved

---

# 17. Validation Before Merge

Before merging generated code, the following agents must approve:

Integration Tester
Security Auditor
System Stabilizer

If any validator rejects the change, the merge must be blocked.

---

# 18. Rule Violations

If an AI agent violates these rules:

The Control Layer must block the operation.

A violation report must be generated.

Example report:

rule_violation_report.json

---

# 19. Final Principle

AI agents assist development.

They do not control system architecture.

Architecture decisions always belong to the developer.

---

# End of AI Development Rules
