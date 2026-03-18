# AgentForgeOS UI Layout & Functional Specification

## Overview

AgentForgeOS is a 5-panel resizable developer operating system interface with 8 module panels, 12 AI agents, and a comprehensive build pipeline visualization.

---

## Layout Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         TOP NAVIGATION BAR                          │
│  [AF Logo] AgentForgeOS    [Project][Workspace][Providers][System][Settings][Profile]
├─────────────────┬───────────────────────────────────────────────────┤
│                 │                                                   │
│    SIDEBAR      │              MAIN WORKSPACE                       │
│    (240px)      │              (Dynamic Content)                    │
│                 │                                                   │
│  ▸ Studio       │    Module-specific panels render here             │
│  ▸ Build Pipes  │                                                   │
│  ▸ Research     │                                                   │
│  ▸ Assets       │                                                   │
│  ▸ Deployment   │                                                   │
│  ▸ Sandbox      │                                                   │
│  ▸ Game Dev     │                                                   │
│  ▸ SaaS Builder │                                                   │
│                 │                                                   │
├─────────────────┼─────────────────────────┬───────────────────────┤
│  AGENT CONSOLE  │   PIPELINE MONITOR      │      OUTPUT LOG        │
│  (Chat + 12     │   (12 Agent Stages)     │   (Real-time logs)     │
│   Agent Avatars)│                         │                        │
└─────────────────┴─────────────────────────┴────────────────────────┘
```

### Panel Resizing

| Divider | Panels |
|---------|--------|
| Horizontal | Sidebar ↔ Workspace, Console ↔ Pipeline ↔ Log |
| Vertical | Top section ↔ Bottom section |

All panels are fully adjustable via drag handles.

---

## Top Navigation Bar

| Element | Function |
|---------|----------|
| AF Logo | Hexagon logo with "AF" letters |
| AgentForgeOS | Brand text (Exo 2 font, 700 weight) |
| Project | Project management dropdown (placeholder) |
| Workspace | Workspace settings (placeholder) |
| Providers | AI provider configuration (placeholder) |
| System | System status/health (placeholder) |
| Settings | App settings (placeholder) |
| Profile | User profile (placeholder) |

---

## Sidebar (Left Panel)

### Module Navigation

8 clickable module buttons with icons:

| Module | Icon | Description |
|--------|------|-------------|
| Studio | Layout | Project workspace and file management |
| Build Pipelines | Layers | Manage and trigger build pipelines |
| Research | FlaskConical | Knowledge graph and research notes |
| Assets | ImageIcon | Generated assets registry |
| Deployment | Rocket | Deploy projects to targets |
| Sandbox | Box | Agent experimentation environment |
| Game Dev | Gamepad2 | Game development assistant |
| SaaS Builder | Building2 | End-to-end SaaS scaffolding |

### Active State

- Red border with pulse animation
- Red left indicator bar
- Icon color changes to red

---

## Main Workspace Modules

### 1. STUDIO (Default)

**Purpose:** Project file browser and workspace management

**Components:**

- **Breadcrumb Navigation:** `workspace > folder > subfolder`
- **File Browser:** List of files/directories with icons
  - Directories: `FolderOpen` icon, clickable
  - Markdown: `FileText` icon
  - Code files: `FileCode` icon
  - Other: `File` icon
- **File Size Display:** Shows KB/MB for files

**Functions:**

```js
loadFiles(path)     // Navigate to directory
```

**Mock Data:**

```json
[
  { "name": "backend", "type": "directory" },
  { "name": "frontend", "type": "directory" },
  { "name": "tests", "type": "directory" },
  { "name": "README.md", "type": "file", "size": 1024 },
  { "name": "package.json", "type": "file", "size": 2048 }
]
```

---

### 2. BUILD PIPELINES

**Purpose:** Trigger and monitor build pipelines

**Components:**

- **Project Name Input:** Text field
- **Trigger Build Button:** Creates new build
- **Build List:** Shows all builds with status

**Status Badges:**

| Status | Color |
|--------|-------|
| queued | Blue |
| running | Yellow |
| success | Green |
| failed | Red |

**Functions:**

```js
triggerBuild()      // Create new build entry
loadRuns()          // Fetch build history
```

**Mock Data:**

```json
[
  { "id": "build_001", "project": "AgentForgeOS", "status": "success" },
  { "id": "build_002", "project": "Studio Module", "status": "running" }
]
```

---

### 3. RESEARCH (Nodular Graph)

**Purpose:** Knowledge graph with draggable nodes and file drop support

**Components:**

- **Node Toolbar:**
  - Doc button — Add document node
  - API button — Add API node
  - DB button — Add database node
  - Drop zone hint
- **Node Canvas:** Draggable node workspace
- **Connection Lines:** SVG lines between connected nodes

**Node Types:**

| Type | Icon | Color |
|------|------|-------|
| document | FileText | Blue (`#60a5fa`) |
| api | Globe | Green (`#4ade80`) |
| database | Database | Orange (`#f59e0b`) |
| image | ImageIcon | Purple (`#c084fc`) |
| audio | Zap | Red (`#f87171`) |

