# Notes

## MCP boundary (agreed)

The plugin and `swc-workload-mcp` split responsibility as follows:

**Plugin owns:**
- Branch → folder resolution (`context-lookup`)
- `.swc/_meta.json` mapping
- All narrative docs in `.swc/<folder>/`: `plan.md`, `architecture.md`, `notes.md`, `changelog.md`, `pipeline.md`
- Per‑workitem docs in `.swc/<folder>/workitems/<N>/`: `requirements.md`, `specs.md`, `solution.md`, `context.md`, `summary.md`, `feedback.md`, `code-review-findings.md`, `quality-baseline.md`, `tech-debt.md`
- Workflow orchestration (Plan / Deliver / Implement skill chains)
- Spawning implementation agents

**MCP owns:**
- The workload artefact at a path the plugin passes in
- Item structure, status markers, parent rollup
- All CRUD on workload items

The MCP does **not** know about branches, folders, `_meta.json`, or anything beyond the single workload file at the path it's given.

## Artefact rename

`workload.md` → `workload.json`. JSON diffs will be noisier in PRs — accepted trade‑off. The rendered visual list (now via MCP) replaces the in‑session need to read the raw file.

## MCP tool surface used by the plugin

| Tool | Used for |
|---|---|
| `init` | Create the workload artefact at a folder path (called from `context-init`) |
| `exists` | Check whether a workload exists at a folder path |
| `list` | Render the full work item list; filter by status |
| `find` | Resolve an item by number or description match |
| `get` | Read a single item's details |
| `add` | Add new items or a breakdown tree |
| `set_status` | Update an item's status; MCP handles parent rollup |
| `find_first(status=not-started)` (or equivalent) | Find the next not‑started item for NEXT STEP |

## `context-lookup` reframe

Output changes from `Located: .swc/<folder>/workload.md` to a structured form that separates context from workload presence:

```
Found context {type: branch, source: main, name: main, location: .swc/main, workload: exists}
```

Field semantics:
- `type` — `branch` or `folder` (the latter for non‑git fallback)
- `source` — the value mapped *from* (branch name or directory name)
- `name` — the resolved context name (post‑mapping, basename of location)
- `location` — full `.swc/<folder>` path
- `workload` — `exists` or `missing` (from MCP `exists` tool, mirrors MCP vocabulary)

For multiple folder candidates, list each in the same shape with its own `workload` status so the user can pick.

## MCP dependency handling (agreed)

The plugin treats `swc-workload-mcp` as an external dependency it does not own. Installation stays the user's responsibility — the plugin checks for it and guides setup when missing.

**Mechanism:**
- A reusable check skill (`swc:mcp-check`) probes for MCP presence and is silent when present.
- When missing, it hands off to a guide skill (`swc:mcp-install`) that walks the user through registering the MCP.
- The check is invoked at two trigger points:
  - **Proactive** — `context-init` runs it at workload creation so first-time setup surfaces the guide before any tool call.
  - **Defensive** — MCP-heavy front-line skills (deliver, plan, report, ship, etc.) run it before their first MCP call.

**Rejected: `PreToolUse` hook keyed on `mcp__swc-workload__*`.** Hooks cannot fire when a tool isn't registered at all, so they don't cover the "not installed" case. A hook may be added later as a safety net if call sites slip through the skill checks.

**Why not pollute every skill:** the check is one skill invocation at the top of each MCP-heavy front-line skill — same shape as the existing `setup-permissions` invocation pattern. Workflow stage skills inherit context from the front-line caller, so they don't re-check.

## Confirmed scope boundaries

- `_meta.json` stays plugin‑owned — MCP doesn't see it
- `pipeline.md` stays plugin‑owned — sits alongside workload but is unrelated
- Spawned agent prompts change: no more "read workload.md" instructions; agents call MCP via the same registration the plugin uses

## Out of scope for this PR

- Refactoring the agent‑side workflow stages (`workflowImplement_*`) beyond their workload touchpoints
- Any new functionality in the MCP itself
- Migration of existing `.swc/<folder>/workload.md` files in other branches — those are orthogonal; users handle their own conversions

## Test scenarios

Key workload interaction moments across the workflows. Each row is a candidate test scenario — described as *trigger → MCP call → what to verify*.

### Plan workflow

| # | Moment | MCP call | Verify |
|---|---|---|---|
| P1 | `workflowPlan_context` — start of planning | `exists(<folder>)` | Branches correctly between "fresh start" and "existing workload" (replace/extend/sibling/new‑sections) |
| P2 | `workflowPlan_context` — fresh start | `init(<folder>)` | Workload artefact created at the resolved path |
| P3 | `workflowPlan_delivery` — write skeleton | `add(...)` × N phases | Top‑level items written with no sub‑items; no status set (all not‑started) |
| P4 | `workflowPlan_breakdown` — write full breakdown | `add(...)` (batched or sequential) | Items + sub‑items written with correct numbering and hierarchy |
| P5 | `workflowPlan_breakdown` — playback | `list()` | Rendered output matches what was written |
| P6 | Sibling mode — existing items renumbered | `add` after renumber | Old item `1.2` ends up at `1.1.2`; new tree at `2.*` |

