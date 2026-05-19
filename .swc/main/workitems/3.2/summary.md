# Summary — 3.2: cli tool for workload

## Pass 1 — 2026-05-18

### Changes

- Added `cli/swc_workload.py` — single-file stdlib-only Python 3 CLI. Owns every read and write against `workload.json`. [superseded by Pass 6 — file renamed to `cli/swc_workload` and split: a new `cli/swc` owns context resolution / `_meta.json` writes / branch awareness; `swc_workload` is now a pure path-driven tree manager]
- Implemented 14 subcommands: `init`, `add`, `remove`, `rename`, `reorder`, `move`, `status`, `list`, `show`, `find`, `summary`, `read`, `exists`, `complete?`. `--json` and `--branch` accepted at both root and subparser scope via shared `_add_common` helper.
- Hash ID scheme: SHA-256 of `getpass.getuser() + ISO timestamp + branch + title`, truncated to 7 hex chars; collision-resolved via `|<n>` suffix and rehash. Uses `getpass.getuser()` (not `$USER`) for Windows compatibility.
- `workload.json` shape: `{"items": [...], "complete": false}` with each item `{"id", "title", "status", "children"}`. Numbers computed at render time, never stored. Descriptions live in `workitems/<hash>/requirements.md` per REQ-30.
- Status enum stored as full strings (`not-started` / `in-progress` / `done`); input aliases (`wip`, `todo`, etc.) normalised via `normalise_status`. Display symbols looked up at render time.
- Rollup runs on every save. Direct parent edits keep the user's value with a stderr warning when children disagree; ancestors above re-derive. Leaf edits flow through normal rollup.
- `done` is sticky on the direct update path — `cmd_status` returns early before writing if a done item would be downgraded (satisfies REQ-13's "file on disk unchanged" assertion).
- Move-cycle check compares target parent's hash ID against the moving item's subtree. Same-parent reorder via `move` handled by adjusting `insert_idx` when popping from before the destination. [superseded by Pass 3 — adjustment removed]
- Number-prefix validation regex `^\d+(\.\d+)+\s+` — rejects `"1.1 something"` but accepts `"12 monkeys"` per REQ-04 boundary scenarios.
- Test isolation via two env vars: `SWC_WORKLOAD_ROOT` (overrides repo root, replaces `git rev-parse`) and `SWC_WORKLOAD_BRANCH` (overrides git branch). Production code still falls back to git when env vars are absent. [superseded by Pass 6 — env-var hack removed; `swc_workload` is now path-driven, `swc` keeps a smaller `SWC_REPO_ROOT`/`SWC_BRANCH` pair for tier-2 fixture isolation only]
- Tests live at `tests/cli/` with a single `conftest.py`. No shared fixture file — each test builds the workload it wants via CLI calls, doubling as integration coverage. Files: `test_lifecycle.py`, `test_authoring.py`, `test_status.py`, `test_lookup_read.py`, `test_missing_help_io.py`.

### Testing

- Scenario-driven TDD against `specs.md`. One failing test per spec scenario, implement until green, move on.
- Pytest invoked via subprocess for each CLI op — true integration coverage of the argparse surface, not unit-level imports.
- Coverage spans REQ-01 through REQ-25 and REQ-28 through REQ-31 (all phase-1-eligible requirements).
- Boundary cases explicitly tested: title with dotted prefix vs. leading-digit-only, downgrade-of-done silently preserved, move-cycle rejection, missing-parent rejection, multi-match find, JSON vs. text output shape.

### Test results

- `python3 -m pytest tests/ -q` — **44 passed in 6.74s, 0 failed**.
- No regressions observed against pre-existing scripts (`workload.py`, `progress.py`) — they were not modified in this pass.

### Pipeline

- `pipeline.md` exists but is still the unfilled template (placeholder `<command to run>`, etc.) — no concrete build command defined yet.
- Pipeline verification performed via the project pytest suite as the de facto build signal: `python3 -m pytest tests/ -q` → 44/44 passing, exit 0.
- Dev environment not applicable for a CLI tool (no long-running process to start/stop).
- Recommend filling in `pipeline.md` with `python3 -m pytest tests/ -q` as the build command before the next pass.

### Build confidence

High for phase 1 scope. Every testable spec requirement in scope has a green scenario; the CLI behaves identically whether invoked manually or by a subprocess test. Confidence is bounded by phase scope only — phases 2 (skill migration) and 3 (pre-edit hook) have not been touched, and REQ-26 (plugin-missing prompt) and REQ-27 (pre-edit hook) remain unmet by design per the brief.

### Scope flags

- **`complete` flag never set by any CLI op.** `complete?` reads `workload.json.complete`, but no current subcommand flips it. The decision in context.md is that a future `workflow-complete` op will own that — flagged here so 3.3 / workflow-completion work picks it up.
- **`move` does not re-roll an orphaned parent.** When `move` removes the last child from a parent, the parent's status is not re-derived against its (now-empty) child set. RESOLVED in pass 2: policy pinned (childless items keep their status) and documented in solution.md "Status semantics"; behaviour locked in by a scenario test.
- **`reorder` / `move` edge cases not exhaustively tested.** Coverage is sufficient for the named spec scenarios but parked combinations (e.g. `reorder top` on an only child, `move` to identical position) are untested.
- **REQ-26 (plugin-missing prompt)** explicitly deferred to work item 3.3 per the user brief — flagged so it isn't lost.
- **REQ-27 (pre-edit hook on `workload.json`)** explicitly deferred to phase 3 of this work item per `solution.md` — flagged so the phase boundary is visible.
- **Skill migration (phase 2)** untouched — all existing skills still read/write workload files directly. This is the next phase of 3.2 and is gated on user signal per `solution.md`.

### Approach needs revisiting

No.

---

## Pass 2 — 2026-05-18

### Changes

- **F-01 (warn) — `move` keyword validation.** `cmd_move` in `cli/swc_workload.py` now checks the optional positional `to_kw`: if it is set to anything other than the literal `"to"`, raises `CLIError("unexpected token <x> between ref and target; expected 'to' or omit it")`. Eliminates the silent-swallow path where `move 2.3 too 3.2` would parse as `move 2.3 to 3.2`.
- **F-02 (warn) — orphaned-parent policy pinned (no code change).** Per the user's policy decision, the existing behaviour (a parent emptied by `move` retains its prior status) is correct: a childless work item is still meaningful and should not auto-revert to `not-started`. No change to `rollup`. Policy documented in `solution.md` under "Status semantics" as a new bullet, and the related scope flag in this summary's Pass 1 section is now marked RESOLVED. Behaviour locked in by a scenario test.
- **F-03 (warn) — coverage for two solution.md behaviours.** Added scenario tests that pin previously-uncovered branches: (a) `cmd_status` parent→done while children disagree writes the warning to stderr, returns 0, and changes the file; (b) `move <item> to <sibling-position>` within the same parent reorders correctly and preserves IDs (this exercises the `insert_idx -= 1` adjustment that fires only on the same-parent path). [superseded by Pass 3 — adjustment removed]
- **F-04 (info) — `cmd_init` aligned to `CLIError` pattern.** Replaced the inline `sys.stderr.write(...) + return 1` with `raise CLIError(f"workload already exists at {workload}")`. Now matches the convention used by every other command. Pre-existing `test_req02_init_refuses_to_overwrite_existing` continues to pass without change.
- **F-07 (info) — schema validation on `workload.json` reads.** Added `_validate_shape(data)` helper called from `load_workload`. Asserts top-level is a dict with `items` (list) and `complete` (bool); recurses into each item asserting `id`/`title`/`status` are strings and `children` is a list. JSON decode errors are also wrapped into `CLIError`. Surfaces a friendly `workload.json invalid: <message> at <jsonpath>` error rather than a raw `KeyError`/`AttributeError` on a hand-edited file.
- Documentation updates: `.swc/main/workitems/3.2/solution.md` (childless-item policy bullet), `.swc/main/workitems/3.2/summary.md` Pass 1 (F-02 scope flag marked RESOLVED), `.swc/main/workitems/3.2/context.md` (new Pass 2 section).

### Testing

- Followed Full TDD per `solution.md`: for each behavioural change (F-01, F-07) wrote the failing test first, confirmed the failure, then implemented until green. F-03 tests were added against existing behaviour to pin it (they passed on first run — that is the point). F-04 was a refactor verified by the pre-existing F-04-adjacent scenario test. F-02 was a behaviour-pinning test only (no code change required).
- 8 new scenario tests added:
  - `tests/cli/test_authoring.py`: `test_move_rejects_unexpected_keyword_between_ref_and_target`, `test_move_still_accepts_literal_to_keyword`, `test_move_still_accepts_omitted_to_keyword`, `test_move_leaves_orphaned_parent_status_untouched`
  - `tests/cli/test_status.py`: `test_parent_marked_done_with_undone_children_warns_on_stderr`, `test_move_within_same_parent_reorders_and_preserves_ids`
  - `tests/cli/test_missing_help_io.py`: `test_load_workload_rejects_malformed_shape_with_clear_error`, `test_load_workload_rejects_top_level_non_dict`
- All run via subprocess against the CLI entry point, matching the existing test style.

### Test results

- `python3 -m pytest tests/ -q` — **52 passed in 8.20s, 0 failed**.
- 44 pre-existing tests still pass (no regressions); 8 new tests pass.

### Pipeline

- `pipeline.md` is still the unfilled template — no concrete build command defined (same state as Pass 1).
- Pipeline verification performed via the project pytest suite as the de facto build signal: `python3 -m pytest tests/ -q` → 52/52 passing, exit 0.
- Dev environment not applicable (CLI tool).

### Build confidence

High. All five required findings are resolved or explicitly pinned, the pre-existing 44 tests still pass, and the 8 new scenario tests lock in both the new validations and the previously-untested branches.

### Scope flags

- **F-05 (info, hash-vs-digit ambiguity)** and **F-06 (info, file size at 938 lines)** deferred to `tech-debt.md` per the brief — not addressed in this pass.
- **`complete` flag never set by any CLI op.** Still unchanged from Pass 1; future `workflow-complete` op will own that.
- **Skill migration (phase 2)** and **pre-edit hook (phase 3)** still untouched — out of scope for this pass per the brief.

### Approach needs revisiting

No.

---

## Pass 3 — 2026-05-18

### Changes

- **F-09 (info) — JSON decode error: include parser line/column and chain original exception.** Changed `load_workload` (`cli/swc_workload.py:189-194`) from `f"workload.json invalid: {e.msg} at <root>"` to `f"workload.json invalid: {e.msg} at line {e.lineno}, column {e.colno}"` and added `from e` to chain the underlying `json.JSONDecodeError`. The `<root>` token was misleading for syntax errors — it's the schema-validation phrase.
- **F-08 (info) — same-parent move test surfaced a real bug.** Wrote the requested source-before-target same-parent test (`move 2.1 to 2.3` against `[a, b, c]` → `[b, c, a]`). The test failed: empirical result was `[b, a, c]`, the off-by-one shape the brief warned against. Traced to the `if target_parent_list is source_parent and source_idx < insert_idx: insert_idx -= 1` block in `cmd_move`, which was applying slot-swap semantics for source-before-target while the rest of the CLI uses final-position semantics. **Removed the adjustment** in `cli/swc_workload.py:638-643` (replaced the conditional with an explanatory comment). The existing same-parent test (`move 2.3 to 2.1` → `[c, a, b]`) still passes because the adjustment never fired for source-after-target anyway.
- **Tests added:** `tests/cli/test_status.py::test_move_within_same_parent_source_before_target_exercises_insert_idx_adjustment` and `tests/cli/test_missing_help_io.py::test_load_workload_json_decode_error_reports_line_and_column`.
- Documentation updates: `.swc/main/workitems/3.2/context.md` (new Pass 3 section with diagnosis and decision); this Pass 3 section in `summary.md`.

### Testing

- Followed Full TDD: wrote both tests first, confirmed failures (F-08 → `[b, a, c]` mismatch; F-09 → message lacked line/column), implemented the fixes, re-ran until green.
- F-08 in particular revealed that the brief's own diagnosis was inverted (it claimed `[b, c, a]` came WITH the adjustment when empirically it comes WITHOUT). The minimal change to make the test pass per the brief's specification was to remove the buggy adjustment block.
- Verified by re-running the existing source-after-target test (`test_move_within_same_parent_reorders_and_preserves_ids` — `move 2.3 to 2.1` → `[c, a, b]`) — still green.

### Test results

- `python3 -m pytest tests/ -q` — **54 passed in 8.70s, 0 failed**.
- 52 pre-existing tests still pass (no regressions); 2 new tests pass.

### Pipeline

- `pipeline.md` is still the unfilled template — no concrete build command defined (same state as Pass 1 and Pass 2).
- Pipeline verification performed via the project pytest suite as the de facto build signal: `python3 -m pytest tests/ -q` → 54/54 passing, exit 0.
- Dev environment not applicable (CLI tool).

### Build confidence

High. Both info-level findings are resolved with passing scenario tests, and the F-08 work also fixed a latent same-parent-move bug that the prior tests didn't exercise. The pre-existing 52 tests still pass and the 2 new tests lock in the new behaviour.

### Scope flags

- **Latent bug fixed beyond the literal brief.** F-08 was scoped as "add a test", but the test failed against existing code, revealing the `insert_idx -= 1` adjustment was buggy. The fix (removing the adjustment) was the only way to make the brief's required `[b, c, a]` assertion pass without breaking the existing same-parent test. Surfacing this so reviewers know the resolution touched implementation, not just tests.
- **`complete` flag never set by any CLI op.** Still unchanged from Pass 1/2; future `workflow-complete` op will own that.
- **F-05 (info, hash-vs-digit ambiguity)** and **F-06 (info, file size at 938 lines)** remain deferred to `tech-debt.md` per the original brief — not in scope for this pass.
- **Skill migration (phase 2)** and **pre-edit hook (phase 3)** still untouched — out of scope for this pass per the brief.

### Approach needs revisiting

No.

---

## Pass 4 — 2026-05-18

### Changes

- **F-10 (warn) — same-parent move tests rewritten to reflect post-Pass-3 truth.** Both same-parent move tests in `tests/cli/test_status.py` had names, docstrings, inline comments, and assertion messages describing the removed `insert_idx -= 1` adjustment as if it still existed.
  - Renamed `test_move_within_same_parent_reorders_and_preserves_ids` → `test_move_same_parent_source_after_target_lands_at_requested_position`. Docstring now describes final-position semantics and explicitly notes that the source-after-target direction never fired the now-removed adjustment.
  - Renamed `test_move_within_same_parent_source_before_target_exercises_insert_idx_adjustment` → `test_move_same_parent_source_before_target_lands_at_requested_position`. Docstring, inline comment, and assertion message rewritten to describe final-position semantics. The assertion message now contains an explicit regression-guard instruction telling a future contributor to revert any re-introduction of the `insert_idx -= 1` block if they see `[b, a, c]`.
- **F-11 (info) — audit history annotated, not rewritten.** Appended `[superseded by Pass 3 — adjustment removed]` markers to four lines that still described the removed adjustment as current design:
  - `.swc/main/workitems/3.2/context.md:17` (Pass 1 decision)
  - `.swc/main/workitems/3.2/context.md:34` (Pass 2 F-03 (b))
  - `.swc/main/workitems/3.2/summary.md:14` (Pass 1 Changes)
  - `.swc/main/workitems/3.2/summary.md:63` (Pass 2 F-03 (b))
  Per the brief, original wording was preserved as audit history.

No production code changes in this pass — `cli/swc_workload.py` was not touched. No new tests added; the test changes were rename + narrative-only.

### Testing

- Verified the suite still passes after the test renames and narrative rewrites. No new scenarios needed — the brief explicitly scoped this pass as documentation/test-narrative cleanup.

### Test results

- `python3 -m pytest tests/ -q` — **54 passed in 8.49s, 0 failed**.
- All 54 pre-existing tests still pass after the renames.

### Pipeline

- `pipeline.md` is still the unfilled template — no concrete build command defined (same state as Pass 1, 2, and 3).
- Pipeline verification performed via the project pytest suite as the de facto build signal: `python3 -m pytest tests/ -q` → 54/54 passing, exit 0.
- Dev environment not applicable (CLI tool).

### Build confidence

High. Both findings are narrative/documentation cleanups with no behavioural change. The 54 tests still pass; the test renames now describe the actual behaviour, and a future contributor reading the docstring/assertion message will be steered away from re-introducing the removed adjustment.

### Scope flags

- **`pipeline.md` still unfilled** — same as prior passes. Recommend filling in `python3 -m pytest tests/ -q` as the build command before the next pass.
- **`complete` flag never set by any CLI op.** Still unchanged from Pass 1/2/3; future `workflow-complete` op will own that.
- **Skill migration (phase 2)** and **pre-edit hook (phase 3)** still untouched — out of scope for this pass per the brief.

### Approach needs revisiting

No.

---

## Pass 5 — 2026-05-18

### Changes

- **CLI `--help` polish to argparse convention.** Review-stage feedback: existing help met REQ-29's literal spec but was below common argparse convention. Bare positionals had no descriptions, subcommands had no `description=`, the `move` `to` keyword was suppressed, and enum/filter-key values were not documented in help text. Applied a focused polish pass in `cli/swc_workload.py` `build_parser`:
  - Added `help="..."` to every positional argument across all subcommands: `ref`, `target`, `title`, `keyword`, `status`, `direction`. Common `ref` description factored into a local `ref_help` string.
  - Added `description="..."` to every subcommand on `add_parser(...)` — the longer top-of-help text shown when running `<subcommand> --help`. Captures the key invariants (e.g. cycle rejection, parent rollup, sticky-done).
  - Exposed the `move` `to_kw` slot: switched from `argparse.SUPPRESS` to a real help string and gave it `metavar="[to]"` so it shows in the usage line as optional.
  - Documented enum values in help text: `status` (not-started, in-progress, done); `--filter` supported keys (v1: status only).
  - Added `help` to bare `--show-ids` / `--no-ids` on the `show` subcommand (previously described only on `list`).
- No behaviour change. No new tests added (text polish only).
- Skipped the full workflow restart for this small mechanical pass per user preference — made the edits directly in the worktree.

### Testing

- Re-ran the existing test suite to confirm no regressions from the argparse changes.

### Test results

- `python3 -m pytest tests/ -q` — **54 passed in 8.68s, 0 failed**.

### Pipeline

- `pipeline.md` still the unfilled template.
- Pipeline verification via pytest as before: 54/54 passing.

### Build confidence

High. Pure text polish; no behaviour surface touched.

### Scope flags

- Examples sections in help, concept overviews (numbers vs hash IDs, status symbols, what `complete?` means), and a user-facing README remain out of scope — to be tackled separately, likely alongside phase 2.
- Same prior flags carry forward: `complete` flag, skill migration (phase 2), pre-edit hook (phase 3), `pipeline.md` template.

### Approach needs revisiting

No.

---

## Pass 6 — 2026-05-18

### Changes

- **Architectural split.** The single `cli/swc_workload.py` is gone. Replaced with two bare executables in `cli/`:
  - **`cli/swc_workload`** — pure tree manager. Path-driven via `--workload <path>` on every subcommand. No git, no `.swc/_meta.json`, no env-var fallbacks. `init` becomes a simple file-creation op against the supplied path. Dropped the `exists` subcommand (moved to `swc`). Dropped `--branch` everywhere (no longer needed). `make_id` payload no longer includes `branch` — the workload path is the implicit anchor at this layer.
  - **`cli/swc`** — new user-facing entry point. Reads `git branch --show-current`, looks up `.swc/_meta.json`, resolves the branch's workload path, and forwards `swc workload <op>` calls to `swc_workload --workload <path> <op>` (stdout / stderr / exit code passed through). Owns the `init` flow (folder create + `_meta.json` registration + forward to `swc_workload init`) and the `exists` flow (branch-aware presence check, never forwards). Honours `SWC_REPO_ROOT` / `SWC_BRANCH` env vars for tier-2 test isolation; falls back to git → cwd otherwise.
- **Help output via delegation.** `swc workload --help` prints a short preamble then forwards `--help` to `swc_workload --help` for the canonical op list. `swc workload <op> --help` delegates straight to `swc_workload <op> --help` — argparse short-circuits `--help` before the `--workload` requirement, so no path is needed. Avoids re-stitching every subcommand's help text in the wrapper.
- **Test restructuring into two tiers.** All previous 54 tests deleted; replaced with 68 tests across two tiers — every prior in-scope REQ scenario has an equivalent in the new layout.
  - **Tier 1 — `tests/cli/test_swc_workload_*.py`** (49 tests). Direct invocation of `cli/swc_workload` against `tmp_path / "workload.json"` per test. Covers tree-manipulation edge cases: hash uniqueness, move keyword validation, cycle rejection, missing-parent rejection, same-parent move semantics (both source-before-target and source-after-target), rollup, downgrade-guard, schema validation, JSON output, read/find/show/summary, parent-marked-done warning, `init`/`complete?` at the bottom tier, missing-workload error message.
  - **Tier 2 — `tests/cli/test_swc_*.py`** (19 tests). Scenario tests against `cli/swc workload <op>`, using a tmp git repo fixture (`swc_repo`). Covers user-facing flows end-to-end: REQ-01/02 (`init` writes both `workload.json` and `_meta.json`; refuses overwrite), REQ-22/30/31 (read + folder layout + citation form via the wrapper), REQ-23 (`exists` boolean — true/false/--json), REQ-25 (missing-workload error message recommends `swc workload init`), REQ-29 (top-level + subcommand help via the wrapper), basic forwarding round-trip.
- **Fixture file rewritten.** `tests/cli/conftest.py` exposes:
  - `swcw` / `swcw_ready` — tier-1 helpers returning `(run_fn, workload_path)` against `tmp_path`.
  - `swc` / `swc_initialised` — tier-2 helpers wrapping a tmp git repo on `feature/test-cli`, with the CLI invoked via `SWC_REPO_ROOT` + `SWC_BRANCH` so the test is independent of the surrounding process state.
- **Docs.** Pass 1 entries in `context.md` and `summary.md` that described the now-removed `cli/swc_workload.py` and `SWC_WORKLOAD_*` env-var hack are annotated inline with `[superseded by Pass 6 — env-var hack removed]` markers. Pass 6 section added to both files.
- **REQ-23 / REQ-25 ownership moved to the wrapper layer** per the brief. REQ-25's "no workload for this branch" message is generated by `swc` (since `swc_workload` no longer knows what a branch is). The tier-1 equivalent (`swc_workload list` against a missing `--workload` path) still exits non-zero with an `init`-recommending message — so the regression coverage exists at both layers.

### Testing

- Full TDD per `solution.md`. For each tier the tests were written from the new fixtures' shape; the implementation followed. No scenarios required more than one fix cycle.
- The two CLIs were manually exercised end-to-end during development (`swc_workload init --workload /tmp/x.json`, `swc workload --help`, etc.) to verify the help preamble and the subprocess forwarding round-trip.

### Test results

- `python3 -m pytest tests/ -q` → **68 passed in 10.51s, 0 failed**.
- Full plugin suite `python3 -m pytest -q` → **86 passed in 10.62s, 0 failed** (68 CLI + 18 workflow-progress; no regressions).

### Pipeline

- `pipeline.md` still unfilled. Pipeline verification via pytest as before.

### Build confidence

High. The split is clean: `swc_workload` is reusable by any future backend (3.4 MCP wrapper, alt storage) without dragging git/`_meta.json` along, and `swc` is small enough that the forwarder logic is obvious by inspection. Every prior in-scope REQ scenario has a replacement test; REQ-01/02 now exercise the full `init` flow end-to-end including the `_meta.json` write.

### Scope flags

- **Hash payload no longer includes branch.** `swc_workload.make_id` was `user|ts|branch|title|suffix` in pass 1; with the path-driven split it's `user|ts|title|suffix`. Per-workload hash uniqueness is still guaranteed by the in-workload existing-IDs check + retry-with-suffix; cross-workload collisions are theoretically more likely but still ~16M per 7-hex-prefix workload, and no behaviour depends on cross-workload uniqueness today. Flagged so 3.3 / 3.4 know the option exists to thread a `--anchor` flag from `swc` to `swc_workload` if cross-workload distinction ever becomes meaningful.
- **`SWC_REPO_ROOT` / `SWC_BRANCH` env vars in `swc`.** Used only by tier-2 fixtures; not documented for end-users. Kept undocumented intentionally to avoid encouraging skills to override branch context.
- **Skill migration (phase 2)** and **pre-edit hook (phase 3)** still untouched — out of scope per the work-item phasing. Now unblocked: skills can shell out to `python3 cli/swc workload <op>` (or the 3.3 PATH stub) without needing to know about path resolution.
- **REQ-26 (plugin-missing prompt)** still deferred to 3.3 — `swc-workload` is not yet a separate plugin.
- **`complete` flag never set by any CLI op.** Unchanged across all six passes; future `workflow-complete` op will own that.
- **`pipeline.md` still the template.** Recommend `python3 -m pytest tests/ -q` as the build command.

### Approach needs revisiting

No. The split was straightforward and the test reorg was largely a port — the resulting layout is cleaner than the original env-var-based isolation.

---

## Pass 7 — 2026-05-19

### Changes

- **Contract change — `--workload` is now a folder path, not a file.** `cli/swc_workload`'s `workload_path_from_args` validates `--workload <folder>` is an existing directory and resolves `<folder>/workload.json` internally. New validations:
  - Folder does not exist → `CLIError("workload folder does not exist: <folder>")`
  - Path is a file, not a directory → `CLIError("--workload expects a folder, got a file: <folder>")`
  The previous cryptic "workload already exists" path that fired when a folder lacked a workload.json is gone — replaced by these clearer messages.
- **`_add_common` help text updated** in `cli/swc_workload`: `"Path to the workload folder (containing workload.json)."` `cmd_init`'s help and description now describe folder-based file creation.
- **`cli/swc` wrapper aligned** — `handle_init` and `forward` now pass the folder path (not a file path) to `swc_workload`. Renamed the local `workload_path` → `folder`. `handle_workload` uses `resolve_folder(...)` and constructs `<folder>/workload.json` only for the presence check before forwarding.
- **`handle_init` reordered** — `_meta.json` is read BEFORE the inner `init` is forwarded, so corrupt `_meta.json` fails fast (no folder mkdir, no workload.json write). On successful inner init, the already-loaded meta is updated and written.
- **F-01 + F-02 (error / warn) resolved — special-op `--help` intercepted at the wrapper.** Restructured `handle_workload` so the special-op routing (`init` / `exists`) runs BEFORE the generic per-subcommand `--help` forwarder. Added `INIT_HELP` and `EXISTS_HELP` constants in `cli/swc` describing the wrapper's full flow. New `handle_init_with_help` short-circuits `--help` to the constant; `handle_exists` does the same inline. Fixes the broken `swc workload exists --help` (was exiting 2 with argparse `invalid choice`) and the misleading `swc workload init --help` (was showing the inner CLI's pure-file-creation description plus `--workload` flag the user never supplies).
- **F-03 (warn) resolved — inner CLI `prog` name no longer leaks.** Single line: `prog="swc_workload"` → `prog="swc workload"` in `cli/swc_workload:build_parser`. Forwarded help and argparse errors now read `usage: swc workload <op> [...]` matching what the user typed.
- **F-04 (warn) resolved — OSError handled in both CLI mains.** Added `except OSError` after the `CLIError` handler in `cli/swc_workload:main` and `cli/swc:main`. Emits `file system error: <msg>` to stderr and exits 1. Real bugs (`BaseException` / `Exception` not derived from `OSError`) still surface as raw tracebacks in development.
- **F-05 (error, user-upgraded) resolved — corrupt `_meta.json` fails loudly.** `cli/swc:read_meta` now raises `SwcError("_meta.json is corrupt and cannot be parsed: <msg> at line <n>, column <m>")` from a `json.JSONDecodeError` rather than silently returning `{"workloads": {}}`. Eliminates the silent-data-loss path where `init` against a corrupt `_meta.json` would overwrite the file with only the new branch entry, dropping every other mapping.
- **F-07 (info) resolved — `_meta.json` byte-equality test.** Extended `test_req02_init_refuses_to_overwrite_existing` in `tests/cli/test_swc_lifecycle.py` to capture `_meta.json` bytes before the second `init` call and assert byte-equality afterwards. Hardens the `if rc == 0:` gate in `handle_init`.
- **New tests added** (all under `tests/cli/`):
  - `test_swc_workload_io.py`: `test_workload_folder_does_not_exist_errors_clearly`, `test_workload_pointed_at_a_file_errors_clearly`, `test_init_requires_folder_to_exist`, `test_oserror_in_save_workload_surfaces_as_friendly_error` (self-skips on root / chmod-ignoring environments).
  - `test_swc_lifecycle.py`: `test_corrupt_meta_json_errors_on_list_without_overwriting`, `test_corrupt_meta_json_errors_on_init_without_overwriting`, `test_oserror_in_write_meta_surfaces_as_friendly_error` (self-skips on chmod-ignoring environments).
  - `test_swc_help.py`: `test_swc_workload_exists_help_exits_zero_and_describes_op`, `test_swc_workload_exists_short_h_flag`, `test_swc_workload_init_help_describes_wrapper_flow`, `test_swc_workload_add_help_does_not_leak_swc_workload_prog_name`, `test_swc_workload_unknown_op_error_does_not_leak_swc_workload`.
