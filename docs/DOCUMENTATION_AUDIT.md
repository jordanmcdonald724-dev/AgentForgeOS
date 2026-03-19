# AgentForgeOS — Documentation Audit Report

> **Date:** 2026-03-18
> **Purpose:** Audit all documentation against the actual repository state to identify mismatches, stale references, missing coverage, and inconsistencies between docs and code.
> **Action:** No files are deleted or modified. This is a read-only alignment report.

---

## How to Use This Report

Each section below covers one documentation file. For every file the audit records:

- **Status** — ✅ Aligned, ⚠️ Partially Aligned, or ❌ Misaligned
- **Findings** — specific mismatches between what the doc says and what actually exists
- **Recommendation** — whether to update, archive, or leave as-is

A summary table and prioritized action list appear at the end.

---

## 1. README.md (root)

**Status:** ⚠️ Partially Aligned

| # | Claim in Doc | Actual State | Issue |
|---|---|---|---|
| 1 | Project Structure lists: `engine/`, `desktop/`, `control/`, `services/`, `providers/`, `agents/`, `knowledge/`, `bridge/`, `apps/`, `frontend/`, `config/`, `docs/`, `tests/` | Repo has **12 additional top-level dirs** not listed: `backend/`, `build_system/`, `infrastructure/`, `memory/`, `models/`, `orchestration/`, `projects/`, `research/`, `scripts/`, `.emergent/`, `.vscode/`, `AgentForgeUI_Image References/` | Missing entries |
| 2 | Running Tests: `python -m unittest discover -s tests` | Tests now run via **`python -m pytest tests/ -v`** (187 tests). unittest also works but pytest is the actual runner. | Stale command |
| 3 | Open the frontend: "Navigate to `http://localhost:8000`" — engine serves Studio UI | Frontend is now a **React + Vite** app. Dev server runs on port 5173 via Vite. The engine does NOT serve the React app directly in dev mode. | Stale workflow |
| 4 | Documentation table lists `docs/UI_STUDIO_LAYOUT.md` twice | Duplicate row | Minor typo |
| 5 | Documentation table does not list `docs/V2_EXECUTION_MODEL.md`, `docs/V2_RUNTIME_RELIABILITY_AND_PREVIEW.md`, `docs/UI_LAYOUT_FUNCTIONAL_SPEC.md` | These docs exist but aren't in the table | Missing entries |
| 6 | Current Build State says "End-to-end integration requires a running Ollama instance" | Still true, but also fails to mention V2 orchestration/task-graph system that has been built | Incomplete |
| 7 | Endpoints list: `GET /api/health`, `GET /api/modules`, `GET /api/setup` | Many more endpoints exist: V2 routes (`/api/v2/command/preview`, `/api/v2/research/*`, `/api/v2/settings`, etc.), pipeline route (`/api/pipeline/run`), all module routes | Incomplete |

**Recommendation:** Update the Project Structure tree, test command, frontend workflow, documentation table, and endpoint list to reflect current state.

---

## 2. docs/REPOSITORY_STRUCTURE.md

**Status:** ❌ Misaligned

| # | Claim in Doc | Actual State | Issue |
|---|---|---|---|
| 1 | Root Structure lists 10 dirs: `desktop/`, `engine/`, `control/`, `services/`, `providers/`, `apps/`, `bridge/`, `knowledge/`, `config/`, `frontend/`, `docs/` | Repo has **25 top-level directories**. Missing from doc: `agents/`, `backend/`, `build_system/`, `infrastructure/`, `memory/`, `models/`, `orchestration/`, `projects/`, `research/`, `scripts/`, `tests/`, `.emergent/`, `.vscode/`, `AgentForgeUI_Image References/` | Major gap — 14 dirs undocumented |
| 2 | engine/ lists: `main.py`, `server.py`, `database.py`, `config.py`, `worker_system.py`, `module_loader.py`, `routes/modules.py`, `routes/agent.py`, `routes/setup.py` | engine/routes/ also contains: `__init__.py`, `pipeline.py`, `v2_infrastructure.py`, `v2_orchestration.py`, `v2_research.py` (5 additional files) | Incomplete |
| 3 | engine/ also has `ws.py` (WebSocket handler) | Not listed in doc | Missing |
| 4 | control/ lists 4 files | control/ actually has **12 files** (8 undocumented: `execution_monitor.py`, `scoring_engine.py`, `recovery_engine.py`, `learning_controller.py`, `dynamic_pipeline_builder.py`, `agent_factory.py`, `module_registry.py`, `__init__.py`) | Major gap |
| 5 | apps/ lists 5 modules: `studio/`, `builds/`, `research/`, `assets/`, `deployment/` | apps/ has **8 modules** (also: `sandbox/`, `game_dev/`, `saas_builder/`) | Missing 3 modules |
| 6 | frontend/ says "static scaffold lives at frontend/index.html + frontend/style.css" | frontend/ is now a **full React + Vite app** with `src/`, `node_modules/`, `vite.config.js`, `package.json`, etc. index.html is a React bootstrap, not a static scaffold. | Stale description |
| 7 | No mention of `orchestration/`, `build_system/`, `infrastructure/`, `models/`, `backend/` | These are core V2 directories with real code | Major gap |

