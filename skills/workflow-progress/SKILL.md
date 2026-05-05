---
description: Print a workflow progress banner showing title, all stages, and the active stage highlighted. Use when starting a new stage in a multi-stage workflow, or when invoked via /workflow-progress.
allowed-tools: Bash
---

# SWC Progress

Emit a workflow progress banner framed with horizontal rules.

## Arguments

```
/workflow-progress title="process X" stages="stage 1,stage 2,stage 3" active="stage 2"
```

- `title` — workflow name
- `stages` — comma-separated ordered list of stage names
- `active` — name of the current stage (must match one entry in `stages`). Pass `""` to indicate all stages are complete.

## Instructions

Parse `title`, `stages`, and `active` from the arguments, then run:

```
echo '{"title": "...", "stages": "...", "active": "..."}' | python3 ${CLAUDE_SKILL_DIR}/progress.py
```

The script outputs either `{"output": "..."}` or `{"error": "..."}`. If `output`, emit it as your text response. If `error`, emit the error message. Do not add preamble or trailing text.
