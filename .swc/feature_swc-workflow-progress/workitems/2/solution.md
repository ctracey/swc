# Solution Design — 2: Store workflow stage progress via MCP

## Approach

A new `swc:workflowProgress-record` skill encapsulates the meta write behaviour — the orchestrator calls it between the progress banner and the stage skill invocation, keeping the orchestrator clean and the recording logic reusable. The skill resolves the work item and workload path from session context. Two fields are maintained under `meta.swc`: `workflowState` (keyed by workflow name, holds `currentStage`) and `workflowEvents` (shared append-only log across all workflows). No changes to the workflow definition schema or entry skills.

## Test approach

Lightweight — implement directly against the spec checklist. Add a scenario to `tests/swc/` covering the meta write behaviour. No automated test file. This is consistent with the existing pattern for SWC skill changes.

## Meta structure

```json
{
  "swc": {
    "workflowState": {
      "deliver": { "currentStage": "specs" }
    },
    "workflowEvents": [
      { "workflow": "deliver", "stage": "requirements", "timestamp": "2026-06-10T..." },
      { "workflow": "deliver", "stage": "specs",        "timestamp": "2026-06-10T..." }
    ]
  }
}
```

## Technical decisions

- **Namespace:** all SWC-owned meta lives under `meta.swc` — no other keys at the root.
- **`workflowState`:** keyed by workflow name, only added when a workflow starts. Holds `currentStage` for quick reads.
- **`workflowEvents`:** single shared log across all workflows for the item — gives a full chronological picture of item progress across parallel workflows (deliver, implement, etc.). Entries: `{ workflow, stage, timestamp }`.
- **New skill:** `swc:workflowProgress-record` — owns all meta write logic. The orchestrator invokes it via `Skill` (already in allowed-tools); no new MCP tools needed on the orchestrator itself.
- **`workflowProgress-record` allowed-tools:** `mcp__swc-workload__list`, `mcp__swc-workload__update`, `Skill` (for context-lookup).
- **Read-before-write for `workflowEvents`:** the MCP `update` tool replaces fields; it cannot atomically append. The skill must: (1) read current meta via `mcp__swc-workload__list(ref=N, json=true)`, (2) append the new entry, (3) write the updated `meta.swc` back via `mcp__swc-workload__update`.
- **Write failure handling:** inform the user and offer ignore/continue or stop-to-fix (per REQ-04).
- **No work item in context:** display a warning and continue (per REQ-03).

## Notes

- `workflowProgress-record` resolves the workload path via `context-lookup`. Resolve once per skill invocation (called per stage by the orchestrator).
- `workflowState.<workflow>` is created on first write if absent — no upfront initialisation needed.
- `workflowEvents` is `[]` if absent — treat as empty array on read.
- Timestamp should be ISO 8601 UTC — use Python's `datetime.utcnow().isoformat() + "Z"` or equivalent in the skill context.