**Recommendation:** This doc needs a significant rewrite to reflect the actual 25-directory repo structure, all V2 additions, and the React frontend evolution.

---

## 3. docs/SYSTEM_ARCHITECTURE.md

**Status:** ⚠️ Partially Aligned

| # | Claim in Doc | Actual State | Issue |
|---|---|---|---|
| 1 | Core Layers: Engine, Control, Services, Apps | Actual layers now also include: **Orchestration** (`orchestration/`), **Build System** (`build_system/`), **Infrastructure** (`infrastructure/`), **V2 Agents** (`agents/v2/`) | Missing V2 layers |
| 2 | Control Layer lists 4 files | Control has 12 files | Incomplete |
| 3 | "Phase 6 scaffold lives in frontend/index.html and frontend/style.css as a static mock" | Frontend is now a full React app with router, context, hooks, pages. index.html is a React bootstrap. | Stale description |
| 4 | Apps listed: studio, builds, research, assets, deployment, sandbox, game_dev, saas_builder | ✅ All 8 match | Aligned |
| 5 | Knowledge Layer section matches actual files | ✅ Aligned | OK |
| 6 | Architecture Rules section is still valid | ✅ Still applicable | OK |
| 7 | No mention of V2 orchestration engine, task model, simulation engine | These are core architectural components now | Missing |
| 8 | No mention of WebSocket system (`engine/ws.py`) | WebSocket is integral to real-time UI | Missing |

**Recommendation:** Add V2 orchestration layer, build system layer, infrastructure layer, and WebSocket system to the architecture map. Update frontend description.

---

## 4. docs/AGENTFORGE_OS_SPEC.md

**Status:** ⚠️ Partially Aligned

| # | Claim in Doc | Actual State | Issue |
|---|---|---|---|
| 1 | Section 3 lists 10 repo dirs | Actual repo has 25 dirs | Same gap as REPOSITORY_STRUCTURE.md |
| 2 | Section 5 Engine files: lists 5 files | Engine now also has `ws.py` and 8 route files | Incomplete |
| 3 | Section 6 Control files: lists 4 files | Control now has 12 files | Incomplete |
| 4 | Section 13 Frontend: "Phase 6 provides a static Studio scaffold" | Now a full React+Vite app | Stale |
| 5 | Section 14 lists the original 12 agents (Planner through Stabilizer) | V2 adds **12 new agent roles** in `agents/v2/`: Origin, Atlas, Forge, Sentinel, Probe, etc. | Missing V2 agents |
| 6 | Module config section mentions `module_config.json` example content | Actual modules use **`manifest.json`** (different filename) | Wrong filename |
| 7 | Config section mentions `settings.json` | ✅ `config/settings.json` exists | OK |
| 8 | Core principles (layered, provider abstraction, local-first, AI safety, modularity) | ✅ All still valid | OK |

**Recommendation:** Update repo structure, engine/control file lists, frontend description, agent listing, and module config filename.

---

## 5. docs/SYSTEM_API_CONTRACTS.md

**Status:** ⚠️ Partially Aligned

