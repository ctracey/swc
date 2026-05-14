import json
import subprocess
import sys
from progress import render

ARROW = " \u2192 "
RULE_CHAR = "\u2500"


def test_active_stage_is_uppercase():
    result = json.loads(render("my workflow", ["a", "b", "c"], "b"))
    assert "B" in result["output"]
    assert "**B**" not in result["output"]


def test_inactive_stages_are_lowercase():
    result = json.loads(render("my workflow", ["a", "b", "c"], "b"))
    lines = result["output"].split("\n")
    stages_line = lines[2]
    assert "a" in stages_line
    assert "c" in stages_line


def test_title_is_not_bold():
    result = json.loads(render("my workflow", ["a", "b"], "a"))
    assert result["output"].startswith("WORKFLOW(my workflow)")
    assert "**" not in result["output"].split("\n")[0]


def test_title_includes_position_counter():
    result = json.loads(render("proj", ["a", "b", "c", "d"], "c"))
    assert "(3/4)" in result["output"].split("\n")[0]


def test_progress_bar():
    # active=c is index 2 (0-based): a=■, b=■, c=▣, d=□
    result = json.loads(render("proj", ["a", "b", "c", "d"], "c"))
    assert "■■▣□" in result["output"].split("\n")[0]


def test_counter_and_bar_right_aligned():
    stages = ["a", "b", "c", "d", "e", "f"]
    result = json.loads(render("my workflow", stages, "c"))
    title_line = result["output"].split("\n")[0]
    rule = result["output"].split("\n")[1]
    assert len(title_line) == len(rule)


def test_progress_bar_first_stage():
    result = json.loads(render("proj", ["a", "b", "c"], "a"))
    assert "▣□□" in result["output"].split("\n")[0]


def test_progress_bar_last_stage():
    result = json.loads(render("proj", ["a", "b", "c"], "c"))
    assert "■■▣" in result["output"].split("\n")[0]


def test_rule_width_matches_plain_stages_line():
    # Stages line is longer than 55 — rule must match it exactly
    stages = ["start", "design", "implement", "review", "finish", "deploy"]
    active = "design"
    result = json.loads(render("proj", stages, active))
    lines = result["output"].split("\n")
    rule = lines[1]
    plain_stages_line = "[ " + ARROW.join(stages) + " ]"
    assert len(rule) == len(plain_stages_line)
    assert all(c == RULE_CHAR for c in rule)


def test_rule_minimum_width():
    # Short stages line — rule must be at least 55 chars
    stages = ["start", "plan", "finish"]
    active = "plan"
    result = json.loads(render("proj", stages, active))
    rule = result["output"].split("\n")[1]
    assert len(rule) >= 55
    assert all(c == RULE_CHAR for c in rule)


def test_stages_line_wrapped_in_brackets():
    result = json.loads(render("t", ["x", "y"], "x"))
    lines = result["output"].split("\n")
    stages_line = lines[2]
    assert stages_line.startswith("[ ")
    assert stages_line.endswith(" ]")


def test_stdin_json_interface():
    payload = json.dumps({"title": "proj", "stages": "one,two,three", "active": "two"})
    proc = subprocess.run(
        [sys.executable, "progress.py"],
        input=payload,
        capture_output=True,
        text=True,
        cwd=__file__.rsplit("/", 1)[0],
    )
    assert proc.returncode == 0
    result = json.loads(proc.stdout)
    assert "TWO" in result["output"]
    assert "**TWO**" not in result["output"]


def test_help_flag():
    for flag in ("-h", "--help"):
        proc = subprocess.run(
            [sys.executable, "progress.py", flag],
            capture_output=True,
            text=True,
            cwd=__file__.rsplit("/", 1)[0],
        )
        assert proc.returncode == 0
        assert "usage:" in proc.stdout
        assert "title" in proc.stdout
        assert "stages" in proc.stdout
        assert "active" in proc.stdout


def test_done_state_full_bar():
    # Empty active → all stages complete, full bar of ■
    result = json.loads(render("proj", ["a", "b", "c"], ""))
    assert "■■■" in result["output"].split("\n")[0]


def test_done_state_counter_shows_total():
    result = json.loads(render("proj", ["a", "b", "c"], ""))
    assert "(3/3)" in result["output"].split("\n")[0]


def test_done_state_no_bold_stages():
    result = json.loads(render("proj", ["a", "b", "c"], ""))
    stages_line = result["output"].split("\n")[2]
    assert "**" not in stages_line


def test_unrecognised_active_stage_returns_error():
    result = json.loads(render("proj", ["a", "b", "c"], "z"))
    assert "error" in result
    assert "z" in result["error"]


def test_stages_with_whitespace_are_stripped():
    payload = json.dumps({"title": "t", "stages": "a , b , c", "active": "b"})
    proc = subprocess.run(
        [sys.executable, "progress.py"],
        input=payload,
        capture_output=True,
        text=True,
        cwd=__file__.rsplit("/", 1)[0],
    )
    result = json.loads(proc.stdout)
    assert "B" in result["output"]
    assert "**B**" not in result["output"]
