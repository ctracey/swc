# Requirements — 1.4.2.6 & 1.4.2.7: Accept stage + status tracking in delivery workflow

## Intent

Two lifecycle gaps in the delivery workflow need closing. First, after Gate 3 (review), the workflow currently ends with "ready for commit and push" but takes no action — commit and push are left to the user. Second, work item status is never updated during the delivery lifecycle: items stay `[ ]` throughout and are never automatically marked in-progress or done. These two items are delivered together because they share the same lifecycle boundary — the new `accept` stage is the natural place to resolve both.

## Constraints

- `swc_push` handles commit and push — the `accept` stage invokes it, does not re-implement git operations
- Only the current work item is marked done — other items in the same PR are unaffected
- The recap in the `accept` stage names the work item (number + description) but stays high-level — it does not re-litigate the review
- `[-]` in-progress marking happens in `swc_workflow_deliver` before the first stage runs, not inside the `accept` stage

## Out of scope

- Batch acceptance of multiple work items
- CI/CD pipeline triggering or deployment — `swc_push` commits and pushes to the PR branch only

## Approach direction

Add an `accept` stage to the delivery workflow (after `review`) backed by a new `swc_workflow_deliver-accept` skill. The stage confirms the user is ready to close the named work item, marks it `[x]`, and invokes `swc_push`. If the user is not ready, it collects feedback and re-launches the delivery workflow from `requirements` for another pass. Status tracking: `swc_workflow_deliver` marks the work item `[-]` immediately before the orchestrator starts running stages.

## Parked

- Feedback path re-entry point: confirmed as `requirements` (same pattern as the review stage feedback path), not a later stage
- Stage name considered and rejected: `uplink`, `lgtm`, `close`, `lock`, `land` — user settled on `accept` as clean and consistent with the dry naming convention of the other stages
