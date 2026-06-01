# Changelog

## Session — delete superseded workload-mechanics skills `2026-06-01`

- Deleted `skills/workload/` (`SKILL.md` + `workload.py`), `skills/workload-update/`, `skills/workload_item-start/`, `skills/context--workload/` — five files, 270 lines.
- Marked work item 2 and sub-items 2.1–2.4 done in `workload.md`.
- Wrote workitem docs under `.swc/feature_mcp-workload-migration/workitems/2/` (requirements, specs, solution, context, summary, code-review-findings).
- Motivation: clear plugin ownership of workload artefact mechanics ahead of MCP rewrites (items 3–6). Callers (`workflowDeliver`, `workflowImplement_orient`, `skill--naming`) are transiently broken until items 5–6 land in the same PR — accepted per plan.
