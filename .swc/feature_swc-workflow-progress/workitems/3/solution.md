# Solution Design — 3: Find a way to persist a workflow stage definition

## Approach

Create a new `context-initWorkflowManifest` skill that generates `workflow-manifest.json` in the active context folder. The skill uses an embedded prompt to have the model produce the workflow JSON from its own knowledge. Add a delegation call to `context-init` as a final step after `mcp__swc-workload__init` succeeds.

## Test approach

Lightweight — implement directly against the spec checklist, no automated test file.

## Technical decisions

- **Manifest prompt**: embed verbatim — "give me a json object with a collection for workflows, each workflow has name and stages, stages is a collection with just the name of the stage"
- **Delegation placement**: after `mcp__swc-workload__init` succeeds in `context-init`, before returning — only runs on successful workload init
- **Write location**: `workflow-manifest.json` in the resolved context folder (`absolute_path`)
