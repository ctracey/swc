"""Tier 1 — direct tests against `cli/swc_workload --workload <tmp-path>`.

Authoring ops (add / remove / rename / reorder / move) — covers the
tree-manipulation edge cases that don't depend on branch resolution:
hash uniqueness, move keyword validation, cycle rejection, same-parent move
semantics, downgrade-guard, schema validation.
"""

import json


# ---------------------------------------------------------------------------
# add — REQ-03 / REQ-04 surface against the path-driven CLI
# ---------------------------------------------------------------------------


def test_add_appends_top_level_item_with_hash_id(swcw_ready):
    run, workload = swcw_ready
    run("add", "first")
    run("add", "second")
    result = run("add", "build a thing")
    assert result.returncode == 0, result.stderr

    listed = run("list", "--json")
    items = json.loads(listed.stdout)["items"]
    assert len(items) == 3
    assert items[2]["title"] == "build a thing"
    assert items[2]["number"] == "3"
    assert len(items[2]["id"]) == 7


def test_add_assigns_unique_hashes_when_titles_collide(swcw_ready):
    """Hash uniqueness — same title added twice must produce two distinct IDs."""
    run, workload = swcw_ready
    run("add", "duplicate title")
    run("add", "duplicate title")
    listed = run("list", "--json")
    items = json.loads(listed.stdout)["items"]
    ids = [i["id"] for i in items]
    assert len(set(ids)) == 2, f"expected unique hash IDs, got {ids}"


def test_add_rejects_dotted_number_prefix_title(swcw_ready):
    run, workload = swcw_ready
    result = run("add", "1.1 something")
    assert result.returncode != 0
    msg = result.stderr.lower()
    assert "number" in msg or "automatically" in msg


def test_add_accepts_leading_digits_without_dot(swcw_ready):
    run, workload = swcw_ready
    result = run("add", "12 monkeys")
    assert result.returncode == 0, result.stderr
    items = json.loads(run("list", "--json").stdout)["items"]
    assert items[0]["title"] == "12 monkeys"


def test_add_as_child_of_parent(swcw_ready):
    run, workload = swcw_ready
    run("add", "one")
    run("add", "two")
    result = run("add", "sub item", "--parent", "2")
    assert result.returncode == 0, result.stderr
    items = json.loads(run("list", "--json").stdout)["items"]
    assert items[1]["children"][0]["title"] == "sub item"
    assert items[1]["children"][0]["number"] == "2.1"


# ---------------------------------------------------------------------------
# remove
# ---------------------------------------------------------------------------


def test_remove_drops_item_and_descendants_with_renumber(swcw_ready):
    run, workload = swcw_ready
    run("add", "one")
    run("add", "two")
    run("add", "three")
    run("add", "two-a", "--parent", "2")
    run("add", "two-b", "--parent", "2")

    result = run("remove", "2")
    assert result.returncode == 0, result.stderr
    items = json.loads(run("list", "--json").stdout)["items"]
    titles = [i["title"] for i in items]
    assert titles == ["one", "three"]
    assert items[1]["number"] == "2"


# ---------------------------------------------------------------------------
# rename — REQ-06 / REQ-07
# ---------------------------------------------------------------------------


def test_rename_preserves_id_status_position(swcw_ready):
    run, workload = swcw_ready
    run("add", "one")
    run("add", "two")
    run("add", "x", "--parent", "2")
    run("add", "y", "--parent", "2")
    run("add", "target", "--parent", "2")
    run("status", "2.3", "in-progress")

    before = json.loads(run("list", "--json").stdout)["items"]
    target_id = before[1]["children"][2]["id"]

    result = run("rename", "2.3", "new title")
    assert result.returncode == 0, result.stderr

    after = json.loads(run("list", "--json").stdout)["items"]
    target = after[1]["children"][2]
    assert target["title"] == "new title"
    assert target["id"] == target_id
    assert target["status"] == "in-progress"
    assert target["number"] == "2.3"


def test_rename_rejects_dotted_number_prefix(swcw_ready):
    run, workload = swcw_ready
    run("add", "first")
    result = run("rename", "1", "2.3 new title")
    assert result.returncode != 0
    items = json.loads(run("list", "--json").stdout)["items"]
    assert items[0]["title"] == "first"


# ---------------------------------------------------------------------------
# reorder
# ---------------------------------------------------------------------------


def test_reorder_up_preserves_ids(swcw_ready):
    run, workload = swcw_ready
    run("add", "parent")
    for label in ("a", "b", "c"):
        run("add", label, "--parent", "1")
    before = json.loads(run("list", "--json").stdout)["items"][0]["children"]
    ids = [c["id"] for c in before]

    result = run("reorder", "1.3", "up")
    assert result.returncode == 0, result.stderr

    after = json.loads(run("list", "--json").stdout)["items"][0]["children"]
    assert [c["title"] for c in after] == ["a", "c", "b"]
    assert {c["id"] for c in after} == set(ids)


def test_reorder_top_moves_to_first_slot(swcw_ready):
    run, workload = swcw_ready
    run("add", "p")
    for label in ("a", "b", "c"):
        run("add", label, "--parent", "1")
    result = run("reorder", "1.3", "top")
    assert result.returncode == 0
    after = json.loads(run("list", "--json").stdout)["items"][0]["children"]
    assert [c["title"] for c in after] == ["c", "a", "b"]
    assert after[0]["number"] == "1.1"


# ---------------------------------------------------------------------------
# move — keyword validation, cycle, missing-parent, same-parent semantics
# ---------------------------------------------------------------------------


