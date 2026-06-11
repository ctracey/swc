---
description: Implementation workflow — drives an implementation agent through orient, implement, and summarise stages. Entry point for the agent-side workflow. Use when an implementation agent receives a work item and needs to execute it.
allowed-tools: Bash, Read, Write, Edit, Glob, Agent
---

# SWC Implementation Workflow

Entry point for the implementation agent. Reads the work item and folder from context, then delegates to `workflow-orchestrator` with the implementation stages.

## Context

The work item number, name, and context folder path are passed in the agent prompt by `workflowDeliver_implement`. These must be available before this skill runs.

## Steps

### 1. Confirm context

Extract from the calling prompt:
- Work item number (e.g. `1.4.4.1`)
- Work item name
- Workload folder path (e.g. `.swc/feature_subagent-workflow/`)

If any are missing, stop and surface the gap — do not proceed without a resolved work item.

### 2. Run the workflow

Invoke `workflow-orchestrator` with the implementation stage definitions:

```json
{
  "title": "implement",
  "workItem": "<work item number from step 1, e.g. \"1.4.4.1\">",
  "stages": [
    { "name": "orient",    "skill": "workflowImplement_orient",    "args": "" },
    { "name": "implement", "skill": "workflowImplement_implement",  "args": "" },
    { "name": "summarise", "skill": "workflowImplement_summarise",  "args": "" }
  ],
  "on_complete": "Implementation workflow complete. Summary artifact written."
}
```

Substitute `workItem` with the actual item number confirmed in step 1 — it is required here; without it the orchestrator cannot record stage progress. The work item number, name, and folder path are available to each stage skill via the calling context.
