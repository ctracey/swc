---
description: Demo a workflow — scaffold workload + plan + architecture from a feature description. Use when starting a new project, plan, or piece of work, or when the user says "begin new work", "start a new plan", "new project", "new piece of work", or invokes /workflowDemo.
allowed-tools: Bash, Read, Write, Edit, Glob
---

# SWC Workflow Demo

Entry point for demoing a workflow. Invoke `workflow-orchestrator` with the following definition:

```json
{
  "title": "demo",
  "purpose": "The output is a demo of an orchestrated workflow.",
  "stages": [
    { "name": "start",   "skill": "workflowDemo_start",   "args": "" },
    { "name": "middle",    "skill": "workflowDemo_middle",    "args": "" },
    { "name": "end",  "skill": "workflowDemo_end",  "args": "" },
  ],
  "on_complete": "Demo complete. Go ahead and create your own workflow now, or ask me to modify this one if you want to see how that works."
}
```
