"""Tier 2 — scenario tests for the new top-level `swc exists` command.

Pass 9 introduced `swc exists` as a top-level command (alongside `swc
workload`). It is branch-aware and warning-aware:

| State                                            | stdout | stderr warning                                                          | Exit |
|--------------------------------------------------|--------|-------------------------------------------------------------------------|------|
| No mapping in _meta.json for branch              | false  | (nothing)                                                               | 0    |
| Mapping exists, folder missing on disk           | false  | warning: context folder missing for branch '<X>'; run init to recreate  | 0    |
| Mapping + folder exist, no workload.json inside  | false  | warning: context folder exists but workload.json is missing; run init  | 0    |
| Mapping + folder + workload.json all present     | true   | (nothing)                                                               | 0    |

Always exits 0 (never errors). Honours `--json`.
"""

import json


# ---------------------------------------------------------------------------
# Four state-table scenarios
# ---------------------------------------------------------------------------


def test_swc_exists_false_when_no_mapping(swc):
    """No `_meta.json` mapping for the current branch → false, no warning."""
    run, repo = swc
    result = run("exists")
    assert result.returncode == 0
    assert result.stdout.strip().lower() == "false"
    # No mapping is a non-set-up branch — nothing to warn about.
    assert result.stderr == "", (
        f"no-mapping case should be silent on stderr, got: {result.stderr!r}"
    )


def test_swc_exists_false_with_warning_when_folder_missing(swc):
    """Mapping in _meta.json but the folder has been deleted on disk →
    false + stderr warning suggesting `swc workload init`.
    """
    run, repo = swc
    swc_dir = repo / ".swc"
    swc_dir.mkdir(parents=True)
    (swc_dir / "_meta.json").write_text(
        json.dumps({"workloads": {"feature/test-cli": "feature_test-cli"}})
    )
    # Folder mapped but missing on disk.
    assert not (swc_dir / "feature_test-cli").exists()

    result = run("exists")
    assert result.returncode == 0
    assert result.stdout.strip().lower() == "false"

    warn = result.stderr.lower()
    assert "warning" in warn
    assert "context folder missing" in warn or "folder missing" in warn
    assert "feature/test-cli" in result.stderr
    assert "swc workload init" in result.stderr


def test_swc_exists_false_with_warning_when_workload_json_missing(swc):
    """Mapping + folder exist on disk but workload.json is absent inside →
    false + stderr warning about the missing workload.json.
    """
    run, repo = swc
    swc_dir = repo / ".swc"
    folder = swc_dir / "feature_test-cli"
    folder.mkdir(parents=True)
    (swc_dir / "_meta.json").write_text(
        json.dumps({"workloads": {"feature/test-cli": "feature_test-cli"}})
    )
    # Folder exists but no workload.json inside.
    assert not (folder / "workload.json").exists()

    result = run("exists")
    assert result.returncode == 0
    assert result.stdout.strip().lower() == "false"

    warn = result.stderr.lower()
    assert "warning" in warn
    assert "workload.json is missing" in warn or "workload.json missing" in warn
    assert "feature/test-cli" in result.stderr
    assert "swc workload init" in result.stderr


def test_swc_exists_true_when_fully_set_up(swc_initialised):
    """Mapping + folder + workload.json all present → true, no warning."""
    run, repo = swc_initialised
    result = run("exists")
    assert result.returncode == 0
    assert result.stdout.strip().lower() == "true"
    assert result.stderr == ""


# ---------------------------------------------------------------------------
# --json output shape
# ---------------------------------------------------------------------------


def test_swc_exists_json_true(swc_initialised):
    run, repo = swc_initialised
    result = run("exists", "--json")
    assert result.returncode == 0
    assert json.loads(result.stdout) == {"exists": True}


def test_swc_exists_json_false_no_mapping(swc):
    run, repo = swc
    result = run("exists", "--json")
    assert result.returncode == 0
    assert json.loads(result.stdout) == {"exists": False}


def test_swc_exists_json_false_with_warning_still_emits_warning(swc):
    """`--json` doesn't suppress the stderr warning — warnings stay on stderr."""
    run, repo = swc
    swc_dir = repo / ".swc"
    swc_dir.mkdir(parents=True)
    (swc_dir / "_meta.json").write_text(
        json.dumps({"workloads": {"feature/test-cli": "feature_test-cli"}})
    )

    result = run("exists", "--json")
    assert result.returncode == 0
    assert json.loads(result.stdout) == {"exists": False}
    assert "warning" in result.stderr.lower()
    assert "swc workload init" in result.stderr


# ---------------------------------------------------------------------------
# `swc exists --help`
# ---------------------------------------------------------------------------


def test_swc_exists_help_exits_zero_and_describes_op(swc):
    """`swc exists --help` prints help and exits 0 without doing the check."""
    run, repo = swc
    result = run("exists", "--help")
    assert result.returncode == 0
    out = result.stdout.lower()
    assert "exists" in out
    assert "branch" in out
    assert "--json" in out


def test_swc_exists_short_h_flag(swc):
    """`-h` alias works the same as `--help`."""
    run, repo = swc
    result = run("exists", "-h")
    assert result.returncode == 0
    assert "exists" in result.stdout.lower()
