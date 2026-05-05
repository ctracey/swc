#!/usr/bin/env python3
"""Render a workload.md file as a visual task list. Outputs JSON with a single `output` field."""

import json
import re
import sys

DONE = "\u2714"        # ✔
IN_PROGRESS = "\u25a3" # ▣
NOT_STARTED = "\u25a1" # □


def status_symbol(marker: str) -> str:
    if marker == "x":
        return DONE
    if marker == "-":
        return IN_PROGRESS
    return NOT_STARTED


def format_item(symbol: str, text: str, indent: int) -> str:
    prefix = "  " * indent
    return f"{prefix}{symbol} {text}"


# Matches lines like:  - [x] 1.2. **Title** or  - [ ] plain text
ITEM_RE = re.compile(r"^(\s*)-\s+\[([x \-])\]\s+(.+)$")


def parse_workload(content: str) -> list[dict]:
    items = []
    for line in content.splitlines():
        m = ITEM_RE.match(line)
        if not m:
            continue
        indent_spaces = len(m.group(1))
        marker = m.group(2).strip() or " "
        # Normalise: space → not started, - → in progress, x → done
        if marker == " ":
            marker = " "
        raw_text = m.group(3)
        # Strip markdown bold markers
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", raw_text)
        # Indent level: base list is 0 spaces; each extra 2 spaces is one level deeper
        level = indent_spaces // 2
        items.append({"marker": marker, "text": text, "level": level})
    return items


def render(path: str) -> str:
    try:
        with open(path) as f:
            content = f.read()
    except FileNotFoundError:
        return json.dumps({"error": f"File not found: {path}"})

    items = parse_workload(content)
    if not items:
        return json.dumps({"error": "No work items found in workload file."})

    lines = [f"WORKLOAD  {path}"]
    # Find the minimum indent level to use as baseline
    min_level = min(i["level"] for i in items)
    for item in items:
        symbol = status_symbol(item["marker"])
        display_indent = item["level"] - min_level
        lines.append(format_item(symbol, item["text"], display_indent))

    return json.dumps({"output": "\n".join(lines)})


HELP = """
usage: echo '<json>' | python3 workload.py

Parses a workload.md and renders work items with visual status symbols.

Input JSON fields:
  path   Absolute path to the workload.md file

Output JSON:
  {"output": "<text string>"}   — rendered task list
  {"error": "<message>"}        — if the file is missing or has no items

Status symbols:
  ✔  Done        (combining strikethrough applied to text)
  ▣  In progress
  □  Not started

Example:
  echo '{"path":"/home/user/.swc/feature_foo/workload.md"}' | python3 workload.py
"""


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print(HELP.strip())
        sys.exit(0)
    data = json.loads(sys.stdin.read())
    print(render(data["path"]))


if __name__ == "__main__":
    main()
