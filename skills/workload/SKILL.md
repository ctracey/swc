---
description: Display work items from the active workload via the swc-workload MCP. Use when the user says "list workitems", "show tasks", "show me the task list", "show workload", "what work items are left", or invokes /workload.
allowed-tools: Skill, mcp__swc-workload__list
---

# SWC Workload

Resolve the active context folder and render its workload items as a hierarchical list with status symbols.

## Arguments

- `/workload` — display work items from the active workload
- `/workload <branch>` — display work items for a specific branch (passed to `context-lookup`)

## Steps

### 0. Ensure swc skill permissions

Follow the `setup-permissions` skill.

### 0a. Verify MCP dependency

Follow the `mcp-check` skill. If the MCP is missing, the check delegates to `mcp-install` — stop here.

### 1. Resolve the active context folder

Follow the `context-lookup` skill to get the resolved context folder path. If lookup fails or the user declines, stop.

### 2. List work items via MCP

Invoke `mcp__swc-workload__list` against the resolved folder path.

### 3. Render

Render the returned items as a hierarchical list using these status symbols:

- `□` for `not-started`
- `▣` for `in-progress`
- `✔` for `done`

Preserve the parent/child hierarchy with two-space indentation per level. Use the item number and title — keep descriptions concise; don't pad. If the MCP returns an empty list, print a single line: `(no work items)`.

Emit only the rendered list — no preamble, no trailing summary.
