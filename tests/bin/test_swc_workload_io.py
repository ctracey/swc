"""Tier 1 — direct tests against `bin/swc_workload --workload <tmp-folder>`.

Read / report ops (list / show / find / summary), JSON output,
schema validation, and JSON-decode error path. These don't depend on
branch resolution so they're covered directly.

The `--workload` contract is folder-path: tests pass `tmp_path` (the
folder); swc_workload resolves <folder>/workload.json internally.
"""

import json
import re

from conftest import run_swc_workload


# ---------------------------------------------------------------------------
# REQ-14 / REQ-20 — find returns all matches
# ---------------------------------------------------------------------------


def test_find_returns_all_matches(swcw_ready):
    run, workload = swcw_ready
    run("add", "cli tool one")
    run("add", "two")
    run("add", "cli wrapper")
    run("add", "cli plugin")

    result = run("find", "cli", "--json")
    assert result.returncode == 0
    matches = json.loads(result.stdout)["matches"]
    titles = [m["title"] for m in matches]
    assert len(matches) == 3
    assert all("cli" in t for t in titles)


def test_find_single_match(swcw_ready):
    run, workload = swcw_ready
    run("add", "boring")
    run("add", "workload radiator")
    run("add", "other thing")

    result = run("find", "workload radiator")
    assert result.returncode == 0
    assert "workload radiator" in result.stdout
    assert "boring" not in result.stdout


# ---------------------------------------------------------------------------
# REQ-15 — resolve by number or hash ID
# ---------------------------------------------------------------------------


def test_resolve_by_number(swcw_ready):
    run, workload = swcw_ready
    run("add", "one")
    run("add", "two")
    run("add", "a", "to", "2")
    run("add", "b", "to", "2")

    result = run("list", "2", "--json")
    assert result.returncode == 0, result.stderr
    items = json.loads(result.stdout)["items"]
    assert items[0]["number"] == "2"
    assert items[0]["title"] == "two"
    assert len(items[0]["children"]) == 2


def test_resolve_by_hash_id(swcw_ready):
    run, workload = swcw_ready
    run("add", "one")
    run("add", "target")
    run("add", "a", "to", "2")

    listed = json.loads(run("list", "--json").stdout)["items"]
    target_id = listed[1]["id"]

    result = run("list", target_id, "--json")
    assert result.returncode == 0
    items = json.loads(result.stdout)["items"]
    assert items[0]["id"] == target_id
    assert items[0]["title"] == "target"


# ---------------------------------------------------------------------------
# REQ-16 — reference not found
# ---------------------------------------------------------------------------


def test_reference_not_found(swcw_ready):
    run, workload = swcw_ready
    run("add", "one")
    result = run("list", "9.9")
    assert result.returncode != 0
    assert "not found" in result.stderr.lower()


# ---------------------------------------------------------------------------
# REQ-17 — list renders full tree with status symbols
# ---------------------------------------------------------------------------


def test_list_renders_full_tree_with_symbols(swcw_ready):
    run, workload = swcw_ready
    run("add", "one")
    run("add", "two")
    run("add", "2a", "to", "2")
    run("complete", "1")
    run("start", "2.1")

    result = run("list")
    assert result.returncode == 0
    out = result.stdout
    assert "one" in out and "two" in out and "2a" in out
    assert "✔" in out  # done
    assert "▣" in out  # in-progress


# ---------------------------------------------------------------------------
# REQ-18 — list with --filter / --exclude
# ---------------------------------------------------------------------------


def test_list_filter_status_in_progress(swcw_ready):
    run, workload = swcw_ready
    run("add", "a")
    run("add", "b")
    run("add", "c")
    run("complete", "1")
    run("start", "2")

    result = run("list", "--filter", "status:in-progress", "--json")
    assert result.returncode == 0
    items = json.loads(result.stdout)["items"]
    titles = [i["title"] for i in items]
    assert "b" in titles
    assert "a" not in titles
    assert "c" not in titles


def test_list_exclude_status_done(swcw_ready):
    run, workload = swcw_ready
    run("add", "a")
    run("add", "b")
    run("add", "c")
    run("complete", "1")
    run("start", "2")

    result = run("list", "--exclude", "status:done", "--json")
    assert result.returncode == 0
    items = json.loads(result.stdout)["items"]
    titles = [i["title"] for i in items]
    assert "a" not in titles
    assert "b" in titles
    assert "c" in titles


# ---------------------------------------------------------------------------
# REQ-19 — `list <ref>` renders that item plus its descendants
# (folded into `list` from the former `show` subcommand)
# ---------------------------------------------------------------------------


def test_list_with_ref_renders_item_with_children(swcw_ready):
    run, workload = swcw_ready
    run("add", "one")
    run("add", "parent")
    run("add", "kid-a", "to", "2")
    run("add", "kid-b", "to", "2")

    result = run("list", "2")
    assert result.returncode == 0
    out = result.stdout
    assert "parent" in out
    assert "kid-a" in out
    assert "kid-b" in out
    assert "one" not in out


