# Changelog

## Session — rename swc_push to ship, fix stale skill references `2026-05-06`

- Renamed `swc_push` skill folder to `ship` and removed redundant `name` frontmatter field — reflects the agreed workflow language where work items are shipped into the release package
- Swept all skills for stale `swc_`-prefixed cross-skill references; corrected to bare skill names (`context-lookup`, `workload_item-start`, `workflow-orchestrator`, `workload-update`, `workload`, `workflowImplement`)
- Removed `swc:` namespace prefix introduced during the rename — within-plugin references use bare names only

