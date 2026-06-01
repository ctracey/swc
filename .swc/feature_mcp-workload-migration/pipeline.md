# Pipeline

## Build

**Command:** `pytest tests/` (existing test suite)
**Expected outcome:** all tests pass; new MCP‑touching tests pass against mock or fixture

## Dev environment

**Start command:** Not applicable — plugin is loaded by Claude Code at session start
**Health check:** Skills appear under `/swc:` in the session
**Stop command:** Not applicable

## Acceptance

Reviewer can:
1. Install the MCP at project level following its repo's instructions
2. Run `/swc:workflowPlan` end‑to‑end and produce a workload via MCP
3. Run `/swc:workflowDeliver <N>` and see work item resolution + status updates flowing through MCP
4. Run `/swc:report` and see the workload rendered by MCP
5. Confirm no references to `workload.md` remain in plugin skills (search: `workload.md`)
