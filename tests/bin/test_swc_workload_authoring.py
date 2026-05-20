"""Tier 1 — direct tests against `bin/swc_workload --workload <tmp-path>`.

Authoring ops (add / delete / rename / move) — covers the
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


def test_add_assigns_unique_hashes_when_titles_collide_across_parents(swcw_ready):
    """Hash uniqueness — same title under different parents must produce
    distinct hash IDs (sibling-collision check is same-parent only, so the
    duplicate is allowed across parents).
    """
    run, workload = swcw_ready
    run("add", "duplicate title")
    run("add", "duplicate title", "to", "1")
    listed = run("list", "--json")
    top = json.loads(listed.stdout)["items"][0]
    child = top["children"][0]
    assert top["id"] != child["id"], (
        f"expected distinct hashes for same title under different parents, "
        f"got {top['id']} and {child['id']}"
    )


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
    result = run("add", "sub item", "to", "2")
    assert result.returncode == 0, result.stderr
    items = json.loads(run("list", "--json").stdout)["items"]
    assert items[1]["children"][0]["title"] == "sub item"
    assert items[1]["children"][0]["number"] == "2.1"


def test_add_rejects_duplicate_sibling_title(swcw_ready):
    """Two siblings cannot share a title (full-string match, case-insensitive)."""
    run, workload = swcw_ready
    run("add", "first")
    result = run("add", "first")
    assert result.returncode != 0
    msg = result.stderr.lower()
    assert "collide" in msg or "first" in msg


def test_add_rejects_case_variant_duplicate_sibling_title(swcw_ready):
    """ASDF and asdf are considered the same title for sibling-collision purposes."""
    run, workload = swcw_ready
    run("add", "ASDF")
    result = run("add", "asdf")
    assert result.returncode != 0
    assert "collide" in result.stderr.lower()


def test_add_allows_same_title_under_different_parent(swcw_ready):
    """Sibling-collision is same-parent only — different parents may share titles."""
    run, workload = swcw_ready
    run("add", "alpha")  # top-level 1
    run("add", "beta")   # top-level 2
    result = run("add", "alpha", "to", "2")
    assert result.returncode == 0, result.stderr
    items = json.loads(run("list", "--json").stdout)["items"]
    assert items[0]["title"] == "alpha"
    assert items[1]["children"][0]["title"] == "alpha"
    assert items[1]["children"][0]["number"] == "2.1"


# ---------------------------------------------------------------------------
# add — `to <parent>` (append under) and `at <position>` (insert at slot)
# ---------------------------------------------------------------------------


def test_add_at_top_level_position_shifts_siblings_down(swcw_ready):
    """`add "x" at 2` inserts x at top-level position 2; existing siblings shift down."""
    run, workload = swcw_ready
    run("add", "a")
    run("add", "b")
    run("add", "c")

    result = run("add", "x", "at", "2")
    assert result.returncode == 0, result.stderr
    titles = [i["title"] for i in json.loads(run("list", "--json").stdout)["items"]]
    assert titles == ["a", "x", "b", "c"]


def test_add_at_nested_position_uses_parent_from_target(swcw_ready):
    """`add "x" at 2.1` inserts x as first child of item 2 (parent inferred)."""
    run, workload = swcw_ready
    run("add", "one")
    run("add", "two")
    run("add", "a", "to", "2")
    run("add", "b", "to", "2")

    result = run("add", "x", "at", "2.1")
    assert result.returncode == 0, result.stderr
    items = json.loads(run("list", "--json").stdout)["items"]
    titles = [c["title"] for c in items[1]["children"]]
    assert titles == ["x", "a", "b"]


def test_add_at_out_of_range_caps_at_end(swcw_ready):
    """Like `move`, an out-of-range slot caps at end — no error."""
    run, workload = swcw_ready
    run("add", "a")
    run("add", "b")

    result = run("add", "x", "at", "99")
    assert result.returncode == 0, result.stderr
    titles = [i["title"] for i in json.loads(run("list", "--json").stdout)["items"]]
    assert titles == ["a", "b", "x"]


def test_add_collision_uses_siblings_at_target_slot(swcw_ready):
    """Sibling-collision check uses the siblings at the target location.
    Inserting a same-title item under a different parent is allowed; inserting
    one alongside an existing same-titled sibling is rejected."""
    run, workload = swcw_ready
    run("add", "alpha")          # 1
    run("add", "two")            # 2
    run("add", "alpha", "to", "2")  # 2.1 — fine, different parent

    # Inserting another `alpha` at 2.2 collides with 2.1's `alpha`.
    result = run("add", "alpha", "at", "2.2")
    assert result.returncode != 0
    assert "collide" in result.stderr.lower()


def test_add_collision_is_case_insensitive_at_target_slot(swcw_ready):
    """Sibling collision check is case-insensitive at the target slot too."""
    run, workload = swcw_ready
    run("add", "ALPHA")
    result = run("add", "alpha", "at", "2")
    assert result.returncode != 0
    assert "collide" in result.stderr.lower()


def test_add_at_rejects_missing_target_parent(swcw_ready):
    """`at 9.9` when there's no item 9 is rejected with a clear error."""
    run, workload = swcw_ready
    run("add", "a")
    result = run("add", "x", "at", "9.9")
    assert result.returncode != 0
    assert "not exist" in result.stderr.lower() or "does not" in result.stderr.lower()