def test_list_with_ref_and_filter_scopes_to_subtree(swcw_ready):
    """Filters apply to the subtree rooted at the ref'd item. apply_filters
    keeps a parent when any descendant matches, so the ref'd item shows up
    whenever something inside it matches."""
    run, workload = swcw_ready
    run("add", "parent")
    run("add", "a", "to", "1")
    run("add", "b", "to", "1")
    run("add", "c", "to", "1")
    run("start", "1.2")

    result = run("list", "1", "--filter", "status:in-progress", "--json")
    assert result.returncode == 0, result.stderr
    items = json.loads(result.stdout)["items"]
    # `parent` survives because a descendant matches; only the matching child remains.
    assert len(items) == 1
    assert items[0]["title"] == "parent"
    titles = [c["title"] for c in items[0]["children"]]
    assert titles == ["b"]


# ---------------------------------------------------------------------------
# REQ-21 — summary
# ---------------------------------------------------------------------------


def test_summary_partial(swcw_ready):
    run, workload = swcw_ready
    for i in range(10):
        run("add", f"item {i}")
    for i in range(1, 5):
        run("complete", str(i))
    for i in range(5, 8):
        run("start", str(i))

    result = run("summary", "--json")
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["total"] == 10
    assert payload["done"] == 4
    assert payload["wip"] == 3
    assert payload["progress"] == 40


def test_summary_text_includes_wip(swcw_ready):
    run, workload = swcw_ready
    run("add", "a")
    run("add", "b")
    run("start", "1")
    result = run("summary")
    assert result.returncode == 0
    assert "wip=1" in result.stdout


# ---------------------------------------------------------------------------
# REQ-28 — --json output shape
# ---------------------------------------------------------------------------


def test_list_json_is_parseable_tree(swcw_ready):
    run, workload = swcw_ready
    run("add", "a")
    run("add", "b")
    run("add", "b1", "to", "2")

    result = run("list", "--json")
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    items = payload["items"]
    assert len(items) == 2
    for item in items:
        assert "id" in item
        assert "title" in item
        assert "status" in item
        assert "children" in item
    assert len(items[1]["children"]) == 1


def test_list_without_json_is_text(swcw_ready):
    run, workload = swcw_ready
    run("add", "alpha")
    result = run("list")
    assert result.returncode == 0
    try:
        json.loads(result.stdout)
        is_json = True
    except json.JSONDecodeError:
        is_json = False
    assert not is_json
    assert "alpha" in result.stdout


# ---------------------------------------------------------------------------
# REQ-31 — citation: hash shown in text output
# ---------------------------------------------------------------------------


def test_text_output_includes_hash_next_to_title(swcw_ready):
    run, workload = swcw_ready
    run("add", "the thing")
    listed = json.loads(run("list", "--json").stdout)["items"]
    item_id = listed[0]["id"]

    result = run("list")
    assert result.returncode == 0
    assert re.search(rf"\({item_id}\)\s+the thing", result.stdout)


# ---------------------------------------------------------------------------
# F-07 / F-09 — schema validation + JSON decode error
# ---------------------------------------------------------------------------


def test_load_workload_rejects_malformed_shape(swcw_ready):
    run, workload = swcw_ready
    malformed = {
        "items": [{"id": "abc1234", "title": "broken", "children": []}],
    }
    workload.write_text(json.dumps(malformed, indent=2))

    result = run("list")
    assert result.returncode != 0
    msg = result.stderr.lower()
    assert "workload.json" in msg or "invalid" in msg
    assert "status" in msg


def test_load_workload_rejects_top_level_non_dict(swcw_ready):
    run, workload = swcw_ready
    workload.write_text(json.dumps(["not", "a", "dict"]))
    result = run("list")
    assert result.returncode != 0
    msg = result.stderr.lower()
    assert "invalid" in msg or "workload.json" in msg


def test_load_workload_json_decode_error_reports_line_and_column(swcw_ready):
    run, workload = swcw_ready
    workload.write_text('{"items": [')  # truncated
    result = run("list")
    assert result.returncode != 0
    msg = result.stderr.lower()
    assert "workload.json invalid" in msg
    assert "line" in msg
    assert "column" in msg
    assert "<root>" not in result.stderr


# ---------------------------------------------------------------------------
# init at the swc_workload layer — pure file creation
# ---------------------------------------------------------------------------


def test_init_creates_workload_json_inside_supplied_folder(swcw):
    """swc_workload init creates workload.json inside --workload <folder>.

    No branch awareness; the folder must already exist (per the new contract).
    """
    run, workload = swcw
    assert not workload.exists()
    result = run("init")
    assert result.returncode == 0, result.stderr
    assert workload.exists()
    data = json.loads(workload.read_text())
    assert data == {"items": []}


def test_init_refuses_to_overwrite_existing_file(swcw_ready):
    """swc_workload init refuses to overwrite an existing workload.json."""
    run, workload = swcw_ready
    original = workload.read_text()
    result = run("init")
    assert result.returncode != 0
    assert str(workload) in (result.stdout + result.stderr) or "already exists" in result.stderr.lower()
    assert workload.read_text() == original


# ---------------------------------------------------------------------------
# Missing-workload path at the swc_workload layer (non-init)
# ---------------------------------------------------------------------------


