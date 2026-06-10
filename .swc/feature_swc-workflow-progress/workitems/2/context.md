## Pass 1 — 2026-06-10

- **Decision:** Created `skills/workflowProgress-record/SKILL.md` as the encapsulated meta write skill. It takes explicit `workflow`, `stage`, `workItem`, and `workload` args from the orchestrator — no implicit context resolution needed inside the skill because the orchestrator already has that information.
- **Decision:** `meta.swc.workflowState` is keyed by workflow name so deliver and implement workflows coexist without collision. `meta.swc.workflowEvents` is a single shared chronological log across all workflows.
- **Decision:** Timestamp generated via Python `datetime.now(timezone.utc)` — consistent UTC ISO-8601 without relying on shell `date` portability.
- **Decision:** `mcp__swc-workload__list` removed from orchestrator's allowed-tools — the orchestrator delegates to `workflowProgress-record` (via Skill) which owns the MCP calls. Orchestrator only calls `context-lookup` (a Skill) for workload path resolution.
- **Decision:** REQ-03 (no active work item) handled in the orchestrator itself, not inside `workflowProgress-record`. The skill is only called when `workItem` is present — cleaner than having the skill check for presence and warn.
- **Assumption:** `context-lookup` resolving the workload path once before the stages loop (reused per stage) is safe — the path doesn't change mid-workflow.
- **Completed:** All 5 acceptance scenarios addressed. New skill `skills/workflowProgress-record/SKILL.md` created. Orchestrator updated with `workItem` schema field and step 2 meta-write hook. Test scenario file written at `tests/swc/workflowProgress_meta-write.md`.
