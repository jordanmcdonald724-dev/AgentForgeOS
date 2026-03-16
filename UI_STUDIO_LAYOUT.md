# AgentForgeOS — Studio UI Layout Specification

Purpose:
Define the exact user interface structure for AgentForgeOS to prevent UI drift and inconsistent dashboards when AI agents generate frontend code.

The UI must follow this layout specification exactly.

---

# 1. Design Principles

AgentForgeOS Studio is designed as a **multi-pane development command center** similar to professional IDEs and control systems.

The interface must support:

• multi-pane layout
• adjustable panels
• persistent workspace state
• modular tool panels
• real-time agent monitoring

The UI must always remain structured and predictable.

---

# 2. Core Layout

The Studio UI uses a **five region layout**.

```
┌───────────────────────────────────────────────┐
│ Top Navigation Bar                            │
├───────────────┬───────────────────────────────┤
│ Left Sidebar  │ Main Workspace                │
│               │                               │
│               │                               │
├───────────────┼───────────────────────────────┤
│ Agent Console │ Pipeline / System Monitor     │
└───────────────┴───────────────────────────────┘
```

Regions:

Top Navigation Bar
Left Sidebar
Main Workspace
Agent Console
System Monitor

---

# 3. Top Navigation Bar

Location:

Top of the interface.

Purpose:

Provide global navigation and system controls.

Components:

• Project selector
• Workspace switcher
• System status indicator
• AI provider status
• Settings access
• User profile

Example layout:

```
[AgentForgeOS] [Project ▼] [Workspace ▼] [Providers] [System Status] [Settings]
```

---

# 4. Left Sidebar

Location:

Left side of the screen.

Purpose:

Primary navigation for all system modules.

Modules must appear here.

Example items:

Studio
Build Pipelines
Research
Assets
Deployment
Sandbox
Game Dev
SaaS Builder
System Logs

Sidebar rules:

• collapsible
• icons + labels
• reorderable modules
• persistent layout

---

# 5. Main Workspace

Location:

Center of the interface.

Purpose:

Primary development workspace.

This area changes based on the active module.

Examples:

Studio module:

• project files
• agent interaction
• build configuration

Research module:

• document ingestion
• knowledge graph viewer

Asset module:

• image generation
• audio generation

Workspace must support:

• tabbed editing
• multiple panels
• drag-to-split layout

---

# 6. Agent Console

Location:

Bottom-left panel.

Purpose:

Interact with AI agents.

Features:

• multi-line prompt input
• prompt history
• agent responses
• execution logs

Example layout:

```
Agent Console

> Ask the AI team to generate a system module...

[Prompt Input Box]
[Send]
```

Console must support:

• expandable height
• markdown rendering
• code block formatting

---

# 7. Pipeline Monitor

Location:

Bottom-right panel.

Purpose:

Visualize agent execution pipelines.

Displays:

• active agents
• task queue
• pipeline stages
• execution logs

Example display:

```
Pipeline Status

Planner → Architect → Builder → Tester → Stabilizer

Current Stage: Builder
```

This panel must update in real time.

---

# 8. Adjustable Pane System

The UI must support fully adjustable panels.

Implementation recommendation:

```
react-resizable-panels
```

Capabilities:

• drag-to-resize
• hide/show panels
• save layout state
• restore layout on restart

Example adjustable layout:

```
Sidebar width adjustable
Console height adjustable
Workspace panels resizable
```

---

# 9. Multi-Panel Workspace

The main workspace must support panel splitting.

Example layout:

```
┌─────────────┬─────────────┐
│ Editor      │ Graph View  │
│             │             │
├─────────────┴─────────────┤
│ Logs / Results            │
└───────────────────────────┘
```

Users can split panels:

Horizontal
Vertical

Panels may contain:

• code editor
• graph viewer
• asset viewer
• build logs

---

# 10. Theme System

AgentForgeOS Studio must support a dark developer theme.

Example styling:

Background:

```
#0f1115
```

Primary panels:

```
#161a22
```

Accent color:

```
#5b8cff
```

Typography:

```
Inter
JetBrains Mono
```

---

# 11. Status Indicators

The UI must display system health.

Indicators:

AI Providers

```
LLM: Connected
Image: Connected
TTS: Offline
```

System Engine

```
Engine: Running
Bridge: Connected
Database: Connected
```

Agent Activity

```
Agents Active: 4
Pipeline Running
```

---

# 12. Module Panels

Each module may create panels inside the workspace.

Examples:

Studio module:

• file explorer
• editor
• build configuration

Research module:

• knowledge graph viewer
• document ingestion

Assets module:

• generation controls
• preview panel

---

# 13. Layout Persistence

The UI must remember layout state.

Store:

• panel positions
• panel sizes
• active modules

Recommended storage:

```
localStorage
```

Example key:

```
agentforge_ui_layout
```

---

# 14. Keyboard Shortcuts

Examples:

```
Ctrl + Enter → Run agent prompt
Ctrl + B → Toggle sidebar
Ctrl + P → Open project
Ctrl + / → Open command palette
```

---

# 15. Command Palette

The UI must include a command palette similar to VSCode.

Example:

```
Open Project
Run Pipeline
Generate Module
Search Knowledge
Open Asset Generator
```

Shortcut:

```
Ctrl + Shift + P
```

---

# 16. Error Handling

Errors must appear in the Agent Console.

Example:

```
Provider Error: Image generation unavailable
```

Do not display raw stack traces to users.

---

# 17. UI Rules

Agents generating UI code must follow these rules:

• do not alter base layout structure
• do not create additional top-level dashboards
• modules must render inside Main Workspace
• console and pipeline monitor must remain bottom panels

---

# End of UI Layout Specification