| # | Claim in Doc | Actual State | Issue |
|---|---|---|---|
| 1 | Lists 8 API sections: Projects, Builds, Research, Assets, Providers, Pipeline, Bridge, Setup Wizard | Missing all **V2 endpoints**: `/api/v2/command/preview`, `/api/v2/projects/{id}/status`, `/api/v2/research/categories`, `/api/v2/research/ingest`, `/api/v2/research/nodes`, `/api/v2/settings`, `/api/v2/local_bridge/projects`, `/api/v2/model_routing/routes` | Major gap — V2 API not documented |
| 2 | Missing module-specific endpoints | Not listed: `/api/modules/assets/generate`, `/api/modules/deployment/launch`, `/api/modules/game_dev/*`, `/api/modules/saas_builder/*`, `/api/modules/sandbox/*` | Missing |
| 3 | Missing WebSocket endpoint | `/ws` is a core real-time endpoint | Missing |
| 4 | Original endpoint paths (e.g. `/api/research/ingest`) | Some may differ from actual implementation (V2 uses `/api/v2/research/ingest`) | Potentially stale paths |
| 5 | Setup Wizard endpoints (`/api/setup`, `/api/setup/save`, `/api/setup/reset`, `/api/setup/bootstrap`) | ✅ All exist and match | OK |

**Recommendation:** Add V2 API section, module endpoints, and WebSocket contract. The `UI_HOOKUP_CHECKLIST.md` already has a comprehensive API reference table that could be promoted here.

---

## 6. docs/BUILD_STATUS.md

**Status:** ⚠️ Partially Aligned

| # | Claim in Doc | Actual State | Issue |
|---|---|---|---|
| 1 | Phase 10 says "173 tests" | Test suite now has **187 tests** (per recent runs) | Stale count |
| 2 | Phase 10 says `python -m unittest discover -s tests` | Tests now run with `python -m pytest tests/ -v` | Stale command |
| 3 | Phase 6 says `frontend/index.html — Five-region layout` is DONE | `frontend/index.html` is now a **12-line React bootstrap**, not the five-region layout. The layout lives in React components. | Stale reference |
| 4 | Phase 6 says `frontend/style.css — Base styles` | ✅ `frontend/style.css` exists (9.7KB) | OK |
| 5 | Phase 9 mentions `frontend/wizard.html` | ✅ Exists (423 lines) | OK |
| 6 | No mention of V2 orchestration system, V2 agents, V2 routes | These are built and tested but not tracked in this doc | Missing V2 coverage |
| 7 | "Remaining Work" lists 3 items | Does not include V2-related remaining work (AAA graph wiring, project health API, etc.) | Incomplete |
| 8 | All Phase 1-8 items marked DONE | ✅ Verified — all code files exist | OK |

**Recommendation:** Update test count, test command, frontend description, and add V2 system tracking.

---

## 7. docs/SYSTEM_CAPABILITY_MAP.md

**Status:** ⚠️ Partially Aligned

| # | Claim in Doc | Actual State | Issue |
|---|---|---|---|
| 1 | Control Layer: lists 11 capabilities | ✅ Actually has 12 files, all listed in SYSTEM_CAPABILITY_MAP match existing files | Close match |
| 2 | Provider Layer: lists 8 items including NoOp | NoOp provider (`noop_provider.py`) exists in `providers/` | ✅ OK — wait, the CAPABILITY_MAP does NOT list NoOp but BUILD_STATUS does | Minor inconsistency between docs |
| 3 | Frontend Layer: says `frontend/index.html` provides five-region layout | index.html is a React bootstrap; layout is in React components | Stale |
| 4 | Database Collections: All 8 marked MISSING | ✅ Still true — no MongoDB collections implemented | OK (correct) |
| 5 | Summary table says 92 total capabilities, 79 complete | May need recounting after V2 additions | Potentially stale count |
| 6 | No mention of V2 orchestration, build_system, infrastructure capabilities | These are built and functional | Missing |
| 7 | Agents Layer lists original 14 items | Missing V2 agents (12 additional in `agents/v2/`) | Missing |

**Recommendation:** Add V2 capabilities (orchestration engine, task model, simulation engine, V2 agents, infrastructure, build system). Update frontend description. Recount totals.

