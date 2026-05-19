"""Shared fixtures for the CLI test tiers.

Two tiers live here:

* `tests/cli/test_swc_workload_*.py` — direct tests against `cli/swc_workload`.
  No git, no _meta.json. Tests pass `--workload <tmp-path>` explicitly.

* `tests/cli/test_swc_*.py` — scenario tests against the user-facing
  `cli/swc workload <op>` wrapper. Need a git-aware repo; uses the
  `swc_repo` fixture below which creates a tmp git repo + branch.

Both tiers invoke the CLIs via subprocess so the argparse surface (and the
exit code / stderr behaviour) is covered end-to-end.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent
SWC_WORKLOAD = PLUGIN_ROOT / "cli" / "swc_workload"
SWC = PLUGIN_ROOT / "cli" / "swc"


# ---------------------------------------------------------------------------
# Tier 1: swc_workload direct invocation
# ---------------------------------------------------------------------------


def _run(cmd: list[str], cwd: Path | None = None, env: dict | None = None):
    final_env = os.environ.copy()
    if env:
        final_env.update(env)
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        env=final_env,
        capture_output=True,
        text=True,
    )


def run_swc_workload(*args, workload: Path | None = None):
    """Invoke `cli/swc_workload` as a subprocess.

    `args` is the full arg list as passed on the command line — including
    `--workload` if the test wants to position it elsewhere. If `workload`
    is supplied, it is prepended as `--workload <folder>` after the op so most
    tests don't have to thread it through every call. The `--workload`
    contract is folder-path: swc_workload resolves <folder>/workload.json
    internally.
    """
    cmd = [sys.executable, str(SWC_WORKLOAD), *map(str, args)]
    if workload is not None:
        cmd.extend(["--workload", str(workload)])
    return _run(cmd)


@pytest.fixture
def swcw(tmp_path):
    """Return (run_fn, workload_json_path).

    `run_fn(*args)` invokes swc_workload against the per-test workload
    folder (pytest's `tmp_path`). The returned `workload` value is the
    expected workload.json path inside that folder (for tests that need to
    read/write the file directly after init runs). The folder exists; the
    workload.json is NOT pre-initialised — each test calls `init` (or seeds
    the file) as needed.
    """
    folder = tmp_path
    workload_json = folder / "workload.json"

    def run(*args):
        return run_swc_workload(*args, workload=folder)

    return run, workload_json


@pytest.fixture
def swcw_ready(swcw):
    """Like `swcw` but with `init` pre-run so the workload exists."""
    run, workload = swcw
    result = run("init")
    assert result.returncode == 0, f"init failed: {result.stderr}"
    return run, workload


# ---------------------------------------------------------------------------
# Tier 2: swc (user-facing wrapper)
# ---------------------------------------------------------------------------


def _git(cwd: Path, *args):
    """Run a git command in cwd, raising on failure."""
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=True,
    )


@pytest.fixture
def swc_repo(tmp_path):
    """A tmp git repo with a single initial commit on a feature branch.

    Returns the repo path. The .swc/ directory is NOT pre-created — tests
    that need it call `swc workload init` to materialise it (the normal flow).

    The branch is `feature/test-cli` so test paths exercise the `/` → `_`
    folder-name convention.
    """
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "Test")
    _git(tmp_path, "commit", "--allow-empty", "-q", "-m", "init")
    # Default branch may be `main` or `master` depending on git config;
    # explicitly create the feature branch we want.
    _git(tmp_path, "checkout", "-q", "-b", "feature/test-cli")
    return tmp_path


def run_swc(*args, cwd: Path):
    """Invoke `cli/swc` against the given repo cwd.

    Uses SWC_REPO_ROOT and SWC_BRANCH to lock context resolution to the
    fixture's repo regardless of where pytest is invoked from. The CLI
    honours both env vars before consulting git, which keeps the test
    independent of the surrounding process state.
    """
    branch_result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=True,
    )
    branch = branch_result.stdout.strip()
    env = {
        "SWC_REPO_ROOT": str(cwd),
        "SWC_BRANCH": branch,
    }
    cmd = [sys.executable, str(SWC), *map(str, args)]
    return _run(cmd, cwd=cwd, env=env)


@pytest.fixture
def swc(swc_repo):
    """Return (run_fn, repo_path) for the user-facing CLI."""

    def run(*args):
        return run_swc(*args, cwd=swc_repo)

    return run, swc_repo


@pytest.fixture
def swc_initialised(swc):
    """Like `swc` but with `workload init` pre-run.

    The workload.json sits under `.swc/feature_test-cli/workload.json` per
    the `/` → `_` folder-naming convention.
    """
    run, repo = swc
    result = run("workload", "init")
    assert result.returncode == 0, f"init failed: {result.stderr}"
    return run, repo