def test_add_rejects_extra_positional_after_target(swcw_ready):
    """Argparse only declares two optional positionals after `title`. Any extra
    args (e.g. an attempt to combine `to` and `at`) are rejected."""
    run, workload = swcw_ready
    run("add", "one")
    result = run("add", "x", "at", "1.1", "to", "1")
    assert result.returncode != 0
    # Argparse rejects "unrecognized arguments" or similar — exit non-zero is enough.


def test_add_to_requires_target(swcw_ready):
    """`add <title> to` without a target must error."""
    run, workload = swcw_ready
    run("add", "one")
    result = run("add", "x", "to")
    assert result.returncode != 0
    assert "target" in result.stderr.lower() or "to" in result.stderr.lower()


def test_add_at_requires_target(swcw_ready):
    """`add <title> at` without a target must error."""
    run, workload = swcw_ready
    run("add", "one")
    result = run("add", "x", "at")
    assert result.returncode != 0
    assert "target" in result.stderr.lower() or "at" in result.stderr.lower()


def test_add_rejects_unknown_placement_keyword(swcw_ready):
    """Second positional must be `to` or `at` (or omitted)."""
    run, workload = swcw_ready
    run("add", "one")
    result = run("add", "x", "in", "1")
    assert result.returncode != 0
    msg = result.stderr.lower()
    assert "'to'" in msg or "'at'" in msg or "expected" in msg


def test_add_at_rejects_non_numeric_target(swcw_ready):
    """`at` target must be a dotted-number reference; hash IDs / arbitrary strings rejected."""
    run, workload = swcw_ready
    run("add", "a")
    result = run("add", "x", "at", "abc1234")
    assert result.returncode != 0
    assert "number" in result.stderr.lower()


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------


def test_delete_drops_item_and_descendants_with_renumber(swcw_ready):
    run, workload = swcw_ready
    run("add", "one")
    run("add", "two")
    run("add", "three")
    run("add", "two-a", "to", "2")
    run("add", "two-b", "to", "2")

    result = run("delete", "2")
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
    run("add", "x", "to", "2")
    run("add", "y", "to", "2")
    run("add", "target", "to", "2")
    run("start", "2.3")

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


def test_rename_rejects_duplicate_sibling_title(swcw_ready):
    """Renaming an item to a sibling's title is rejected (case-insensitive)."""
    run, workload = swcw_ready
    run("add", "alpha")
    run("add", "beta")
    result = run("rename", "2", "ALPHA")
    assert result.returncode != 0
    msg = result.stderr.lower()
    assert "collide" in msg or "alpha" in msg
    items = json.loads(run("list", "--json").stdout)["items"]
    # Original title preserved.
    assert items[1]["title"] == "beta"


def test_rename_allows_no_op_self_rename(swcw_ready):
    """Renaming an item to its current title is a no-op, not a collision."""
    run, workload = swcw_ready
    run("add", "alpha")
    result = run("rename", "1", "alpha")
    assert result.returncode == 0, result.stderr


def test_rename_allows_case_change_of_own_title(swcw_ready):
    """Renaming an item to a case-variant of its own title is allowed
    (the item is excluded from its own collision check)."""
    run, workload = swcw_ready
    run("add", "alpha")
    result = run("rename", "1", "ALPHA")
    assert result.returncode == 0, result.stderr
    items = json.loads(run("list", "--json").stdout)["items"]
    assert items[0]["title"] == "ALPHA"


def test_rename_allows_same_title_as_non_sibling(swcw_ready):
    """Renaming to a title that exists elsewhere in the tree (but not as a
    sibling) is allowed."""
    run, workload = swcw_ready
    run("add", "alpha")  # 1
    run("add", "beta")   # 2
    run("add", "gamma", "to", "1")  # 1.1
    result = run("rename", "2", "gamma")  # not a sibling of 1.1
    assert result.returncode == 0, result.stderr


# ---------------------------------------------------------------------------
# move — direction form (relative shift among siblings)
# ---------------------------------------------------------------------------


