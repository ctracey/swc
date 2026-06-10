# Architecture — Meta + Workflow Progress

Extension to the workload-MCP design that lets SWC record stage progress per work item without coupling the MCP to SWC's workflow shape.

## Goal

Record a work item's progress through SWC workflow stages (Plan, Deliver, Implement and their sub-stages) in the workload artefact, so that:

1. A user can loop back to an earlier stage and the record stays coherent.
2. A new session can resume work on item N by reading where it left off.
3. The MCP remains scenario-agnostic — it does not know about SWC stages, workflows, or exit criteria.

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
│  swc-workload-mcp                                            │
│   - Stores workitems: { id, title, notes, status, meta }     │
│   - status is one of: not-started | wip | done               │
│   - meta is a namespaced free-form JSON blob                 │
│   - No knowledge of any namespace's contents                 │
└──────────────────────────────────────────────────────────────┘
```

The MCP is a generic workload store. SWC is the only thing that knows what a "workflow stage" is.

## Workitem shape (MCP-owned)

```jsonc
{
  "id": "uuid-or-stable-id",
  "n": 4,                       // human-friendly ordinal
  "title": "Add meta support to MCP",
  "notes": "Free text. Replaces 'description'. No structure imposed.",
  "status": "not-started" | "wip" | "done",
  "meta": {
    "<namespace>": { /* any valid JSON */ }
  }
}
```

Changes vs current shape:

- `description` → **`notes`** (it's just a text bucket; the new name reflects that).
- `meta` is added as a top-level object, keyed by namespace.

## SWC's namespace: `swc-workflow-status`

SWC writes its progress blob under `meta["swc-workflow-status"]`. The MCP does not validate this — schema ownership lives in SWC.

```jsonc
{
  "version": 1,
  "currentWorkflow": "deliver",          // "plan" | "deliver" | "implement"
  "currentStage": "implement",           // skill-level stage name
  "stages": {
    "requirements":    { "state": "done",    "enteredAt": "...", "completedAt": "...", "exitEvidence": { /* free */ } },
    "specs":           { "state": "done",    "enteredAt": "...", "completedAt": "..." },
    "solutionDesign":  { "state": "done",    "enteredAt": "...", "completedAt": "..." },
    "implement":       { "state": "active",  "enteredAt": "..." },
    "refine":          { "state": "pending" },
    "review":          { "state": "pending" },
    "accept":          { "state": "pending" }
  },
  "history": [                           // optional append-only log of transitions
    { "at": "...", "from": "specs", "to": "requirements", "kind": "loopback" }
  ]
}
```

Stage states:

- `pending` — not yet entered.
- `active` — currently being worked on.
- `done` — exit criteria met and recorded.
- `superseded` — was `done`, then a loopback re-opened an earlier stage and invalidated this one.

## MCP tool surface

### Renames / changes

- All references to `description` become **`notes`**.
- `list` and `find` **do not** return `meta` by default. They accept an opt-in flag.

### New tools

- **`get(target)`** — exact lookup by `n` or `id`. Returns the full workitem **including `meta` by default**. Errors if not found.
- **(optional) `set_meta(target, namespace, value)`** — replace one namespace blob.
- **(optional) `patch_meta(target, namespace, partial)`** — shallow-merge into a namespace blob.

If `set_meta` / `patch_meta` are not added, SWC writes via an extended `update`/`set_status` that accepts a `meta` patch — see open questions.

### `includeMeta` semantics

Where it applies:

| Tool       | Default              | Opt-in flag                                                 |
| ---------- | -------------------- | ----------------------------------------------------------- |
| `list`     | meta omitted         | `includeMeta: true` or `metaNamespaces: ["swc-workflow-status", ...]` |
| `find`     | meta omitted         | same                                                        |
| `summary`  | meta omitted         | same                                                        |
| `get`      | **meta included**    | `includeMeta: false` to opt out                             |

`metaNamespaces` is preferred over a boolean — keeps payloads small as meta grows and lets callers ask for exactly what they need.

### `find` semantics (to confirm)

`find` is a search-style tool — it should return **zero or more** matches against a query (e.g. title substring). `get` is the new exact-match counterpart. This separation is the standard MCP pattern (`find` = many by query, `get` = one by identity); confirmation against the current MCP impl is an open question below.

## Scenario walkthroughs

### A. Stage advance (happy path)

1. Orchestrator finishes stage `specs` for item 4. Calls `patch_meta(4, "swc-workflow-status", { stages: { specs: { state: "done", completedAt: now } } })`.
2. Orchestrator enters next stage `solutionDesign`. Calls `patch_meta(4, "swc-workflow-status", { currentStage: "solutionDesign", stages: { solutionDesign: { state: "active", enteredAt: now } } })`.
3. Item `status` flips to `wip` on first stage entry; flips to `done` only when the terminal `accept` stage completes.

### B. Loopback

User re-enters `requirements` from `solutionDesign`:

1. Orchestrator computes the set of stages later than `requirements` in the workflow definition.
2. Orchestrator marks those stages as `superseded` (preserving their prior `exitEvidence` so it can be reused) and `requirements` as `active`.
3. One `patch_meta` call commits the whole transition. `history` appends a `{ kind: "loopback" }` entry.

Rule: **entering an earlier stage invalidates all later stages.** The MCP can't enforce this — the orchestrator does, before writing.

### C. Fresh-session resume

User says "let's continue with item 4":

1. Skill calls `get(4)` — `meta` is returned by default, so `swc-workflow-status` comes back in one call.
2. Skill reads `currentWorkflow` + `currentStage` and routes to the matching SWC stage skill.
3. Stage skill inspects its own `stages[currentStage]` to decide resume-mid-stage vs start-fresh.

## Open questions

1. **Does current `find` already return multiple matches?** Needs verification against `swc-workload-mcp/tools.py` before we lock the `find` vs `get` split.
2. **Atomicity of status + meta writes.** When the terminal stage completes, we want item `status: done` and `meta["swc-workflow-status"].currentStage: accept (done)` to land together. Options: (a) extend `complete`/`set_status` to accept an optional `meta` patch, (b) accept eventual consistency between two calls, (c) introduce a transactional `update` tool. Leaning (a).
3. **Dedicated `set_meta` / `patch_meta` vs piggy-backing on `update`.** Two narrow tools are easier to reason about; one general tool is fewer surface items. Probably narrow tools.
4. **Namespace key style.** `swc-workflow-status` (kebab) vs `swc:workflow-status` (colon-namespaced). Colon scales better if SWC adds more namespaces (`swc:notes-index`, etc.). Probably colon.
5. **Schema versioning.** `version: 1` on the meta blob is cheap insurance — SWC can migrate older blobs on read. Worth doing from day one.
6. **Loopback: `superseded` vs reset to `pending`.** `superseded` preserves prior exit evidence for re-use (faster re-traversal); `pending` is simpler. Preference: `superseded`, but it adds a state to handle.
7. **Validation.** Should SWC ship a tiny validator skill that checks `swc-workflow-status` shape on read? Belt-and-braces, low cost. Probably yes.
8. **`summary` tool surface.** Should `summary` synthesise stage progress for display (e.g. "3/7 stages done") even though it doesn't understand the namespace? Likely no — keep `summary` generic; SWC computes display from `get` results.
9. **Listing by stage.** Do we need `list({ metaFilter: { "swc-workflow-status.currentStage": "implement" } })` to find "everything currently in implement"? Useful, but couples MCP to meta-path querying. Defer until a real use case appears.
10. **`history` size growth.** Append-only history can grow indefinitely with loopbacks. Cap at last N entries, or leave unbounded? Probably cap (e.g. last 20) — it's mostly diagnostic.
11. **Migration of existing items.** Existing workloads have no `meta` and use `description`. Need a one-shot migration path: rename `description` → `notes`, add empty `meta: {}`. Cheap; do as part of the MCP version bump.