---

## 8. docs/UI_HOOKUP_CHECKLIST.md

**Status:** ⚠️ Partially Aligned (by design)

| # | Claim in Doc | Actual State | Issue |
|---|---|---|---|
| 1 | All G-1 through G-6 marked ❌ | Per REVERT_UI_PLAN.md, these were completed then **intentionally reverted** back to ❌. Some may have been re-implemented since (CORSMiddleware, ws proxy, etc.) | Status may be stale after re-implementation |
| 2 | All page tasks (S-1 through SS-2) marked ❌ | Some tasks (S-1–S-5, CC-1–CC-3) were completed in past branches per repo memories, then reverted | Status may need re-verification |
| 3 | API Quick Reference table | ✅ Comprehensive and matches actual endpoints well | Good reference |
| 4 | WebSocket Event Schema | ✅ Well documented | Good reference |
| 5 | RL-1 marked 🔴 CRITICAL — body mismatch | Needs verification if still true | May need re-check |

**Recommendation:** Re-verify each task status against current branch state. The API reference and WebSocket schema sections are excellent and should be kept. Consider promoting the API reference to SYSTEM_API_CONTRACTS.md.

---

## 9. docs/UI_LAYOUT_FUNCTIONAL_SPEC.md

**Status:** ✅ Aligned

This document describes the **intended** UI design spec (colors, typography, animations, module panels, etc.). It serves as a design target rather than a claim about current implementation. All described modules (Studio, Build Pipelines, Research, Assets, Deployment, Sandbox, Game Dev, SaaS Builder) exist as React components.

| # | Note | Status |
|---|---|---|
| 1 | File Structure section says `/app/frontend/src/` | Actual path is `/frontend/src/` (no `/app/` prefix) | Minor path error |
| 2 | 12 agents listed | ✅ All exist | OK |
| 3 | 8 modules listed | ✅ All exist as pages/components | OK |

**Recommendation:** Fix the file structure path. Otherwise this is a solid design reference.

---

## 10. docs/UI_STUDIO_LAYOUT.md

**Status:** ✅ Aligned

This is a design specification for the Studio UI shell. It defines the five-region layout, theme, keyboard shortcuts, and rules. As a spec (target), it remains valid.

**Recommendation:** Keep as-is. This is a reference spec, not a build status claim.

---

## 11. docs/V2_EXECUTION_MODEL.md

**Status:** ✅ Aligned

Defines the V2 task-graph execution model and 12 V2 agent roles (Origin, Architect, Archivist, Guardian, Analyst, Builder, Surface, Core, Synth, Launcher, Autopsy, Chronicle). All corresponding V2 agent files exist in `agents/v2/`. The orchestration engine, task model, and related files in `orchestration/` implement this spec.

| # | Note | Status |
|---|---|---|
| 1 | 12 V2 agents defined | ✅ All exist in `agents/v2/` | OK |
| 2 | Task graph model | ✅ Implemented in `orchestration/task_model.py` | OK |
| 3 | Section 14 agent mapping table | ✅ Matches implementation | OK |

**Recommendation:** Keep as-is. Well-aligned to codebase.

---

## 12. docs/V2_RUNTIME_RELIABILITY_AND_PREVIEW.md

**Status:** ✅ Aligned

Describes runtime contracts, declared outputs, project status API, and live preview. References `orchestration.engine`, `orchestration.task_model` which exist.

| # | Note | Status |
|---|---|---|
| 1 | References `archive/BUILD_BIBLE_V2.md` | ✅ File exists | OK |
| 2 | Describes `OrchestrationEngine` | ✅ Exists in `orchestration/engine.py` | OK |
| 3 | Describes `/api/v2/projects/{id}/status` | ✅ Implemented in `engine/routes/v2_orchestration.py` | OK |
| 4 | Describes declared outputs for all 12 V2 roles | ✅ Implemented and tested | OK |

**Recommendation:** Keep as-is. Excellent alignment.

---

## 13. docs/AI_DEVELOPMENT_RULES.md

**Status:** ⚠️ Partially Aligned