def test_move_reparents_and_reflows_both_sides(swcw_ready):
    run, workload = swcw_ready
    for label in ("one", "two", "three"):
        run("add", label)
    for label in ("2a", "2b", "2c"):
        run("add", label, "--parent", "2")
    run("add", "moveme", "--parent", "2.3")  # 2.3.1
    for label in ("3a", "3b"):
        run("add", label, "--parent", "3")

    before = json.loads(run("list", "--json").stdout)["items"]
    target_id = before[1]["children"][2]["children"][0]["id"]

    result = run("move", "2.3.1", "to", "3.2")
    assert result.returncode == 0, result.stderr

    after = json.loads(run("list", "--json").stdout)["items"]
    three_children = after[2]["children"]
    assert [c["title"] for c in three_children] == ["3a", "moveme", "3b"]
    assert three_children[1]["id"] == target_id
    assert three_children[1]["number"] == "3.2"
    assert after[1]["children"][2]["children"] == []


def test_move_rejects_cycle(swcw_ready):
    run, workload = swcw_ready
    run("add", "one")
    run("add", "two")
    for label in ("2a", "2b", "2c"):
        run("add", label, "--parent", "2")
    run("add", "deep", "--parent", "2.3")  # 2.3.1

    before = json.loads(run("list", "--json").stdout)["items"]
    result = run("move", "2", "to", "2.3.1")
    assert result.returncode != 0
    assert "cycle" in result.stderr.lower()
    after = json.loads(run("list", "--json").stdout)["items"]
    assert after == before


def test_move_rejects_missing_target_parent(swcw_ready):
    run, workload = swcw_ready
    run("add", "one")
    run("add", "two")
    run("add", "2a", "--parent", "2")

    before = json.loads(run("list", "--json").stdout)["items"]
    result = run("move", "2.1", "to", "9.9")
    assert result.returncode != 0
    msg = result.stderr.lower()
    assert "not exist" in msg or "does not" in msg
    after = json.loads(run("list", "--json").stdout)["items"]
    assert after == before


def test_move_rejects_unexpected_keyword_between_ref_and_target(swcw_ready):
    """F-01: typo `too` instead of literal `to` must fail loudly and leave the tree untouched."""
    run, workload = swcw_ready
    for label in ("one", "two"):
        run("add", label)
    for label in ("2a", "2b"):
        run("add", label, "--parent", "2")

    before = json.loads(run("list", "--json").stdout)["items"]
    result = run("move", "2.1", "too", "2.2")
    assert result.returncode != 0
    msg = result.stderr.lower()
    assert "too" in msg or "unexpected" in msg or "'to'" in msg
    after = json.loads(run("list", "--json").stdout)["items"]
    assert after == before


def test_move_accepts_literal_to_keyword(swcw_ready):
    """F-01 sibling: the literal `to` between ref and target still works."""
    run, workload = swcw_ready
    run("add", "one")
    run("add", "two")
    result = run("move", "2", "to", "1")
    assert result.returncode == 0, result.stderr


def test_move_accepts_omitted_to_keyword(swcw_ready):
    """F-01 sibling: the optional keyword may be omitted entirely."""
    run, workload = swcw_ready
    run("add", "one")
    run("add", "two")
    result = run("move", "2", "1")
    assert result.returncode == 0, result.stderr


def test_move_leaves_orphaned_parent_status_untouched(swcw_ready):
    """F-02 pinned policy: when `move` empties a parent's children, the
    parent's status is preserved — it does NOT auto-revert to not-started.
    """
    run, workload = swcw_ready
    run("add", "one")
    run("add", "parent")
    run("add", "kid", "--parent", "2")
    run("status", "2.1", "in-progress")

    before = json.loads(run("list", "--json").stdout)["items"]
    assert before[1]["status"] == "in-progress"

    result = run("move", "2.1", "to", "2")
    assert result.returncode == 0, result.stderr

    after = json.loads(run("list", "--json").stdout)["items"]
    orphaned = next(i for i in after if i["title"] == "parent")
    assert orphaned["children"] == []
    assert orphaned["status"] == "in-progress"


def test_move_same_parent_source_after_target_lands_at_requested_position(swcw_ready):
    """Final-position semantics: `move 2.3 to 2.1` against [a, b, c] → [c, a, b]."""
    run, workload = swcw_ready
    run("add", "one")
    run("add", "two")
    for label in ("2a", "2b", "2c"):
        run("add", label, "--parent", "2")

    result = run("move", "2.3", "to", "2.1")
    assert result.returncode == 0, result.stderr

    after = json.loads(run("list", "--json").stdout)["items"]
    titles = [c["title"] for c in after[1]["children"]]
    assert titles == ["2c", "2a", "2b"]


def test_move_same_parent_source_before_target_lands_at_requested_position(swcw_ready):
    """F-08 final-position semantics: `move 2.1 to 2.3` against [a, b, c] → [b, c, a].

    Regression guard for the removed `insert_idx -= 1` adjustment in cmd_move:
    if this assertion ever flips to [b, a, c], the adjustment has been re-added
    and must be removed again.
    """
    run, workload = swcw_ready
    run("add", "one")
    run("add", "two")
    for label in ("a", "b", "c"):
        run("add", label, "--parent", "2")

    ids_before = {c["title"]: c["id"]
                  for c in json.loads(run("list", "--json").stdout)["items"][1]["children"]}

    result = run("move", "2.1", "to", "2.3")
    assert result.returncode == 0, result.stderr

    after = json.loads(run("list", "--json").stdout)["items"]
    titles = [c["title"] for c in after[1]["children"]]
    ids_after = {c["title"]: c["id"] for c in after[1]["children"]}

    assert titles == ["b", "c", "a"], (
        f"expected [b, c, a] (final-position semantics); got {titles}. "
        "If this is [b, a, c], the removed `insert_idx -= 1` block has been re-added."
    )
    assert ids_after == ids_before