**Functions:**

```js
handleDrop(e)           // Process dropped files
handleNodeMouseDown()   // Start dragging node
handleMouseMove()       // Update node position
addNewNode(type)        // Create new node
deleteNode(id)          // Remove node and connections
```

**Mock Data:**

```json
[
  { "id": 1, "type": "document", "title": "Architecture Patterns", "x": 50, "y": 50, "connections": [2] },
  { "id": 2, "type": "api", "title": "API Design Notes", "x": 300, "y": 80, "connections": [3] },
  { "id": 3, "type": "database", "title": "Schema Definitions", "x": 200, "y": 200, "connections": [] }
]
```

---

### 4. ASSETS

**Purpose:** Registry of generated assets

**Components:**

- **Asset List:** Shows registered assets with type badges

**Asset Types:**

| Type | Badge Color |
|------|-------------|
| image | Purple |
| audio | Purple |

**Mock Data:**

```json
[
  { "type": "image", "path": "/assets/logo.png", "source": "Generated" },
  { "type": "audio", "path": "/assets/notification.mp3", "source": "TTS Provider" },
  { "type": "image", "path": "/assets/icon_set.svg", "source": "Generated" }
]
```

---

### 5. DEPLOYMENT

**Purpose:** Deploy projects to various targets

**Components:**

- **Project Input:** Project name
- **Version Input:** Version string
- **Target Selector:** Dropdown (`local` / `staging` / `production`)
- **Deploy Button:** Red danger-styled button
- **Deployment History:** List with status badges

**Functions:**

```js
deploy()            // Create new deployment
```

**Mock Data:**

```json
[
  { "id": "dep_001", "project": "AgentForgeOS", "version": "1.0.0", "target": "staging", "status": "done" }
]
```

---

### 6. SANDBOX (Emergent-Inspired)

**Purpose:** Agent experimentation with live preview

**Layout:** 3-column grid

```
┌──────────────┬─────────────────────┬──────────────┐
│ BUILD        │    LIVE PREVIEW     │   OUTPUT     │
│ PIPELINE     │                     │   CONSOLE    │
│              │                     │              │
│ ● Initialize │   [Preview Area]    │ > logs...    │
│ ● Parse      │                     │              │
│ ○ Generate   │                     │              │
│ ○ Validate   │                     │              │
│ ○ Deploy     │                     │              │
└──────────────┴─────────────────────┴──────────────┘
│          [Prompt Input Area]                       │
│                           [Reset] [Run Experiment] │
└────────────────────────────────────────────────────┘
```

**Build Pipeline Steps:**

1. Initialize *(pre-done)*
2. Parse Request *(pre-done)*
3. Generate
4. Validate
5. Deploy

**Step Status:**

| Status | Indicator |
|--------|-----------|
| done | Green filled circle |
| running | Spinner animation |
| idle | Empty circle |

**Functions:**

```js
runExperiment()     // Start build simulation
resetSandbox()      // Clear state and preview
```

**Console Output Types:**

| Type | Style |
|------|-------|
| system | Gray text |
| user | Red text (prompt) |
| info | Blue text |
| success | Green text |
| error | Red text |

---

### 7. GAME DEV

**Purpose:** Game development project management

**Components:**

- **Title Input:** Game title
- **Genre Input:** Game genre
- **Platform Selector:** Dropdown
  - cross-platform
  - PC
  - mobile
  - web
- **Create Design Doc Button**
- **Project List:** Shows game projects

**Functions:**

```js
createDesign()      // Create new game design document
```

**Mock Data:**

```json
[
  { "id": "game_001", "title": "Cyber Runner", "genre": "platformer", "platform": "cross-platform", "status": "done" }
]
```

---

### 8. SAAS BUILDER

**Purpose:** End-to-end SaaS project scaffolding

**Components:**

- **Name Input:** Project name
- **Frontend Stack Selector:** React / Vue / Svelte
- **Backend Stack Selector:** FastAPI / Express / Django
- **Scaffold Project Button**
- **Project List:** Shows SaaS projects

**Functions:**

```js
scaffold()          // Create new SaaS project scaffold
```

**Mock Data:**