| # | Claim in Doc | Actual State | Issue |
|---|---|---|---|
| 1 | References `AGENTFORGE_OS_SPEC.md`, `SYSTEM_ARCHITECTURE.md`, `REPOSITORY_STRUCTURE.md` | ✅ All exist | OK |
| 2 | Section 7: modules must include `module_config.json` | Actual modules use **`manifest.json`** | Wrong filename |
| 3 | Section 7: references `STUDIO_MODULE_SYSTEM.md` | ✅ Exists | OK |
| 4 | Core rules about protected directories, file modification limits | ✅ Still valid | OK |

**Recommendation:** Fix module config filename reference from `module_config.json` to `manifest.json`.

---

## 14. docs/AI_PIPELINE_SYSTEM.md

**Status:** ⚠️ Partially Aligned

| # | Claim in Doc | Actual State | Issue |
|---|---|---|---|
| 1 | Describes original 12-agent pipeline (Planner→Stabilizer) | ✅ These agents still exist in `agents/strategic/`, `agents/architecture/`, `agents/production/`, `agents/validation/` | OK |
| 2 | Does not mention V2 agent team or V2 execution model | V2 has a completely different 12-agent team (Origin, Atlas, Forge, etc.) with different pipeline semantics | Missing V2 coverage |
| 3 | Section 11 mentions "Phase 4 scaffolding provides in-memory implementations" | Phase 4 is complete with real implementations, not just scaffolds | Stale language |
| 4 | Pipeline configuration stored in `config/pipeline_config.json` | This file does **not exist** | Non-existent file referenced |

**Recommendation:** Add a note about the V2 agent pipeline (or create a separate doc). Remove stale "Phase 4 scaffolding" language. Remove or annotate the `pipeline_config.json` reference.

---

## 15. docs/CONTROL_LAYER.md

**Status:** ⚠️ Partially Aligned

| # | Claim in Doc | Actual State | Issue |
|---|---|---|---|
| 1 | Lists 4 components | Control layer now has **12 files** including execution_monitor, scoring_engine, recovery_engine, learning_controller, dynamic_pipeline_builder, agent_factory, module_registry | Major gap — 8 components undocumented |
| 2 | AI Router classifies 5 task types | ✅ Still valid | OK |
| 3 | File Guard protects 4 directories | ✅ Still valid | OK |

**Recommendation:** Add documentation for all 8 new control layer components.

---

## 16. docs/DATABASE_SCHEMA.md

**Status:** ✅ Aligned (as a spec)

This doc defines 8 MongoDB collections. Per SYSTEM_CAPABILITY_MAP.md, all 8 collections are marked ❌ MISSING — they are specified but not yet implemented (the system uses in-memory storage). This is consistent.

**Recommendation:** Keep as-is. Mark clearly that these are target schemas, not implemented collections.

---

## 17. docs/ERROR_HANDLING_SYSTEM.md

**Status:** ✅ Aligned

Defines the standard error response JSON format. This is a small spec doc and remains valid as a coding standard.

**Recommendation:** Keep as-is.

---

## 18. docs/PROVIDER_IMPLEMENTATION_GUIDE.md

**Status:** ✅ Aligned

Lists provider interfaces (LLM, Image, TTS) and implementations (Fal, OpenAI, Ollama, ComfyUI, Piper). All exist in `providers/`.

| # | Note | Status |
|---|---|---|
| 1 | Does not mention `noop_provider.py` | NoOp provider exists as the safe default | Minor omission |

**Recommendation:** Add NoOp provider to the implementations list.

---

## 19. docs/SETUP_WIZARD_WINDOWS.md

**Status:** ✅ Aligned

Describes the Windows 10 local setup wizard flow. References `frontend/wizard.html`, `config/.env`, `/api/setup` endpoints — all exist and match.

**Recommendation:** Keep as-is.

---

## 20. docs/STUDIO_MODULE_SYSTEM.md

**Status:** ⚠️ Partially Aligned

