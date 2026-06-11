# Architecture — Workflow Stage Progress

SWC-side design for recording work item stage progress using the MCP's existing `meta` support.

## Layering principle

```
┌──────────────────────────────────────────────────────────────┐
│  SWC plugin (skills + workflow-orchestrator)                 │
│   - Owns workflow shape (stages, ordering, exit criteria)    │
│   - Owns the meta.swc schema                                 │
│   - Computes transitions, detects resume, records completion │
│   - Writes its state under meta["swc"]                       │
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

## Orchestrator hook points

The workflow orchestrator owns all reads and writes of workflow progress. Per run:

1. **Before the stage loop** — read `meta.swc.workflowState["<workflow>"]` to detect an interrupted run (resume).
2. **On each stage entry** — between the progress banner and the stage skill, `workflow-recordProgress` writes the stage entry (covers every stage in every workflow, including re-invokes on loopback; a crash mid-stage still records entry).
3. **After the final stage** — `workflow-recordProgress complete=true` records completion.

No per-stage skill changes are needed, and every workflow that runs through the orchestrator (deliver, implement, planning) gets recording and resume for free.

## Work item identity

The orchestrator learns the work item from an explicit `workItem` field on the workflow definition — entry skills that know the item (`workflowDeliver`, `workflowImplement`) resolve it and pass it in the JSON handoff. Inference from conversation history proved unreliable in testing (the orchestrator declined to commit to an item and skipped all meta writes), so the explicit field is the contract; session context is only a fallback. Workflows not tied to an item (planning, demo) omit the field and run without recording.

## `meta.swc` schema

All SWC state lives under the single `meta.swc` namespace on the work item:

```jsonc
{
  "workflowState": {
    // keyed by workflow name — multiple workflows coexist per item
    "deliver":   { "currentStage": "implement", "completed": false },
    "implement": { "currentStage": null,        "completed": true  }
  },
  "workflowEvents": [
    // append-only log; entries are never modified or removed
    { "workflow": "deliver", "stage": "requirements", "timestamp": "2026-06-11T02:39:12Z" },
    { "workflow": "deliver", "stage": "implement",    "timestamp": "2026-06-11T03:24:21Z" },
    { "workflow": "implement", "event": "completed",  "timestamp": "2026-06-11T03:29:40Z" }
  ]
}
```

State semantics per workflow:

- `currentStage: "<name>"`, `completed: false` — in-flight run, interrupted or active. Resume candidate.
- `currentStage: null`, `completed: true` — last run finished cleanly. Never offered for resume.
- Stage-entry writes always set `completed: false`, so a new pass over a previously completed workflow (e.g. a second implementation pass spawned by the refine loop) flips the state back to in-flight on its first stage.

`workflow-recordProgress` encapsulates the read-modify-write for both modes; the orchestrator never edits meta directly.

## Scenario: fresh-session resume

1. User says "continue item 4" → `workflowDeliver` runs its status check and hands the **full** stage definition — including `workItem: "4"` — to the orchestrator, as always.
2. The orchestrator resolves the work item and workload path, then reads `meta.swc.workflowState["deliver"]`.
3. `currentStage` is non-null → the confirm-intent prompt becomes a resume prompt: earlier stages ticked, recorded stage highlighted, "resume or restart?".
4. On resume, the stage loop starts at the recorded stage. Banners, progress recording, and gates apply to every stage that runs — resume never invokes a stage skill outside the loop.
5. The recorded stage may be unfinished; the stage skill starts normally and discovers existing docs/notes itself.

Guard rails: a recorded stage missing from the current definition, or a failed meta read, degrades to a fresh run with a warning — resume never blocks the workflow.

## Workflow definition persistence (resolved)

Resume does not need a persisted definition: the entry skill always supplies the full stage+skill list when invoking the orchestrator, and the recorded `currentStage` is matched against it by name. `workflow-manifest.json` (written by `context-initWorkflowManifest`) remains a reporting/future artefact — e.g. for a generic resume that routes without an entry skill — and is not read by the orchestrator.

## Scenario: loopback

User re-enters `requirements` from `implement`: the orchestrator runs the stage loop from `requirements`; the stage-entry write moves `currentStage` back and appends a new event. The event log preserves the full history — `workflowState` only ever holds the latest position. Per-stage states (`superseded` etc.) were considered and not implemented; the append-only log covers the audit need.
