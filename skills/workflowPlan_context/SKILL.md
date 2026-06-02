---
description: Confirm the working branch, check for existing workloads, and create stub planning docs. First phase of the planning conversation. Use at the start of a planning session or when invoked via /workflowPlan_context.
allowed-tools: Read, Write, Edit, Glob, Bash, Skill, mcp__swc-workload__exists, mcp__swc-workload__list
---

# Plan Context

Establish context before the planning conversation begins.

## Steps

### 1. Resolve the folder

Invoke `context-lookup --create`. It handles:
- Git repo detection and optional initialisation
- Branch recommendation and confirmation
- Folder name derivation and `_meta.json` update

Returns: confirmed branch name + resolved context (including `absolute_path`).

### 2. Check for an existing workload

Invoke `mcp__swc-workload__exists` against the resolved context's `absolute_path`.

**Result `missing`** — fresh start. Go to step 3.

**Result `exists`** — invoke `mcp__swc-workload__list` against the resolved context's `absolute_path` to read its items. Surface a brief summary (work item count, done count), then ask:

> I found an existing workload for `<branch>` (M work items, X done). How does this new work relate?
>
> 1. **Replace** — archive or discard the existing workload and start fresh
> 2. **Extend** — add new work items continuing from the highest existing number
> 3. **Sibling** — nest existing work items one level deeper and add this as a peer
> 4. **New sections** — keep the workload as-is but add sections to existing docs

Wait for the user's choice before proceeding.

#### Mode handling

**Replace**
- Ask: "Archive the existing docs (rename folder with `_archived` suffix), or discard?"
- Remove or rename the old entry in `_meta.json`. Treat as a fresh start.

**Extend**
- Ask how the new work relates to the existing scope (one sentence — append to `notes.md`).
- New work items will be appended continuing from the highest existing number.
- Skip step 3.

**Sibling**
- Ask: "What should the label be for the existing work as a group?" (e.g. "Phase 1", "Backend")
- Renumber existing work items one level deeper:
  - Old top-level item `1` with sub-items `1.1`, `1.2` → becomes `1.1` with sub-items `1.1.1`, `1.1.2`
  - Old top-level item `2` with sub-item `2.1` → becomes `1.2` with sub-item `1.2.1`
- New work becomes item `2` with its own breakdown.
- Skip step 3.

**New sections**
- Ask what the new section is about (one sentence).
- Add a named section to `notes.md` and/or `architecture.md` as appropriate.
- Skip step 3 and skip to `workflowPlan_delivery`.

### 3. Scaffold stub docs

Invoke `context-init` with the resolved context (passing its `absolute_path`). It creates the five stub files.

### 4. Confirm

Say: "Workload ready at `.swc/<folder>/`. Let's start with what's driving this work."

## Exit criteria

**Done when:**
- Branch confirmed (via `context-lookup`)
- `_meta.json` updated (via `context-lookup`)
- Existing-work mode chosen (if applicable)
- Stub docs present at `.swc/<folder>/` (via `context-init` or existing files)
- User acknowledged

**Return control to the calling skill.**
