# AgentForge V2 Build Bible

> NOTE: This document captures the V2 specification provided on March 17, 2026. It is used as a target architecture for future implementation and audits.

==================================================
PRIMARY DIRECTIVE
==================================================

Implement AgentForge as an AI engineering platform capable of planning, simulating, building, testing, and deploying software products and games through a structured multi-agent workflow.

The system must support:
- freeform user command input
- required build simulation before execution
- architecture preview and feasibility review
- recursive build loops
- local execution for Unity, Unreal, and Web projects
- research ingestion and build autopsy learning

Do not deviate from these goals.

==================================================
NON-NEGOTIABLE ANTI-DRIFT RULES
==================================================

You MUST obey all of the following:

1. Do NOT modify the 3-page frontend architecture.
2. Do NOT remove the 12-agent system.
3. Do NOT bypass the orchestration engine.
4. Do NOT start builds without simulation approval.
5. Do NOT collapse agent roles into a single agent.
6. Do NOT change the repository structure.
7. Do NOT merge multiple systems into one generic service.
8. Do NOT replace the multi-agent workflow with a simpler chatbot loop.
9. Do NOT replace the task graph with ad hoc agent calls.
10. Do NOT invent extra top-level product pages.
11. Do NOT implement a different data model than the one implied here.
12. Do NOT output partial examples only. Create real files and real structure.

If there is any uncertainty, choose the option that preserves the exact Build Bible architecture.

==================================================
REPOSITORY STRUCTURE (MANDATORY)
==================================================

Create or preserve this exact root repository layout:

frontend/
backend/
agents/
orchestration/
build_system/
knowledge/
research/
infrastructure/
models/
memory/
projects/
tests/
scripts/
docs/

Do not rename these directories.
Do not collapse them.
Do not move their responsibilities elsewhere.

==================================================
PRODUCT ARCHITECTURE OVERVIEW
==================================================

AgentForge must operate as a structured AI engineering organization, not a single monolithic assistant.

Core system requirements:
- architecture-first development
- simulation required before build
- 12 specialized agents with strict roles
- recursive build improvement loop
- persistent knowledge graph memory
- local execution bridge for game engines
- controlled orchestration engine
- AI model routing layer through fal.ai-compatible routing logic

==================================================
FRONTEND ARCHITECTURE (STRICTLY 3 PAGES ONLY)
==================================================

The frontend MUST be limited to exactly these 3 pages:

1. Command Center
2. Project Workspace
3. Research & Knowledge Lab

Do not create additional core pages.
Modal panels, dialogs, drawers, and overlays are acceptable only as sub-UI inside these pages.

Frontend stack:
- React
- TypeScript
- TailwindCSS
- ShadCN-style component structure
- Framer Motion where useful
- Monaco Editor in workspace
- WebSocket-ready architecture for live agent updates

--------------------------------------------------
PAGE 1: COMMAND CENTER
--------------------------------------------------

Purpose:
This is the primary operational dashboard where the user submits commands, reviews build simulation, sees agent activity, and tracks build queue.

Required subareas:
- command input
- simulation report
- agent activity
- build queue
- task graph / architecture preview
- live execution status

Required layout behavior:
- clear command entry area
- visible simulation and feasibility output before any build
- visible task planning / graph output from orchestration
- visible agent activity stream
- visible build queue
- dark, high-signal, system-control aesthetic
- layout should feel like an AI operations console, not a generic dashboard

Required components to implement:
- CommandInput
- SimulationReport
- TaskGraphView
- AgentActivityPanel
- BuildQueue
- status summaries / execution indicators as needed

CommandCenter file requirements:
- fully implemented page component
- realistic mock state if backend is not yet fully connected
- structured to consume real backend data without rewrite later

--------------------------------------------------
PAGE 2: PROJECT WORKSPACE
--------------------------------------------------

Purpose:
This is the execution workspace for viewing and interacting with project files, architecture, code, history, and engine launch controls.

Required functional zones:
- editor area
- architecture view or system view
- build history
- engine launch controls
- live logs or execution stream
- file navigation / project structure access

Required technologies:
- Monaco Editor for code editing area
- room for local bridge actions such as launch Unity / launch Unreal
- log display panel
- project-aware layout, not a generic text editor

Required components and areas:
- file explorer / project tree
- Monaco editor panel
- log stream
- architecture panel and/or build history panel
- engine launch section