- **Tier-1 fixture migration.** `conftest.py::swcw` now passes `tmp_path` (the folder) as `--workload`; the returned `workload` value remains the workload.json path inside for tests that read/write the file directly. No tier-1 test body changes needed — they all go through the fixture closure.
- **Renamed `test_init_creates_workload_json_at_supplied_path` → `test_init_creates_workload_json_inside_supplied_folder`** in `test_swc_workload_io.py` to match the new contract.

### Testing

- Followed the existing TDD pattern: wrote the contract-violation tests first against the old code (would have failed), then implemented the validations + dispatch reorder + prog rename, then re-ran.
- Manually exercised the help surface end-to-end in a tmp git repo: `swc workload --help`, `swc workload init --help`, `swc workload exists --help`, `swc workload add --help` — confirmed wrapper-aware text, no `swc_workload` leakage, correct exit codes.
- Manually exercised the corrupt-meta error path in a tmp repo to confirm message format and exit code.

### Test results

- `python3 -m pytest tests/ -q` → **80 passed in 11.04s, 0 failed** (68 prior + 12 new).
- Full plugin suite `python3 -m pytest -q` → **98 passed in 11.21s, 0 failed** (80 CLI + 18 workflow-progress; no regressions).

### Pipeline

- `pipeline.md` still the unfilled template (same state as prior passes).
- Pipeline verification via the project pytest suite as the de facto build signal: `python3 -m pytest tests/ -q` → 80/80 passing, exit 0.
- Dev environment not applicable (CLI tool).

