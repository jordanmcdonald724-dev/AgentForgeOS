# AgentForgeOS — Bootstrap Prompt for AI Coding Agents

Purpose:

Provide the exact instructions AI coding agents must follow when initializing the repository.

---

# Bootstrap Instructions

1. Read all documents inside the /docs directory.

Required reading order:

AGENTFORGE_OS_SPEC.md
SYSTEM_ARCHITECTURE.md
REPOSITORY_STRUCTURE.md
BOOTSTRAP_PLAN.md
AI_DEVELOPMENT_RULES.md

---

2. Create the repository structure exactly as defined in:

REPOSITORY_STRUCTURE.md

Do not invent additional directories.

---

3. Build the system following the phases defined in:

BOOTSTRAP_PLAN.md

Do not skip phases.

---

4. Respect architecture rules defined in:

SYSTEM_ARCHITECTURE.md

Do not modify protected directories.

---

5. All feature development must follow:

STUDIO_MODULE_SYSTEM.md

Modules must be created inside:

apps/

---

6. UI components must follow:

UI_STUDIO_LAYOUT.md

Do not modify the base layout.

---

7. All backend routes must follow:

SYSTEM_API_CONTRACTS.md

Do not invent new endpoints.

---

8. All AI integrations must follow:

PROVIDER_IMPLEMENTATION_GUIDE.md

External APIs must never be called directly.

---

9. All generated code must comply with:

AI_DEVELOPMENT_RULES.md

Violations must stop the pipeline.

---

# Final Instruction

The AI coding agent must treat the documentation inside /docs as the authoritative architecture of the system.

If a task conflicts with the documentation, the task must be rejected.

---

# End of Bootstrap Prompt
