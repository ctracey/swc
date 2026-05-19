# Code Review Findings — 3.2: cli tool for workload — 2026-05-19

## Summary

Pass 10 re-review. All four targeted findings from pass 9 (F-02 dead constant, F-03 stale docstring, F-04 EXISTS_HELP interceptor, F-05 `--help` anywhere in op_args for forwarded ops) are correctly applied. The fixes are mechanically tight and follow the Pass 8 idiom consistently: `EXISTS_HELP` mirrors `INIT_HELP`'s constant+interceptor pattern, and the new `any(a in ("--help", "-h") for a in op_args)` check in the forwarded-op branch matches the identical pattern already used in `handle_init_with_help`, `handle_exists`, and the new exists branch in `handle_workload`. F-01 (docstring vs corrupt `_meta.json`) is explicitly accepted per the brief — no change expected. All 105/105 tests pass with no regressions. Manual verification confirms `swc workload exists --help` (and `-h`) hides `--workload` and renders `EXISTS_HELP`; `swc workload add --help` and `swc workload add --json --help` on an unmapped branch both forward to the inner CLI's add help and exit 0. The dead `NO_WORKLOAD_REQUIRED` constant is gone (confirmed via grep). The test docstring rewrite at `test_swc_workload_exists_help_exits_zero_and_describes_op` accurately describes the Pass 10 wrapper-interception behaviour, and the `assert "--workload" not in result.stdout` guard is in place on both `test_swc_workload_exists_help_exits_zero_and_describes_op` and `test_swc_workload_exists_short_h_flag`. No new issues introduced.

Verification details:
- **F-02:** `grep NO_WORKLOAD_REQUIRED cli/swc cli/swc_workload` returns nothing. The dispatch in `handle_workload` uses explicit `if op == "init"` / `if op == "exists"` branches at lines 405, 418 — clearer at the dispatch site than a set-membership check would be (each branch carries its own handler and special-help/bypass semantics).
- **F-03:** `tests/cli/test_swc_help.py:65-88` — docstring now describes Pass 10's interception behaviour ("intercepted at the wrapper layer ... no forward, no `--workload` flag leak"). The stale F-01 marker is replaced by a "Pass 10 — F-04" section comment at line 59. The `assert "--workload" not in result.stdout` guard is present on both the `--help` test (line 86) and the `-h` test (line 97).
- **F-04:** `EXISTS_HELP` constant at `cli/swc:334-347` mirrors `INIT_HELP`'s shape (lines 233-243): wrapper-aware prose, no `--workload` flag, identical `--json` description tone ("Emit structured JSON output."), and a pointer to top-level `swc exists` for the integrity-aware check. Interceptor at line 419 uses the Pass 8 `any(...)` idiom and is placed BEFORE the bypass/forward logic in `handle_workload`'s exists branch (lines 418-429). Wired directly into `handle_workload` rather than via a new `handle_exists_with_help` wrapper — sensible because the exists branch's bypass/forward logic already lives inline in `handle_workload`, so the help interception sits alongside it. The dispatch reads cleanly.
- **F-05:** Single-line change at `cli/swc:438` — `if op_args and op_args[0] in (...)` is now `if any(a in (...) for a in op_args)`. Source comment at lines 433-437 explains the trap for future maintainers and references the Pass 8 fix it mirrors. Manual reproduction: `swc workload add --help` and `swc workload add --json --help` on the unmapped fresh branch both print the forwarded inner add help with exit 0 and no "no workload for branch" stderr. (The inner add help correctly DOES advertise `--workload` because that's the inner CLI's own surface — this is expected per the design.)

Test suite: `python3 -m pytest tests/ -q` → 105/105 passed in ~12s. The Pass 10 additions are `test_swc_workload_add_help_on_unmapped_branch_shows_help_not_error`, `test_swc_workload_add_json_then_help_on_unmapped_branch_shows_help`, `test_swc_workload_add_dash_h_in_non_first_position_shows_help` (all three pin the F-05 contract), plus the new `--workload` guards on the two exists-help tests (F-04). No regressions.

## Findings

None.

## Verdict

**PASS**

Pass 10 cleanly resolves all four targeted info findings with mechanically minimal changes that follow the established Pass 8 idiom; the full 105-test suite is green and manual reproduction of the three brief-required scenarios produces the expected output.
