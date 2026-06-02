---
description: Orient stage of the implementation workflow — read the full brief, understand the starting point, open a new pass section in context.md. First stage of the implementation workflow. Use when invoked by workflowImplement.
allowed-tools: Read, Write, Edit, Glob, Bash, Skill, mcp__swc-workload__list, mcp__swc-workload__start
---

# Implement — Orient Stage

## Steps

### 1. Resolve the context folder

Use the `context-lookup` skill to find the active context folder. This gives you the `<folder>` path (e.g. `.swc/feature_subagent-workflow/`).

### 2. Confirm the work item

Invoke `mcp__swc-workload__list` with `ref=<N>` and `json=true` against the resolved context's `absolute_path` for the work item number passed in the calling context. Note the name and description — these define the scope of this pass.

Mark the work item in-progress by invoking `mcp__swc-workload__start` against the resolved context's `absolute_path` with the work item number. The MCP is idempotent on status — safe to run on pass 1, 2, or 3, and it won't downgrade a `done` item.

### 3. Read the brief

Read in parallel from `.swc/<folder>/`:
- `plan.md`
- `architecture.md`

Read in parallel from `.swc/<folder>/workitems/<N>/`:
- `requirements.md`
- `specs.md`
- `solution.md`
- `quality-baseline.md` — skip silently if absent

### 4. Read prior context

Check `.swc/<folder>/workitems/<N>/context.md`:

- **Exists:** read it in full. Count `## Pass` headers to determine the next pass number. Understand what was tried, what decisions were made, and where things were left. This is the memory that carries across sessions — treat it as ground truth for what has already happened.
- **Does not exist:** this is pass 1. No prior context.

### 5. Understand the starting point

With the brief and prior context loaded, establish:
- **Test approach** — read the `## Test approach` section of `solution.md`. This is the agreed approach: either `Full TDD` (write test per scenario, implement, update docs) or `Lightweight` (implement directly against spec checklist). If absent, default to Full TDD. The implement stage follows this.
- What does the spec require, and what does "passing" look like for this work item type?
- Which files and areas of the codebase are in scope? Grep for symbols, file names, or concepts from the work item description.
- If this is a subsequent pass: what was the state at the end of the last pass? What scenarios remain? Was there a blocker?

### 6. Open a new pass section in context.md

Append to `.swc/<folder>/workitems/<N>/context.md` (create the file if absent):

```markdown
## Pass <N> — <YYYY-MM-DD>
```

Do not pre-fill entries — entries are written during the implement stage at decision points.

## Exit criteria

- Context folder resolved
- Work item name and description confirmed via `mcp__swc-workload__list`
- Work item marked `in-progress` via `mcp__swc-workload__start`
- All brief docs read: requirements.md, specs.md, solution.md, plan.md, architecture.md
- quality-baseline.md read if present; absence noted
- Prior context understood, or confirmed as pass 1
- Codebase starting point understood — relevant files located
- New pass section opened in context.md
