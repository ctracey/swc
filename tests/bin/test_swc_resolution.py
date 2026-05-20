"""Tier 2 — scenario tests for the `swc` wrapper's context resolution.

Covers REQ-23 (exists boolean) and REQ-25 (missing-workload op error
recommending init), plus the basic happy-path forwarding behaviour.
"""

import json


# ---------------------------------------------------------------------------
# Pass 9 — `swc workload exists` delegates to swc_workload exists
#
# After the Pass 9 split, the wrapper does NOT do the branch-aware integrity
# check anymore — that moved to top-level `swc exists`. The wrapper now:
#   * No mapping for the branch → bypass forward, emit `false` directly
#   * Mapping present          → forward `exists` to swc_workload with the
#                                resolved folder; the inner CLI does the
#                                lenient file-presence check.
# Both cases exit 0; never errors. Honours --json.
# ---------------------------------------------------------------------------


def test_swc_workload_exists_true_after_init(swc_initialised):
    """Given the current branch has a workload (mapping + file)
    When I run `swc workload exists`
    Then the inner file-presence check returns true
    """
    run, repo = swc_initialised
    result = run("workload", "exists")
    assert result.returncode == 0
    assert "true" in result.stdout.lower()


def test_swc_workload_exists_false_without_mapping(swc):
    """Given the current branch has no _meta.json mapping
    When I run `swc workload exists`
    Then the wrapper short-circuits to false (no forwarding)
    And exits 0
    """
    run, repo = swc
    result = run("workload", "exists")
    assert result.returncode == 0
    assert "false" in result.stdout.lower()
    # Lenient — no warning at the wrapper layer (warnings live at swc exists).
    assert result.stderr == ""


def test_swc_workload_exists_json_form(swc_initialised):
    run, repo = swc_initialised
    result = run("workload", "exists", "--json")
    assert result.returncode == 0
    assert json.loads(result.stdout)["exists"] is True


def test_swc_workload_exists_json_form_no_mapping(swc):
    """`--json` honoured on the no-mapping short-circuit path."""
    run, repo = swc
    result = run("workload", "exists", "--json")
    assert result.returncode == 0
    assert json.loads(result.stdout) == {"exists": False}


def test_swc_workload_exists_delegates_when_folder_missing(swc):
    """Mapping in _meta.json but the folder on disk has been deleted →
    swc workload exists must still answer (false). It forwards to
    swc_workload exists with the folder path; the inner CLI's lenient
    contract handles the missing folder cleanly.
    """
    run, repo = swc
    # Hand-craft a mapping with a folder that does not exist on disk.
    swc_dir = repo / ".swc"
    swc_dir.mkdir(parents=True)
    (swc_dir / "_meta.json").write_text(
        json.dumps({"workloads": {"feature/test-cli": "feature_test-cli"}})
    )
    # Folder is absent — no `.swc/feature_test-cli/`.
    assert not (swc_dir / "feature_test-cli").exists()

    result = run("workload", "exists")
    assert result.returncode == 0
    assert "false" in result.stdout.lower()


# ---------------------------------------------------------------------------
# REQ-25 — non-init/non-exists op on branch with no workload exits non-zero,
#          recommends `swc workload init`
# ---------------------------------------------------------------------------


def test_req25_list_with_no_workload_recommends_init(swc):
    run, repo = swc
    result = run("workload", "list")
    assert result.returncode != 0
    msg = result.stderr.lower()
    assert "init" in msg
    assert "no workload" in msg or "swc workload init" in msg


def test_req25_add_with_no_workload_recommends_init(swc):
    run, repo = swc
    result = run("workload", "add", "anything")
    assert result.returncode != 0
    assert "init" in result.stderr.lower()


def test_req25_exists_does_not_require_workload(swc):
    """exists is the exception — should not require a workload to answer."""
    run, repo = swc
    result = run("workload", "exists")
    assert result.returncode == 0


def test_req25_init_does_not_require_existing_workload(swc):
    """init obviously doesn't require an existing workload."""
    run, repo = swc
    result = run("workload", "init")
    assert result.returncode == 0


# ---------------------------------------------------------------------------
# Forwarding — confirm a vanilla op (add + list) round-trips through swc to
# the resolved workload path.
# ---------------------------------------------------------------------------


def test_swc_forwards_add_and_list_to_resolved_workload(swc_initialised):
    """Add via swc, then read back via swc — confirms forwarding works end-to-end."""
    run, repo = swc_initialised
    add = run("workload", "add", "first")
    assert add.returncode == 0, add.stderr

    listed = run("workload", "list", "--json")
    assert listed.returncode == 0, listed.stderr
    items = json.loads(listed.stdout)["items"]
    assert len(items) == 1
    assert items[0]["title"] == "first"


def test_swc_resolves_via_meta_json_mapping(swc_initialised):
    """After init the branch→folder mapping is in _meta.json; subsequent ops
    resolve through that mapping rather than re-deriving the folder name.
    """
    run, repo = swc_initialised

    meta = json.loads((repo / ".swc" / "_meta.json").read_text())
    assert meta["workloads"]["feature/test-cli"] == "feature_test-cli"

    # An op against the resolved mapping should succeed.
    result = run("workload", "list")
    assert result.returncode == 0


def test_swc_branch_with_slash_uses_underscore_folder(swc_initialised):
    """`/` in branch names maps to `_` in folder names (mirrors context-lookup)."""
    run, repo = swc_initialised
    folder = repo / ".swc" / "feature_test-cli"
    assert folder.exists()
    # No folder named with the slash form.
    assert not (repo / ".swc" / "feature").exists()