```json
[
  { "id": "saas_001", "name": "TaskFlow Pro", "stack": { "frontend": "react", "backend": "fastapi" }, "status": "done" }
]
```

---

## Bottom Panels

### AGENT CONSOLE (Left)

**Purpose:** Chat interface with 12 AI agents

**Components:**

- **Agent Selector Row:** 6 avatar chips + "+6" indicator
- **Message List:** Chat messages with avatars
- **Prompt Input:** Textarea for user input
- **Send Button:** Submit prompt

**12 Core Agents:**

| ID | Name | Short Name |
|----|------|------------|
| planner | Project Planner | Planner |
| architect | System Architect | Architect |
| router | Task Router | Router |
| builder | Module Builder | Builder |
| api | API Architect | API |
| data | Data Architect | Data |
| backend | Backend Engineer | Backend |
| frontend | Frontend Engineer | Frontend |
| ai | AI Integration Engineer | AI Eng |
| tester | Integration Tester | Tester |
| auditor | Security Auditor | Auditor |
| stabilizer | System Stabilizer | Stabilizer |

**Message Types:**

| Type | Style |
|------|-------|
| user | Right-aligned, red border |
| agent | Left-aligned, with avatar |

**Functions:**

```js
sendMessage(e)      // Send prompt to agent
getAgent(id)        // Get agent by ID
```

**Typing Animation:** 3 bouncing dots

---

### PIPELINE MONITOR (Center)

**Purpose:** Display all 12 agent stages

**Pipeline Stages (chips):**

```
Project Planner | System Architect | Task Router | Module Builder
API Architect | Data Architect | Backend Engineer | Frontend Engineer
AI Integration Engineer | Integration Tester | Security Auditor | System Stabilizer
```

**Active State:** Red border with pulse animation

---

### OUTPUT LOG (Right)

**Purpose:** Real-time system logging

**Log Entry Format:**

```
[TIME] [LEVEL] Message
07:03:37 AM [INFO] AgentForgeOS initialized
```

**Log Levels:**

| Level | Color |
|-------|-------|
| info | Blue |
| warn | Yellow |
| error | Red |
| success | Green |

**Functions:**

```js
addLog(level, message)    // Add log entry (max 50 entries)
```

---

## Styling Reference

### Color Palette

```css
--bg-void: #050507;
--bg-deep: #0a0a0c;
--bg-surface: #0f0f12;
--bg-elevated: #141418;
--bg-card: #1a1a1f;

--border-subtle: #1f1f26;
--border-default: #2a2a33;
--border-hover: #3a3a45;

--text-primary: #f5f5f7;
--text-secondary: #a1a1aa;
--text-muted: #71717a;

--accent-red: #dc2626;
--accent-red-hover: #ef4444;
--accent-red-dim: rgba(220, 38, 38, 0.15);

--status-success: #22c55e;
--status-warning: #f59e0b;
--status-error: #ef4444;
--status-info: #3b82f6;
```

### Typography

| Role | Font | Weight |
|------|------|--------|
| Display/Headings | Exo 2 | 700 |
| Body | Inter | 400–500 |
| Monospace/Code | JetBrains Mono | — |

### Animations

| Name | Duration | Usage |
|------|----------|-------|
| border-pulse | 3s ease-in-out | Active items |
| dot-pulse | 1.5s | Status indicators |
| typing-bounce | 1.4s | Chat typing dots |
| spin | 0.8s | Loading spinners |

---

## API Endpoints (Mocked)

All endpoints return mock data from local state:

```
GET  /api/bridge/list?path={path}       # File browser
GET  /api/modules/builds/runs           # Build history
POST /api/modules/builds/trigger        # Trigger build
GET  /api/modules/research/notes        # Research notes
POST /api/modules/research/notes        # Add note
POST /api/modules/research/search       # Search notes
GET  /api/modules/assets/list           # Asset list
GET  /api/modules/deployment/list       # Deployment history
POST /api/modules/deployment/deploy     # Deploy
GET  /api/modules/sandbox/experiments   # Experiments
POST /api/modules/sandbox/run           # Run experiment
GET  /api/modules/game_dev/projects     # Game projects
POST /api/modules/game_dev/design       # Create design
GET  /api/modules/saas_builder/projects # SaaS projects
POST /api/modules/saas_builder/scaffold # Scaffold project
POST /api/agent/run                     # Agent prompt
```

---

## File Structure

```
/app/frontend/src/
├── App.js          # Main component with all modules
├── App.css         # Module-specific styles
├── index.css       # Base styles, variables, fonts
└── components/ui/  # Shadcn UI components
    └── resizable.jsx  # Resizable panel component
```

---

*End of Specification*
