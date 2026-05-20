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

- Skills must not edit `workload.json` directly. A hook should prevent direct edits and redirect to the CLI.
- The CLI must follow the existing branch → folder lookup via `.swc/_meta.json`.
- Status updates must roll up to the parent automatically.
- Status updates must never downgrade a `[x]` item silently (preserve current `workload_item-start` guard).
- Each work item must have a stable ID that does not change across renumbering, re-ordering, or re-parenting.
- Items can be looked up by ID or by number.
- Numbers can change; IDs cannot.
- New work items must not have a number prefix in the title — the CLI assigns numbers at render time; the user does not.
- Numbers are display-only. They are computed on render from the item's position in the tree and are **not stored** in `workload.json`.
- Workitem folders under `.swc/<workload>/workitems/` are named by SHA hash ID — never by number — so folder paths survive renumbering.
- Cross-doc references (changelog, notes, plan) cite items as `[<hash>] <title>` — e.g. `[abc123] CLI tool for workload`. Hash is the durable anchor; title is for human readability and may go stale if the item is renamed.
- Reports can show or hide hashes.
- The CLI must handle missing/non-existent workload files with a clear error and recommend `init`.
- Must include automated tests.

## Out of scope

- Plugin packaging / dependency management beyond what's needed for the swc / swc-workload split (deeper packaging covered by 3.3).
- MCP wrapper (covered by 3.4).
- Workload radiator / progress visualisation (covered by 4).
- Concurrency / merge handling — workloads are branch-scoped; the user manages merges manually for now.
- Migration of existing markdown workloads to JSON / IDs — fresh start, no automated backfill.

## Decisions

Resolved during planning — moved here from Parked.

### Data format
Source of truth is `workload.json`. CLI emits plain text for terminals. The hook blocks direct edits to `workload.json` and points the agent at the CLI. Existing skills must switch to CLI invocations rather than reading or editing the file.

### Tool surface
- `swc` is a new parent command, shipped in the main swc plugin. Owns context resolution (current branch → workload.json path via `.swc/_meta.json`) and forwards to the workload backend.
- `swc workload <op>` delegates to `swc_workload --workload <resolved-path> <op>`. `swc_workload` is a pure tree manager — given a path, it manipulates that workload. No git, no `_meta.json`, no branch awareness.
- **3.2 deliverable:** both `swc` and `swc_workload` live in `cli/` of the main `swc` plugin.
- **3.3 deliverable:** `swc_workload` is extracted into its own `swc-workload` plugin, installed via the marketplace. When it's missing, `swc workload` shows an install-guidance prompt referencing the architecture docs (REQ-26). This leaves room for alternative backends later (local / Trello / Jira / Obsidian / etc).

### Workitem ID
SHA hash over: machine username + timestamp + branch + workitem title. Machine username (not git config) so IDs work in non-git contexts. Hash specifics (algorithm, length, timestamp resolution, username source) are still parked.

### Branch & merge scope
Workloads stay branch-scoped. No concurrency primitives, no automatic merge support — when branches merge, the user reconciles workloads manually.

### Folder naming & citation
- Workitem folders under `.swc/<workload>/workitems/` use the SHA hash as the folder name (e.g. `.swc/main/workitems/abc123/requirements.md`).
- In-document references use `[<hash>] <title>` — e.g. `[abc123] CLI tool for workload`. The hash is the durable anchor; the title is included for readability and is allowed to go stale on rename.

### Numbers are display-only
- `workload.json` stores a tree of items (`id`, `title`, `status`, `parent` / `children`) — **no numbers**.
- Numbers (`1.2.3`-style) are computed at render time from depth-first position in the tree.
- CLI lookup accepts numbers as input (`swc workload show 2.3.1`) and resolves them against the current tree state.
- `list`, `show`, and report output still display numbers — they're the human-facing reference.

### Authoring — `move` (consolidated)
A single `move` subcommand handles both relative shifts and absolute repositioning, dispatched on the second positional:
- `move <item> <up|down|top|bottom>` — relative shift within current parent. Siblings reflow; IDs and parent unchanged.
- `move <item> to <target>` — absolute position. The literal `to` keyword is **required**. May reparent (e.g. `move 2.3.1 to 3.2`) or stay within parent (e.g. `move 2.3 to 2.7`). Validates target parent exists; rejects cycles (moving an item into its own subtree).
- Neither form replaces existing items — siblings at the destination shift to make room.
- When moving across parents, **both** the old parent's children and the new parent's children renumber.
- IDs never change on move; only the rendered number changes.

