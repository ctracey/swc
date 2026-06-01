---
description: Accept stage of the delivery workflow — confirm work item completion, mark done, and commit/push via ship. Seventh stage of the delivery workflow. Use when invoked by workflowDeliver or via /workflowDeliver_accept.
allowed-tools: Read, Write, Edit, Bash, Skill, Glob, mcp__swc-workload__set_status
---

# Deliver — Accept Stage

Closes the work item loop: confirms the user is ready to mark the item done, updates the workload status, and triggers commit and push.

## Context

The work item number and name are available from the calling context. If missing, read the active workload via `context-lookup`.

## Steps

### 1. Run final test check

Read `.swc/<folder>/workitems/<N>/pipeline.md` to find the test command. If `pipeline.md` does not exist or defines no test command, skip this step silently.

If a test command is found, run it via Bash. Then report the result inline:

> "Final test check: [pass — N tests passed] / [FAIL — N failures]"

**If tests fail:** surface the failure output and ask:

> "Tests are failing. How would you like to proceed?
> 1. **Fix first** — pause here, address the failures, then re-run accept
> 2. **Push anyway** — continue with known failures (not recommended)"

Wait for the user's choice. If they choose fix first, stop here and return control to the orchestrator. If they choose push anyway, continue.

### 2. Recap and confirm

Open with a brief, high-level recap anchored to the work item:

> "Work item **[N]: [name]** has been reviewed and accepted.
>
> Ready to mark it done and push?"

Wait for the user's response.

### 3. Happy path — mark done and push

If the user confirms:

1. Invoke `mcp__swc-workload__set_status` against the resolved folder with the work item number and status `done`. The MCP handles parent rollup.
2. Invoke `ship` to commit and push.

### 4. Not ready path — collect feedback

If the user is not ready, ask what's left:

> "What still needs to be done before this is ready to close?"

Listen and collect their feedback. Play it back:

> "So the remaining work is: [summary]. Is that right?"

Correct and re-confirm if needed.

Write to `.swc/<folder>/workitems/<N>/feedback.md` (replace any existing file):

```markdown
# Feedback — [work item number]: [work item name]

[The confirmed feedback, verbatim as the user described it]
```

Announce:

> "Feedback captured. Re-launching the delivery workflow — requirements will open with your feedback as context."

Invoke `workflowDeliver` with the work item number as the argument.

## Exit criteria

**Done when (happy path):**
- Work item marked `done` via `mcp__swc-workload__set_status`
- `ship` invoked and completed
- Control returned to orchestrator

**Done when (feedback path):**
- Feedback confirmed by user
- `feedback.md` written to `.swc/<folder>/workitems/<N>/`
- Delivery workflow re-launched

**Return control to the calling skill.**
