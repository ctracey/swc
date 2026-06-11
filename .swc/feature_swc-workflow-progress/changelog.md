# Changelog

## Session — version skill + workflow manifest persistence `2026-06-11`

- Added `/version` skill: single-line report of SWC plugin, MCP server, and CLI versions; Python script gates MCP availability via settings file inspection, shows `N/A` when not registered
- Added `context-initWorkflowManifest` skill: writes `workflow-manifest.json` to the context folder with all workflow stage definitions; triggered by `context-init` after workload init with soft-fail semantics
- Updated `context-init` step 3 to delegate to `context-initWorkflowManifest` after successful workload init
- Updated `.claude/settings.json` with permissions for the swc plugin skill path
- Items 3 and 6 delivered and marked done

