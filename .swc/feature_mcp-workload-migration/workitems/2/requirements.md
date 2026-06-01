# Requirements — 2: Delete superseded artefact‑mechanics skills

## Intent

Remove the four plugin skills that own workload artefact mechanics now that `swc-workload-mcp` will own this responsibility. Targets: `skills/workload/` (including `workload.py`), `skills/workload-update/`, `skills/workload_item-start/`, and `skills/context--workload/`. Deleting these clears the way for the workflow-skill rewrites in items 3–6 to call the MCP instead of the now-removed in-process helpers.

## Constraints

- Delete only the four named folders — no edits to caller skills in this work item (those rewrites are tracked separately under items 5 and 6).
- Plugin will be transiently broken between this item and the completion of items 5/6 — accepted in the plan ("Deletes before rewrites to avoid maintaining dead code mid-refactor"). The PR as a whole is the review unit, not this commit.

## Out of scope

- Edits to skills that *call* the deleted skills (`workflowDeliver`, `workflowImplement_orient`, `skill--naming` examples, etc.) — covered by items 5, 6, 7.
- Changelog references to deleted skills — historical, leave intact.
- Tests exercising deleted code — covered by item 8.1.

## Approach direction

Four `rm -rf` operations against the absolute skill paths. Verify each folder is gone. No code edits.
