"""Tier 2 — scenario tests for `swc workload --help` and subcommand help.

REQ-29: top-level and per-subcommand help are emitted by the wrapper.
The wrapper prepends a short preamble explaining the resolver + special
ops, then delegates to swc_workload --help for the full op list.
"""


def test_swc_workload_help_lists_all_ops(swc):
    """`swc workload --help` shows every op from swc_workload."""
    run, repo = swc
    result = run("workload", "--help")
    assert result.returncode == 0
    out = result.stdout
    for op in ("init", "add", "delete", "list", "start", "complete", "reset", "exists"):
        assert op in out, f"swc workload --help missing {op!r}"
    # Preamble should explain the wrapper.
    assert "swc workload" in out


def test_swc_workload_subcommand_help_describes_flags(swc):
    """`swc workload add --help` shows the add op help (delegated to swc_workload)."""
    run, repo = swc
    result = run("workload", "add", "--help")
    assert result.returncode == 0
    out = result.stdout
    assert "add" in out
    assert "to" in out and "at" in out


def test_swc_top_level_help_lists_workload_command(swc):
    """`swc --help` lists the `workload` command."""
    run, repo = swc
    result = run("--help")
    assert result.returncode == 0
    assert "workload" in result.stdout


def test_swc_top_level_help_lists_exists_command(swc):
    """`swc --help` lists the new top-level `exists` command alongside `workload`."""
    run, repo = swc
    result = run("--help")
    assert result.returncode == 0
    out = result.stdout
    assert "workload" in out
    assert "exists" in out


def test_swc_workload_with_no_op_shows_help(swc):
    """`swc workload` (no op) shows the workload help."""
    run, repo = swc
    result = run("workload")
    assert result.returncode == 0
    assert "workload" in result.stdout
    assert "init" in result.stdout


# ---------------------------------------------------------------------------
# Pass 10 — F-04: `swc workload exists --help` is intercepted at the wrapper
# layer (mirrors INIT_HELP pattern) — EXISTS_HELP is wrapper-owned and does
# NOT expose the inner CLI's `--workload` flag to the user.
# ---------------------------------------------------------------------------


def test_swc_workload_exists_help_exits_zero_and_describes_op(swc):
    """`swc workload exists --help` is intercepted at the wrapper layer and
    shows EXISTS_HELP — no forward, no `--workload` flag leak.

    Pass 10 mirrors the INIT_HELP / handle_init_with_help pattern for exists:
    EXISTS_HELP is wrapper-owned wrapper-aware prose. The inner CLI's
    `--workload` flag (which the user never supplies at the swc layer) must
    not appear in the rendered help — matches the existing init-help guard.
    """
    run, repo = swc
    result = run("workload", "exists", "--help")
    assert result.returncode == 0
    out = result.stdout.lower()
    assert "exists" in out
    # Should describe the branch-aware presence check, not produce an
    # argparse "invalid choice" error.
    assert "invalid choice" not in out
    assert "invalid choice" not in result.stderr.lower()
    assert "presence" in out or "branch" in out or "boolean" in out
    # Wrapper layer must not advertise the inner CLI's --workload flag —
    # mirror the init-help guard.
    assert "--workload" not in result.stdout, (
        "EXISTS_HELP must not leak the inner CLI's --workload flag"
    )


def test_swc_workload_exists_short_h_flag(swc):
    """`-h` is the standard alias for `--help` and must behave the same."""
    run, repo = swc
    result = run("workload", "exists", "-h")
    assert result.returncode == 0
    assert "exists" in result.stdout.lower()
    assert "--workload" not in result.stdout


# ---------------------------------------------------------------------------
# F-02 — `swc workload init --help` describes the wrapper's flow
# ---------------------------------------------------------------------------


def test_swc_workload_init_help_describes_wrapper_flow(swc):
    """`swc workload init --help` describes the wrapper's full flow
    (folder creation + _meta.json registration), NOT the inner CLI's pure
    file-creation primitive. The `--workload` flag must not appear because
    users never supply it at the swc layer.
    """
    run, repo = swc
    result = run("workload", "init", "--help")
    assert result.returncode == 0
    out = result.stdout
    assert "_meta.json" in out, "wrapper help must mention _meta.json registration"
    assert ".swc/" in out, "wrapper help should mention the folder creation"
    assert "--workload" not in out, "wrapper help must not advertise --workload"


# ---------------------------------------------------------------------------
# F-03 — inner CLI's prog name no longer leaks as `swc_workload`
# ---------------------------------------------------------------------------


def test_swc_workload_add_help_does_not_leak_swc_workload_prog_name(swc):
    """`swc workload add --help` (forwarded) must show `swc workload add`
    in the usage line, not `swc_workload add`.
    """
    run, repo = swc
    result = run("workload", "add", "--help")
    assert result.returncode == 0
    assert "swc_workload" not in result.stdout, (
        f"inner CLI prog name leaked: {result.stdout!r}"
    )
    assert "swc workload" in result.stdout


def test_swc_workload_unknown_op_error_does_not_leak_swc_workload(swc):
    """A bogus op forwarded to the inner CLI's argparse should not surface
    `swc_workload` in its error message.
    """
    run, repo = swc
    # Need a workload to exist for the inner CLI to be invoked.
    run("workload", "init")
    result = run("workload", "bogus-op")
    assert result.returncode != 0
    combined = result.stdout + result.stderr
    assert "swc_workload" not in combined, (
        f"inner CLI prog name leaked in error: {combined!r}"
    )


# ---------------------------------------------------------------------------
# Pass 8 — F-01: `--help` anywhere in op_args, not just first position
# ---------------------------------------------------------------------------


