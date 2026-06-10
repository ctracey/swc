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

- **SWC writes under `meta["swc-workflow-status"]`**: `{ currentStage, enteredAt, workflow, stages }`. The MCP stores it verbatim; SWC owns the schema.
- **Trigger point**: the workflow orchestrator fires the MCP meta write between emitting the progress banner and invoking the stage skill — a single central point that covers every stage in every workflow, including re-invokes on loopback.
- **Orchestrator gets work item identity** via an optional `workItem` field added to the workflow definition schema. Entry skills (`workflowDeliver`, `workflowPlan`, etc.) pass the item number when handing off to the orchestrator.
- **Workflow definition persistence**: how a fresh session reconstructs the full stage list (not just `currentStage`) is an open question — see below.
- **Resume**: a fresh session reads `meta["swc-workflow-status"]`, gets `currentStage` + the stage list, and routes to the matching skill.

Full layering detail and the `swc-workflow-status` schema live in `architecture.md`.

## Open Questions

1. **Workflow definition persistence.** On resume, we need the full stage list to route correctly. Options: (a) store the stage list in meta at workflow start, (b) derive it from `workflow` name (SWC hard-codes the mapping). Option (a) is more robust; option (b) is simpler. Not yet decided.
2. **Loopback handling.** When a user re-enters an earlier stage, do we mark later stages `superseded` (preserving exit evidence) or reset to `pending` (simpler)? Prefer `superseded` but adds a state to handle.
3. **Atomicity.** When the terminal stage completes, `item.status: done` and the meta update should land together. Likely two sequential MCP calls — acceptable for now.
