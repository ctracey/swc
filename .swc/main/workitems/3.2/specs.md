---
name: WI-3.2 specs
description: Acceptance scenarios and EARS requirements for the swc workload CLI tool.
type: project
---

# Specs — 3.2: cli tool for workload

## Users and Personas

### Developer (human)
Invokes the CLI directly from a terminal (`swc workload list`, `swc workload add "title"`). Reads human-readable output. Goal: manage the workload without hand-editing files.

### Skill (AI agent)
Invokes the CLI programmatically from inside a skill chain. Parses JSON output (`--json`) to drive subsequent steps. Goal: read, write, and check workload state without parsing markdown.

## User Journeys

### Happy paths

1. **Init** — developer runs `swc workload init` on a new branch; CLI creates `workload.json` and registers branch in `_meta.json`.
2. **Author** — developer adds, renames, deletes items; CLI assigns hash IDs; numbers reflow on every structural change.
3. **Edit structure** — developer reorders within a parent or moves across parents; IDs stay stable, numbers reflow.
4. **Status flow** — skill or developer transitions item between `not-started → in-progress → done` via `reset` / `start` / `complete`; parent rolls up automatically.
5. **Read** — `list` (full tree or `list <ref>` for a subtree), `find` for developer; `summary`, `exists` for skills.
6. **Bridge to docs** — `ship` skill queries CLI to match changed files against items.

### Non-happy / alt paths

7. **Probe non-existent workload** — skill calls `exists`; CLI returns `false`; skill decides what to do.
8. **Find returns multiple hits** — `find "cli"` returns several matches; caller decides which to act on.

### Error paths

9. **Direct edit attempt** — agent tries to edit `workload.json`; pre-edit hook blocks the write and instructs use of the CLI.
10. **Title with number prefix** — `add "1.1 something"` rejected with clear message.
11. **Status downgrade** — `reset <done item>` (or `start <done item>`) silently preserves done.
12. **Move cycle** — `move 2.3 to 2.3.1` rejected with clear cycle message.
13. **Move target missing parent** — rejected with clear error.
14. **Op on branch with no workload** — non-`init`, non-`exists` op exits non-zero recommending `init`.
15. **`swc-workload` plugin not installed** — `swc workload <op>` shows install-guidance prompt referencing architecture docs.
16. **Reference does not resolve** — `show 9.9` (no such item) exits non-zero with not-found message.

## Requirements

### Lifecycle
- **REQ-01** (event) — WHEN `init` runs on a branch with no workload, the CLI SHALL create `workload.json` and register the branch→folder mapping in `_meta.json`.
- **REQ-02** (unwanted) — IF `init` runs on a branch that already has a workload, THEN the CLI SHALL refuse to overwrite and report the existing path.

