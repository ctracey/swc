# SWC Workflow Progress — Meta Write Scenarios

Covers `swc:workflow-recordProgress` and the orchestrator's work item tracking.

---

## SCENARIO: Stage advance records workflow, stage, and history entry

**Setup:** Work item 3 is active in session context. The "deliver" workflow is running.

**Trigger:** Orchestrator advances to stage "specs".

**Expected:**
- `mcp__swc-workload__list(ref=3, json=true)` is called to read current meta
- `mcp__swc-workload__update` is called with `path=meta.swc` and a value containing:
  - `workflowState.deliver.currentStage` = `"specs"`
  - a new entry appended to `workflowEvents`: `{ workflow: "deliver", stage: "specs", timestamp: <ISO-UTC> }`
- The stage skill ("workflowDeliver_specs") is invoked after the meta write

---

## SCENARIO: Loopback to earlier stage appends new history entry without losing prior entries

**Setup:** Work item 3 is active. Workflow has previously advanced through "requirements" and "specs".
`meta.swc.workflowEvents` contains two entries (requirements, specs).

**Trigger:** Orchestrator re-enters stage "requirements" following a loopback.

**Expected:**
- `mcp__swc-workload__update` is called with an updated `meta.swc` where:
  - `workflowState.deliver.currentStage` = `"requirements"`
  - `workflowEvents` contains three entries: requirements, specs, requirements (new)
  - The original requirements and specs entries are unchanged
- The stage skill is invoked after the meta write

---

## SCENARIO: No active work item — warning shown, workflow continues

**Setup:** Orchestrator is running a workflow with no `workItem` field in the definition.

**Expected:**
- A note is displayed once before the first stage: "no work item is being tracked..."
- No `mcp__swc-workload__list` or `mcp__swc-workload__update` calls are made
- Each stage skill is invoked as normal

---

## SCENARIO: Meta write fails — user ignores and continues

**Setup:** Work item 3 is active. The `mcp__swc-workload__update` call fails.

**Expected:**
- The user is informed of the failure with the error message
- The user is offered: (1) Ignore and continue, (2) Stop to fix
- If the user chooses ignore: the stage skill is invoked as normal

---

## SCENARIO: Meta write fails — user stops to fix

**Setup:** Work item 3 is active. The `mcp__swc-workload__update` call fails.

**Expected:**
- The user is informed of the failure
- The user is offered: (1) Ignore and continue, (2) Stop to fix
- If the user chooses stop: workflow halts, stage skill is NOT invoked
