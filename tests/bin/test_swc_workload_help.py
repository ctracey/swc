"""Tier 1 — direct tests against `bin/swc_workload --help` and subcommand help.

These confirm REQ-29 holds at the bottom layer; the swc-tier equivalents
(swc workload --help) are covered separately and exercise the wrapper's
preamble + delegation.
"""

import subprocess
import sys
from pathlib import Path

SWC_WORKLOAD = Path(__file__).resolve().parent.parent.parent / "bin" / "swc_workload"


def _run(*args):
    return subprocess.run(
        [sys.executable, str(SWC_WORKLOAD), *args],
        capture_output=True,
        text=True,
    )


def test_top_level_help_lists_all_ops():
    result = _run("--help")
    assert result.returncode == 0
    out = result.stdout
    for op in ("init", "add", "delete", "list", "start", "complete", "reset", "exists"):
        assert op in out, f"top-level help missing {op!r}"
    # Should mention the required --workload flag.
    assert "--workload" in out or "swc workload" in out.lower()


def test_subcommand_help_describes_flags():
    result = _run("add", "--help")
    assert result.returncode == 0
    out = result.stdout
    assert "add" in out
    assert "to" in out and "at" in out
    assert "--workload" in out


def test_subcommand_help_works_without_workload_flag():
    """argparse short-circuits --help before requiring --workload, so
    `swc_workload list --help` exits 0 without needing a workload path.
    """
    result = _run("list", "--help")
    assert result.returncode == 0
    assert "--filter" in result.stdout
