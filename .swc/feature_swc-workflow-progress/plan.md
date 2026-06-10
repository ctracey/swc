# Plan

## Goal

Record each work item's progress through SWC workflow stages (Plan, Deliver, Implement and their sub-stages) on the workload artefact, so that:

1. A user can loop back to an earlier stage and the record stays coherent.
2. A new session can resume work on item N by reading where it left off.
3. The MCP remains scenario-agnostic — it has no knowledge of SWC stages, workflows, or exit criteria.

## Background

The workload-MCP currently stores workitems as `{ id, n, title, description, status }`. SWC drives multi-stage workflows (Plan → Deliver → Implement, each with sub-stages) but has nowhere durable to record where a given workitem sits in that journey. Without this, resuming work across sessions or looping back to an earlier stage relies on inference rather than recorded state.

The design pressure is to add stage tracking **without** coupling the MCP to SWC's workflow shape — the MCP should remain a generic workload store usable by any orchestrator.

## Approach

Layer the change so that SWC owns workflow semantics and the MCP stays generic:

- **MCP gains a `meta` field** on each workitem: a namespaced free-form JSON blob the MCP stores but does not validate.
- **`description` → `notes`** rename (it's just a text bucket; the new name reflects that).
- **New `get(target)` tool** for exact lookup by `n` or `id`, returning the full workitem including `meta` by default.
- **`list` / `find` / `summary` omit `meta` by default**, with opt-in via `includeMeta: true` or `metaNamespaces: [...]` to keep payloads small.
- **SWC writes under `meta["swc-workflow-status"]`** (namespace key style TBD — see open questions): `{ version, currentWorkflow, currentStage, stages: { <name>: { state, enteredAt, completedAt, exitEvidence } }, history }`.
- **Stage states:** `pending` → `active` → `done`, plus `superseded` for stages invalidated by a loopback.
- **Loopback rule:** entering an earlier stage marks all later stages `superseded` (preserving their prior `exitEvidence` for re-use). The orchestrator computes the transition; one `patch_meta` call commits it; `history` appends a `{ kind: "loopback" }` entry.
- **Resume:** a fresh session calls `get(n)`, reads `currentWorkflow` + `currentStage`, and routes to the matching SWC stage skill.
- **Migration:** existing items have no `meta` and use `description` — one-shot migration renames the field and adds `meta: {}`, shipped with the MCP version bump.

Tooling for meta writes is still open: either dedicated `set_meta` / `patch_meta` tools, or extending `update` / `set_status` to accept a `meta` patch. Leaning toward narrow dedicated tools — see open questions.

Full design detail (workitem shape, scenario walkthroughs, `includeMeta` semantics table) lives in `architecture.md`.

## Open Questions

1. **Does current `find` already return multiple matches?** Needs verification against `swc-workload-mcp/tools.py` before locking the `find` vs `get` split.
2. **Atomicity of status + meta writes.** When the terminal stage completes, `status: done` and `meta["swc-workflow-status"].currentStage: accept (done)` should land together. Options: (a) extend `complete` / `set_status` to accept an optional `meta` patch, (b) accept eventual consistency, (c) introduce a transactional `update`. Leaning (a).
3. **Dedicated `set_meta` / `patch_meta` vs piggy-backing on `update`.** Narrow tools are easier to reason about; one general tool is fewer surface items. Probably narrow tools.
4. **Namespace key style.** `swc-workflow-status` (kebab) vs `swc:workflow-status` (colon-namespaced). Colon scales better as SWC adds more namespaces. Probably colon.
5. **Schema versioning.** `version: 1` on the meta blob is cheap insurance — worth doing from day one.
6. **Loopback: `superseded` vs reset to `pending`.** `superseded` preserves prior exit evidence; `pending` is simpler. Preference: `superseded`, but it adds a state to handle.
7. **Validation.** Should SWC ship a tiny validator skill that checks `swc-workflow-status` shape on read? Probably yes — belt-and-braces, low cost.
8. **`summary` tool surface.** Should `summary` synthesise stage progress for display? Likely no — keep `summary` generic; SWC computes display from `get` results.
9. **Listing by stage.** Do we need `list({ metaFilter: { "swc-workflow-status.currentStage": "implement" } })`? Useful, but couples the MCP to meta-path querying. Defer until a real use case appears.
10. **`history` size growth.** Cap at last N entries (e.g. 20) or leave unbounded? Probably cap — it's mostly diagnostic.
11. **Migration of existing items.** Rename `description` → `notes`, add empty `meta: {}`. Cheap; do as part of the MCP version bump.