| # | Claim in Doc | Actual State | Issue |
|---|---|---|---|
| 1 | Module structure requires: `backend/`, `frontend/`, `module_config.json`, `README.md` | Actual modules have: `backend/`, `manifest.json`, `module.py`, `README.md` — **no `frontend/` subdirectory** within each app and **no `module_config.json`** | Wrong filename & structure |
| 2 | Lists 8 modules | ✅ All 8 exist | OK |
| 3 | `module_config.json` example has fields: name, version, display_name, icon, entry_route, ui_entry, enabled | `manifest.json` has similar but different fields | Different schema |
| 4 | Frontend integration says components live in `apps/module_name/frontend/` | Frontend pages actually live in **`frontend/src/ui/pages/`** (centralized), not in each app's subdirectory | Wrong location |
| 5 | Service access, provider access, isolation rules | ✅ Still valid principles | OK |

**Recommendation:** Update module structure to show `manifest.json` + `module.py` pattern. Update frontend component location. Fix the config file example to match actual `manifest.json` schema.

---

## 21. docs/TASK_DECOMPOSITION_SYSTEM.md

**Status:** ✅ Aligned

This is a process/rules spec for how AI agents should decompose tasks. It remains valid as a methodology document.

**Recommendation:** Keep as-is.

---

## 22. docs/ARCHITECTURE_DECISION_RECORDS.md

**Status:** ⚠️ Partially Aligned

| # | Claim in Doc | Actual State | Issue |
|---|---|---|---|
| 1 | ADR-0005 lists 9 agents | System now has original 12 + V2 12 agents | Incomplete agent list |
| 2 | ADR-0002 lists providers including `EmbeddingProvider` | No standalone `EmbeddingProvider` interface exists in `providers/` (embeddings are handled by `knowledge/embedding_service.py`) | Incorrect reference |
| 3 | Only 5 ADRs recorded | V2 orchestration model, task-graph execution, simulation-before-build, React frontend migration — none of these decisions are recorded | Missing ADRs |

**Recommendation:** Add ADRs for V2 decisions: task-graph execution model, simulation-before-build, V2 agent roles, React+Vite frontend, orchestration engine.

---

## 23. docs/ICON_PACK.md

**Status:** ✅ Aligned

This is a utility script doc for generating icon packs. It's standalone and doesn't make claims about repo state.

**Recommendation:** Keep as-is.

---

## 24. docs/LOCAL_RUN_CHECKLIST.md

**Status:** ⚠️ Partially Aligned

| # | Claim in Doc | Actual State | Issue |
|---|---|---|---|
| 1 | "Open the frontend: navigate to `http://localhost:8000`" | Frontend is now React+Vite on port 5173 in dev mode | Stale |
| 2 | Tests: `python -m unittest discover -s tests` | Works but `python -m pytest tests/ -v` is the modern runner | Stale command |
| 3 | "The engine serves the frontend automatically — no separate web server is needed" | In dev mode, Vite serves the frontend on port 5173 with proxy to engine on 8000 | Stale workflow |

**Recommendation:** Add Vite dev server instructions. Update test command.

---

## 25. docs/REVERT_UI_PLAN.md

**Status:** ✅ Aligned (historical document)

This is a plan document for a specific branch operation. Per repo memories, the revert described here was completed. Section 7 claims "AgentForgeUI_Image References" folder does not exist — but it **does exist** now (with 14 JPEG files added in commit cfb9df2).

| # | Note | Issue |
|---|---|---|
| 1 | Section 7: "This folder does not exist in the repository" | **Incorrect** — `AgentForgeUI_Image References/` exists with 14 images | Stale claim |

**Recommendation:** Mark this doc as historical/completed. Correct Section 7 note about the image references folder.

---

## 26. docs/PHASE_AUDIT.md (also docs/PHASE10_COMPLIANCE.md, docs/PHASE7-10_REPORT.md)

**Status:** ⚠️ Partially Aligned

| # | Claim in Doc | Actual State | Issue |
|---|---|---|---|
| 1 | Phase 6 references `frontend/index.html` as five-region layout | index.html is now a React bootstrap | Stale |
| 2 | Phase 8 correctly says `manifest.json` | ✅ Matches | OK |
| 3 | PHASE10_COMPLIANCE says 173 tests, uses unittest command | 187 tests, pytest command | Stale |
| 4 | No mention of V2 system phases | V2 is a significant addition | Missing |

**Recommendation:** These are historical audit/compliance docs. Add a note that V2 work is tracked separately, or update to include V2.

