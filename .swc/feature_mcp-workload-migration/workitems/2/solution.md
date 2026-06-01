# Solution Design — 2: Delete superseded artefact‑mechanics skills

## Approach

Four directory deletions under the repo's `skills/` folder: `workload/`, `workload-update/`, `workload_item-start/`, `context--workload/`. No code edits. Verify each path exists before delete; verify gone after.

## Test approach

Lightweight — implement directly against spec checklist, no automated test file. Deletions are binary and observable via filesystem (and `git status`).

## Technical decisions

- **Target is the workspace repo, not the marketplace install** — deletions are against `/Users/tracer/workspace/tracer/swc/skills/`. The marketplace install at `/Users/tracer/claude-plugins/plugins/swc/skills/` is a separate clone and must not be touched.
- **Callers will break transiently** — `workflowDeliver`, `workflowImplement_orient`, `skill--naming` reference these skills. Plan accepts this between item 2 and items 5/6 within the same PR. No mitigation needed in this work item.