def test_move_up_preserves_ids(swcw_ready):
    run, workload = swcw_ready
    run("add", "parent")
    for label in ("a", "b", "c"):
        run("add", label, "to", "1")
    before = json.loads(run("list", "--json").stdout)["items"][0]["children"]
    ids = [c["id"] for c in before]

    result = run("move", "1.3", "up")
    assert result.returncode == 0, result.stderr

    after = json.loads(run("list", "--json").stdout)["items"][0]["children"]
    assert [c["title"] for c in after] == ["a", "c", "b"]
    assert {c["id"] for c in after} == set(ids)


def test_move_top_moves_to_first_slot(swcw_ready):
    run, workload = swcw_ready
    run("add", "p")
    for label in ("a", "b", "c"):
        run("add", label, "to", "1")
    result = run("move", "1.3", "top")
    assert result.returncode == 0
    after = json.loads(run("list", "--json").stdout)["items"][0]["children"]
    assert [c["title"] for c in after] == ["c", "a", "b"]
    assert after[0]["number"] == "1.1"


def test_move_direction_rejects_unexpected_target(swcw_ready):
    """Direction form must not accept a target. `move 2 up 3` is an error."""
    run, workload = swcw_ready
    run("add", "one")
    run("add", "two")
    result = run("move", "2", "up", "1")
    assert result.returncode != 0
    msg = result.stderr.lower()
    assert "unexpected" in msg or "up" in msg


# ---------------------------------------------------------------------------
# move — `to <target>` form (absolute reposition; may reparent)
# ---------------------------------------------------------------------------


def test_move_reparents_and_reflows_both_sides(swcw_ready):
    run, workload = swcw_ready
    for label in ("one", "two", "three"):
        run("add", label)
    for label in ("2a", "2b", "2c"):
        run("add", label, "to", "2")
    run("add", "moveme", "to", "2.3")  # 2.3.1
    for label in ("3a", "3b"):
        run("add", label, "to", "3")

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
        run("add", label, "to", "2")
    run("add", "deep", "to", "2.3")  # 2.3.1

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
    run("add", "2a", "to", "2")

    before = json.loads(run("list", "--json").stdout)["items"]
    result = run("move", "2.1", "to", "9.9")
    assert result.returncode != 0
    msg = result.stderr.lower()
    assert "not exist" in msg or "does not" in msg
    after = json.loads(run("list", "--json").stdout)["items"]
    assert after == before


def test_move_rejects_unknown_second_token(swcw_ready):
    """Second positional must be a direction or the literal `to`. Anything
    else (typo, garbage) errors loudly and leaves the tree untouched.
    """
    run, workload = swcw_ready
    for label in ("one", "two"):
        run("add", label)
    for label in ("2a", "2b"):
        run("add", label, "to", "2")

    before = json.loads(run("list", "--json").stdout)["items"]
    result = run("move", "2.1", "too", "2.2")
    assert result.returncode != 0
    msg = result.stderr.lower()
    assert "too" in msg or "expected" in msg or "'to'" in msg
    after = json.loads(run("list", "--json").stdout)["items"]
    assert after == before


def test_move_to_requires_target(swcw_ready):
    """`move <ref> to` without a target must error — `to` form requires a target."""
    run, workload = swcw_ready
    run("add", "one")
    run("add", "two")
    result = run("move", "2", "to")
    assert result.returncode != 0
    assert "target" in result.stderr.lower()


def test_move_target_without_to_errors(swcw_ready):
    """Omitting the literal `to` between ref and target is now an error
    (previously was an accepted shorthand)."""
    run, workload = swcw_ready
    run("add", "one")
    run("add", "two")
    result = run("move", "2", "1")
    assert result.returncode != 0
    msg = result.stderr.lower()
    # Bare "1" isn't a direction or "to", so the dispatcher rejects it.
    assert "expected" in msg or "'to'" in msg or "1" in msg


def test_move_to_target_works(swcw_ready):
    """The canonical absolute form `move <ref> to <target>` works."""
    run, workload = swcw_ready
    run("add", "one")
    run("add", "two")
    result = run("move", "2", "to", "1")
    assert result.returncode == 0, result.stderr


def test_move_leaves_orphaned_parent_status_untouched(swcw_ready):
    """F-02 pinned policy: when `move` empties a parent's children, the
    parent's status is preserved — it does NOT auto-revert to not-started.
    """
    run, workload = swcw_ready
    run("add", "one")
    run("add", "parent")
    run("add", "kid", "to", "2")
    run("start", "2.1")

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
        run("add", label, "to", "2")

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
        run("add", label, "to", "2")

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
