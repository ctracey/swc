# Changelog

## Session — close item 4 terminology + track sweep `2026-06-02`

- 4.4 — adjacent "No matching workload" → "No matching context" in Step 2 of `context-lookup/SKILL.md`. The headline string was already corrected during the script-backed refactor.
- `context-lookup/SKILL.md` description, arguments, and goal — replaced "workload folder" / "workload" with "context folder" / "context" where they referred to the parent folder (not the MCP-owned workload artefact).
- Added 5.14 to track a terminology sweep across other skills (`report-*`, `context--files`, `workload` skill body, any 5.x leftovers) once the bulk of 5.x is in.
- Item 4 closed; all five sub-items done.

## Session — multi-folder picker, script-backed lookup, PreToolUse hook `2026-06-02`

- **4.3** Multi-folder case in `context-lookup` now lists candidates as compact `{name, location, workload}` with `mcp__swc-workload__exists` per row. Header renamed to "Multiple contexts found"; trailing prompt to "fresh context".
- **4.5** Backed `context-lookup` with `context-lookup.py` — single-call `probe` collapses 5–7 model-driven tool calls into one for the happy path; `persist` writes `_meta.json` mapping. Interactive cases and the single MCP `exists` call stay in the skill. SKILL.md rewritten as a thin conductor.
- **Item 9** New top-level item: PreToolUse hook for workload-context enforcement.
  - `hooks/swc-workload-guard.py` — resolves expected workload from `_meta.json` + current branch, denies the call with an informative reason on mismatch / missing arg / no mapping. Allows silently when the arg matches.
  - `hooks/hooks.json` — registers the matcher `mcp__swc-workload__.*` via `${CLAUDE_PLUGIN_ROOT}`.
  - Initial hooks.json shape was missing the top-level `"hooks"` wrapper required by Claude Code's plugin hook schema — fixed once the user couldn't see hooks load even after reinstall. Hook now firing.
- **notes.md** Updated the MCP dependency handling section — reframed the earlier `PreToolUse` hook rejection. The skill-based `mcp-check` handles the "not installed" case; the hook handles the "wrong workload arg" case. Complementary, not alternatives.
- Motivation: testing revealed the model bypasses `context-lookup` when calling MCP tools directly (different prompt phrasings hit different code paths). The hook is the only mechanism that enforces context consistency uniformly across every MCP call.

## Session — context-lookup reframe + workload skill restored `2026-06-01`

- `skills/context-lookup/SKILL.md` — single-folder confirm and locate-mode return now print `Found context {type, source, name, location, workload}` instead of `Located: .swc/<folder>/workload.md`. `workload` field populated via `mcp__swc-workload__exists`.
- `allowed-tools` updated to include `Skill` and `mcp__swc-workload__exists`.
- New `skills/workload/SKILL.md` — wraps `context-lookup` + `mcp__swc-workload__list` + render with status symbols. Replaces the skill deleted in item 2.1, refactored to use MCP. Restores the "list workitems" entry point so context-lookup runs upstream of MCP list (otherwise the model bypassed it).
- Tracked as new workload item 5.13 — added and marked done.
- Marked workload items 4.1 and 4.2 done; item 4 in progress (4.3 and 4.4 still outstanding).
- Motivation: gap surfaced during testing — "list workitems" bypassed `context-lookup` once the wrapper skill was deleted, so the new `Found context {...}` line never appeared. Bringing back the thin wrapper restores the lookup → render flow.

## Session — context-init delegates workload artefact to MCP `2026-06-01`

- `skills/context-init/SKILL.md` — dropped the `workload.md` stub block; added a new Step 2 that invokes `mcp__swc-workload__init` against the resolved folder; renumbered return to Step 3.
- Frontmatter `allowed-tools` updated to include `Skill` (for `mcp-check`) and `mcp__swc-workload__init`.
- Marked workload items 3.1, 3.2, 3.3 done; item 3 (Adapt `context-init`) rolls up to done.

## Session — setup-permissions allowlists MCP tools `2026-06-01`

- `skills/setup-permissions/SKILL.md` — added `mcp__swc-workload__*` to the allowlist Step 4 writes; Step 2 idempotency check now verifies all three entries (`Skill(swc:*)`, `Read(<swc_skills_path>/*)`, `mcp__swc-workload__*`) so existing projects re-run picks up the new MCP entry.
- Marked workload item 1.2 done; item 1 (Plumbing) rolls up to done.
- Permission syntax confirmed via claude-code-guide: `mcp__<server>__*` (wildcard form) is canonical, no `Tool()`/`MCP()` wrapper needed.

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
