---
name: swc_workload-update
description: Update the status of a work item in the active workload. ALWAYS use this skill for status changes — never edit workload.md directly. Direct edits miss parent rollup and leave stale status markers. Use when the user says "mark X done", "mark X as done", "start task X", "complete task X", "task X is done", "work item X done", or invokes /swc-workload-update.
allowed-tools: Read, Edit, Glob, Bash
---

# SWC Update

Update a work item status in the active workload file, then roll up the parent status.

## Arguments

- `/swc-workload-update <item> done` — mark a work item done (`[x]`)
- `/swc-workload-update <item> in-progress` — mark a work item in progress (`[-]`)
- `/swc-workload-update <item> reset` — mark a work item not started (`[ ]`)
- Item can be a number (`2.6`), a description match, or implied from context ("the current item", "next item")

## Steps

### 1. Resolve the active workload

1. Run `git branch --show-current`
2. Read `.swc/_meta.json`
3. Look up branch in `workloads` map → folder name
4. Fallback: most recently modified folder under `.swc/`

Edit `.swc/<folder>/workload.md`.

### 2. Resolve the target work item

- Match by item number (e.g. `2.6`) or description keyword
- If ambiguous, confirm with the user before editing

### 3. Apply the status change

Update the checkbox on the matched line:
- `done` → `[x]`
- `in-progress` → `[-]`
- `reset` → `[ ]`

### 4. Roll up the parent status

After updating the sub-item, re-evaluate the parent work item status:

| Sub-item state | Parent becomes |
|---|---|
| All sub-items `[x]` | `[x]` |
| Any sub-item `[-]` or `[x]`, but not all `[x]` | `[-]` |
| All sub-items `[ ]` | `[ ]` |

Update the parent line if its current marker does not match the rolled-up result.

If the parent has no sub-items, update it directly — no rollup needed.

### 5. Confirm

Output a single confirmation line, e.g.:

```
✔ Marked 2.6 done. Parent work item 2 updated to [-] (2.7 still outstanding).
```

No other output.
