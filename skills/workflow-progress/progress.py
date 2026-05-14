#!/usr/bin/env python3
"""Render a workflow progress banner. Outputs JSON with a single `output` field."""

import json
import sys

ARROW = " \u2192 "
RULE_CHAR = "\u2500"


def render(title: str, stages: list[str], active: str) -> str:
    if active and active not in stages:
        return json.dumps({"error": f"Active stage '{active}' not found in stages: {stages}"}, ensure_ascii=False)

    total = len(stages)
    done = not active

    if done:
        stage_parts = stages[:]
        bar = "■" * total
        position = total
    else:
        stage_parts = [s.upper() if s == active else s for s in stages]
        position = stages.index(active) + 1
        bar = "".join("■" if i < position - 1 else "▣" if i == position - 1 else "□" for i in range(total))

    stages_line = "[ " + ARROW.join(stage_parts) + " ]"
    plain_stages = "[ " + ARROW.join(stages) + " ]"

    right = f"{bar}({position}/{total})"
    title_prefix = f"WORKFLOW({title})"  # visible chars only (no markdown)
    # Rule must be wide enough for both the stages line and the title line
    rule_width = max(55, len(plain_stages), len(title_prefix) + len(right))
    rule = RULE_CHAR * rule_width

    padding = rule_width - len(title_prefix) - len(right)
    title_line = f"WORKFLOW({title}){' ' * padding}{right}"
    return json.dumps({"output": "\n".join([title_line, rule, stages_line])}, ensure_ascii=False)


HELP = """
usage: echo '<json>' | python3 progress.py

Renders a workflow progress banner and outputs JSON with a single `output` field
containing the formatted markdown string.

Input JSON fields:
  title   Workflow name displayed at the top
  stages  Comma-separated ordered list of stage names
  active  Name of the current stage (must match one entry in stages).
          Pass "" (empty string) to indicate all stages are complete.

Workflow lifecycle:
  Start  — pass the first stage as active: ▣□□(1/N)
  Middle — pass any stage as active:       ■▣□(K/N)
  Done   — pass active as "":             ■■■(N/N), no stage highlighted

Output JSON:
  {"output": "<markdown string>"}

Examples:
  echo '{"title":"deploy","stages":"build,test,release","active":"test"}' | python3 progress.py
  echo '{"title":"deploy","stages":"build,test,release","active":""}' | python3 progress.py

Output format:
  WORKFLOW(**<title>**) <bar>(<position>/<total>)
  <rule>
  [ stage1 → **ACTIVE** → stage3 ]
"""


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print(HELP.strip())
        sys.exit(0)
    data = json.loads(sys.stdin.read())
    stages = [s.strip() for s in data["stages"].split(",")]
    print(render(data["title"], stages, data["active"]))


if __name__ == "__main__":
    main()
