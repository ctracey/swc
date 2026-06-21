---
description: Drive delivery of a work item — clarify requirements, define test strategy and acceptance criteria. Use when implementing a work item, delivering a task, starting implementation, "work on this", "let's build", "implement task N", or when invoked via /workflowDeliver.
allowed-tools: Bash, Read, Write, Edit, Glob, Skill, mcp__swc-workload__list, mcp__swc-workload__find, mcp__swc-workload__add, mcp__swc-workload__start, mcp__swc-workload__complete
---

# SWC Workflow Deliver

Entry point for delivering a work item. Delegates the delivery conversation to `swc-workflow-orchestrator`.

## Steps

### 0. Ensure swc skill permissions

Follow the `setup-permissions` skill.

### 0a. Verify MCP dependency

Follow the `mcp-check` skill. If the MCP is missing, the check delegates to `mcp-install` and the workflow cannot proceed — stop here.

### 1. Resolve the work item

Locate the active context folder via `context-lookup` to get the resolved context. All MCP calls below take its `absolute_path` as their `workload` argument — the underlying CLI does not resolve folder names or relative paths.

**If the user named a specific item** — resolve it via the MCP:
- If they gave a number (`2.3`), invoke `mcp__swc-workload__list` with `ref=2.3` and `json=true` to fetch it.
- If they gave a description, invoke `mcp__swc-workload__find` and use the best match (ambiguous matches → surface to user).

Proceed to the status check below.

**If no item was specified** — invoke `mcp__swc-workload__list` filtered to status `in-progress`:
- Exactly one in-progress item → use that item and proceed to the status check below.
- Multiple in-progress items, or none → ask the user which item they want to deliver.

**If the item does not exist on the workload** — the user has described work that isn't tracked yet. Before proceeding:
1. Confirm the title and a one-line description with the user.
2. Add it via `mcp__swc-workload__add` (under the appropriate parent, or as a new top-level item if unclear — ask if unsure).
3. Confirm the new item number returned by the MCP, then treat it as a fresh not-started item below.

---

#### Status check — once the work item is resolved

Check the item's current status marker and any existing task-specific docs at `.swc/<folder>/workitems/<N>/`. `<N>` is the **full work item number** — e.g. `1.1`, `2.3`, not just the top-level number.

**`in-progress`:**
Read any existing task docs (e.g. `requirements.md`, `context.md`) and summarise what has already been captured:
> "Continuing work on **[N]: [name]**. Here's where things stand:
> [one bullet per doc found — what it contains, e.g. 'requirements.md — intent and approach direction captured']"

Then proceed. Do not re-walk or summarise workflow stages here — if the item has recorded workflow progress on its meta, the orchestrator detects it and offers to resume at the recorded stage.

**`not-started`, but task docs exist:**
Surface the existing context as part of your opening:
> "**[N]: [name]** hasn't been started yet, but I found existing context for it: [list docs found]. I'll use that as background when we begin."

Proceed to step 1 without waiting — this is informational, not a gate.

**`not-started`, no task docs:**
Announce and proceed:
> "Starting work on **[N]: [name]**."

**`done`:**
Do not proceed automatically. Clarify with the user:
> "**[N]: [name]** is marked as done. How would you like to proceed?
> - If this was marked done in error, I can reopen it
> - If you want to extend or revise completed work, it may be worth a new related work item
> - If something else, tell me what you need"

Wait for their answer and act accordingly before continuing.

### 2. Mark work item in-progress

Before starting the workflow, silently invoke `mcp__swc-workload__start` against the resolved context's `absolute_path` with the work item number. The MCP handles parent rollup. Emit no output — this is a silent side-effect.

### 3. Run the workflow

**Use the Skill tool to invoke `workflow-orchestrator`.** Do not run stages inline — the orchestrator manages the progress banner, stage gates, and exit criteria checks. Pass the following workflow definition as the args:

```json
{
  "title": "deliver",
  "workItem": "<full work item number resolved in step 1, e.g. \"2.3\">",
  "stages": [
    { "name": "requirements",    "skill": "workflowDeliver_requirements",    "args": "" },
    { "name": "specs",           "skill": "workflowDeliver_specs",           "args": "" },
    { "name": "solution-design", "skill": "workflowDeliver_solutionDesign",  "args": "" },
    { "name": "implement",       "skill": "workflowDeliver_implement",       "args": "" },
    { "name": "refine",          "skill": "workflowDeliver_refine",          "args": "" },
    { "name": "review",          "skill": "workflowDeliver_review",          "args": "" },
    { "name": "accept",          "skill": "workflowDeliver_accept",          "args": "" }
  ],
  "on_complete": "Delivery workflow complete."
}
```

Substitute `workItem` with the actual item number resolved in step 1 — it is required here, not optional; without it the orchestrator cannot record progress or resume.

Always pass the full stage list, even when continuing an in-progress item — the orchestrator reads the item's recorded progress and starts at the right stage itself. Never skip stages from the definition or invoke a stage skill directly to "jump ahead".

## Role boundary

**Plan. Do not implement.**

Implementation does not start until the delivery workflow is complete and the user has confirmed they are ready to proceed.
