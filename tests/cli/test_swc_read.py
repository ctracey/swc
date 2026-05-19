"""Tier 2 — scenario tests for `swc workload read` and folder-layout invariants.

REQ-22 (read item details), REQ-30 (workitem folders named by hash, never by number),
REQ-31 (citation form from --json payload).
"""

import json


def test_req22_read_returns_title_and_description_via_swc(swc_initialised):
    """`swc workload read 1 --json` returns title + description; description
    is loaded from <folder>/workitems/<hash>/requirements.md.
    """
    run, repo = swc_initialised
    run("workload", "add", "the item")
    listed = json.loads(run("workload", "list", "--json").stdout)["items"]
    item_id = listed[0]["id"]

    # Seed a description file at the conventional path.
    folder = repo / ".swc" / "feature_test-cli"
    workitem_dir = folder / "workitems" / item_id
    workitem_dir.mkdir(parents=True, exist_ok=True)
    (workitem_dir / "requirements.md").write_text("the description here")

    result = run("workload", "read", "1", "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["title"] == "the item"
    assert "the description here" in payload["description"]


def test_req30_workitem_folder_named_by_hash_not_number(swc_initialised):
    """`read` resolves the description path under workitems/<hash>/, never
    workitems/<number>/.
    """
    run, repo = swc_initialised
    run("workload", "add", "thing")
    listed = json.loads(run("workload", "list", "--json").stdout)["items"]
    item_id = listed[0]["id"]

    folder = repo / ".swc" / "feature_test-cli"
    hash_folder = folder / "workitems" / item_id
    hash_folder.mkdir(parents=True, exist_ok=True)
    (hash_folder / "requirements.md").write_text("body")

    result = run("workload", "read", "1", "--json")
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert "body" in payload["description"]

    numeric = folder / "workitems" / "1"
    assert not numeric.exists(), "workitem folder should NOT be named by number"


def test_req31_citation_form_from_read_json(swc_initialised):
    """`read --json` payload carries hash + title; consumers can format
    `[<hash>] <title>` citations from it.
    """
    run, repo = swc_initialised
    run("workload", "add", "cli tool for workload")
    result = run("workload", "read", "1", "--json")
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    citation = f"[{payload['id']}] {payload['title']}"
    assert citation.startswith("[")
    assert payload["id"] in citation
    assert payload["title"] in citation
