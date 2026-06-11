---
description: Record a workflow stage entry or workflow completion on the active work item's MCP meta. Called by the workflow orchestrator between the progress banner and stage skill invocation (one call per stage advance), and once more with complete=true after the final stage. Use when the orchestrator needs to append a record to meta["swc"]["workflowEvents"] and update meta["swc"]["workflowState"]["<workflow>"].
allowed-tools: Bash, Read, Skill, mcp__swc-workload__list, mcp__swc-workload__update
---

# workflow-recordProgress

Record a workflow stage entry — or workflow completion — on the active work item's MCP meta. Encapsulates all meta read-modify-write logic so the orchestrator stays clean.

## Arguments

```
workflow=<name>  stage=<name>  workItem=<ref>  workload=<absolute_path>  [complete=true]
```

`workflow`, `workItem`, and `workload` are always required. The orchestrator resolves `workItem` and `workload` from session context and passes them explicitly. `workItem` is a string — either a plain number (`2`) or dotted notation (`1.4.4.1`).

Two modes:
- **Stage entry** (default) — `stage` is required; records entry into that stage.
- **Completion** (`complete=true`) — `stage` is omitted; records that the workflow run finished.

## Steps

### 1. Read current meta

Invoke `mcp__swc-workload__list` with `ref=<workItem>`, `json=true`, and `workload=<workload>`. Extract `items[0].meta` from the response — treat as `{}` if absent or null.

### 2. Build the updated meta blob

From the existing meta:

1. Read `meta.swc` — treat as `{}` if absent.
2. Read `meta.swc.workflowState` — treat as `{}` if absent.
3. Read `meta.swc.workflowEvents` — treat as `[]` if absent.

Construct the new `meta.swc` object.

**Stage-entry mode** (default):

```jsonc
{
  "workflowState": {
    // preserve all existing workflow keys, then upsert the current workflow:
    "<workflow>": { "currentStage": "<stage>", "completed": false }
  },
  "workflowEvents": [
    // all existing entries, then append:
    { "workflow": "<workflow>", "stage": "<stage>", "timestamp": "<ISO-8601-UTC>" }
  ]
}
```

Setting `completed: false` on every stage entry matters — it is what turns a previously completed workflow back into an in-flight one when a new pass starts.

**Completion mode** (`complete=true`):

```jsonc
{
  "workflowState": {
    // preserve all existing workflow keys, then upsert the current workflow:
    "<workflow>": { "currentStage": null, "completed": true }
  },
  "workflowEvents": [
    // all existing entries, then append:
    { "workflow": "<workflow>", "event": "completed", "timestamp": "<ISO-8601-UTC>" }
  ]
}
```

Generate the timestamp with Python:

```bash
python3 -c "from datetime import datetime, timezone; print(datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))"
```

### 3. Write updated meta

Invoke `mcp__swc-workload__update` with:
- `workload` = `<workload>`
- `ref` = `<workItem>`
- `path` = `meta.swc`
- `value` = the JSON-serialised `meta.swc` object from step 2

### 4. Handle failure

If either the `mcp__swc-workload__list` read or the `mcp__swc-workload__update` write fails or returns an error:

Display to the user (in completion mode, say "completion of workflow **'<workflow>'**" instead of naming a stage):
> "Error: failed to record workflow progress for stage **'<stage>'** on work item **<workItem>**.
> MCP error: [error message]
>
> How would you like to proceed?
> 1. **Fix** — resolve the issue and retry; the stage will not start until the record succeeds
> 2. **Continue** — skip the meta write and proceed with the stage anyway"

- **Fix:** wait for the user to resolve the issue, then retry from step 1. Repeat until success or the user chooses Continue.
- **Continue:** proceed normally, emit no further output.
- **Stop:** if at any point the user says stop or gives up, emit exactly `##WORKFLOW_HALT##` on its own line and return. The orchestrator will halt the workflow.

### 5. Return

Return silently on success — the orchestrator does not need any output from this skill.

## Notes

- `meta.swc` is the single SWC-owned namespace on the item's meta. All SWC keys live under it.
- `workflowState` is keyed by workflow name — multiple workflows (deliver, implement) can coexist.
- A non-null `currentStage` means an in-flight run; `currentStage: null` + `completed: true` means the last run finished. The orchestrator's resume logic keys off this distinction.
- `workflowEvents` is an append-only log. Never remove or modify existing entries.
- This skill is always called with an active work item — the orchestrator handles the no-work-item case itself (REQ-03) and only calls this skill when `workItem` is resolved.
