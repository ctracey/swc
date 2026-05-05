---
name: context--workload
description: SWC workload.md conventions — work item status markers, parent rollup rules, and cleanup. Use when reading or updating workload.md, checking or changing work item status, or completing a workload.
allowed-tools: Read
---
# SWC Workload.md Conventions

`workload.md` is the work item list for a branch — one file per workload folder under `.swc/`.

## Work item status markers

| Marker | Meaning |
|--------|---------|
| `[ ]`  | Not started |
| `[-]`  | In progress (one or more sub-items started or done, but not all done) |
| `[x]`  | Done (all sub-items complete) |

## Parent work item rules

- When sub-items exist, the parent status reflects them: any sub-item in progress → parent is `[-]`; all sub-items done → parent is `[x]`
- If a parent has no sub-items, mark it directly

## Cleanup

When all items complete, recommend deleting the workload folder. Git history preserves it. Don't let completed workloads accumulate.