---

## 27. docs/archive/ (BOOTSTRAP_PROMPT, BOOTSTRAP_PLAN, BUILD_BIBLE_V2)

**Status:** ✅ Properly Archived

These are clearly marked as archived historical documents.

| Doc | Note |
|---|---|
| `AGENTFORGE_BOOTSTRAP_PROMPT.md` | References reading order for original bootstrap — historical | 
| `BOOTSTRAP_PLAN.md` | Phase-by-phase build plan — historical |
| `BUILD_BIBLE_V2.md` | V2 target architecture spec — **still actively relevant** as the V2 implementation reference |

**Recommendation:** `BUILD_BIBLE_V2.md` is still actively referenced by V2 docs. Consider moving it out of `archive/` back to main `docs/`, or add a note that it is still active despite being in archive.

---

## 28. docs/legacy/ (V1_SYSTEM_BIBLE, phases/)

**Status:** ✅ Properly Archived

| Doc | Note |
|---|---|
| `AGENTFORGE_V1_SYSTEM_BIBLE.md` | V1 system bible — historical, superseded by V2 | 
| `phases/PHASE_AUDIT.md` | Duplicate of `docs/PHASE_AUDIT.md` — content identical |
| `phases/PHASE7-10_REPORT.md` | Duplicate of `docs/PHASE7-10_REPORT.md` — content identical |
| `phases/PHASE10_COMPLIANCE.md` | Duplicate of `docs/PHASE10_COMPLIANCE.md` — content identical |

**Recommendation:** The three phase docs exist in **both** `docs/` and `docs/legacy/phases/`. This creates confusion about which is authoritative. Consider removing the duplicates from `docs/` root (keeping them only in `docs/legacy/phases/`) since they are historical.

---

## Cross-Document Inconsistencies

### Module Config Filename

| Document | Says | Actual |
|---|---|---|
| `STUDIO_MODULE_SYSTEM.md` | `module_config.json` | **`manifest.json`** |
| `AI_DEVELOPMENT_RULES.md` | `module_config.json` | **`manifest.json`** |
| `BUILD_STATUS.md` | `manifest.json` | ✅ Correct |
| `PHASE_AUDIT.md` | `manifest.json` | ✅ Correct |

### Test Command

| Document | Says | Actual |
|---|---|---|
| `README.md` | `python -m unittest discover -s tests` | `python -m pytest tests/ -v` |
| `LOCAL_RUN_CHECKLIST.md` | `python -m unittest discover -s tests` | `python -m pytest tests/ -v` |
| `PHASE10_COMPLIANCE.md` | `python -m unittest discover -s tests` | `python -m pytest tests/ -v` |

### Frontend State

| Document | Says | Actual |
|---|---|---|
| `REPOSITORY_STRUCTURE.md` | Static scaffold in `frontend/index.html + frontend/style.css` | Full React+Vite app |
| `SYSTEM_ARCHITECTURE.md` | Phase 6 scaffold in index.html/style.css | Full React+Vite app |
| `AGENTFORGE_OS_SPEC.md` | Phase 6 static scaffold | Full React+Vite app |
| `BUILD_STATUS.md` | Five-region layout in index.html | index.html is React bootstrap only |

### Agent System

| Document | Covers | Missing |
|---|---|---|
| `AI_PIPELINE_SYSTEM.md` | Original 12 agents (Planner→Stabilizer) | V2 12 agents (Origin→Chronicle) |
| `V2_EXECUTION_MODEL.md` | V2 12 agents (Origin→Chronicle) | — |
| Both exist but are **not cross-referenced** | | Need linking |

### Repository Structure

| Document | Dirs Listed | Actual Dir Count |
|---|---|---|
| `README.md` | 13 | 25 |
| `REPOSITORY_STRUCTURE.md` | 10 | 25 |
| `AGENTFORGE_OS_SPEC.md` | 10 | 25 |
| `archive/BUILD_BIBLE_V2.md` | 13 | 25 |

---

## Duplicate Content

