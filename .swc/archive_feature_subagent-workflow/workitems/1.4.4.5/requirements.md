# Requirements — 1.4.4.5: Implementation workflow — mark work item as in-progress at start of orient stage

## Intent

When the implementation agent picks up a work item, the orient stage should mark it `[-]` (in-progress) in workload.md. This closes the gap where workload status required manual update — the agent now owns the `[ ]` → `[-]` transition as part of its normal orient flow.

## Constraints

- Must use `swc_workload-update`, not a direct edit to workload.md
- Must be idempotent — works correctly on pass 1, 2, 3 (re-marking `[-]` is safe)
- Must happen after the work item is confirmed from workload.md, not before

## Out of scope

- Marking the item done (`[x]`) — covered by a later work item
- Status changes on the blocked path
- Deliver-side status changes (covered by 1.4.2.7)

## Approach direction

Add a status update call to orient step 2, immediately after the work item is confirmed. Invoke `swc_workload-update` with the work item number and `in-progress`.
