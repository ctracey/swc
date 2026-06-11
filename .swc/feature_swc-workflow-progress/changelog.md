# Changelog

## Session — cross-session resume via orchestrator `2026-06-11`

- `workflow-orchestrator`: reads `meta.swc.workflowState[<workflow>].currentStage` before the stage loop and offers to resume at the recorded stage (or restart); unknown stage or failed meta read degrades to a fresh run with a warning. Motivation: new sessions previously re-walked the deliver workflow from stage 1 on in-progress items
- `workflow-orchestrator`: records completion after the final stage via `workflow-recordProgress complete=true`
- `workflow-recordProgress`: new completion mode sets `{ currentStage: null, completed: true }` and appends a `completed` event; stage-entry writes now set `completed: false` so repeat passes (e.g. implement via the refine loop) aren't mistaken for finished runs
- Workflow definition schema gains an explicit `workItem` field; `workflowDeliver` and `workflowImplement` now pass the resolved item number in the handoff. Motivation: testing showed session-context inference was unreliable — the orchestrator skipped all meta writes when it wouldn't commit to an item
- New test scenarios `tests/swc/workflowResume_recorded-stage.md`; `architecture.md` re-synced to the shipped `meta.swc` schema (was still describing `swc-workflow-status`); manifest gap for pre-existing contexts noted as tech debt
- Verified by user: meta write fires at stage entry with the explicit `workItem` contract

## Session — version skill + workflow manifest persistence `2026-06-11`

- Added `/version` skill: single-line report of SWC plugin, MCP server, and CLI versions; Python script gates MCP availability via settings file inspection, shows `N/A` when not registered
- Added `context-initWorkflowManifest` skill: writes `workflow-manifest.json` to the context folder with all workflow stage definitions; triggered by `context-init` after workload init with soft-fail semantics
- Updated `context-init` step 3 to delegate to `context-initWorkflowManifest` after successful workload init
- Updated `.claude/settings.json` with permissions for the swc plugin skill path
- Items 3 and 6 delivered and marked done

