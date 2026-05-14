---
name: WI-3.2 requirements
description: Requirements for the swc workload CLI tool — consolidates all workload.md operations behind a single interface so skills no longer edit the file directly.
type: project
---

# Requirements — 3.2: cli tool for workload

## Intent

Build a single CLI tool that owns every operation against `workload.md`. Skills should call the CLI rather than read/edit the file directly. This consolidates rollup logic, downgrade guards, lookup, and rendering in one place — making the behaviour testable, consistent, and ready for follow-on work (3.3 plugin packaging, 3.4 MCP wrapper).

The CLI is also a step toward more durable workload identity: items get a stable ID so docs and cross-references survive renumbering, re-ordering, and re-parenting.

## Constraints

- Skills must not edit `workload.md` directly. A hook should prevent direct edits and redirect to the CLI.
- The CLI must follow the existing branch → folder lookup via `.swc/_meta.json`.
- Status updates must roll up to the parent automatically.
- Status updates must never downgrade a `[x]` item silently (preserve current `workload_item-start` guard).
- Each work item must have a stable ID that does not change across renumbering, re-ordering, or re-parenting.
- ID format is two-part: `<branch-id>.<workitem-id>`.
- Items can be looked up by ID or by number.
- Numbers can change; IDs cannot.
- New work items must not have a number prefix in the title — the CLI assigns numbers; the user does not.
- Docs should reference items by ID, not number.
- Reports can show or hide IDs.
- The CLI must handle missing/non-existent workload files with a clear error and recommend `init`.
- Must include automated tests.

## Out of scope

- Plugin packaging / dependency management (covered by 3.3).
- MCP wrapper (covered by 3.4).
- Workload radiator / progress visualisation (covered by 4).

## Approach direction

Consolidate all workload operations behind a single CLI. Likely invoked as `swc workload <op>` (e.g. `swc workload list`, `swc workload add`). Skills shell out to the CLI for every workload interaction. A pre-edit hook on `workload.md` blocks direct edits and points the agent at the CLI.

Numbering and IDs are decoupled: numbers reflect current position in the hierarchy and can change; IDs are stable and used for cross-references. Branch-id prefixes anchor IDs to the workload they came from, which helps when workloads merge.

## Operations the CLI must support

Compiled from the catalog in notes.md plus new requirements in this conversation.

### Lifecycle
- `init` — create a fresh workload (file + heading scaffold, assign branch-id)
- Archive — rename folder with `_archived` suffix (CLI op or stays outside? — see Parked)
- Cleanup — delete folder once all items complete (CLI op or stays outside? — see Parked)

### Authoring
- `add` — add a work item (title only; CLI assigns number; validate no number prefix in title)
- `remove` — remove a work item
- `rename` — rename a work item (title only; ID and status preserved)
- `reorder` — change item order among siblings (mechanism — see Parked)
- `reparent` — change item hierarchy (e.g. 2.4.1 → sibling of 2.4, or sibling → child)

### Status
- Set status (`done` / `in-progress` / `not-started`)
- Roll up parent automatically
- Never downgrade `[x]` silently

### Lookup / resolution
- Locate file from current branch via `_meta.json` (fallback: most recently modified folder)
- Resolve target item by number, ID, or description keyword
- Disambiguate when multiple matches

### Read / report
- `list` — full workload, visual rendering with status symbols
- `list --filter status:in-progress` — match filter (only items matching)
- `list --filter-out status:done` — exclude filter (everything except matches)
- `show <item>` — show a work item plus its child items
- `find <keyword>` — replace ad-hoc grep usage in skills
- `summary` — total count, done count, % progress (used by report-plan)
- `read <item>` — fetch a single item's name + description (used by workflowDeliver_implement to brief the implementation agent)
- `exists` — boolean: does workload.md exist for this branch (cheap presence check)
- `complete?` — is the workload populated and confirmed (used by workflowPlan_finalise)

### Cross-doc support
- Expose item descriptions in machine-readable form so `ship` can match changed files against items and prompt the user.

### Help & discoverability
- `--help` at the top level
- Per-op `--help`

### Output formats
- Human-readable for terminal use
- JSON / structured output for skills to parse

## Parked — to resolve in solution-design

These are open questions and design decisions to work through before specs are sealed.

### Data format
- Stay with markdown (current — human-greppable, but harder to parse reliably and can't store IDs cleanly)
- Move to JSON / YAML (robust, structured, supports IDs, but loses the "open workload.md and read it" affordance)
- Hybrid (e.g. JSON as source of truth, markdown as a generated view)

### Branch-id scheme
- When is `<branch-id>` assigned? On `init`?
- Where stored — `_meta.json`? Inline in the workload file?
- How is uniqueness guaranteed across branches that may later merge?
- Format — short slug, hash, sequential int?

### Workitem-id scheme
- Sequential? Hash? UUID?
- How are IDs assigned to existing workloads on migration?
- Consider a git-commit-style content hash (e.g. SHA over title + timestamp + branch-id + parent-id). Content-addressed IDs make parallel additions across branches essentially collision-free without coordination — same approach git uses for commit SHAs. Trade-off: longer IDs vs sequential ints, but stable and merge-safe.

### Concurrency & merge
- Atomic writes? Lock file? Or rely on git for conflict resolution?
- What's the merge story when two parallel branches both add items to the same workload?

### Migration
- Existing workloads have no IDs. How does the CLI add IDs to current items on first run?
- Backfill from filename / position? Generate fresh?

### Reorder mechanism
- Move-to-position (`reorder 2.3 after 2.5`)?
- Up/down (`reorder 2.3 up`)?
- Drag-style index assignment?

### Reparent mechanism
- Explicit (`reparent 2.4.1 --parent 2`)?
- Promote/demote shorthand?

### Tool name & invocation
- `swc workload <op>` feels right — confirms the surface
- Single binary `swc` with subcommands, vs separate `swc-workload` CLI?

### Language & runtime
- Python (matches existing `workload.py` script, no extra runtime needed beyond what skills already use)
- Other (Node, Go, Rust)?
- Trade-off: Python keeps things simple and consistent with the current codebase; alternatives may package better as a standalone binary for 3.3.

### Packaging & install location in the plugin
- Where does the script live so it's packaged with the plugin and discoverable to skills?
- Invocation path — relative to plugin root? On PATH?

### List report formatting
- What does the default list look like? (Current `workload.py` output is a good baseline.)
- How are IDs shown when `--show-ids` is on — inline, trailing column, separate line?
- Filter syntax — `key:value` pairs only, or richer expressions?

### Hook design
- Where does the pre-edit hook live? Plugin-level hook? settings.json?
- How does it detect a `workload.md` edit attempt and redirect?
- What's the message shown to the agent when blocked?

### Test strategy
- Unit tests for parsing, rollup, downgrade guard
- Integration tests for end-to-end CLI invocations
- Test data — sample workloads in fixtures
- Where tests live in the plugin

### Doc references by ID
- How are existing docs migrated to reference IDs instead of numbers?
- Convention for citing an item — `[3.2]` (number) vs `[id:abc123]` vs both?
