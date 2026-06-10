# Requirements — 2: Store workflow stage progress via MCP

## Intent

When the workflow orchestrator advances to a new stage, it appends an entry to a stage history log stored on the active work item's MCP meta. Every stage transition is durably recorded — not just the current stage — creating an audit trail that survives across sessions. This uses the MCP's existing freeform meta support; no MCP changes are required.

## Constraints

- The MCP remains generic — it stores the blob verbatim, with no knowledge of SWC stage semantics.
- A meta write failure must not halt the workflow — the write is best-effort.
- Work item identity and workload path are resolved from session context, not passed through the workflow definition schema.

## Out of scope

- Loopback state management (marking superseded stages).
- Per-stage completion writes (only stage entry is recorded here).
- Resume routing (reading meta to reconstruct workflow state).
- Any changes to the workflow definition schema or entry skills.

## Approach direction

Add `mcp__swc-workload__update` to the orchestrator's `allowed-tools`. Between the progress banner and stage skill invocation, if a work item is active in session context, resolve the workload path via `context-lookup` and append a stage-entry record to `meta["swc-workflow-status"]`. The exact history structure (shape of the audit trail) is to be agreed in solution-design.

## Parked

- History structure / mechanic — exact shape of the audit trail entries deferred to solution-design.
