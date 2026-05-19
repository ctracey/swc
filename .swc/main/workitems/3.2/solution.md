---
name: WI-3.2 solution design
description: Design decisions for implementing the swc workload CLI.
type: project
---

# Solution Design — 3.2: cli tool for workload

## Approach

Build **two thin Python 3 CLIs** inside the existing `swc` plugin, sharing a clean split of concerns:

- **`cli/swc_workload`** — pure workload-tree manager. Takes `--workload <path>` on every op. Knows nothing about branches, git, or `.swc/_meta.json`. Given a path to a `workload.json`, it manipulates that tree. Pure function of "given this file, do X." Reusable by future backends (MCP wrapper from 3.4; alternative storage backends).
- **`cli/swc`** — context resolver and forwarder. User-facing entry point. Resolves the current branch's workload path (via `git branch --show-current` + `.swc/_meta.json`), writes the branch→folder mapping during `init`, then invokes `swc_workload --workload <resolved-path> <op>` and passes through stdout / stderr / exit code. Skills call `swc workload <op>` — not `swc_workload` directly.

This split keeps the context-resolution logic (already worked out in pass 1) in one place that any future backend can share, and makes `swc_workload` trivially testable (no git, no env vars, no `_meta.json` — just pass a path).

Three phases inside this work item, each gated on user signal before the next starts:

1. **Build + test both CLIs** end-to-end against specs.md. Scenario-driven TDD against `swc workload <op>` (the user-facing surface); a smaller set of direct tests against `swc_workload --workload <path>` for tree-manipulation edge cases.
2. **Migrate existing skills** to invoke `swc workload <op>` rather than reading/editing workload files directly.
3. **Pre-edit hook on `workload.json`** — added once skills are on the CLI so the hook does not block in-flight migration work.

What stays in this work item versus what defers to 3.3:

| Concern | 3.2 | 3.3 |
|---|---|---|
| `swc_workload` (path-driven workload manager) | ✓ | |
| `swc` thin forwarder + path resolution + `_meta.json` writes | ✓ | |
| Both CLIs live in `cli/` of the main `swc` plugin | ✓ | |
| Plugin split — extract `swc-workload` into its own marketplace plugin | | ✓ |
| Install-guidance prompt when `swc-workload` plugin missing (REQ-26) | | ✓ |
| PATH stub so `swc workload <op>` works without `python3 cli/swc <op>` | | ✓ |

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
  - **Childless work items:** when `move` empties a parent's children, the parent's status is preserved (not re-derived to `not-started`). A childless item is still a valid item in its own right.
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
- **Branch / file resolution (owned by `swc`):** `swc` reads `git branch --show-current` and looks up `.swc/_meta.json` to resolve a `workload.json` path. `swc init` writes the branch→folder mapping. `swc_workload` never touches `_meta.json` or git.
- **CLI entry points:**
  - User-facing: `python3 <plugin>/cli/swc workload <op>` — what skills and humans use. Resolves path, forwards to `swc_workload`.
  - Backend: `python3 <plugin>/cli/swc_workload --workload <path> <op>` — direct invocation for testing the tree manipulation in isolation.
  - The PATH stub that exposes `swc workload <op>` as a bare command (no `python3 cli/` prefix) is 3.3's scope.
- **Test layout:** `tests/` at plugin root, alongside `cli/`. Pytest. Two tiers:
  - `tests/cli/test_swc_*.py` — scenario tests against `cli/swc workload <op>`, covering the user-facing spec scenarios end-to-end (path resolution + tree manipulation).
  - `tests/cli/test_swc_workload_*.py` — direct tests against `cli/swc_workload --workload <path>`, covering tree-manipulation edge cases without going through resolution.
  - Fixtures under `tests/fixtures/` hold sample workloads.
- **`SWC_WORKLOAD_*` env-var test isolation goes away.** With `swc_workload` taking `--workload <path>` explicitly, tests just generate a temp path. The git-resolution hack disappears entirely. The `swc` layer can keep a small env-var fallback if useful for testing path resolution itself (e.g. `SWC_REPO_ROOT`), but it's not required.
- **REQ-26 (plugin-missing prompt):** non-tested in 3.2 — `swc-workload` plugin doesn't exist as a separate package yet. Kept in `specs.md` as a handoff to 3.3, where it'll be implemented and tested alongside the plugin split.
- **Pre-edit hook (phase 3):** PreToolUse hook intercepting Edit/Write tool calls targeting `.swc/**/workload.json`, denying the action, and returning a message instructing the agent to invoke `swc workload <op>`. Hook lives in plugin-level config so it ships with the plugin. Implemented after phase 2 lands.
- **Top-level `swc exists` is the canonical branch-aware presence check** (Pass 9). `swc workload exists` and `swc_workload exists` are pure file-presence probes (lenient — never error, always emit a boolean). The branch-aware integrity check — verify mapping in `_meta.json` AND folder exists AND workload.json exists — lives at the top level as `swc exists` so callers asking the question "is this branch's workload set up?" hit a single canonical command. `swc exists` always exits 0 and surfaces stderr warnings (with a `swc workload init` hint) for recoverable states (mapping ok but folder/workload.json gone). This split keeps each layer's contract clean: `swc_workload` answers "does this file exist?", `swc workload` answers the same question via the resolved-folder forward, and `swc` answers "does this branch have a fully set-up workload?". The split also fixes a Pass 8 help-listing gap — `exists` is now a real op on `swc_workload`, so it shows up under `swc workload --help` alongside the other 13 ops.

## Deferred

- **Plugin split (extract `swc-workload` into its own marketplace plugin)** — entirely 3.3's scope. When this lands, the scenario tests against `swc workload <op>` stay where they are; the `swc_workload`-direct tests move with `swc_workload` to its new repo. The `swc` plugin gains a small set of integration tests proving forwarding behaviour.
- **Install-guidance prompt when `swc-workload` plugin missing (REQ-26)** — 3.3 scope.
- **PATH wrapper / shell stub** for `swc workload` — 3.3 scope.
- **Migration of existing markdown workloads** — out of scope per requirements. User handles manually.
- **Filter keys beyond `status`** — add as concrete needs arise.

## Notes

- Skills currently touching `workload.md` directly (must be migrated in phase 2): `workload`, `workload-update`, `workload_item-start`, `ship`, `context-init`, `context-lookup`, `context--workload`, `workflowPlan_context`, `workflowPlan_delivery`, `workflowPlan_breakdown`, `workflowPlan_finalise`, `workflowDeliver`, `workflowDeliver_implement`, `workflowDeliver_refine`, `workflowImplement_orient`.
- Existing markdown rendering logic in `workload.py` is the baseline for terminal output formatting — port the visual style, then add the `(<hash>)` token.
- Tests should cover the rollup logic and downgrade guard explicitly — these are the highest-risk behaviours.
- Keep CLI surface small and consistent. Every op returns 0 on success, non-zero on failure, and emits a clear single-line error to stderr when it fails.
