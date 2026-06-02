---
description: Spawn implementation agent for a work item — pass work item number only, then evaluate and report exit criteria. Fourth stage of the delivery workflow. Use when spawning an implementation agent, or when invoked via /workflowDeliver_implement.
allowed-tools: Bash, Read, Glob, Agent
---

# Deliver — Implement Stage

Spawns a fresh implementation agent for the active work item, then evaluates and reports exit criteria.

## Context

The work item number is available from the calling context (set by `workflowDeliver` before the workflow started). If not available, resolve the active context via `context-lookup` and ask the user which item to implement. The implementation agent is responsible for discovering its own folder and work item name via `context-lookup` + `mcp__swc-workload__list` (with `ref=<N>`).

## Steps

### 1. Confirm the work item

Display the work item being handed to the implementation agent:

> "Spawning implementation agent for **[N]: [name]**."

### 2. Pre-flight health check (opt-in)

Ask the user:
> "Want to run a quick health check before spawning the agent? (y/n)"

**If no:** skip to step 3.

**If yes:**

1. Read `.swc/<folder>/workitems/<N>/solution.md` for check commands. If none found, read `architecture.md`. If still none, inform the user and skip:
   > "No check commands found in solution.md or architecture.md — skipping pre-flight."

2. Run each command and collect output.

3. Present results to the user — for each failure, include an assessment of whether it is in scope for this work item or pre-existing noise:
   > "Pre-flight results:
   > ✔ [command] — passed
   > ✗ [command] — [failure summary] _(in scope / pre-existing)_"

4. If any failures: ask the user how they want to proceed:
   > "Some checks failed. How would you like to proceed?"

   Wait for their response and capture it.

5. Write `.swc/<folder>/workitems/<N>/quality-baseline.md`:

   ```markdown
   # Quality Baseline — [N]: [name]

   ## Commands run

   - `[command]` — pass / fail: [brief result]

   ## Findings

   [Failure details and scope relevance assessment. Omit section if all passed.]

   ## Decisions

   [User's decision on each failure. Omit section if no failures.]
   ```

### 3. Spawn the implementation agent

Use the Agent tool to spawn a general-purpose agent. Pass only the work item number — the agent uses `context-lookup` to discover the context folder and `mcp__swc-workload__list` (with `ref=<N>`) to fetch the work item name and details.

If `quality-baseline.md` was written in step 2, include a note in the prompt so the agent reads it during orient.

```
Agent(
  subagent_type: "general-purpose",
  mode: "bypassPermissions",
  description: "Implement work item [N]",
  prompt: "You are an implementation agent for work item [N].

Use the context-lookup skill to find the active context, then invoke `mcp__swc-workload__list` with `ref=[N]`, `json=true`, and `workload` set to the context's `absolute_path` to confirm the name and details for work item [N].

Follow the workflowImplement skill to complete this work item.

[Include only if quality-baseline.md exists:]
A quality-baseline.md exists at .swc/<folder>/workitems/<N>/quality-baseline.md — read it during orient.
It records the pre-flight check results and user decisions on any failures.
Use the same commands to verify you have not introduced new failures before completing your pass.

CONSTRAINTS — you may NOT:
- Run git commit, git push, git tag, or any variant
- Run gh commands (pull requests, issues, releases)
- Push or publish anything to a remote

You MAY: read and write files, run build/test/lint commands, invoke skills, spawn subagents for review.
Delivery and git operations happen after user review — your job ends at a working, tested implementation."
)
```

Wait for the agent to return.

### 4. Evaluate exit criteria

After the agent completes, check `.swc/<folder>/workitems/<N>/` for outputs.

| Criterion | How to evaluate |
|-----------|----------------|
| Agent completed | Did the agent return without error? |
| Agent documented its progress | Does `context.md` exist at `.swc/<folder>/workitems/<N>/context.md`? |
| Summary report exists | Does `summary.md` exist at `.swc/<folder>/workitems/<N>/summary.md`? |
| Work item ready for review | Does `context.md` contain a completed pass section and no unresolved blockers? |

### 5. Report results

Display all four criteria with pass/fail status:

> **Implement stage — exit criteria:**
> - [pass/fail] Agent completed
> - [pass/fail] Agent documented its progress (`context.md`)
> - [pass/fail] Summary report exists (`summary.md`)
> - [pass/fail] Work item ready for review

### 6. Return control

Return to the orchestrator with the criteria evaluation result. Do not attempt to self-advance if criteria are unmet — the orchestrator handles the gate decision.

## Exit criteria

**Done when:**
- Agent returned without error
- `context.md` exists with at least one completed pass section — confirms orient ran
- `summary.md` exists — confirms the agent reached and completed the summarise stage (full workflow ran to completion)
- No unresolved blockers in `context.md`

**Return control to the calling skill.**
