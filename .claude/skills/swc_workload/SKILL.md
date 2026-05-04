---
name: swc_workload
description: Display the active workload in a visual format with status symbols. Use when the user says "show tasks", "show me the task list", "show workload", "what work items are left", or invokes /swc-workload.
allowed-tools: Read, Glob, Bash
---

# SWC Workload

Read the active workload file and display work items using visual status symbols.

## Arguments

- `/swc-workload` — display work items from the active workload
- `/swc-workload <branch>` — display work items for a specific branch

## Steps

### 1. Resolve the active workload

Follow the `swc_lookup` skill to get the path to `workload.md`. If the lookup fails or the user declines, stop.

### 2. Render via script

Run:

```bash
echo '{"path": "<absolute path to workload.md>"}' | python3 ~/.claude/skills/swc_workload/workload.py
```

The script outputs either `{"output": "..."}` or `{"error": "..."}`.

The script outputs either `{"output": "..."}` or `{"error": "..."}`. If `output`, emit it as your text response. If `error`, emit the error message. Do not add preamble or trailing text.
