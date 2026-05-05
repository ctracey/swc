---
name: workflowPlan_breakdown
description: Propose and confirm the work item breakdown for a piece of work. Fifth phase of the planning conversation. Use when creating a task list, a workload breakdown, or when invoked via /workflowPlan_breakdown.
allowed-tools: Read, Write, Edit, Glob, Bash
---

# Plan Breakdown

Create the workload. Always confirm before writing.

## Steps

### 1. Ask how to navigate

> "How do you want to organise the work items — do you have a logical map in mind, or would you prefer to walk through it by user, feature set, or journey/scenario?"

| Approach | What it means |
|---|---|
| Logical / technical map | Work items follow the system structure — components, layers, modules |
| User / persona | Work items grouped by who benefits |
| Feature set | Work items grouped by capability area |
| Journey / scenario | Work items follow an end-to-end flow |

The user may mix these. Follow their lead — don't impose structure.

### 2. Draft the workload

With the delivery shape and navigation approach in mind, draft the full work item list. Present as plain text using the `swc-list` visual format:

```
□ 1. First work item
  □ 1.1. Sub-item
  □ 1.2. Sub-item
□ 2. Second work item
  □ 2.1. Sub-item
```

For **Sibling** mode, show the full renumbered list — existing items nested under `1.` and new work under `2.` — before any files change.

### 3. Confirm

> "Does this numbering and breakdown look right? Say yes to write the files, or tell me what to adjust."

Wait for explicit confirmation. Iterate if requested. Do not write until confirmed.

### 4. Capture

Write the confirmed workload to `.swc/<folder>/workload.md`:

```markdown
# [Branch] — [work title]

## Work items

- [ ] **1. [First work item]**
  - [ ] 1.1. [Sub-item]
  - [ ] 1.2. [Sub-item]

- [ ] **2. [Second work item]**
  - [ ] 2.1. [Sub-item]
```

Work item granularity: small and specific, with a clear "done when" implied by each name. More than ~5 sub-items under one parent → consider splitting the parent.

### 5. Present

Run `swc-list` to show the full workload. Then ask:

> "That's the full breakdown. Anything to adjust before we wrap up?"

Wait for any final adjustments, then proceed to `workflowPlan_finalise`.

## Exit criteria

**Done when:**
- Full workload written to `.swc/<folder>/workload.md`
- User confirmed the breakdown

**Return control to `workflowPlan`.**
