"""Tier 1 — direct tests against `cli/swc_workload --workload <tmp-path>`.

Status updates, rollup, downgrade-guard, and the parent-marked-done warning
path. These are the highest-risk behaviours per solution.md, so they're
covered directly without the indirection of branch resolution.
"""

import json


# ---------------------------------------------------------------------------
# REQ-12 — status update and rollup
# ---------------------------------------------------------------------------


def test_marking_child_in_progress_rolls_parent_to_in_progress(swcw_ready):
    run, workload = swcw_ready
    run("add", "one")
    run("add", "two")
    run("add", "three")
    run("add", "3a", "--parent", "3")
    run("add", "3b", "--parent", "3")

    result = run("status", "3.2", "in-progress")
    assert result.returncode == 0, result.stderr

    after = json.loads(run("list", "--json").stdout)["items"]
    parent = after[2]
    assert parent["children"][1]["status"] == "in-progress"
    assert parent["status"] == "in-progress"


def test_marking_last_child_done_rolls_parent_to_done(swcw_ready):
    run, workload = swcw_ready
    run("add", "p")
    run("add", "a", "--parent", "1")
    run("add", "b", "--parent", "1")

    run("status", "1.1", "done")
    run("status", "1.2", "in-progress")
    result = run("status", "1.2", "done")
    assert result.returncode == 0, result.stderr

    after = json.loads(run("list", "--json").stdout)["items"]
    p = after[0]
    assert p["children"][1]["status"] == "done"
    assert p["status"] == "done"


# ---------------------------------------------------------------------------
# REQ-13 — done is sticky
# ---------------------------------------------------------------------------


def test_done_is_sticky_and_leaves_file_unchanged(swcw_ready):
    run, workload = swcw_ready
    run("add", "leaf")
    run("status", "1", "done")

    original = workload.read_text()
    result = run("status", "1", "in-progress")
    assert result.returncode == 0, result.stderr

    assert workload.read_text() == original

    after = json.loads(run("list", "--json").stdout)["items"]
    assert after[0]["status"] == "done"


# ---------------------------------------------------------------------------
# F-03 (a) — parent marked done with undone children warns on stderr
# ---------------------------------------------------------------------------


def test_parent_marked_done_with_undone_children_warns_on_stderr(swcw_ready):
    run, workload = swcw_ready
    run("add", "p")
    run("add", "a", "--parent", "1")
    run("add", "b", "--parent", "1")
    run("add", "c", "--parent", "1")

    run("status", "1.1", "done")
    before = workload.read_text()

    result = run("status", "1", "done")
    assert result.returncode == 0, result.stderr
    msg = result.stderr.lower()
    assert "warning" in msg
    assert "1" in result.stderr
    assert "done" in msg
    assert workload.read_text() != before
    after = json.loads(run("list", "--json").stdout)["items"]
    assert after[0]["status"] == "done"