### Build confidence

High. The contract change is mechanical and well-covered: new validations have explicit tests, the wrapper's forwarder now passes folder paths uniformly, and the dispatch reorder fixed both the broken `exists --help` and the misleading `init --help`. F-05's safer corrupt-meta behaviour is pinned by two tests covering the two ways the data loss could happen (list path, init path). The OSError handlers are tested where the environment honours read-only chmod, and the tests self-skip cleanly elsewhere so the suite stays green.

### Scope flags

- **F-06 (file size at 945 lines)** — explicitly deferred per the brief; lives in tech-debt.
- **F-08 (orphan folder on init failure)** — explicitly deferred per the brief ("good enough for now").
- **REQ-26 (plugin-missing prompt)** — still handed off to 3.3.
- **REQ-27 (pre-edit hook)** — still phase 3 of this work item.
- **Skill migration** — still phase 2 of this work item.
- **OSError tests self-skip** in environments that don't honour chmod (root, some CI). This is intentional — the tests are genuinely conditional on filesystem permission semantics; running them as root and asserting failure would be unsound.

### Approach needs revisiting

No.

---

## Pass 8 — 2026-05-19

### Changes

- **F-01 (error) fixed** — `cli/swc::handle_init_with_help` now checks `any(a in ("--help", "-h") for a in op_args)` instead of `op_args[0] in (...)`. This closes the regression where `swc workload init --json --help` fell through to the full init flow, called `folder.mkdir(parents=True, exist_ok=True)`, forwarded `--help` to the inner CLI (argparse short-circuited with exit 0), then the wrapper's `if rc == 0:` gate wrote a stale `_meta.json` registration pointing at an empty folder. Docstring updated with an explanatory note so a future change can't silently regress it.
- **F-02 (warn) fixed** — same one-line change in `cli/swc::handle_exists`. `swc workload exists --json --help` now emits `EXISTS_HELP` instead of `{"exists": false}`. Docstring updated identically.
- **F-03 (info) fixed (Option B)** — `INIT_HELP` in `cli/swc` lost the `(path to the created workload)` parenthetical from the `--json` description. Now reads `Emit structured JSON output.` — matches `EXISTS_HELP`'s tone and stops the wrapper-level help from leaking the inner CLI's output shape. Chose Option B over Option A on the brief's recommendation — the user doesn't care that the flag is forwarded.

