---
name: WI-3.2 solution design
description: Design decisions for implementing the swc workload CLI.
type: project
---

# Solution Design — 3.2: cli tool for workload

## Approach

Build a single Python 3 CLI (`swc workload <op>`) inside the existing `swc` plugin. The CLI owns every read and write against the workload tree, persisted as `workload.json`. Skills shell out to the CLI rather than parsing or editing the file directly. A pre-edit hook blocks direct writes to `workload.json` and redirects the agent to the CLI.

Two phases inside this work item:
1. **Build + test the CLI** end-to-end against specs.md.
2. **Migrate existing skills** to call the CLI. Sequenced after phase 1 — user signals when to start phase 2.

Plugin split into a separate `swc-workload` plugin is out of scope here — that's work item 3.3. For 3.2 everything lives in the main `swc` plugin.

## Test approach

Full TDD — write the test for each scenario in `specs.md` before implementing, watch it fail, implement until it passes, update docs, move on. Tests use pytest. Fixtures hold sample workloads.

## Technical decisions

- **Language / runtime:** Python 3. Already in use by `workload.py` / `progress.py`; no new runtime. Cross-platform via `pathlib`, `getpass.getuser()`, explicit UTF-8 encoding on file I/O. **Do not** use `$USER` — it is Unix-only.
- **Data model:** `workload.json` stores a tree of items: `{id, title, status, children}`. **No numbers** — numbers are computed at render time from depth-first position. **No descriptions** — title is the only human-facing label; richer context lives in `.swc/<workload>/workitems/<id>/requirements.md`.
- **Item lookup:** by number or hash ID only. Keyword is used for `find` and `list --filter`, never as an item reference. If a reference does not resolve to exactly one item, exit non-zero with a not-found message.
- **Hash ID:** SHA-256 of `getpass.getuser() + iso8601(timestamp) + branch + title`, truncated to 7 hex chars. Collisions on 7 chars within a single workload are rejected by re-hashing with an incrementing suffix.
- **Status semantics:**
  - Each item has its own status: `not-started` / `in-progress` / `done`.
  - When a child is updated, the parent is re-derived using the standard rollup (all-done → done; any in-progress or any done but not all → in-progress; all not-started → not-started).
  - When a parent is updated directly, accept the change but emit a warning if children are not all done (e.g. `warning: parent marked done while 2 of 3 children are not done`).
  - `done` is sticky on the direct-update path — silently preserve `done`, no error, exit 0.
- **Output format:**
  - Default: terminal-friendly tree, current `workload.py` style.
  - Composite reference per item: `<status-symbol> N.n(<hash>) <title>` — e.g. `▣ 3.2(abc123d) cli tool for workload`.
  - `--json` flag emits structured output (`{id, number, title, status, children}` recursively).
- **Filter syntax:**
  - `--filter key:val` — single value.
  - `--filter key:val1,val2` — OR within key.
  - Repeating `--filter` — AND across keys.
  - `--filter-out` — negation; same value semantics.
  - Supported keys for v1: `status`. Other keys deferred.
- **Branch / file resolution:** keep using `.swc/_meta.json` for branch→folder mapping. CLI continues this convention.
- **Pre-edit hook:** PreToolUse hook that intercepts Edit/Write tool calls targeting `.swc/**/workload.json`, denies the action, and returns a message instructing the agent to invoke `swc workload <op>`. Hook lives in plugin-level config so it ships with the plugin.
- **CLI entry point:** invoked as `python3 <plugin>/cli/swc-workload <op>` initially. Whether/how to wrap in a shell stub on PATH is parked.

## Deferred

- **Plugin split (`swc` parent + `swc-workload` child) and install-guidance prompt** — entirely 3.3's scope.
- **PATH wrapper / shell stub** for `swc workload` — punt until plugin split.
- **Migration of existing markdown workloads** — out of scope per requirements. User handles manually.
- **Filter keys beyond `status`** — add as concrete needs arise.

## Notes

- Skills currently touching `workload.md` directly (must be migrated in phase 2): `workload`, `workload-update`, `workload_item-start`, `ship`, `context-init`, `context-lookup`, `context--workload`, `workflowPlan_context`, `workflowPlan_delivery`, `workflowPlan_breakdown`, `workflowPlan_finalise`, `workflowDeliver`, `workflowDeliver_implement`, `workflowDeliver_refine`, `workflowImplement_orient`.
- Existing markdown rendering logic in `workload.py` is the baseline for terminal output formatting — port the visual style, then add the `(<hash>)` token.
- Tests should cover the rollup logic and downgrade guard explicitly — these are the highest-risk behaviours.
- Keep CLI surface small and consistent. Every op returns 0 on success, non-zero on failure, and emits a clear single-line error to stderr when it fails.
