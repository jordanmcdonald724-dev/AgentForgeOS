# AgentForgeOS — Studio Shell Lock

This document defines the **permanent Studio interface shell**. The shell layout is immutable and must always be present.

## Required Regions (never remove or replace)

- **Top Navigation Bar** — Global navigation and system controls.
- **Left Sidebar** — Primary module navigation and entry points.
- **Main Workspace** — All module content and tools render here.
- **Agent Console** — Dedicated panel for agent interaction and logs.
- **Pipeline Monitor** — Dedicated panel for pipeline/status visualization.

## Rules

1. These five regions **must always exist**; do not delete, replace, or relocate them.
2. All UI components and module UIs **must render inside these regions**, not alongside or outside them.
3. Variations to styling or contents are allowed only if the region boundaries and purpose remain intact.
4. Do **not** add alternative top-level shells or bypass this layout.

This shell lock ensures consistent Studio structure across all generated or hand-authored UI code.***