### Testing

- Full TDD per pass policy. Four scenario tests added to `tests/cli/test_swc_help.py` BEFORE the fix; all four failed against the buggy code, then passed after the fix.
- `test_swc_workload_init_help_after_json_does_not_touch_filesystem` — the headline F-01 test: asserts `swc workload init --json --help` shows `INIT_HELP`, exits 0, and NEITHER `.swc/_meta.json` NOR `.swc/<folder>/` exists afterward. Both filesystem checks are necessary because the original bug created the folder via `mkdir(exist_ok=True)` AND wrote `_meta.json`.
- `test_swc_workload_init_json_then_dash_h_does_not_touch_filesystem` — variant that pins the "anywhere in op_args" contract with `-h` at op_args[1] (after `--json`). Wrote `init -h --json` first; it passed against the buggy code because `-h` was at op_args[0] — rewrote to `init --json -h` to actually exercise the bug.
- `test_swc_workload_exists_help_after_json_prints_help_not_boolean` — F-02 test: asserts help text indicators (`exists`, plus one of `usage:` / `presence` / `branch`) and confirms no JSON boolean payload (`"exists"` quoted string would be in the JSON output but isn't).
- `test_swc_workload_init_help_describes_json_consistently` — F-03 test: asserts `--json` is still documented but the previous parenthetical is gone.
- Manual F-01 reproduction: created a tmp git repo on `feature/test`, ran `swc workload init --json --help` against it, confirmed `INIT_HELP` is shown and `ls .swc/` errors with "No such file or directory" — folder absent, meta absent. Exact regression scenario from the finding now produces the correct behaviour.

### Test results

- `python3 -m pytest tests/ -q` → **84 passed in 11.03s**. 80 prior + 4 new. No regressions in the existing 80-test suite.
- Tier-1 (swc_workload direct) and tier-2 (swc wrapper) tiers both green.

### Pipeline

`pipeline.md` is still the template stub (placeholder `<command to run>` etc.) — no project-level pipeline command to run. Pipeline check skipped.

### Build confidence

High. The fix is one-line in two functions plus a one-line text edit; the four new tests pin both the literal F-01 reproduction and the general "anywhere in op_args" contract that prevents recurrence; manual repro from a fresh tmp repo confirms `_meta.json` corruption path is closed.

### Scope flags

None.

### Approach needs revisiting

No.

---

## Pass 9 — 2026-05-19

### Changes

- **Split `exists` into two complementary commands at different layers.** Closes a help-listing gap from Pass 8 where `exists` was invisible under `swc workload --help` because it was wrapper-only.
- **`cli/swc_workload` gained an `exists` subcommand** — pure file-presence check with a lenient folder contract. Returns `false` (exit 0, nothing on stderr) for: folder missing, path is a file not a directory, or folder exists without `workload.json`. Returns `true` only when the folder exists, is a directory, and contains `workload.json`. The `description=` text calls out the lenient contract explicitly — it is the only `swc_workload` op that does NOT enforce the strict folder validations introduced in Pass 7. Honours `--json` to emit `{"exists": true/false}`.
- **`cli/swc` `handle_workload` reworked for `exists`** — the old wrapper-level `handle_exists` and its `EXISTS_HELP` constant were removed. `swc workload exists` now flows through the standard dispatch with one exception: bypass the strict "no mapping → error" rule. If no `_meta.json` mapping exists for the current branch, the wrapper emits `false` directly via a new `_emit_boolean(value, op_args)` helper (no folder to forward into). If a mapping exists, it forwards `exists` to `swc_workload exists` with the resolved folder, where the inner CLI's lenient check handles the missing-folder / missing-workload.json cases uniformly. `--help` short-circuits to `handle_subcommand_help("exists")`, which delegates to `swc_workload exists --help`.
- **New top-level `swc exists` command.** Added as a sibling to `swc workload` at the top level. Branch-aware integrity check; always emits a boolean (never errors). Warns to stderr (with a `swc workload init` recovery hint) when the mapping exists but the folder or `workload.json` is missing — recoverable states the user should see. Help text in a new `SWC_EXISTS_HELP` constant; `--help` / `-h` detection anywhere in op_args (same Pass 8 `any(...)` idiom).
- **State table for `swc exists`:**

  | State                                            | stdout | stderr warning                                                              | Exit |
  |--------------------------------------------------|--------|-----------------------------------------------------------------------------|------|
  | No mapping in `_meta.json` for branch            | false  | (nothing)                                                                   | 0    |
  | Mapping exists, folder missing on disk           | false  | warning: context folder missing for branch '<X>'; run `swc workload init`   | 0    |
  | Mapping + folder exist, no workload.json inside  | false  | warning: context folder exists for branch '<X>' but workload.json missing   | 0    |
  | Mapping + folder + workload.json all present     | true   | (nothing)                                                                   | 0    |

- **Top-level `swc --help` updated to list both subcommands** (`workload`, `exists`). `handle_workload_help` preamble for `swc workload --help` rewritten to describe the new bypass-when-no-mapping / forward-otherwise behaviour and pointing readers at top-level `swc exists` for the branch-aware integrity check.
- **`main()` dispatch extended** to route on `cmd ∈ {"workload", "exists"}`. Error message for unknown commands updated to list both available commands.

### Testing

- TDD per pass policy. Wrote tier-1 tests for the new `swc_workload exists` first (4 state-table cases + 2 JSON variants); confirmed all 6 failed against the unmodified CLI; implemented `cmd_exists` and the subparser registration; all 6 passed.
- Wrote tier-2 tests next (delegation + top-level `swc exists` 4-state matrix + JSON + help); implemented the dispatch rework + new top-level handler; all passed.
- Manual verification in a tmp git repo on `feature/manual-verify` covered all four `swc exists` states and confirmed `swc --help`, `swc workload --help`, `swc exists --help`, and `swc workload exists --help` all render sensible text.

#### New tests

- `tests/cli/test_swc_workload_io.py` (tier 1): `test_exists_false_when_folder_is_missing`, `test_exists_false_when_path_is_a_file`, `test_exists_false_when_folder_exists_but_no_workload_json`, `test_exists_true_when_workload_json_present`, `test_exists_json_form_true`, `test_exists_json_form_false`.
- `tests/cli/test_swc_resolution.py` (tier 2 — `swc workload exists`): `test_swc_workload_exists_true_after_init`, `test_swc_workload_exists_false_without_mapping`, `test_swc_workload_exists_json_form`, `test_swc_workload_exists_json_form_no_mapping`, `test_swc_workload_exists_delegates_when_folder_missing`. (The previous `test_req23_*` tests were renamed/rewritten — same scenarios, narrative now matches the post-split behaviour.)
- `tests/cli/test_swc_exists.py` (tier 2 — NEW file for the top-level command): `test_swc_exists_false_when_no_mapping`, `test_swc_exists_false_with_warning_when_folder_missing`, `test_swc_exists_false_with_warning_when_workload_json_missing`, `test_swc_exists_true_when_fully_set_up`, `test_swc_exists_json_true`, `test_swc_exists_json_false_no_mapping`, `test_swc_exists_json_false_with_warning_still_emits_warning`, `test_swc_exists_help_exits_zero_and_describes_op`, `test_swc_exists_short_h_flag`.
- `tests/cli/test_swc_help.py`: `test_swc_top_level_help_lists_exists_command` — asserts `swc --help` lists both `workload` and `exists`.

### Test results

- `python3 -m pytest tests/ -q` → **102 passed in 12.31s**. 84 prior + 18 new. No regressions.

### Pipeline

`pipeline.md` is still the template stub. Pipeline verification via the project pytest suite as the de facto build signal.

### Build confidence

High. The split is mechanical and each layer's contract is now explicit: tier-1 tests pin the lenient file-presence semantics on `swc_workload exists`; tier-2 tests pin the delegation behaviour of `swc workload exists` (including the no-mapping bypass and the stale-mapping forward); a dedicated test file pins the four-state matrix and warning copy of the new top-level `swc exists`. The `swc workload exists` help is no longer hidden — the inner CLI now lists it as a real op.

### Scope flags

None new. The deferred set carries forward from Pass 8: F-04/F-05 (info, accepted), F-06 (file size, tech-debt), F-08 (orphan folder on init failure, accepted), REQ-26 (plugin-missing prompt, 3.3), REQ-27 (pre-edit hook, phase 3), skill migration (phase 2).

### Approach needs revisiting

No.

---

## Pass 10 — 2026-05-19

### Changes

- **F-02 (info) — removed unused `NO_WORKLOAD_REQUIRED` constant.** Deleted the dead `NO_WORKLOAD_REQUIRED = {"init", "exists"}` set from `cli/swc` (was at line 381). Never referenced — the dispatch in `handle_workload` uses explicit `if op == "init"` / `if op == "exists"` branches. User chose remove over refactor.
- **F-04 (info) — `EXISTS_HELP` interceptor added in `cli/swc`.** New constant mirroring `INIT_HELP`'s pattern: wrapper-aware help text describing the bypass-when-no-mapping / forward-when-mapping flow, with a pointer to top-level `swc exists` for the integrity-aware check. Wired into `handle_workload`'s exists branch with the `any(a in ("--help", "-h") for a in op_args)` idiom from Pass 8, placed BEFORE the bypass / forward logic. Hides the inner CLI's `--workload` flag (wrapper-controlled, never user-supplied) — matches the existing `init` help's contract.
- **F-05 (info) — `--help` discovery for forwarded ops fixed.** Single-line change in `cli/swc::handle_workload`: `if op_args and op_args[0] in (...)` → `if any(a in (...) for a in op_args)`. Closes the gap where `swc workload add --json --help` on an unmapped branch short-circuited to `"no workload for branch ..."` (exit 1) instead of showing add's help. Mirrors Pass 8's fix on `init` / `exists`. Source comment explains the trap for future maintainers.
- **F-03 (info) — stale test docstring rewritten.** `test_swc_workload_exists_help_exits_zero_and_describes_op` in `tests/cli/test_swc_help.py` previously claimed `swc workload exists --help` "must NOT forward to swc_workload" — that became false after Pass 9 and is false-again-with-different-mechanism after Pass 10. New docstring describes the final Pass 10 behaviour (intercepted at the wrapper, no forward, no `--workload` leak). Also added the `assert "--workload" not in result.stdout` guard mirroring the init-help test. Removed the stale `F-01` section comment; replaced with a Pass 10 / F-04 marker.
- **Pass 9 context note annotated.** The Pass 9 manual-verification line that explicitly accepted the `--workload` leak in `swc workload exists --help` now carries `[superseded by Pass 10 — EXISTS_HELP interceptor added]` per the brief's "annotate rather than rewrite history" instruction.

### Testing

- Followed TDD per pass policy. Added 3 new scenario tests + extended 2 existing tests to assert the new contracts; all failures observed BEFORE implementation:
  - `test_swc_workload_exists_help_exits_zero_and_describes_op` — added `assert "--workload" not in result.stdout` guard (failed: stdout contained `--workload` from the forwarded inner CLI help).
  - `test_swc_workload_exists_short_h_flag` — added the same `--workload` guard (failed for the same reason).
  - `test_swc_workload_add_help_on_unmapped_branch_shows_help_not_error` — new, F-05 (failed: exit 1, "no workload for branch ...").
  - `test_swc_workload_add_json_then_help_on_unmapped_branch_shows_help` — new, F-05 with `--help` at op_args[1] (failed).
  - `test_swc_workload_add_dash_h_in_non_first_position_shows_help` — new, F-05 with `-h` at op_args[1] (failed).
- Implemented the fixes (EXISTS_HELP constant + interceptor; `any(...)` idiom for forwarded ops; removed `NO_WORKLOAD_REQUIRED`). All 4 new + 1 extended test passed.
- Manual verification in a fresh tmp git repo on `feature/manual-check` covered all three brief-listed checks:
  - `swc workload exists --help` → prints EXISTS_HELP with no `--workload` mention ✓
  - `swc workload add --help` (unmapped) → add's help, exit 0 ✓
  - `swc workload add --json --help` (unmapped) → add's help, exit 0 ✓

### Test results

- `python3 -m pytest tests/ -q` → **105 passed in 12.65s, 0 failed**. 102 prior + 3 new (F-03 was a docstring rewrite of an existing test; F-04's guards were added to existing tests).
- No regressions in the prior 102-test suite.

### Pipeline

No pipeline.md defined — pipeline verification skipped (same as prior passes; flagged across Passes 1–9 but never filled in).

### Build confidence

High. All four in-scope findings are resolved with passing scenario tests pinning the new contracts. F-04 closes the user-facing inconsistency between `init` and `exists` help; F-05 closes the silent unhelpful error path on `--help` for forwarded ops on unmapped branches; F-02 removes a small piece of dead code; F-03 brings the test docstring in sync with the implementation. Manual verification confirmed all three brief-required scenarios produce the expected output.

### Scope flags

- **`pipeline.md` still unfilled** — same flag as Passes 1–9. Recommend `python3 -m pytest tests/ -q` as the build command before the next pass.
- **F-01 (docstring vs. corrupt `_meta.json` reality)** — explicitly accepted per the brief ("user said 'noted', accept as-is. No change"). The `handle_exists` and `cmd_exists` docstrings still say "never errors" but raise `SwcError`/`CLIError` (exit 1) when `_meta.json` is corrupt — that's the documented contract from Pass 7 (F-05) and stays.
- **F-06 (file size)** — deferred to tech-debt.
- **F-08 (orphan folder on init failure)** — accepted per user, carries forward.
- **REQ-26 (plugin-missing prompt)** — handed off to 3.3.
- **REQ-27 (pre-edit hook)** — phase 3 of this work item, not started.
- **Skill migration** — phase 2 of this work item, not started.

### Approach needs revisiting

No.
