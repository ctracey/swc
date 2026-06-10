# Architecture — Workflow Stage Progress

SWC-side design for recording work item stage progress using the MCP's existing `meta` support.

## Layering principle

```
┌──────────────────────────────────────────────────────────────┐
│  SWC plugin (skills + workflow-orchestrator)                 │
│   - Owns workflow shape (stages, ordering, exit criteria)    │
│   - Owns swc-workflow-status schema                          │
│   - Computes transitions, enforces loopback invariants       │
│   - Writes its state under meta["swc-workflow-status"]       │
└──────────────────────────────┬───────────────────────────────┘
                               │ MCP calls
                               ▼
┌──────────────────────────────────────────────────────────────┐
│  swc-workload-mcp (v1.0.0 — no changes required)            │
│   - Stores workitems: { id, title, status, meta }            │
│   - meta is a namespaced free-form JSON blob                 │
│   - No knowledge of any namespace's contents                 │
└──────────────────────────────────────────────────────────────┘
```

The MCP is a generic workload store. SWC is the only thing that knows what a "workflow stage" is.

## Orchestrator hook point

The workflow orchestrator runs each stage in this sequence:

1. Emit progress banner (`workflow-progress`)
2. **→ Write MCP meta** ← new step
3. Invoke stage skill

Step 2 fires when `workItem` is present in the workflow definition. It writes the current stage name and timestamp to `meta["swc-workflow-status"]` before the stage skill is invoked. This means:

- Every stage in every workflow is covered — no per-stage skill changes needed.
- Re-invokes (on loopback or gate failure) are naturally recorded.
- The write happens before the stage does any work, so a crash mid-stage still records entry.

## Orchestrator input schema change

A single optional field is added to the workflow definition:

```jsonc
{
  "title": "deliver",
  "workItem": 4,          // optional — item ordinal; enables meta writes when present
  "stages": [ ... ],
  "on_complete": "..."
}
```

Entry skills (`workflowDeliver`, `workflowPlan`, `workflowImplement`) pass `workItem` when they know the active item number.

## `swc-workflow-status` schema

SWC writes this blob under `meta["swc-workflow-status"]`:

```jsonc
{
  "version": 1,
  "workflow": "deliver",           // workflow name — used to reconstruct stage list on resume
  "currentStage": "implement",     // stage name currently active
  "enteredAt": "2026-06-10T...",   // ISO timestamp of last stage entry
  "stages": {                      // optional: per-stage state for loopback tracking
    "requirements": { "state": "done",   "completedAt": "..." },
    "specs":        { "state": "done",   "completedAt": "..." },
    "implement":    { "state": "active", "enteredAt": "..."   },
    "refine":       { "state": "pending" }
  }
}
```

Stage states: `pending` → `active` → `done` (+ `superseded` for loopback, if implemented).

## Workflow definition persistence (open question)

On resume, we need the full stage list to route to the right skill. Two options:

- **(a) Store in meta at workflow start** — write `stages` array (name + skill) into the meta blob when the orchestrator starts. Fully self-contained; no coupling to SWC internals.
- **(b) Derive from `workflow` name** — SWC hard-codes the mapping (`"deliver"` → `workflowDeliver` stage list). Simpler but couples resume logic to the workflow definition in code.

Not yet decided. Option (a) is preferred for resilience.

## Scenario: fresh-session resume

1. User says "continue item 4".
2. Skill calls `mcp__swc-workload__get(4)` — meta comes back in one call.
3. Reads `currentStage` from `meta["swc-workflow-status"]`.
4. Routes to the matching SWC stage skill.
5. Stage skill inspects its own `stages[currentStage]` to decide resume-mid-stage vs start-fresh.

## Scenario: loopback

User re-enters `requirements` from `implement`:

1. Orchestrator marks `implement` and any later stages as `superseded` in the meta blob.
2. Sets `currentStage: requirements`, `state: active`.
3. One MCP meta write commits the full transition.

The orchestrator enforces the invariant — the MCP stores it blindly.