| File A | File B | Status |
|---|---|---|
| `docs/PHASE_AUDIT.md` | `docs/legacy/phases/PHASE_AUDIT.md` | **Identical** — duplicate |
| `docs/PHASE7-10_REPORT.md` | `docs/legacy/phases/PHASE7-10_REPORT.md` | **Identical** — duplicate |
| `docs/PHASE10_COMPLIANCE.md` | `docs/legacy/phases/PHASE10_COMPLIANCE.md` | **Identical** — duplicate |

**Recommendation:** Keep one copy of each. Since these are historical, `docs/legacy/phases/` is the natural home.

---

## Undocumented Directories & Components

These exist in the repo but have **no documentation** in `docs/`:

| Directory | Contents | Purpose |
|---|---|---|
| `orchestration/` | `engine.py`, `runtime.py`, `task_model.py` | V2 task-graph orchestration engine |
| `build_system/` | `recursive_loop.py`, `simulation_engine.py` | Build simulation and recursive loops |
| `infrastructure/` | `local_bridge.py`, `model_router.py` | Local bridge and model routing |
| `models/` | `settings.py` | Settings model |
| `backend/` | `server.py`, `agents/`, `control/`, `knowledge/`, `services/`, `systems/`, tests | Alternative backend layout (may be legacy) |
| `agents/v2/` | 13 V2 agent files | V2 agent implementations |
| `research/` | (needs verification) | Research module root |
| `memory/` | `.gitkeep`, `README.md` | Memory storage placeholder |
| `projects/session_default/` | Full project artifact tree | Default project workspace |
| `AgentForgeUI_Image References/` | 14 UI wireframe JPEGs + info txt | Visual design references |
| `.emergent/` | `emergent.yml` | Emergent system config |

---

## Priority Action Items

### 🔴 High Priority (causes confusion / leads to wrong implementations)

1. **REPOSITORY_STRUCTURE.md** — Rewrite to list all 25 directories with descriptions
2. **STUDIO_MODULE_SYSTEM.md** — Fix `module_config.json` → `manifest.json`, update module structure and frontend location
3. **AI_DEVELOPMENT_RULES.md** — Fix `module_config.json` → `manifest.json`
4. **SYSTEM_API_CONTRACTS.md** — Add V2 endpoints, module endpoints, and WebSocket contract
5. **CONTROL_LAYER.md** — Document all 12 control layer components

### 🟡 Medium Priority (stale info but doesn't break anything)

6. **README.md** — Update project structure, test command, frontend workflow, endpoint list, doc table
7. **SYSTEM_ARCHITECTURE.md** — Add V2 layers, update frontend description
8. **BUILD_STATUS.md** — Update test count/command, frontend description, add V2 tracking
9. **SYSTEM_CAPABILITY_MAP.md** — Add V2 capabilities, update frontend, recount totals
10. **AI_PIPELINE_SYSTEM.md** — Add V2 reference, fix stale Phase 4 language, fix `pipeline_config.json` ref
11. **LOCAL_RUN_CHECKLIST.md** — Add Vite dev server instructions, update test command
12. **ARCHITECTURE_DECISION_RECORDS.md** — Add ADRs for V2 decisions
13. **AGENTFORGE_OS_SPEC.md** — Update throughout to match current state

### 🟢 Low Priority (cleanup / nice-to-have)

14. **Duplicate phase docs** — Consolidate into `docs/legacy/phases/` only
15. **REVERT_UI_PLAN.md** — Correct Section 7 about image references folder
16. **archive/BUILD_BIBLE_V2.md** — Consider moving out of archive since it's still active
17. **PROVIDER_IMPLEMENTATION_GUIDE.md** — Add NoOp provider
18. **UI_LAYOUT_FUNCTIONAL_SPEC.md** — Fix file structure path prefix
19. **UI_HOOKUP_CHECKLIST.md** — Re-verify task statuses against current branch

---

## Summary Statistics

| Category | Count |
|---|---|
| Total docs audited | 28 |
| ✅ Fully Aligned | 10 |
| ⚠️ Partially Aligned | 15 |
| ❌ Misaligned | 1 (REPOSITORY_STRUCTURE.md) |
| Duplicate files found | 3 pairs |
| Undocumented directories | 11 |
| Cross-doc inconsistencies | 4 categories |
| Action items | 19 |

---

*End of Documentation Audit Report*
