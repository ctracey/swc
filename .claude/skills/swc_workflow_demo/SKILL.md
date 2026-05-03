---
name: swc_workflow_demo
description: Demo a workflow — scaffold workload + plan + architecture from a feature description. Use when starting a new project, plan, or piece of work, or when the user says "begin new work", "start a new plan", "new project", "new piece of work", or invokes /swc-workflow-demo.
allowed-tools: Bash, Read, Write, Edit, Glob
---

# SWC Workflow Demo

Entry point for demoing a workflow. Delegates the demo conversation to `swc_workflow-orchestrator`.

## Steps

### 0. Confirm intent

Before starting, read the `stages` array from the JSON config in step 1. For each stage, render its `name` as a bullet with a one-line description of what that stage covers (inferred from the name and your knowledge of the workflow). Present this to the user:

> "Would you like to run through a demo workflow? The output is a demo of an orchestrated workflow. It covers [N] stages:
> [generated bullets]
>
> Want to go ahead?"

If yes, proceed. If no, ask what they actually need and stop here.

### 1. Run the workflow

Invoke `swc_workflow-orchestrator` with the following definition:

```json
{
  "title": "planning",
  "stages": [
    { "name": "start",   "skill": "swc-workflow_demo-start",   "args": "" },
    { "name": "middle",    "skill": "swc-workflow_demo-middle",    "args": "" },
    { "name": "end",  "skill": "swc-workflow_demo-end",  "args": "" },
  ],
  "on_complete": "Demo complete. Go ahead and create your own workflow now, or ask me to modify this one if you want to see how that works."
}
```