def test_swc_workload_init_help_after_json_does_not_touch_filesystem(swc):
    """`swc workload init --json --help` must print INIT_HELP and NOT mutate
    the filesystem. Previously the wrapper only checked op_args[0], so
    `--help` after `--json` fell through to the full init flow: the folder
    was created and `_meta.json` was written with a stale registration
    pointing at an empty folder (no workload.json).
    """
    run, repo = swc
    swc_dir = repo / ".swc"
    meta = swc_dir / "_meta.json"
    folder = swc_dir / "feature_test-cli"

    assert not meta.exists(), "precondition: no _meta.json before run"
    assert not folder.exists(), "precondition: no workload folder before run"

    result = run("workload", "init", "--json", "--help")
    assert result.returncode == 0
    # Wrapper-aware help text was printed, not the inner CLI's primitive.
    assert "_meta.json" in result.stdout
    assert "--workload" not in result.stdout

    # Filesystem must be untouched — no folder created, no _meta.json written.
    assert not meta.exists(), (
        f"INIT_HELP path should not write _meta.json, but it exists: "
        f"{meta.read_text() if meta.exists() else ''!r}"
    )
    assert not folder.exists(), (
        "INIT_HELP path should not create the workload folder"
    )


def test_swc_workload_init_json_then_dash_h_does_not_touch_filesystem(swc):
    """Pins the general 'anywhere in op_args' contract — `-h` AFTER
    `--json` (so it isn't op_args[0]) must also short-circuit to
    INIT_HELP without filesystem writes.
    """
    run, repo = swc
    swc_dir = repo / ".swc"
    meta = swc_dir / "_meta.json"
    folder = swc_dir / "feature_test-cli"

    result = run("workload", "init", "--json", "-h")
    assert result.returncode == 0
    assert "_meta.json" in result.stdout

    assert not meta.exists()
    assert not folder.exists()


# ---------------------------------------------------------------------------
# Pass 8 — F-02: `swc workload exists --json --help` must show EXISTS_HELP
# ---------------------------------------------------------------------------


def test_swc_workload_exists_help_after_json_prints_help_not_boolean(swc):
    """`swc workload exists --json --help` must print EXISTS_HELP (not the
    `{"exists": false}` JSON payload). Previously the wrapper only checked
    op_args[0], so `--help` after `--json` was silently ignored and the
    boolean was emitted instead of the help text.
    """
    run, repo = swc
    result = run("workload", "exists", "--json", "--help")
    assert result.returncode == 0
    out = result.stdout
    # Help text indicators (not the JSON boolean payload).
    assert "exists" in out.lower()
    assert "usage:" in out.lower() or "presence" in out.lower() or "branch" in out.lower()
    # Must NOT be the JSON boolean output.
    assert '"exists"' not in out, (
        f"EXISTS_HELP should be shown, got JSON payload: {out!r}"
    )


# ---------------------------------------------------------------------------
# Pass 8 — F-03: INIT_HELP no longer advertises forwarding implementation
# ---------------------------------------------------------------------------


def test_swc_workload_init_help_describes_json_consistently(swc):
    """INIT_HELP should describe `--json` cleanly (without leaking that it's
    forwarded to the inner CLI). The current wording was a minor narrative
    drift; cleaned up under Option B (drop the parenthetical).
    """
    run, repo = swc
    result = run("workload", "init", "--help")
    assert result.returncode == 0
    out = result.stdout
    assert "--json" in out
    # The previous "(path to the created workload)" parenthetical was the
    # inner CLI's output shape leaking into wrapper-level help — should be gone.
    assert "(path to the created workload)" not in out


# ---------------------------------------------------------------------------
# Pass 10 — F-05: `--help` discovery for forwarded ops must work anywhere in
# op_args (not just position 0). Mirror Pass 8's `init` / `exists` fix.
# ---------------------------------------------------------------------------


def test_swc_workload_add_help_on_unmapped_branch_shows_help_not_error(swc):
    """`swc workload add --help` on a branch with no workload must show add's
    help (forwarded via `handle_subcommand_help("add")`) and exit 0 — NOT
    short-circuit to `"no workload for branch ..."` (exit 1).

    Pre-Pass-10 the forwarded-op `--help` discovery only checked op_args[0],
    so `--help` at position 0 worked but anywhere else fell through to the
    missing-workload guard.
    """
    run, repo = swc
    result = run("workload", "add", "--help")
    assert result.returncode == 0
    assert "no workload for branch" not in result.stderr
    out = result.stdout
    # Add's help text indicators.
    assert "add" in out
    assert "to" in out and "at" in out


def test_swc_workload_add_json_then_help_on_unmapped_branch_shows_help(swc):
    """`swc workload add --json --help` on a branch with no workload must
    show add's help, NOT `"no workload for branch ..."`. This pins the
    "anywhere in op_args" contract — Pass 8's fix for init / exists must
    extend to forwarded ops too.
    """
    run, repo = swc
    result = run("workload", "add", "--json", "--help")
    assert result.returncode == 0, (
        f"expected exit 0, got {result.returncode}; stderr: {result.stderr!r}"
    )
    assert "no workload for branch" not in result.stderr
    out = result.stdout
    assert "add" in out
    assert "to" in out and "at" in out


def test_swc_workload_add_dash_h_in_non_first_position_shows_help(swc):
    """Pins the `-h` variant of the same contract: `-h` in non-first
    position must short-circuit to forwarded help, not the
    missing-workload guard.
    """
    run, repo = swc
    result = run("workload", "add", "--json", "-h")
    assert result.returncode == 0
    assert "no workload for branch" not in result.stderr
    assert "add" in result.stdout
