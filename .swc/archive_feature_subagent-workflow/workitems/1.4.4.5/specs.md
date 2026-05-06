# Specs — 1.4.4.5: Implementation workflow — mark work item as in-progress at start of orient stage

## Acceptance criteria

- After orient runs, the target work item in workload.md is marked `[-]` (in-progress)
- The status update occurs after the work item is confirmed from workload.md (step 2), before any brief docs are read
- The update is made via `swc_workload-update`, not a direct file edit
- Behaviour is idempotent — running orient on a work item already marked `[-]` or `[x]` does not error or regress the status

## Error cases

- Orient must not mark the item done (`[x]`) — only `[-]`