def test_op_on_missing_workload_recommends_init(swcw):
    """At the bottom tier, a non-init op against a missing path errors clearly."""
    run, workload = swcw
    result = run("list")
    assert result.returncode != 0
    assert "init" in result.stderr.lower()


# ---------------------------------------------------------------------------
# --workload <folder> contract: folder must exist + must be a directory
# ---------------------------------------------------------------------------


def test_workload_folder_does_not_exist_errors_clearly(tmp_path):
    """--workload pointing at a nonexistent folder produces a clear error.

    Replaces the older cryptic "workload already exists" message that fired
    when a folder was passed but no workload.json was inside it.
    """
    missing = tmp_path / "no-such-folder"
    result = run_swc_workload("list", workload=missing)
    assert result.returncode != 0
    msg = result.stderr.lower()
    assert "does not exist" in msg
    assert "folder" in msg


def test_workload_pointed_at_a_file_errors_clearly(tmp_path):
    """--workload <some-file> (not a directory) produces a clear error."""
    f = tmp_path / "not-a-folder.json"
    f.write_text("{}")
    result = run_swc_workload("list", workload=f)
    assert result.returncode != 0
    msg = result.stderr.lower()
    assert "folder" in msg
    assert "file" in msg


def test_init_requires_folder_to_exist(tmp_path):
    """`init --workload <missing-folder>` errors — does NOT create the folder."""
    missing = tmp_path / "no-such-folder"
    result = run_swc_workload("init", workload=missing)
    assert result.returncode != 0
    assert "does not exist" in result.stderr.lower()
    assert not missing.exists(), "init should not create the folder"


# ---------------------------------------------------------------------------
# Pass 9 — `exists` at the swc_workload layer: pure file-presence check
#
# Lenient contract: returns false (exit 0) for missing folder, wrong-type
# folder, or folder-without-workload.json. Returns true only when the
# folder exists, is a directory, and contains workload.json. Never errors.
# ---------------------------------------------------------------------------


def test_exists_false_when_folder_is_missing(tmp_path):
    """Folder does not exist → false; lenient — does not error."""
    missing = tmp_path / "no-such-folder"
    result = run_swc_workload("exists", workload=missing)
    assert result.returncode == 0
    assert result.stdout.strip().lower() == "false"
    assert result.stderr == ""


def test_exists_false_when_path_is_a_file(tmp_path):
    """Path is a file, not a directory → false; lenient — does not error."""
    f = tmp_path / "not-a-folder.json"
    f.write_text("{}")
    result = run_swc_workload("exists", workload=f)
    assert result.returncode == 0
    assert result.stdout.strip().lower() == "false"
    assert result.stderr == ""


def test_exists_false_when_folder_exists_but_no_workload_json(swcw):
    """Folder exists but no workload.json inside → false."""
    run, workload = swcw
    assert not workload.exists()
    result = run("exists")
    assert result.returncode == 0
    assert result.stdout.strip().lower() == "false"
    assert result.stderr == ""


def test_exists_true_when_workload_json_present(swcw_ready):
    """Folder exists and workload.json is present → true."""
    run, workload = swcw_ready
    assert workload.exists()
    result = run("exists")
    assert result.returncode == 0
    assert result.stdout.strip().lower() == "true"
    assert result.stderr == ""


def test_exists_json_form_true(swcw_ready):
    """`--json` emits a structured boolean."""
    run, workload = swcw_ready
    result = run("exists", "--json")
    assert result.returncode == 0
    assert json.loads(result.stdout) == {"exists": True}


def test_exists_json_form_false(swcw):
    """`--json` emits a structured boolean even when no workload exists."""
    run, workload = swcw
    result = run("exists", "--json")
    assert result.returncode == 0
    assert json.loads(result.stdout) == {"exists": False}


# ---------------------------------------------------------------------------
# F-04 — OSError surfaces as a friendly error, not a Python traceback
# ---------------------------------------------------------------------------


def test_oserror_in_save_workload_surfaces_as_friendly_error(tmp_path):
    """A PermissionError raised inside save_workload (via a read-only folder)
    surfaces as `file system error: ...` rather than a multi-line traceback.

    Run as a separate test (not via `swcw`) so we can build the read-only
    folder ourselves. Some environments (root, certain CI) ignore the chmod;
    in that case the inner CLI succeeds and the test self-skips.
    """
    import pytest
    import stat as _stat

    folder = tmp_path / "ro-folder"
    folder.mkdir()
    # Drop write permission. POSIX-only; on Windows this is a no-op.
    folder.chmod(_stat.S_IRUSR | _stat.S_IXUSR)
    try:
        result = run_swc_workload("init", workload=folder)
        if result.returncode == 0:
            pytest.skip("read-only chmod not honoured in this environment")
        msg = result.stderr.lower()
        assert "file system error" in msg or "permission" in msg, (
            f"expected friendly OSError message, got: {result.stderr!r}"
        )
        assert "traceback" not in msg, "raw Python traceback leaked"
    finally:
        # Restore so pytest can clean up tmp_path.
        folder.chmod(_stat.S_IRWXU)