ProjectWorkspace file requirements:
- must be structured to support local project execution
- must visually represent that projects can run locally
- should make room for future local sync and engine launch integration

--------------------------------------------------
PAGE 3: RESEARCH & KNOWLEDGE LAB
--------------------------------------------------

Purpose:
This page handles research ingestion and memory visualization.

Required functional zones:
- research ingestion controls
- uploaded source handling
- documentation / PDF / transcript ingestion entry points
- knowledge graph or memory visualization
- research insights browsing

Required behavior:
- user can conceptually ingest GitHub repos, PDFs, docs, video transcripts
- extracted techniques and architecture patterns must have a place to surface
- knowledge graph / memory visualization must feel like a first-class system

Required components and areas:
- ingestion panel
- memory / graph visualization panel
- research insights panel or equivalent
- source intake UI

==================================================
BACKEND CORE SYSTEMS (MANDATORY)
==================================================

Backend must include and separate the following core systems:

1. API Layer
2. Orchestration Engine
3. Agent System
4. Recursive Builder Engine
5. Knowledge Graph System
6. Research Ingestion System
7. Execution Infrastructure
8. Local Bridge System
9. Model Routing Layer

Use FastAPI for the API layer.

Do not collapse these into one file or one generic service.

--------------------------------------------------
API LAYER
--------------------------------------------------

Implement a FastAPI backend that exposes structured endpoints for:
- command submission
- simulation request / retrieval
- task graph retrieval
- agent activity retrieval
- build queue retrieval
- research ingestion initiation
- settings retrieval / update
- local bridge actions where appropriate
- health / status endpoints

API design rules:
- use clear route separation
- return structured JSON models
- preserve future WebSocket compatibility for live updates

--------------------------------------------------
ORCHESTRATION ENGINE
--------------------------------------------------

This is mandatory and central.

Responsibilities:
- parse user commands
- convert requests into structured tasks
- generate task graphs
- enforce dependency handling
- coordinate agent dispatch
- ensure simulation occurs before build execution
- collect structured outputs from agents
- coordinate recursive refinement loop

Rules:
- all tasks pass through orchestration engine
- agents never communicate directly with each other
- orchestration is the only legal coordination path

Required orchestration concepts:
- task creation
- dependency fields
- task status
- agent assignment
- structured inputs
- structured outputs

You must implement an orchestration controller and task graph model.

--------------------------------------------------
AGENT SYSTEM (MANDATORY 12 AGENTS)
--------------------------------------------------

You MUST implement exactly these 12 specialized agents with strict roles:

1. Commander
   - interprets commands
   - coordinates builds
   - supervises task chain

2. Atlas
   - architecture design

3. Forge
   - code generation

4. Frontend Engineer
   - UI systems

5. Backend Engineer
   - API and services

6. Game Engine Engineer
   - Unreal / Unity gameplay integration

7. AI Engineer
   - model routing and inference pipelines

8. Prism
   - asset generation

9. Sentinel
   - security and architecture validation

10. Probe
   - testing and simulation

11. DevOps Engineer
   - deployment

12. Research Agent
   - research ingestion

Implementation rules for agents:
- each agent must have its own file
- each agent must have a defined role matching the list above
- each agent must accept structured task input
- each agent must return structured output
- no direct agent-to-agent communication
- Commander coordinates the chain through orchestration only

Do not reduce this to generic “tool handlers.”
Do not replace named roles with abstract classes only.
Do not omit behavioral stubs.

--------------------------------------------------
BUILD SIMULATION ENGINE
--------------------------------------------------

This is required before build execution.

Simulation engine responsibilities:
- parse project requirements
- estimate module complexity
- predict build duration
- predict project size
- generate architecture preview
- produce feasibility report

Rules:
- simulation approval must occur before build starts
- UI must visibly expose the simulation report
- orchestration must respect simulation gating

Implement:
- simulation service/module
- response schema for complexity, duration, project size, architecture preview, feasibility
- connection from command submission to simulation output

--------------------------------------------------
RECURSIVE BUILD LOOP
--------------------------------------------------

Implement the recursive build loop with these explicit stages:

- Plan
- Build
- Test
- Review
- Refine
- Rebuild

Rules:
- this is not optional
- it must exist as a formal system, not just comments
- orchestration must be able to invoke or represent this loop
- outputs from one stage should feed the next
- review/refine should prepare future iteration

==================================================
KNOWLEDGE GRAPH ARCHITECTURE
==================================================

