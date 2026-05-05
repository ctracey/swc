---
description: Drive delivery of a work item — clarify requirements, define test strategy and acceptance criteria. Use when implementing a work item, delivering a task, starting implementation, "work on this", "let's build", "implement task N", or when invoked via /workflowDeliver.
allowed-tools: Bash, Read, Write, Edit, Glob, Skill
---

# SWC Workflow Deliver

Entry point for delivering a work item. Delegates the delivery conversation to `swc-workflow-orchestrator`.

## Steps

### 0. Resolve the work item

Locate the active workload via `swc_lookup`. Read `workload.md`.

**If the user named a specific item** — find it by number or description match and proceed to the status check below.

**If no item was specified** — check for items with status `[-]` (in progress):
- Exactly one in-progress item → use that item and proceed to the status check below
- Multiple in-progress items, or none → ask the user which item they want to deliver

**If the item does not exist on the workload** — the user has described work that isn't tracked yet. Before proceeding:
1. Confirm the title and a one-line description with the user
2. Add it to the workload as a new item (append under the appropriate section, or as a new top-level item if unclear — ask if unsure)
3. Confirm the new item number, then treat it as a fresh `[ ]` item below

---

#### Status check — once the work item is resolved

Check the item's current status marker and any existing task-specific docs at `.swc/<folder>/workitems/<N>/`. `<N>` is the **full work item number** — e.g. `1.1`, `2.3`, not just the top-level number.

**`[-]` In progress:**
Read any existing task docs (e.g. `requirements.md`, `context.md`) and summarise what has already been captured:
> "We're continuing work on **[N]: [name]**. Here's where things stand:
> [one bullet per doc found — what it contains, e.g. 'requirements.md — intent and approach direction captured']
>
> Ready to pick up from here?"

Wait for confirmation before proceeding.

**`[ ]` Not started, but task docs exist:**
Surface the existing context as part of your opening:
> "**[N]: [name]** hasn't been started yet, but I found existing context for it: [list docs found]. I'll use that as background when we begin."

Proceed to step 1 without waiting — this is informational, not a gate.

**`[ ]` Not started, no task docs:**
Confirm simply:
> "I'll work on **[N]: [name]** — is that right?"

Wait for confirmation before proceeding.

**`[x]` Done:**
Do not proceed automatically. Clarify with the user:
> "**[N]: [name]** is marked as done. How would you like to proceed?
> - If this was marked done in error, I can reopen it
> - If you want to extend or revise completed work, it may be worth a new related work item
> - If something else, tell me what you need"

Wait for their answer and act accordingly before continuing.

### 1. Confirm intent

Before starting, read the `stages` array from the JSON config in step 2. For each stage, render its `name` as a bullet with a one-line description of what that stage covers. Present to the user:

> "Ready to start the delivery workflow for **[item number]: [item name]**. It covers [N] stages:
> [generated bullets]
>
> Want to go ahead?"

If yes, proceed. If no, ask what they actually need and stop here.

### 2. Mark work item in-progress

Before starting the workflow, silently mark the work item `[-]` by invoking `swc_workload-item-start` with the work item number. Emit no output — this is a silent side-effect.

### 3. Run the workflow

**Use the Skill tool to invoke `swc_workflow-orchestrator`.** Do not run stages inline — the orchestrator manages the progress banner, stage gates, and exit criteria checks. Pass the following workflow definition as the args:

```json
{
  "title": "deliver",
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

## Role boundary

**Plan. Do not implement.**

Implementation does not start until the delivery workflow is complete and the user has confirmed they are ready to proceed.
