# Changelog

## Session — rename code-reviewer agent to match naming convention `2026-05-08`

- Renamed `agents/swc_code-reviewer.md` → `agents/code-reviewer.md` — `code` is the object, `reviewer` is the action, matching the SWC `-` separator convention
- Fixed frontmatter opening delimiter in agent file (`--` → `---`)
- Updated all references in `workflowDeliver_refine/SKILL.md`, including correcting `subagent_type` to fully-qualified `swc:code-reviewer`

## Session — rename swc_push to ship, fix stale skill references `2026-05-06`

- Renamed `swc_push` skill folder to `ship` and removed redundant `name` frontmatter field — reflects the agreed workflow language where work items are shipped into the release package
- Swept all skills for stale `swc_`-prefixed cross-skill references; corrected to bare skill names (`context-lookup`, `workload_item-start`, `workflow-orchestrator`, `workload-update`, `workload`, `workflowImplement`)
- Removed `swc:` namespace prefix introduced during the rename — within-plugin references use bare names only