### Authoring
- **REQ-03** (event) — WHEN `add "<title>"` runs, the CLI SHALL assign a stable hash ID, append the item under the chosen parent, and include it in subsequent list output.
- **REQ-04** (unwanted) — IF the supplied title begins with a number-prefix pattern, THEN the CLI SHALL reject with a message stating numbers are auto-assigned.
- **REQ-05** (event) — WHEN `delete <item>` runs, the CLI SHALL delete the item and its descendants; remaining siblings reflow numbers.
- **REQ-06** (event) — WHEN `rename <item> "<new title>"` runs, the CLI SHALL update the title and preserve the item's ID, status, and position.
- **REQ-07** (unwanted) — IF a `rename` title begins with a number-prefix pattern, THEN the CLI SHALL reject the request.
- **REQ-08** (event) — WHEN `move <item> <up|down|top|bottom>` runs (direction form), the CLI SHALL shift the item among its current siblings; ID and parent unchanged; numbers reflow.
- **REQ-09** (event) — WHEN `move <item> to <target>` runs (absolute form, `to` keyword required), the CLI SHALL relocate the item and its subtree to the target position, reparenting if necessary; IDs preserved; numbers reflow for both old and new parent.
- **REQ-10** (unwanted) — IF a `move` would create a cycle (target inside source's subtree), THEN the CLI SHALL reject with a clear cycle message and non-zero exit.
- **REQ-11** (unwanted) — IF the move target's parent does not exist, THEN the CLI SHALL reject with a clear error.

### Status
- **REQ-12** (event) — WHEN `reset <item>` / `start <item>` / `complete <item>` runs, the CLI SHALL set the item's status (to `not-started` / `in-progress` / `done` respectively) and re-roll the parent (all-done → done; any-in-progress-or-partial-done → in-progress; all-not-started → not-started).
- **REQ-13** (unwanted) — IF `start` is invoked on a `done` item, THEN the CLI SHALL silently preserve `done` (no error, no file change) and exit 0. `reset` is an explicit re-open verb and SHALL change a `done` item back to `not-started`.

### Lookup / resolution
- **REQ-14** (state) — WHILE `find` or `list --filter` matches multiple items, the CLI SHALL return all matches in the output (no disambiguation prompt — caller decides what to do).
- **REQ-15** (event) — WHEN the user references an item by number or ID, the CLI SHALL resolve it to a single item and proceed.
- **REQ-16** (unwanted) — IF a reference does not resolve to exactly one item, THEN the CLI SHALL exit non-zero with a clear "not found" message.

### Read / report
- **REQ-17** (event) — WHEN `list` runs with no `ref` and no filters, the CLI SHALL render the full tree with visual status symbols.
- **REQ-18** (event) — WHEN `list` runs with `--filter` / `--exclude` and no `ref`, the CLI SHALL respect the filter and render only matching / non-matching items.
- **REQ-19** (event) — WHEN `list <ref>` runs (item reference supplied), the CLI SHALL render that item plus its descendants. Filters (`--filter` / `--exclude`) are also accepted and apply to the subtree — a parent is kept when any descendant matches.
- **REQ-20** (event) — WHEN `find <keyword>` runs, the CLI SHALL return all items whose title matches.
- **REQ-21** (event) — WHEN `summary` runs, the CLI SHALL emit total count, done count, in-progress (wip) count, and progress percentage.
- **REQ-22** (removed) — `read <item>` was a planned machine-readable item-detail op. Removed during phase 1 once it became clear that consumers (notably workflowDeliver_implement) can read `requirements.md` directly from `workitems/<id>/` without going through the CLI. No `read` subcommand exists on either `swc_workload` or `swc workload`.
- **REQ-23** (event) — WHEN `exists` runs, the CLI SHALL emit a boolean for whether a workload exists for the current branch.
- **REQ-24** (removed) — `complete?` was a planned op for checking whether a workload was populated and marked complete. Removed during phase 1 — no consumer materialised, and the underlying `complete` flag was never wired into a workflow-complete op. The `complete` boolean has also been dropped from the `workload.json` schema; it can be added back later if a future workflow-complete op needs it.

### Missing prerequisites
- **REQ-25** (unwanted) — IF a non-`init`, non-`exists` op runs on a branch with no workload, THEN the CLI SHALL exit non-zero with an error recommending `init`.
- **REQ-26** (unwanted) — IF `swc workload <op>` runs without the `swc-workload` plugin installed, THEN `swc` SHALL display an install-guidance prompt referencing the architecture docs.

### Direct-edit guard (hook)
- **REQ-27** (unwanted) — IF an agent attempts to edit `workload.json` directly, THEN the pre-edit hook SHALL block the write and instruct the agent to use the CLI.

### Output / discoverability
- **REQ-28** (optional) — WHERE `--json` is supplied, the CLI SHALL emit structured JSON output for skill parsing.
- **REQ-29** (event) — WHEN `--help` is invoked at any scope, the CLI SHALL emit usage information for that scope.

### Citation & folder layout
- **REQ-30** (ubiquitous) — Workitem folders under `.swc/<workload>/workitems/` SHALL be named by SHA hash ID, never by number.
- **REQ-31** (ubiquitous) — Cross-doc references to items SHALL use the form `[<hash>] <title>`.

### Sibling title uniqueness
- **REQ-32** (unwanted) — IF `add` is given a title that matches an existing sibling's title (full-string match, case-insensitive), THEN the CLI SHALL reject the request with a clear collision message and leave the workload unchanged.
- **REQ-33** (unwanted) — IF `rename` is given a title that matches another sibling's title (full-string match, case-insensitive), THEN the CLI SHALL reject the request with a clear collision message and leave the workload unchanged. The item being renamed is excluded from its own collision check, so renaming to the current title (or a case variant of it) is allowed.

## Acceptance Scenarios

### REQ-01 — init creates workload
```gherkin
Scenario: init on a fresh branch
  Given the current branch has no entry in .swc/_meta.json
  And no folder under .swc/ matches the branch
  When I run `swc workload init`
  Then a workload.json file is created at .swc/<folder>/workload.json
  And .swc/_meta.json maps the branch to <folder>
  And the CLI exits 0
```

### REQ-02 — init refuses to overwrite
```gherkin
Scenario: init when workload already exists
  Given the current branch already maps to an existing workload
  When I run `swc workload init`
  Then the CLI prints the existing workload path
  And the existing workload.json is unchanged
  And the CLI exits non-zero
```

### REQ-03 — add appends an item
```gherkin
Scenario: add a top-level item
  Given a workload with N top-level items
  When I run `swc workload add "build a thing"`
  Then a new item with a generated hash ID is appended at top level
  And `swc workload list` shows the item at position N+1
  And the CLI exits 0

Scenario: add a child item
  Given a workload with item 2
  When I run `swc workload add "sub item" --parent 2`
  Then the item is appended as a child of item 2
  And it appears in `list` numbered 2.<last>
```

### REQ-04 — add rejects number-prefix title
```gherkin
Scenario: add with number-prefix title (just inside invalid)
  When I run `swc workload add "1.1 something"`
  Then the CLI exits non-zero
  And the error explains that numbers are assigned automatically
  And no item is added

Scenario: add with leading-digit title that is NOT a prefix pattern (just inside valid)
  When I run `swc workload add "12 monkeys"`
  Then the CLI accepts the title
  And the item appears in `list`
```

### REQ-05 — delete drops item and descendants
```gherkin
Scenario: delete a parent with children
  Given item 2 has two children 2.1 and 2.2
  When I run `swc workload delete 2`
  Then item 2, 2.1, and 2.2 are gone
  And former item 3 is now numbered 2
  And the CLI exits 0
```

### REQ-06 — rename preserves ID, status, position
```gherkin
Scenario: rename keeps stable attributes
  Given item 2.3 exists with hash <H>, status [-], and position 3 under parent 2
  When I run `swc workload rename 2.3 "new title"`
  Then item 2.3 has the new title
  And the hash ID is still <H>
  And the status is still [-]
  And its parent is still 2 and its position is still 3
```

### REQ-07 — rename rejects number-prefix title
```gherkin
Scenario: rename with number-prefix title
  When I run `swc workload rename 2.3 "2.3 new title"`
  Then the CLI exits non-zero
  And the title is unchanged
```

### REQ-08 — move direction form (relative shift among siblings)
```gherkin
Scenario: move up
  Given items 2.1, 2.2, 2.3 exist as siblings
  When I run `swc workload move 2.3 up`
  Then 2.3's previous position is now 2 and 2.2 is now at position 3
  And IDs are unchanged
  And the parent is unchanged

Scenario: move top
  When I run `swc workload move 2.3 top`
  Then the item is now numbered 2.1
  And former 2.1, 2.2 shift down by one
```

### REQ-09 — move `to` form (absolute reposition; may reparent)
```gherkin
Scenario: move reparents and reflows both sides
  Given item 2.3.1 exists and item 3 has two children
  When I run `swc workload move 2.3.1 to 3.2`
  Then the item now lives under parent 3 at position 2
  And the item's hash ID is unchanged
  And former 3.2 is now 3.3
  And numbers under parent 2.3 reflow to fill the gap

Scenario: `to` keyword is required for absolute form
  When I run `swc workload move 2.3 3.2`  # missing `to`
  Then the CLI exits non-zero with a message that the second positional
  must be a direction or the literal `to`
  And the tree is unchanged
```

### REQ-10 — move rejects cycle
```gherkin
Scenario: move into own subtree
  When I run `swc workload move 2 to 2.3.1`
  Then the CLI exits non-zero
  And the error states that this would create a cycle
  And the tree is unchanged
```

### REQ-11 — move rejects missing parent
```gherkin
Scenario: move to non-existent parent
  When I run `swc workload move 2.3 to 9.9`
  Then the CLI exits non-zero
  And the error states the target parent does not exist
  And the tree is unchanged
```

### REQ-12 — status update and parent rollup
```gherkin
Scenario: `start` on a child rolls parent to in-progress
  Given parent 3 has children 3.1 [ ], 3.2 [ ]
  When I run `swc workload start 3.2`
  Then 3.2 is [-]
  And 3 is [-]

Scenario: `complete` on the last child rolls parent to done
  Given parent 3 has children 3.1 [x], 3.2 [-]
  When I run `swc workload complete 3.2`
  Then 3.2 is [x]
  And 3 is [x]
```

### REQ-13 — `start` preserves done; `reset` re-opens
```gherkin
Scenario: `start` on a done item silently preserves done
  Given item 1 is [x]
  When I run `swc workload start 1`
  Then item 1 is still [x]
  And the CLI exits 0
  And the file on disk is unchanged

Scenario: `reset` on a done item re-opens it
  Given item 1 is [x]
  When I run `swc workload reset 1`
  Then item 1 is [ ]
  And the CLI exits 0
```

### REQ-14 — multi-match for find / list filter
```gherkin
Scenario: find with multiple matches
  Given three items contain "cli" in their titles
  When I run `swc workload find cli`
  Then all three items are listed in the output
  And the CLI exits 0
```

### REQ-15 — resolve single by number or ID
```gherkin
Scenario: resolve by number
  When I run `swc workload list 3.2`
  Then the CLI prints the item at number 3.2 and its children
  And the CLI exits 0

Scenario: resolve by hash ID
  Given item 3.2 has hash <H>
  When I run `swc workload list <H>`
  Then the CLI prints the same item
```

### REQ-16 — reference not found
```gherkin
Scenario: reference does not resolve
  When I run `swc workload list 9.9`
  Then the CLI exits non-zero
  And the error states the item was not found
```

### REQ-17 — list with no filter
```gherkin
Scenario: list renders full tree
  When I run `swc workload list`
  Then every item in the workload is printed
  And each line shows a status symbol matching its status
```

### REQ-18 — list with filter
```gherkin
Scenario: list with match filter
  When I run `swc workload list --filter status:in-progress`
  Then only items whose status is [-] are printed

Scenario: list with exclude filter
  When I run `swc workload list --exclude status:done`
  Then items with status [x] are omitted
  And all other items are printed
```

### REQ-19 — `list <ref>` renders item plus descendants
```gherkin
Scenario: list a single item plus its children
  Given item 3 has children 3.1, 3.2
  When I run `swc workload list 3`
  Then the output contains item 3
  And the output contains items 3.1 and 3.2

Scenario: list with ref + filter scopes to the subtree
  Given item 3 has children 3.1 [ ], 3.2 [-], 3.3 [ ]
  When I run `swc workload list 3 --filter status:in-progress`
  Then the output contains item 3
  And the output contains item 3.2
  And the output does NOT contain items 3.1 or 3.3
```

### REQ-20 — find by keyword
```gherkin
Scenario: find single match
  When I run `swc workload find "workload radiator"`
  Then exactly the matching item is printed
```

### REQ-21 — summary
```gherkin
Scenario: summary on a partially complete workload
  Given a workload with 10 items, 4 of which are [x] and 3 of which are [-]
  When I run `swc workload summary`
  Then the output reports total=10, done=4, wip=3, progress=40%
```

### REQ-22 — removed (read item details)

The `read` op was removed during phase 1. Consumers can read `workitems/<id>/requirements.md` directly. See the REQ-22 entry under Requirements above.

### REQ-23 — exists check
```gherkin
Scenario: exists returns true
  Given the current branch has a workload
  When I run `swc workload exists`
  Then the output is a truthy boolean

Scenario: exists returns false
  Given the current branch has no workload
  When I run `swc workload exists`
  Then the output is a falsy boolean
  And the CLI exits 0
```

### REQ-24 — removed (`complete?` check)

The `complete?` op was removed during phase 1. See the REQ-24 entry under Requirements above.

### REQ-25 — op on missing workload
```gherkin
Scenario: list with no workload
  Given the current branch has no workload
  When I run `swc workload list`
  Then the CLI exits non-zero
  And the error recommends `swc workload init`
```

### REQ-26 — swc-workload plugin missing
```gherkin
Scenario: swc workload op without plugin installed
  Given the swc-workload plugin is not installed
  When I run `swc workload list`
  Then the parent swc command prints an install-guidance prompt
  And the prompt references the architecture docs
  And the CLI exits non-zero
```

### REQ-27 — hook blocks direct edit
```gherkin
Scenario: agent attempts to write workload.json directly
  Given the pre-edit hook is registered
  When an Edit/Write tool targets .swc/<folder>/workload.json
  Then the hook denies the write
  And the agent receives a message instructing it to use `swc workload <op>`
```

### REQ-28 — JSON output
```gherkin
Scenario: list --json emits parseable JSON
  When I run `swc workload list --json`
  Then the output is valid JSON
  And parsing the JSON produces a tree of items with id, title, status, children

Scenario: any command without --json emits text
  When I run `swc workload list`
  Then the output is human-readable text (not JSON)
```

### REQ-29 — help
```gherkin
Scenario: top-level help
  When I run `swc workload --help`
  Then the output lists the available subcommands and their one-line descriptions

Scenario: subcommand help
  When I run `swc workload add --help`
  Then the output describes the `add` operation and its flags
```

### REQ-30 — workitem folder layout
```gherkin
Scenario: workitem folder named by hash
  Given an item with hash <H>
  Then any files created under .swc/<workload>/workitems/ for that item live under workitems/<H>/
  And no path component is the item's number
```

### REQ-31 — citation format
```gherkin
Scenario: cross-doc reference format
  When the CLI emits a citation to an item
  Then the citation has the form [<hash>] <title>
```

### REQ-32 — add rejects duplicate sibling title (case-insensitive)
```gherkin
Scenario: exact-match duplicate at the same level
  Given a workload with top-level item "first"
  When I run `swc workload add "first"`
  Then the CLI exits non-zero with a collision message
  And no new item is added

Scenario: case-variant duplicate at the same level
  Given a workload with top-level item "ASDF"
  When I run `swc workload add "asdf"`
  Then the CLI exits non-zero with a collision message
  And no new item is added

Scenario: same title allowed under a different parent
  Given a workload with top-level items "alpha", "beta"
  When I run `swc workload add "alpha" --parent 2`
  Then the item is added successfully
  And both items named "alpha" exist with distinct hash IDs
```

### REQ-33 — rename rejects duplicate sibling title (case-insensitive)
```gherkin
Scenario: rename to a sibling's title
  Given siblings "alpha" and "beta"
  When I run `swc workload rename 2 "ALPHA"`
  Then the CLI exits non-zero with a collision message
  And the item is still titled "beta"

Scenario: rename to a non-sibling's title
  Given top-level items "alpha", "beta" and a child "gamma" under "alpha"
  When I run `swc workload rename 2 "gamma"`
  Then the rename succeeds (different parents, no collision)

Scenario: self-rename is allowed (case-variant of own title)
  Given an item titled "alpha"
  When I run `swc workload rename 1 "ALPHA"`
  Then the rename succeeds and the title becomes "ALPHA"
```

## Validation Rules

| Field | Type | Required | Rules |
|---|---|---|---|
| Title (add / rename) | string | yes | non-empty; must NOT start with a number-prefix pattern (digits + optional dotted digits + whitespace); must NOT match an existing sibling's title (full-string, case-insensitive); `rename` excludes the item being renamed from its own collision check |
| Status | enum | yes | one of `not-started`, `in-progress`, `done` — selected via the `reset` / `start` / `complete` subcommands rather than a single `status <value>` op |
| Reorder direction | enum | yes | one of `up`, `down`, `top`, `bottom` |
| Item reference | string | yes | number (e.g. `3.2`) or hash ID; resolves against current tree |
| Move target | string | yes | number or top-level number; parent path must exist; cycle rejected |

### Business rules

- Numbers are display-only and computed from tree position. They are not stored.
- Hash IDs are stable across renumber, reorder, reparent.
- Status updates always re-evaluate the parent rollup.
- `done` is sticky — direct downgrade is silently ignored.
- Title validation applies on both `add` and `rename`.
