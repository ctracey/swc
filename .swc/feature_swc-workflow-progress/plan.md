# Plan

## Goal

Record each work item's progress through SWC workflow stages (Plan, Deliver, Implement and their sub-stages) in the MCP workload artefact, so that:

1. A user can loop back to an earlier stage and the record stays coherent.
2. A new session can resume work on item N by reading where it left off.
3. The MCP remains scenario-agnostic — it has no knowledge of SWC stages, workflows, or exit criteria.

## Background

`swc-workload-mcp` v1.0.0 already supports freeform JSON meta per work item (`meta` is a namespaced free-form blob the MCP stores but does not validate). SWC drives multi-stage workflows (Plan → Deliver → Implement, each with sub-stages) but has nowhere durable to record where a given work item sits in that journey. Without this, resuming work across sessions or looping back to an earlier stage relies on inference rather than recorded state.

All work is SWC-side — no MCP changes required.

## Approach

- **SWC writes under `meta["swc"]`**: `workflowState` (latest position per workflow: `{ currentStage, completed }`) and `workflowEvents` (append-only history). The MCP stores it verbatim; SWC owns the schema.
- **Trigger point**: the workflow orchestrator fires the MCP meta write between emitting the progress banner and invoking the stage skill — a single central point that covers every stage in every workflow, including re-invokes on loopback. A second write after the final stage records completion (`currentStage: null`, `completed: true`).
- **Orchestrator gets work item identity** from an explicit `workItem` field on the workflow definition, passed by the entry skill (session-context inference proved unreliable in testing); the workload path is resolved once via `context-lookup`.
- **Resume (work item 4)**: the orchestrator — not the entry skill — reads `meta.swc.workflowState["<workflow>"]` before the stage loop. A non-null `currentStage` turns the confirm-intent prompt into a resume prompt (resume at recorded stage / restart); the stage loop then starts at the chosen stage with banners, recording, and gates intact. Completed runs (`completed: true`) are never offered for resume; stage-entry writes reset `completed: false` so repeat passes (e.g. implement via the refine loop) behave correctly.
- **Workflow definition persistence (resolved)**: the entry skill always passes the full stage+skill definition to the orchestrator, so resume needs no persisted definition. `workflow-manifest.json` stays a reporting/future artefact and is not read on resume.

Full layering detail and the `meta.swc` schema live in `architecture.md`.

## Open Questions

1. **Loopback handling.** Resolved for now: `workflowState` holds only the latest position and `workflowEvents` preserves full history; per-stage `superseded` states were considered and not implemented.
2. **Atomicity.** When the terminal stage completes, `item.status: done` and the meta update should land together. Likely two sequential MCP calls — acceptable for now.