### Deliver workflow

| # | Moment | MCP call | Verify |
|---|---|---|---|
| D1 | `workflowDeliver` entry — user names item by number | `get("2.3")` | Returns the correct item; missing item triggers "add untracked" flow |
| D2 | `workflowDeliver` entry — user names item by description | `find("auth bug")` | Returns the best match; ambiguous matches surface to user |
| D3 | `workflowDeliver` entry — no item specified | `list(status=in-progress)` | Single in‑progress item is auto‑picked; multiple/none → ask user |
| D4 | `workflowDeliver` entry — user describes untracked work | `add(...)` | New item appended; correct number returned and used downstream |
| D5 | `workflowDeliver` entry — mark item in‑progress (silent) | `set_status(N, in-progress)` | Item flips to `[-]`; parent rolls up to `[-]` |
| D6 | `workflowDeliver_requirements` / `_review` — read item | `get(N)` | Item name + description loaded for display |
| D7 | `workflowDeliver_accept` — happy path | `set_status(N, done)` | Item flips to `[x]`; parent rolls up to `[x]` only when all siblings are `[x]` |
| D8 | `workflowDeliver_accept` — partial sibling completion | `set_status(N, done)` | Parent stays `[-]` while any sibling is still `[ ]` or `[-]` |

### Implement workflow (agent‑side)

| # | Moment | MCP call | Verify |
|---|---|---|---|
| I1 | `workflowImplement_orient` — pass 1 | `get(N)`, `set_status(N, in-progress)` | Item name resolved; status flipped to `[-]` |
| I2 | `workflowImplement_orient` — pass 2 / 3 (refine loop) | `set_status(N, in-progress)` | Idempotent — already‑`[-]` stays `[-]`; never downgrades `[x]` |
| I3 | Refine loop re‑spawn | `get(N)` (in new agent) | Spawned agent resolves correct item via MCP, not via filesystem read |

### Reporting

| # | Moment | MCP call | Verify |
|---|---|---|---|
| R1 | `/workload` | `list()` | Full tree rendered with status symbols (✔ / ▣ / □) |
| R2 | `/report` — NEXT STEP | `find_first(status=not-started)` (or equivalent) | Returns first `[ ]` item top‑to‑bottom; respects hierarchy |
| R3 | `/workload` — empty workload | `list()` | Returns empty cleanly; doesn't error |

### Ship

| # | Moment | MCP call | Verify |
|---|---|---|---|
| S1 | Match local changes → items | `list()` + local keyword match | Candidate items surfaced for user confirmation |
| S2 | User confirms status updates | `set_status(N, done)` per item | Multiple updates applied; rollups correct |

### Cross‑cutting scenarios

Highest‑risk areas — cover these first.

- **C1 — Parent rollup correctness**: When the MCP applies rollup, the plugin must trust it. Cover all transitions: `[ ]` → `[-]`, partial `[x]` → `[-]`, all `[x]` → `[x]`. Driven by D5/D7/D8 but worth isolating.
- **C2 — `set_status(in-progress)` idempotency**: Called from `workflowDeliver` entry *and* every pass of `workflowImplement_orient`. Must be safe to repeat. Must not downgrade `[x]`.
- **C3 — Spawned agent has MCP access**: After `workflowDeliver_implement` spawns the agent, the agent's first MCP call succeeds without re‑registering. One‑shot smoke test; if it breaks, everything fails.
- **C4 — Missing workload at path**: Every read‑side call (`list`/`get`/`find`/`find_first`) called against a folder where `exists` is false. MCP should error sensibly; plugin should surface that as "no workload — run `/swc:workflowPlan`".
- **C5 — `context-lookup` output when workload missing**: `Found context {... workload: missing}` — verifies the new structured output correctly reflects MCP state.

### Suggested test layering

1. **Unit‑level (mocked MCP)** — one test per skill, asserting it makes the right MCP call(s) for each branch in its logic. Fast, deterministic, covers most of the table.
2. **Integration (real MCP)** — one happy‑path walk of each workflow end‑to‑end (plan → deliver → implement → accept → ship). Catches plumbing breaks.
3. **Cross‑cutting** — C1–C5 as targeted scenarios against the real MCP. These are the ones a unit test can't honestly cover.

## Open questions

None at planning time. If MCP behaviour differs from assumptions during implementation, capture in `changelog.md` and surface back to planning.
