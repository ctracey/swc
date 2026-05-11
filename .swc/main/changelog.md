# Changelog

## Session — workload restructure for docs epics `2026-05-11`

- Marked 2.1 (update tests for scenarios) done
- Reorganised section 2 sub-items: nested "including usage" and "pattern docs" under 2.2 (docs for swc); nested "plugin usage" and "plugin marketplace" under 2.3 (build instructions)

## Session — ship skill branch and PR enforcement `2026-05-08`

- Updated `ship` skill to check for `main`/`master` branch early and prompt to create a feature branch before proceeding
- PR step now always creates a PR with a summary + motivation body if one doesn't exist, rather than optionally commenting
- `git push` updated to `git push -u origin <branch>` to handle new branches correctly

## Session — rename code-reviewer agent to match naming convention `2026-05-08`

- Renamed `agents/swc_code-reviewer.md` → `agents/code-reviewer.md` — `code` is the object, `reviewer` is the action, matching the SWC `-` separator convention
- Fixed frontmatter opening delimiter in agent file (`--` → `---`)
- Updated all references in `workflowDeliver_refine/SKILL.md`, including correcting `subagent_type` to fully-qualified `swc:code-reviewer`

## Session — rename swc_push to ship, fix stale skill references `2026-05-06`

- Renamed `swc_push` skill folder to `ship` and removed redundant `name` frontmatter field — reflects the agreed workflow language where work items are shipped into the release package
- Swept all skills for stale `swc_`-prefixed cross-skill references; corrected to bare skill names (`context-lookup`, `workload_item-start`, `workflow-orchestrator`, `workload-update`, `workload`, `workflowImplement`)
- Removed `swc:` namespace prefix introduced during the rename — within-plugin references use bare names only

