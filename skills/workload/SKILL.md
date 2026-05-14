---
description: Display the active workload in a visual format with status symbols. Use when the user says "show tasks", "show me the task list", "show workload", "what work items are left", or invokes /workload.
allowed-tools: Read, Glob, Bash
---

# SWC Workload

Read the active workload file and display work items using visual status symbols.

## Arguments

- `/workload` — display work items from the active workload
- `/workload <branch>` — display work items for a specific branch

## Steps

### 0. Ensure swc skill permissions

Follow the `setup-permissions` skill.

### 1. Resolve the active workload

Follow the `context-lookup` skill to get the path to `workload.md`. If the lookup fails or the user declines, stop.

### 2. Render via script

Run:

```bash
echo '{"path": "<absolute path to workload.md>"}' | python3 ${CLAUDE_SKILL_DIR}/workload.py
```

The script outputs either `{"output": "..."}` or `{"error": "..."}`.

The script outputs either `{"output": "..."}` or `{"error": "..."}`. If `output`, emit it as your text response. If `error`, emit the error message. Do not add preamble or trailing text.
