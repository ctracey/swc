# Changelog

## Session — usage docs: MCP setup steps `2026-06-01`

- `docs/usage.md` — added Step 2 substeps (2.1 trigger setup by attempting an SWC workflow, 2.2 follow guide or have it installed by the MCP setup skill, 2.3 what gets installed) and a new Step 3 smoke test.
- Marked workload items 1.1 (MCP server config registered manually outside this session) and 1.3 (docs updated) done.
- Motivation: complete the user-facing setup story for item 1 plumbing — first-time users now have a clear "trigger → guide → install → verify" path.

## Session — MCP dependency check + placeholder install guide `2026-06-01`

- Added `swc:mcp-check` skill — silent dependency probe; delegates to `swc:mcp-install` when the `mcp__swc-workload__*` tool namespace is unavailable.
- Added `swc:mcp-install` skill — surfaces the missing-MCP message and points the user at `https://github.com/ctracey/swc-workload-mcp/blob/main/docs/usage.md`.
- Wired `mcp-check` into `context-init` (Step 0) and front-line workflow skills `workflowPlan`, `workflowDeliver`, `report`, `ship` (Step 0a after `setup-permissions`).
- Expanded item 1 in `workload.md` with new sub-items 1.4, 1.5, 1.6 and marked them done.
- Notes: added `MCP dependency handling (agreed)` section capturing the check pattern, trigger points, and the rejection of a `PreToolUse` hook fallback (hooks can't fire when the tool is unregistered).
- Motivation: do the error scenario first — if the MCP isn't installed, users hit a clear guide before any silent failure. Items 1.1/1.2/1.3 (register, allowlist, docs) still pending.

## Session — delete superseded workload-mechanics skills `2026-06-01`

- Deleted `skills/workload/` (`SKILL.md` + `workload.py`), `skills/workload-update/`, `skills/workload_item-start/`, `skills/context--workload/` — five files, 270 lines.
- Marked work item 2 and sub-items 2.1–2.4 done in `workload.md`.
- Wrote workitem docs under `.swc/feature_mcp-workload-migration/workitems/2/` (requirements, specs, solution, context, summary, code-review-findings).
- Motivation: clear plugin ownership of workload artefact mechanics ahead of MCP rewrites (items 3–6). Callers (`workflowDeliver`, `workflowImplement_orient`, `skill--naming`) are transiently broken until items 5–6 land in the same PR — accepted per plan.
