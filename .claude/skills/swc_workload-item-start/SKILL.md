---
name: swc_workload-item-start
description: Silently mark a work item as in-progress ([-]) inside an agent workflow. Designed for programmatic use inside skill chains — emits no text output. Use when an implementation agent needs to mark its own work item in-progress during orient. Do NOT use for interactive top-level status changes — use swc_workload-update instead.
allowed-tools: Read, Edit, Bash, Glob
---

# SWC Workload Item Start

Mark a work item `[-]` (in-progress) and roll up the parent. Designed for silent use inside agent skill chains — **do not emit any text output**.

## Arguments

Work item number passed from the calling context (e.g. `2.2`, `3.1`).

## Steps

### 1. Resolve the workload folder

1. Run `git branch --show-current`
2. Read `.swc/_meta.json` — look up the branch in the `workloads` map to get the folder name
3. Fallback if absent: use the most recently modified folder under `.swc/`

### 2. Update the work item line

In `.swc/<folder>/workload.md`, find the line for the target work item number and update its checkbox to `[-]`:

- `[ ]` → `[-]`
- `[x]` → leave as `[x]` (never downgrade a completed item)
- `[-]` → leave as-is (already in-progress)

### 3. Roll up the parent

Re-evaluate the parent work item's status based on its sub-items:

| Sub-item state | Parent becomes |
|---|---|
| All sub-items `[x]` | `[x]` |
| Any sub-item `[-]` or `[x]`, but not all `[x]` | `[-]` |
| All sub-items `[ ]` | `[ ]` |

Update the parent line if its current marker does not match.

If the work item has no parent, skip this step.

## Output

**None.** Do not emit any text, confirmation, or status message. Do not end your response turn. Return immediately to the calling workflow and continue.