The original separate `reorder` subcommand was folded into `move` during phase 1 — single verb, single concept, dispatched on the second positional.

## Approach direction

Consolidate all workload operations behind a thin two-tier CLI: a context resolver (`swc`) that turns "current branch" into a workload path, and a tree manager (`swc_workload`) that operates on whatever path it's given. User-facing command is `swc workload <op>` (e.g. `swc workload list`, `swc workload add`). Skills shell out to `swc workload <op>` for every interaction. A pre-edit hook on `workload.json` blocks direct edits and points the agent at the CLI.

Numbering and IDs are decoupled: numbers reflect current position in the hierarchy and can change; IDs are stable and used for cross-references. Branch-id prefixes anchor IDs to the workload they came from, which helps when workloads merge.

## Operations the CLI must support

Compiled from the catalog in notes.md plus new requirements in this conversation.

### Lifecycle
- `init` — create a fresh workload (file + heading scaffold, assign branch-id)
- Archive — rename folder with `_archived` suffix (CLI op or stays outside? — see Parked)
- Cleanup — delete folder once all items complete (CLI op or stays outside? — see Parked)

### Authoring
- `add` — add a work item (title only; CLI assigns number; validate no number prefix in title)
- `delete` — delete a work item
- `rename` — rename a work item (title only; ID and status preserved)
- ~~`reorder`~~ — folded into `move <item> <up|down|top|bottom>` during phase 1. See "Authoring — `move` (consolidated)" above.
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
- `summary` — total count, done count, wip (in-progress) count, % progress (used by report-plan)
- ~~`read <item>` — fetch a single item's name + description~~ — **removed during phase 1.** Consumers read `workitems/<id>/requirements.md` directly; the CLI does not need to wrap this access. See REQ-22 in specs.md.
- `exists` — boolean: does workload.md exist for this branch (cheap presence check)
- ~~`complete?` — is the workload populated and confirmed~~ — **removed during phase 1.** No consumer materialised; `workflowPlan_finalise` can read items directly if needed. See REQ-24 in specs.md.

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

### Workitem ID specifics
- Hash algorithm — SHA-1 or SHA-256?
- Hash length — full, or truncated git-style (7 chars)?
- Timestamp resolution — epoch seconds, ms, ISO 8601?
- Username source — `$USER`, `whoami`, `os.getlogin()`? Behaviour when unset.
- Is a separate `branch-id` still needed alongside the workitem hash, or does the hash subsume it?

### ID surfacing in reports
- How hashes show in the default `list` view without making it noisy (default visibility — citation format is decided).

### Reorder / move edge cases
- Out-of-range target — `move 2.3 to 2.7` when parent 2 only has 4 children. Cap at end, or error?
- Top-level moves — does `move 2.3 to 4` (no dot) promote an item to a new top-level position? Symmetric for demote (`move 4 to 2.3`)?
- Boundary `up`/`down` — `reorder 2.1 up` when already at top. Silent no-op or error?
- Self-move — `move 2.3 to 2.3`. Silent no-op?
- Cycle prevention error semantics — message format and exit code when target is inside the source's subtree.
- Is `reorder` redundant given `move` is a strict superset? Keep `reorder up/down/top/bottom` as ergonomic shortcuts, or fold into `move`?

### Filter syntax
- Deferred — revisit when designing `list` / `find`.
- JSON-style filter (`filter:{status:[wip,not-started]}`) is the candidate; final shape TBC.

### Language & runtime
- Python (matches existing `workload.py` script, no extra runtime needed beyond what skills already use)
- Other (Node, Go, Rust)?
- Trade-off: Python keeps things simple and consistent with the current codebase; alternatives may package better as a standalone binary in `swc-workload`.

### Packaging & install location
- How `swc` (in the main plugin) discovers and invokes `swc-workload` (in its own plugin).
- Whether `swc` is on PATH or invoked via a plugin-relative wrapper.
- Wording + content of the install-guidance prompt when `swc-workload` is missing.
- Where the architecture docs that the prompt references will live.

### List report formatting
- What does the default list look like? (Current `workload.py` output is a good baseline.)
- How are IDs shown when `--show-ids` is on — inline, trailing column, separate line?

### Hook design
- Where does the pre-edit hook live? Plugin-level hook? settings.json?
- How does it detect a `workload.json` edit attempt and redirect?
- What's the message shown to the agent when blocked?

### Test strategy
- Unit tests for parsing, rollup, downgrade guard
- Integration tests for end-to-end CLI invocations
- Test data — sample workloads in fixtures
- Where tests live in the plugin
