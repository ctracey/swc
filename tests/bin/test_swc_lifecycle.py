"""Tier 2 — scenario tests against the user-facing `bin/swc workload <op>` wrapper.

Lifecycle: REQ-01 (init creates workload + registers in _meta.json),
REQ-02 (init refuses to overwrite existing).
"""

import json


# ---------------------------------------------------------------------------
# REQ-01 — init creates workload AND registers branch in _meta.json
# ---------------------------------------------------------------------------


def test_req01_init_on_fresh_branch_creates_workload_and_registers_meta(swc):
    """Given the current branch has no entry in .swc/_meta.json
    And no folder under .swc/ matches the branch
    When I run `swc workload init`
    Then a workload.json file is created at .swc/<folder>/workload.json
    And .swc/_meta.json maps the branch to <folder>
    """
    run, repo = swc

    result = run("workload", "init")
    assert result.returncode == 0, f"stderr: {result.stderr}"

    # Branch is `feature/test-cli` from the swc_repo fixture; folder is `feature_test-cli`.
    workload_path = repo / ".swc" / "feature_test-cli" / "workload.json"
    assert workload_path.exists(), "workload.json should be created"

    meta = json.loads((repo / ".swc" / "_meta.json").read_text())
    assert meta["workloads"]["feature/test-cli"] == "feature_test-cli"


# ---------------------------------------------------------------------------
# REQ-02 — init refuses to overwrite existing workload
# ---------------------------------------------------------------------------


def test_req02_init_refuses_to_overwrite_existing(swc):
    """Given the current branch already maps to an existing workload
    When I run `swc workload init`
    Then the CLI prints the existing workload path
    And the existing workload.json is unchanged
    And _meta.json is also unchanged (byte-equal — F-07)
    And the CLI exits non-zero
    """
    run, repo = swc
    run("workload", "init")
    workload_path = repo / ".swc" / "feature_test-cli" / "workload.json"
    meta_path = repo / ".swc" / "_meta.json"
    original = workload_path.read_text()
    # F-07: pin that _meta.json is byte-identical after refused re-init —
    # nothing in handle_init should re-write meta when forward("init") fails.
    meta_before = meta_path.read_bytes()

    result = run("workload", "init")
    assert result.returncode != 0
    assert "feature_test-cli" in (result.stdout + result.stderr) or "already exists" in result.stderr.lower()
    assert workload_path.read_text() == original
    assert meta_path.read_bytes() == meta_before, (
        "_meta.json must not be re-written when init refuses to overwrite"
    )


# ---------------------------------------------------------------------------
# F-05 — corrupt _meta.json fails loudly (no silent fallback / overwrite)
# ---------------------------------------------------------------------------


def test_corrupt_meta_json_errors_on_list_without_overwriting(swc):
    """`swc workload list` against a corrupt _meta.json errors clearly and
    leaves the file untouched. Previously: silently swallowed → empty dict.
    """
    run, repo = swc
    meta_path = repo / ".swc" / "_meta.json"
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    corrupt = '{"workloads": {"feature/test-cli": "feature_test-cli"'  # truncated
    meta_path.write_text(corrupt)
    meta_before = meta_path.read_bytes()

    result = run("workload", "list")
    assert result.returncode != 0
    msg = result.stderr.lower()
    assert "_meta.json" in result.stderr or "_meta" in result.stderr.lower()
    assert "corrupt" in msg or "cannot be parsed" in msg
    # File must not be mutated by the read.
    assert meta_path.read_bytes() == meta_before


def test_corrupt_meta_json_errors_on_init_without_overwriting(swc):
    """`swc workload init` against a corrupt _meta.json errors clearly and
    does NOT overwrite the file (which would silently drop other mappings).
    """
    run, repo = swc
    meta_path = repo / ".swc" / "_meta.json"
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    corrupt = '{"workloads": {"other-branch": "other-folder"'  # truncated
    meta_path.write_text(corrupt)
    meta_before = meta_path.read_bytes()

    result = run("workload", "init")
    assert result.returncode != 0
    msg = result.stderr.lower()
    assert "corrupt" in msg or "cannot be parsed" in msg
    # The key safety claim: corrupt _meta.json is NOT overwritten.
    assert meta_path.read_bytes() == meta_before


# ---------------------------------------------------------------------------
# F-04 (wrapper layer) — OSError surfaces as friendly error
# ---------------------------------------------------------------------------


def test_oserror_in_write_meta_surfaces_as_friendly_error(swc):
    """If write_meta raises OSError (e.g. .swc/ unwritable), the wrapper
    catches it in main() and emits a friendly error rather than a traceback.
    """
    import pytest
    import stat as _stat

    run, repo = swc
    # Make .swc/ read-only after creating it. The wrapper's handle_init tries
    # to mkdir .swc/<folder>/ inside an unwritable .swc/ — fails with OSError.
    swc_dir = repo / ".swc"
    swc_dir.mkdir(parents=True, exist_ok=True)
    swc_dir.chmod(_stat.S_IRUSR | _stat.S_IXUSR)
    try:
        result = run("workload", "init")
        if result.returncode == 0:
            pytest.skip("read-only chmod not honoured in this environment")
        msg = result.stderr.lower()
        assert "file system error" in msg or "permission" in msg, (
            f"expected friendly OSError message, got: {result.stderr!r}"
        )
        assert "traceback" not in msg
    finally:
        swc_dir.chmod(_stat.S_IRWXU)