Implement the knowledge system with support for these memory categories:

- architecture_patterns
- code_templates
- bug_patterns
- optimization_patterns
- gameplay_systems
- research_insights
- project_genomes

Storage architecture target:
- graph database layer concept compatible with Neo4j
- vector database layer concept compatible with Qdrant
- embedding-compatible ingestion pathway

You may scaffold adapters or interfaces if full infra is not yet connected, but you must preserve the architecture.

Knowledge system responsibilities:
- store insights
- retrieve patterns
- persist reusable architectural memory
- support research-derived knowledge
- support build autopsy learning

==================================================
RESEARCH INGESTION SYSTEM
==================================================

Implement a research ingestion system that can accept conceptually:

- GitHub repos
- PDFs
- documentation
- video transcripts

Responsibilities:
- extract techniques
- extract architecture patterns
- store insights in the knowledge graph
- expose ingestion entrypoints in backend and UI

Do not reduce research ingestion to just file upload.
Do not omit extraction pipeline placeholders and schemas.

==================================================
LOCAL BRIDGE SYSTEM
==================================================

Implement a Local Bridge system with architecture to support:

- syncing projects to local machine
- launching Unity Editor
- launching Unreal Editor
- compiling game builds
- streaming logs to Command Center

Rules:
- local bridge must be limited to project directory
- command execution must be whitelisted
- no direct filesystem access outside project directories

UI and backend must both reserve real space for this system.

==================================================
PROJECT DIRECTORY STRUCTURE
==================================================

Generated local projects must be compatible with this structure:

C:/AgentForgeProjects/
- unity/
- unreal/
- web/
- mobile/
- ai_apps/

Represent this in configuration and local bridge logic.
Make pathing configurable in settings.

==================================================
TASK GRAPH PROTOCOL
==================================================

All tasks must follow a structured protocol.

Each task should conceptually include:
- task_id
- assigned_agent
- dependencies
- inputs
- outputs
- status

Rules:
- all tasks pass through orchestration engine
- agents never communicate directly
- tasks have dependency fields
- agents return structured outputs
- Commander coordinates task chain

Implement a task model and supporting types for this protocol.

==================================================
MODEL ROUTING LAYER
==================================================

Implement model routing logic that preserves these route intentions:

- Code generation -> DeepSeek / CodeLlama style route
- Images -> Flux style route
- 3D assets -> Shap-E style route
- Voice -> Bark style route
- Audio -> AudioCraft style route

Rules:
- routing controlled by AI Engineer-related system logic
- keep the routing layer abstracted so providers can be swapped later
- do not bury model decisions inside unrelated services

==================================================
SETTINGS CONFIGURATION
==================================================

Implement settings support for:

- Unity Editor Path
- Unreal Engine Path
- Local Project Directory
- Local Bridge Port
- Auto Launch Editor Toggle
- Enable Simulation Mode

Requirements:
- settings must exist in backend schema and frontend UI representation
- settings must support future persistence
- settings must be clearly separated from execution logic

==================================================
EXECUTION SAFETY RULES
==================================================

Must be preserved in code architecture:

- local bridge limited to project directory
- command whitelist for engine execution
- all builds sandboxed in Docker
- no direct filesystem access outside project directories

Do not ignore these.
Create safety-oriented abstractions or guards where needed.

==================================================
IMPLEMENTATION EXPECTATIONS
==================================================

You are expected to generate:

1. Full frontend page files
2. Required frontend components
3. App-level routing or page switching for the 3 required pages
4. FastAPI backend scaffolding and route modules
5. Orchestration engine files
6. Task graph models
7. Agent base class and 12 agent files
8. Simulation engine scaffolding
9. Recursive build loop scaffolding
10. Knowledge graph abstractions
11. Research ingestion modules
12. Local bridge modules
13. Model routing modules
14. Settings models/services
15. Basic tests
16. Clear imports and compile-safe structure

==================================================
CODE QUALITY RULES
==================================================

- Use production-style naming
- Use TypeScript types for frontend data models
- Use Python typing where useful
- Keep responsibilities separated by folder
- Do not leave empty placeholder files
- Do not output pseudocode only
- Implement working scaffolds with realistic state and interfaces
- Where backend integration is not complete, use structured mock data that matches final schemas
- Ensure all imports resolve
- Ensure the project compiles after generation
- Preserve expandability without changing architecture later
