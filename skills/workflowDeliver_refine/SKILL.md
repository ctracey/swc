---
description: Refine stage of the delivery workflow — spawn code-reviewer, present findings to user, resolve or defer to tech debt, loop if needed. Fifth stage of the delivery workflow. Use when invoked by workflowDeliver or via /workflowDeliver_refine.
allowed-tools: Read, Write, Edit, Glob, Bash, Agent
---

# Deliver — Refine Stage

Runs after the implementation agent returns. Spawns `code-reviewer`, presents findings to the user, and manages the quality loop. The user decides what to resolve and what to accept as tech debt.

## Context

The work item number, name, and context folder path are available from the calling context. If missing, resolve the active context via `context-lookup`.

## Steps

### 1. Check preconditions

Confirm `summary.md` exists at `.swc/<folder>/workitems/<N>/summary.md`. If not, surface the gap:

> "No summary.md found for work item [N]. The implement stage must complete before refine can run."

Stop and return to the orchestrator.

### 2. Spawn code-reviewer

Use the Agent tool:

```
Agent(
  subagent_type: "swc:code-reviewer",
  description: "Review code for work item [N]",
  prompt: "Review work item [N]: [name].

Context folder: .swc/<folder>/
Work item folder: .swc/<folder>/workitems/<N>/

Read requirements.md, specs.md (if present), solution.md (if present), summary.md (latest pass), context.md (latest pass), and all code files listed in the summary Changes section.

Write findings to: .swc/<folder>/workitems/<N>/code-review-findings.md"
)
```

Wait for the agent to return.

### 3. Read findings

Read `.swc/<folder>/workitems/<N>/code-review-findings.md`.

Extract:
- Verdict (`BLOCK`, `WARN`, or `PASS`)
- List of findings with severity and description

### 4. Handle verdict

**PASS** — no action needed. Announce and advance:

> "Review complete — no issues found. Advancing to review."

Return control to the orchestrator.

**WARN or BLOCK** — present findings to the user:

> "Review complete — [N] finding(s):
>
> [For each finding:]
> **F-NN** ([severity]) `file:line` — [description]
>
> For each finding, choose:
> - **Resolve** — implement agent will address this in the next pass
> - **Tech debt** — accept and document; will not block Gate 3
>
> (Or resolve/defer all at once if the choice is consistent)"

Collect the user's decisions. Group findings into:
- `to_resolve` — findings the user wants fixed
- `to_defer` — findings accepted as tech debt

### 5. Handle tech debt

For each finding in `to_defer`, append to `.swc/<folder>/tech-debt.md`:

```markdown
## [work item N] — F-NN: [short title] — <YYYY-MM-DD>

**Severity:** [warn|info]
**Location:** `file:line`
**Description:** [copy from findings]
**Accepted because:** [user's reason, or "accepted during delivery of [N]"]
```

Create the file if it doesn't exist.

### 6. Loop if needed

If `to_resolve` is non-empty:

Track the loop count (start at 1, increment each iteration). If this is the first pass through the loop, announce:

> "Spawning implementation agent — pass [N] — to address [count] finding(s)."

Spawn a fresh implementation agent via the Agent tool (same prompt as `workflowDeliver_implement`, with findings appended):

```
Agent(
  subagent_type: "general-purpose",
  mode: "bypassPermissions",
  description: "Implement work item [N] — pass [P] (resolve review findings)",
  prompt: "You are an implementation agent for work item [N], pass [P].

Use the context-lookup skill to find the active context, then invoke `mcp__swc-workload__list` with `ref=[N]`, `json=true`, and `workload` set to the context's `absolute_path` to confirm the name and details for work item [N].

Follow the workflowImplement skill to complete this pass.

REVIEW FINDINGS TO RESOLVE:
[paste the to_resolve findings verbatim]

Address each finding. Update summary.md (append a new pass section). Update context.md (append a new pass section). The spec must still pass.

CONSTRAINTS — you may NOT:
- Run git commit, git push, git tag, or any variant
- Run gh commands (pull requests, issues, releases)
- Push or publish anything to a remote"
)
```

After the agent returns, re-run from step 2 (spawn reviewer again, fresh findings).

**Loop limit:** After 2 loops (implement → review → implement → review), if findings remain, do not loop again autonomously. Escalate to the user:

> "After 2 passes, [N] finding(s) remain:
> [list remaining findings]
>
> How would you like to proceed?
> 1. **Another pass** — implement agent will address these
> 2. **Accept as tech debt** — document and advance to Gate 3
> 3. **Stop** — halt here and review manually"

Wait for the user's choice and act accordingly.

### 7. Advance

Once all findings are resolved or deferred, announce:

> "Refine complete. [N] finding(s) resolved, [N] deferred to tech-debt.md. Advancing to review."

Return control to the orchestrator.

## Exit criteria

**Done when:**
- `code-reviewer` has run at least once
- Verdict is PASS, or all WARN/BLOCK findings are resolved or deferred to tech-debt.md
- Any tech debt appended to `.swc/<folder>/tech-debt.md`
- User has been involved in any defer decisions

**Return control to the calling skill.**
