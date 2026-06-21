---
description: Begin a new piece of work — scaffold workload + plan + architecture from a feature description. Use when starting a new project, plan, or piece of work, or when the user says "begin new work", "start a new plan", "new project", "new piece of work", or invokes /workflowPlan.
allowed-tools: Bash, Read, Write, Edit, Glob
---

# SWC Workflow Plan

Entry point for starting a new piece of work. Delegates the planning conversation to `swc-workflow-orchestrator`.

## Steps

### 0. Ensure swc skill permissions

Follow the `setup-permissions` skill.

### 0a. Verify MCP dependency

Follow the `mcp-check` skill. If the MCP is missing, the check delegates to `mcp-install` and the workflow cannot proceed — stop here.

### 1. Run the workflow

Invoke `swc-workflow-orchestrator` with the following definition:

```json
{
  "title": "planning",
  "stages": [
    { "name": "context",   "skill": "workflowPlan_context",   "args": "" },
    { "name": "intent",    "skill": "workflowPlan_intent",    "args": "" },
    { "name": "solution",  "skill": "workflowPlan_solution",  "args": "" },
    { "name": "delivery",  "skill": "workflowPlan_delivery",  "args": "" },
    { "name": "breakdown", "skill": "workflowPlan_breakdown", "args": "" },
    { "name": "finalise",  "skill": "workflowPlan_finalise",  "args": "" }
  ],
  "on_complete": "Planning complete. Run `/swc-execute` to begin the first work item."
}
```

## Role boundary

**Plan. Do not implement.**

Implementation does not start until the user has explicitly confirmed the plan is correct — that confirmation is what `workflowPlan_finalise` is waiting for.
